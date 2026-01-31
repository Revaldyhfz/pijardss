"""
Single Path Simulation.

Simulates one complete trajectory of the business over the time horizon.
This is the core unit of Monte Carlo simulation - we generate many paths
and analyze the distribution of outcomes.

Path Structure:
--------------
- Month 0: Initial state (capital, 0 customers)
- Months 1 to dev_duration: Development phase (burn only)
- Months dev_duration+1 to horizon: Sales phase (leads → customers → revenue)

Each path tracks:
- Equity curve (capital over time)
- Customer evolution
- Monthly P&L
- Risk events and regime states
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..distributions import (
    TriangularDistribution,
    BetaDistribution,
    LogNormalDistribution,
    GammaDistribution,
)
from ..processes import PoissonProcess, RegimeSwitchingModel, RegimeType
from .business_model import BusinessModel, BusinessState
from .risk_events import RiskEventManager, RiskEventConfig


@dataclass
class PathResult:
    """
    Result of a single path simulation.
    
    Contains all data needed for aggregation and analysis.
    """
    # Core outcomes
    initial_capital: float
    final_capital: float
    total_return: float  # (final - initial) / initial * 100
    max_drawdown: float  # As percentage
    breakeven_month: int  # -1 if never achieved
    is_ruin: bool  # capital <= 0
    
    # Time series
    equity_curve: NDArray
    monthly_pnl: NDArray
    customer_series: NDArray
    
    # Regime data
    regime_path: List[str]
    months_in_stress: int
    
    # Risk event data
    total_shocks: int
    shock_timeline: List[Tuple[int, str, float]]  # (month, type, severity)
    
    # Parameter realizations (for sensitivity analysis)
    realized_params: Dict[str, float]


class PathSimulator:
    """
    Simulates a single path of the business.
    
    Orchestrates the interaction between:
    - Business model (revenue, costs, churn)
    - Regime switching (economic conditions)
    - Risk events (discrete shocks)
    
    Parameters
    ----------
    business_model : BusinessModel
        Domain logic for revenue/costs
    regime_model : RegimeSwitchingModel, optional
        Economic regime dynamics
    risk_manager : RiskEventManager, optional
        Risk event handling
    time_horizon : int
        Number of months to simulate
    """
    
    def __init__(
        self,
        business_model: BusinessModel,
        regime_model: Optional[RegimeSwitchingModel] = None,
        risk_manager: Optional[RiskEventManager] = None,
        time_horizon: int = 36
    ):
        self.business_model = business_model
        self.regime_model = regime_model
        self.risk_manager = risk_manager
        self.time_horizon = time_horizon
    
    def simulate(
        self,
        initial_capital: float,
        dev_duration: int,
        dev_burn: float,
        leads_per_month: float,
        win_rate_bumn: float,
        win_rate_open: float,
        bumn_ratio: float,
        annual_churn_rate: float,
        rng: Generator
    ) -> PathResult:
        """
        Run a single path simulation.
        
        Parameters
        ----------
        initial_capital : float
            Starting capital
        dev_duration : int
            Months in development phase
        dev_burn : float
            Monthly burn during development
        leads_per_month : float
            Expected leads per month
        win_rate_bumn : float
            Win rate for BUMN deals
        win_rate_open : float
            Win rate for open market
        bumn_ratio : float
            Fraction of BUMN leads
        annual_churn_rate : float
            Annual customer churn rate
        rng : Generator
            Random number generator
            
        Returns
        -------
        PathResult
            Complete path results
        """
        # Initialize state
        state = BusinessState(
            capital=initial_capital,
            customers=0,
            peak_capital=initial_capital
        )
        
        # Initialize tracking arrays
        equity_curve = np.zeros(self.time_horizon + 1)
        equity_curve[0] = initial_capital
        monthly_pnl = np.zeros(self.time_horizon)
        customer_series = np.zeros(self.time_horizon + 1, dtype=np.int64)
        
        # Initialize regime
        regime_path = []
        current_regime = RegimeType.NORMAL
        months_in_stress = 0
        
        if self.regime_model:
            current_regime = self.regime_model.initial_regime
        
        # Initialize risk tracking
        if self.risk_manager:
            self.risk_manager.reset()
        shock_timeline = []
        total_shocks = 0
        
        # Lead arrival process
        lead_process = PoissonProcess(base_rate=leads_per_month)
        
        # Compute average contract value
        avg_contract = self.business_model.compute_avg_contract_value()
        
        # Store realized parameters for sensitivity analysis
        realized_params = {
            'initial_capital': initial_capital,
            'dev_duration': dev_duration,
            'dev_burn': dev_burn,
            'leads_per_month': leads_per_month,
            'win_rate_bumn': win_rate_bumn,
            'win_rate_open': win_rate_open,
            'annual_churn_rate': annual_churn_rate
        }
        
        # Main simulation loop
        is_ruin = False
        
        for month in range(self.time_horizon):
            # 1. Sample regime for this month
            if self.regime_model:
                current_regime = self.regime_model.sample_next_regime(current_regime, rng)
                regime_params = self.regime_model.get_parameters(current_regime)
                regime_multipliers = regime_params.to_dict()
                
                if current_regime == RegimeType.STRESS:
                    months_in_stress += 1
            else:
                regime_multipliers = {}
            
            regime_path.append(current_regime.value if self.regime_model else 'normal')
            
            # 2. Check for risk events
            risk_multipliers = {'adoption': 1.0, 'churn': 1.0, 'revenue': 1.0, 'cost': 1.0}
            
            if self.risk_manager:
                risk_intensity_mult = regime_multipliers.get('risk_intensity_multiplier', 1.0)
                new_shocks = self.risk_manager.check_for_arrivals(month, rng, risk_intensity_mult)
                
                for shock in new_shocks:
                    shock_timeline.append((month, shock.impact_type, shock.severity))
                    total_shocks += 1
                
                self.risk_manager.process_recoveries(rng)
                risk_multipliers = self.risk_manager.get_multipliers()
            
            # 3. Combine regime and risk multipliers
            combined_multipliers = {
                k: regime_multipliers.get(f'{k}_multiplier', 1.0) * risk_multipliers.get(k, 1.0)
                for k in ['adoption', 'churn', 'revenue', 'cost']
            }
            combined_multipliers['win_rate_multiplier'] = regime_multipliers.get('win_rate_multiplier', 1.0)
            
            # 4. Determine if in development phase
            is_dev_phase = month < dev_duration
            
            # 5. Business operations
            if is_dev_phase:
                # Development: no revenue, only burn
                revenue = 0.0
                costs = self.business_model.compute_costs(
                    state, True, dev_burn, combined_multipliers
                )
                new_customers = 0
                churned = 0
            else:
                # Sales phase
                # 5a. Generate leads
                effective_lead_rate = leads_per_month * combined_multipliers.get('adoption', 1.0)
                n_leads = rng.poisson(max(0, effective_lead_rate))
                
                # 5b. Process new leads into pipeline
                self.business_model.process_new_leads(
                    state, month, n_leads,
                    win_rate_bumn, win_rate_open, bumn_ratio,
                    rng, combined_multipliers
                )
                
                # 5c. Process pipeline closings
                new_customers = self.business_model.process_pipeline_closings(state, month)
                
                # 5d. Apply churn
                effective_churn = annual_churn_rate * combined_multipliers.get('churn', 1.0)
                churned = self.business_model.apply_churn(state, effective_churn, rng)
                
                # 5e. Compute revenue and costs
                revenue = self.business_model.compute_revenue(state, avg_contract, combined_multipliers)
                costs = self.business_model.compute_costs(state, False, 0, combined_multipliers)
            
            # 6. Update capital
            net_flow = revenue - costs
            state.capital += net_flow
            
            # 7. Update tracking
            state.update_drawdown()
            
            if state.breakeven_month == -1 and state.capital >= initial_capital and not is_dev_phase:
                state.breakeven_month = month + 1
            
            # Record time series
            monthly_pnl[month] = net_flow
            equity_curve[month + 1] = state.capital
            customer_series[month + 1] = state.customers
            
            state.monthly_revenues.append(revenue)
            state.monthly_costs.append(costs)
            state.monthly_customers.append(state.customers)
            state.monthly_new_customers.append(new_customers)
            state.monthly_churned.append(churned)
            
            # 8. Check for ruin
            if state.capital <= 0:
                is_ruin = True
                # Fill remaining months with final state
                for future_month in range(month + 2, self.time_horizon + 1):
                    equity_curve[future_month] = state.capital
                    customer_series[future_month] = 0
                for future_month in range(month + 1, self.time_horizon):
                    monthly_pnl[future_month] = 0
                break
        
        # Compute final metrics
        final_capital = state.capital
        total_return = (final_capital - initial_capital) / initial_capital * 100
        
        return PathResult(
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            max_drawdown=state.max_drawdown * 100,
            breakeven_month=state.breakeven_month,
            is_ruin=is_ruin,
            equity_curve=equity_curve,
            monthly_pnl=monthly_pnl,
            customer_series=customer_series,
            regime_path=regime_path,
            months_in_stress=months_in_stress,
            total_shocks=total_shocks,
            shock_timeline=shock_timeline,
            realized_params=realized_params
        )