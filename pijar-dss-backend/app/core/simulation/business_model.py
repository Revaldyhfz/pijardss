"""
Business Model Logic for Revenue, Costs, and Churn.

This module encapsulates the domain-specific logic of how the
Pijar PT expansion generates revenue and incurs costs.

Business Model Overview:
-----------------------
1. Development Phase (months 0 to dev_duration):
   - No revenue
   - Fixed burn rate
   
2. Sales Phase (post-development):
   - Leads arrive via Poisson process
   - Leads enter pipeline with conversion probability
   - Pipeline deals close after sales cycle
   - Customers generate recurring revenue
   - Customers churn stochastically

Revenue Model:
- Annual contract value varies by PT size
- Revenue = customers × (avg_contract / 12)

Cost Model:
- Fixed: operational overhead
- Variable: cost per customer (support, infrastructure)
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ..distributions import (
    TriangularDistribution,
    BetaDistribution,
    LogNormalDistribution,
    GammaDistribution,
)
from ..processes import PoissonProcess


@dataclass
class PipelineDeal:
    """
    A deal in the sales pipeline.
    
    Attributes
    ----------
    entry_month : int
        Month when lead entered pipeline
    close_month : int
        Expected closing month
    will_convert : bool
        Whether this deal will convert (determined at entry)
    contract_value : float
        Annual contract value if converted
    is_bumn : bool
        Whether this is a BUMN deal
    """
    entry_month: int
    close_month: int
    will_convert: bool
    contract_value: float
    is_bumn: bool


@dataclass
class BusinessState:
    """
    Current state of the business.
    
    Tracks all state variables that evolve over time.
    """
    capital: float
    customers: int
    pipeline: List[PipelineDeal] = field(default_factory=list)
    
    # Tracking metrics
    cumulative_revenue: float = 0.0
    cumulative_costs: float = 0.0
    peak_capital: float = 0.0
    max_drawdown: float = 0.0
    breakeven_month: int = -1
    
    # Monthly metrics (for analysis)
    monthly_revenues: List[float] = field(default_factory=list)
    monthly_costs: List[float] = field(default_factory=list)
    monthly_customers: List[int] = field(default_factory=list)
    monthly_new_customers: List[int] = field(default_factory=list)
    monthly_churned: List[int] = field(default_factory=list)
    
    def update_drawdown(self):
        """Update peak and drawdown tracking."""
        if self.capital > self.peak_capital:
            self.peak_capital = self.capital
        
        if self.peak_capital > 0:
            current_dd = (self.peak_capital - self.capital) / self.peak_capital
            self.max_drawdown = max(self.max_drawdown, current_dd)


class BusinessModel:
    """
    Core business model for PT expansion.
    
    Encapsulates all domain logic for revenue, costs, and customer dynamics.
    
    Parameters
    ----------
    contract_distributions : dict
        Mapping of size -> LogNormalDistribution for contract values
    size_weights : dict
        Probability distribution over PT sizes
    sales_cycle_dist : GammaDistribution
        Distribution for sales cycle duration
    op_overhead : float
        Monthly operational overhead
    cost_per_customer : float
        Monthly variable cost per customer
    """
    
    def __init__(
        self,
        contract_distributions: dict,
        size_weights: dict,
        sales_cycle_dist: GammaDistribution,
        op_overhead: float,
        cost_per_customer: float
    ):
        self.contract_distributions = contract_distributions
        self.size_weights = size_weights
        self.sales_cycle_dist = sales_cycle_dist
        self.op_overhead = op_overhead
        self.cost_per_customer = cost_per_customer
        
        # Normalize size weights
        total = sum(size_weights.values())
        self.size_probs = {k: v/total for k, v in size_weights.items()}
        self.sizes = list(self.size_probs.keys())
        self.probs = list(self.size_probs.values())
    
    def sample_contract_value(self, rng: Generator) -> Tuple[str, float]:
        """
        Sample a contract value for a new deal.
        
        Returns
        -------
        tuple
            (size_category, annual_contract_value)
        """
        # Sample size category
        size = rng.choice(self.sizes, p=self.probs)
        
        # Sample value from corresponding distribution
        value = self.contract_distributions[size].sample(rng=rng)[0]
        
        return size, value
    
    def sample_sales_cycle(self, rng: Generator) -> int:
        """Sample sales cycle duration in months."""
        duration = self.sales_cycle_dist.sample(rng=rng)[0]
        return max(1, int(np.round(duration)))
    
    def process_new_leads(
        self,
        state: BusinessState,
        month: int,
        n_leads: int,
        win_rate_bumn: float,
        win_rate_open: float,
        bumn_ratio: float,
        rng: Generator,
        regime_multipliers: dict = None
    ) -> int:
        """
        Process new leads entering the pipeline.
        
        Parameters
        ----------
        state : BusinessState
            Current business state
        month : int
            Current month
        n_leads : int
            Number of new leads
        win_rate_bumn : float
            Win rate for BUMN deals
        win_rate_open : float
            Win rate for open market deals
        bumn_ratio : float
            Fraction of leads that are BUMN
        rng : Generator
            Random number generator
        regime_multipliers : dict, optional
            Multipliers from current regime
            
        Returns
        -------
        int
            Number of leads added to pipeline
        """
        regime_multipliers = regime_multipliers or {}
        win_mult = regime_multipliers.get('win_rate_multiplier', 1.0)
        
        for _ in range(n_leads):
            # Determine if BUMN or open market
            is_bumn = rng.random() < bumn_ratio
            
            # Get effective win rate
            base_win = win_rate_bumn if is_bumn else win_rate_open
            effective_win = min(1.0, base_win * win_mult)
            
            # Determine if will convert
            will_convert = rng.random() < effective_win
            
            # Sample contract value and sales cycle
            _, contract_value = self.sample_contract_value(rng)
            cycle = self.sample_sales_cycle(rng)
            
            # Create pipeline deal
            deal = PipelineDeal(
                entry_month=month,
                close_month=month + cycle,
                will_convert=will_convert,
                contract_value=contract_value,
                is_bumn=is_bumn
            )
            state.pipeline.append(deal)
        
        return n_leads
    
    def process_pipeline_closings(
        self,
        state: BusinessState,
        month: int
    ) -> int:
        """
        Process deals that are closing this month.
        
        Returns
        -------
        int
            Number of new customers acquired
        """
        closing_deals = [
            d for d in state.pipeline 
            if d.close_month <= month and d.will_convert
        ]
        
        # Remove closed deals from pipeline
        state.pipeline = [
            d for d in state.pipeline 
            if d.close_month > month or not d.will_convert
        ]
        
        new_customers = len(closing_deals)
        state.customers += new_customers
        
        return new_customers
    
    def apply_churn(
        self,
        state: BusinessState,
        annual_churn_rate: float,
        rng: Generator,
        regime_multipliers: dict = None
    ) -> int:
        """
        Apply monthly churn to customer base.
        
        Converts annual churn rate to monthly probability:
        P(churn in month) = 1 - (1 - annual_rate)^(1/12)
        
        Returns
        -------
        int
            Number of customers churned
        """
        if state.customers == 0:
            return 0
        
        regime_multipliers = regime_multipliers or {}
        churn_mult = regime_multipliers.get('churn_multiplier', 1.0)
        
        # Convert annual to monthly
        effective_annual = min(0.99, annual_churn_rate * churn_mult)
        monthly_churn_prob = 1 - (1 - effective_annual) ** (1/12)
        
        # Sample number of churns (binomial)
        churned = rng.binomial(state.customers, monthly_churn_prob)
        state.customers = max(0, state.customers - churned)
        
        return churned
    
    def compute_revenue(
        self,
        state: BusinessState,
        avg_contract_value: float,
        regime_multipliers: dict = None
    ) -> float:
        """
        Compute monthly revenue.
        
        Revenue = customers × (avg_annual_contract / 12)
        """
        regime_multipliers = regime_multipliers or {}
        rev_mult = regime_multipliers.get('revenue_multiplier', 1.0)
        
        monthly_contract = avg_contract_value / 12
        revenue = state.customers * monthly_contract * rev_mult
        
        return revenue
    
    def compute_costs(
        self,
        state: BusinessState,
        is_dev_phase: bool,
        dev_burn: float,
        regime_multipliers: dict = None
    ) -> float:
        """
        Compute monthly costs.
        
        Dev phase: fixed burn rate
        Sales phase: overhead + variable costs
        """
        regime_multipliers = regime_multipliers or {}
        cost_mult = regime_multipliers.get('cost_multiplier', 1.0)
        
        if is_dev_phase:
            return dev_burn * cost_mult
        
        fixed = self.op_overhead
        variable = state.customers * self.cost_per_customer
        
        return (fixed + variable) * cost_mult
    
    def compute_avg_contract_value(self) -> float:
        """Compute expected average contract value."""
        total = 0.0
        for size, prob in self.size_probs.items():
            total += prob * self.contract_distributions[size].mean
        return total