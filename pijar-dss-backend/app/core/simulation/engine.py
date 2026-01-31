"""
Monte Carlo Simulation Engine.

Orchestrates the execution of many path simulations and aggregates
results into summary statistics and distributions.

Architecture:
------------
1. Parameter Sampling: Draw from input distributions
2. Path Simulation: Run single path with sampled params
3. Aggregation: Collect results across all paths
4. Statistics: Compute summary metrics

Parallelization:
---------------
Paths are embarrassingly parallel - each can run independently.
We use joblib for parallel execution with proper RNG management.
"""

import numpy as np
from numpy.random import Generator, SeedSequence, PCG64
from numpy.typing import NDArray
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
import time
from joblib import Parallel, delayed

from ..distributions import (
    BaseDistribution,
    TriangularDistribution,
    BetaDistribution,
    LogNormalDistribution,
    GammaDistribution,
)
from ..processes import RegimeSwitchingModel, RegimeType, DEFAULT_REGIMES
from ..models.parameters import SimulationInput, DistributionSpec, DistributionType
from ..models.results import (
    SimulationResult,
    SummaryStatistics,
    PathData,
    PathPercentile,
    OutcomeDistribution,
    ReturnBucket,
    RiskMetrics,
    PremortemAnalysis,
    SimulationMeta,
    RecommendationType,
)
from .business_model import BusinessModel
from .risk_events import RiskEventManager, RiskEventConfig
from .path import PathSimulator, PathResult


def create_distribution(spec: DistributionSpec) -> BaseDistribution:
    """
    Factory function to create distribution from specification.
    
    Parameters
    ----------
    spec : DistributionSpec
        Distribution specification from API input
        
    Returns
    -------
    BaseDistribution
        Configured distribution instance
    """
    if spec.type == DistributionType.TRIANGULAR:
        return TriangularDistribution(
            min_val=spec.params['min'],
            mode=spec.params['mode'],
            max_val=spec.params['max']
        )
    elif spec.type == DistributionType.BETA:
        return BetaDistribution(
            alpha=spec.params['alpha'],
            beta=spec.params['beta']
        )
    elif spec.type == DistributionType.LOGNORMAL:
        if 'mean' in spec.params and 'cv' in spec.params:
            return LogNormalDistribution.from_mean_cv(
                mean=spec.params['mean'],
                cv=spec.params['cv']
            )
        else:
            return LogNormalDistribution(
                mu=spec.params['mu'],
                sigma=spec.params['sigma']
            )
    elif spec.type == DistributionType.GAMMA:
        return GammaDistribution(
            shape=spec.params['shape'],
            scale=spec.params['scale']
        )
    elif spec.type == DistributionType.FIXED:
        # Fixed value as degenerate triangular
        val = spec.params['value']
        return TriangularDistribution(min_val=val, mode=val, max_val=val)
    else:
        raise ValueError(f"Unknown distribution type: {spec.type}")


@dataclass
class SampledParameters:
    """Parameters sampled for a single simulation run."""
    initial_capital: float
    dev_duration: int
    dev_burn: float
    leads_per_month: float
    win_rate_bumn: float
    win_rate_open: float
    bumn_ratio: float
    annual_churn_rate: float
    contract_small: float
    contract_medium: float
    contract_large: float


class SimulationEngine:
    """
    Monte Carlo simulation engine.
    
    Manages the full simulation workflow from input parameters
    to aggregated results.
    
    Parameters
    ----------
    input_params : SimulationInput
        Complete input specification
    n_jobs : int
        Number of parallel workers (-1 for all cores)
    """
    
    def __init__(self, input_params: SimulationInput, n_jobs: int = -1):
        self.input = input_params
        self.n_jobs = n_jobs
        
        # Create input distributions
        self.distributions = self._create_distributions()
        
        # Create regime model if enabled
        self.regime_model = None
        if input_params.config.enable_regime_switching:
            self.regime_model = RegimeSwitchingModel.create_default(
                stress_probability=0.20,
                boom_probability=0.10,
                persistence=0.85
            )
        
        # Create risk event configs
        self.risk_configs = self._create_risk_configs()
    
    def _create_distributions(self) -> Dict[str, BaseDistribution]:
        """Create all input distributions."""
        dists = {}
        
        # Capital & Dev
        dists['initial_capital'] = create_distribution(self.input.capital_dev.initial_capital)
        dists['dev_duration'] = create_distribution(self.input.capital_dev.dev_duration)
        dists['dev_burn'] = create_distribution(self.input.capital_dev.dev_burn)
        
        # Sales
        dists['leads_per_month'] = create_distribution(self.input.sales.leads_per_month)
        dists['win_rate_bumn'] = create_distribution(self.input.sales.win_rate_bumn)
        dists['win_rate_open'] = create_distribution(self.input.sales.win_rate_open)
        dists['sales_cycle'] = create_distribution(self.input.sales.sales_cycle_months)
        
        # Pricing
        dists['contract_small'] = create_distribution(self.input.pricing.contract_small)
        dists['contract_medium'] = create_distribution(self.input.pricing.contract_medium)
        dists['contract_large'] = create_distribution(self.input.pricing.contract_large)
        
        # Retention
        dists['churn_rate'] = create_distribution(self.input.retention_costs.churn_rate)
        
        return dists
    
    def _create_risk_configs(self) -> List[RiskEventConfig]:
        """Create risk event configurations."""
        configs = []
        
        for event in self.input.risk_events:
            config = RiskEventConfig(
                name=event.name,
                intensity=event.intensity,
                impact_type=event.impact_type,
                severity_dist=TriangularDistribution(
                    min_val=event.severity_min,
                    mode=event.severity_mode,
                    max_val=event.severity_max
                ),
                recovery_rate=event.recovery_rate,
                start_month=event.start_month,
                end_month=event.end_month
            )
            configs.append(config)
        
        return configs
    
    def _sample_parameters(self, rng: Generator) -> SampledParameters:
        """Sample all input parameters for one simulation."""
        return SampledParameters(
            initial_capital=float(self.distributions['initial_capital'].sample(rng=rng)[0]),
            dev_duration=int(round(self.distributions['dev_duration'].sample(rng=rng)[0])),
            dev_burn=float(self.distributions['dev_burn'].sample(rng=rng)[0]),
            leads_per_month=float(self.distributions['leads_per_month'].sample(rng=rng)[0]),
            win_rate_bumn=float(np.clip(self.distributions['win_rate_bumn'].sample(rng=rng)[0], 0, 1)),
            win_rate_open=float(np.clip(self.distributions['win_rate_open'].sample(rng=rng)[0], 0, 1)),
            bumn_ratio=self.input.sales.bumn_ratio,
            annual_churn_rate=float(np.clip(self.distributions['churn_rate'].sample(rng=rng)[0], 0, 1)),
            contract_small=float(self.distributions['contract_small'].sample(rng=rng)[0]),
            contract_medium=float(self.distributions['contract_medium'].sample(rng=rng)[0]),
            contract_large=float(self.distributions['contract_large'].sample(rng=rng)[0]),
        )
    
    def _run_single_path(self, seed: int) -> PathResult:
        """Run a single path simulation with given seed."""
        rng = Generator(PCG64(seed))
        
        # Sample parameters
        params = self._sample_parameters(rng)
        
        # Create business model
        contract_dists = {
            'small': LogNormalDistribution.from_mean_cv(params.contract_small, 0.1),
            'medium': LogNormalDistribution.from_mean_cv(params.contract_medium, 0.1),
            'large': LogNormalDistribution.from_mean_cv(params.contract_large, 0.1),
        }
        
        sales_cycle_dist = GammaDistribution.from_mean_cv(mean=5.0, cv=0.3)
        
        business_model = BusinessModel(
            contract_distributions=contract_dists,
            size_weights=self.input.pricing.size_distribution,
            sales_cycle_dist=sales_cycle_dist,
            op_overhead=self.input.retention_costs.op_overhead,
            cost_per_customer=self.input.retention_costs.cost_per_customer
        )
        
        # Create risk manager if enabled
        risk_manager = None
        if self.input.config.enable_risk_events and self.risk_configs:
            risk_manager = RiskEventManager(self.risk_configs)
        
        # Create path simulator
        simulator = PathSimulator(
            business_model=business_model,
            regime_model=self.regime_model,
            risk_manager=risk_manager,
            time_horizon=self.input.config.time_horizon
        )
        
        # Run simulation
        result = simulator.simulate(
            initial_capital=params.initial_capital,
            dev_duration=params.dev_duration,
            dev_burn=params.dev_burn,
            leads_per_month=params.leads_per_month,
            win_rate_bumn=params.win_rate_bumn,
            win_rate_open=params.win_rate_open,
            bumn_ratio=params.bumn_ratio,
            annual_churn_rate=params.annual_churn_rate,
            rng=rng
        )
        
        return result
    
    def run(self) -> Tuple[List[PathResult], float]:
        """
        Run the full Monte Carlo simulation.
        
        Returns
        -------
        tuple
            (list of PathResult, computation_time_ms)
        """
        start_time = time.time()
        
        n_sims = self.input.config.n_simulations
        base_seed = self.input.config.seed or int(time.time() * 1000) % (2**31)
        
        # Generate seeds for each simulation
        seed_seq = SeedSequence(base_seed)
        seeds = [int(s.generate_state(1)[0]) for s in seed_seq.spawn(n_sims)]
        
        # Run simulations (parallel or serial)
        if self.n_jobs == 1:
            # Serial execution (useful for debugging)
            results = [self._run_single_path(seed) for seed in seeds]
        else:
            # Parallel execution
            results = Parallel(n_jobs=self.n_jobs)(
                delayed(self._run_single_path)(seed) for seed in seeds
            )
        
        computation_time = (time.time() - start_time) * 1000  # ms
        
        return results, computation_time
    
    def aggregate_results(
        self, 
        path_results: List[PathResult],
        computation_time_ms: float
    ) -> SimulationResult:
        """
        Aggregate path results into summary statistics.
        
        This is where we compute all the metrics shown in the dashboard.
        """
        n_sims = len(path_results)
        time_horizon = self.input.config.time_horizon
        
        # Extract arrays for vectorized computation
        final_capitals = np.array([r.final_capital for r in path_results])
        initial_capitals = np.array([r.initial_capital for r in path_results])
        returns = np.array([r.total_return for r in path_results])
        max_drawdowns = np.array([r.max_drawdown for r in path_results])
        breakeven_months = np.array([r.breakeven_month for r in path_results])
        is_ruin = np.array([r.is_ruin for r in path_results])
        
        # Stack equity curves
        equity_curves = np.vstack([r.equity_curve for r in path_results])
        
        # === SUMMARY STATISTICS ===
        avg_initial = float(np.mean(initial_capitals))
        
        prob_profit = float(np.mean(returns > 0))
        prob_double = float(np.mean(returns >= 100))
        prob_ruin = float(np.mean(is_ruin))
        
        return_mean = float(np.mean(returns))
        return_median = float(np.median(returns))
        return_std = float(np.std(returns))
        return_p5 = float(np.percentile(returns, 5))
        return_p95 = float(np.percentile(returns, 95))
        
        # VaR and CVaR (as capital loss)
        losses = initial_capitals - final_capitals
        var_5 = float(np.percentile(losses, 95))  # 5% worst loss
        cvar_5 = float(np.mean(losses[losses >= np.percentile(losses, 95)]))
        
        max_dd_mean = float(np.mean(max_drawdowns))
        max_dd_p95 = float(np.percentile(max_drawdowns, 95))
        
        # Breakeven
        achieved_breakeven = breakeven_months > 0
        breakeven_rate = float(np.mean(achieved_breakeven))
        breakeven_mean = float(np.mean(breakeven_months[achieved_breakeven])) if np.any(achieved_breakeven) else None
        
        # Recommendation
        if prob_profit >= 0.80 and return_mean >= 50 and prob_ruin < 0.05:
            recommendation = RecommendationType.PROCEED
        elif prob_profit >= 0.60:
            recommendation = RecommendationType.CAUTION
        elif prob_profit >= 0.40:
            recommendation = RecommendationType.REASSESS
        else:
            recommendation = RecommendationType.DO_NOT_PROCEED
        
        summary = SummaryStatistics(
            prob_profit=prob_profit,
            prob_double=prob_double,
            prob_ruin=prob_ruin,
            return_mean=return_mean,
            return_median=return_median,
            return_std=return_std,
            return_p5=return_p5,
            return_p95=return_p95,
            var_5=var_5,
            cvar_5=cvar_5,
            max_drawdown_mean=max_dd_mean,
            max_drawdown_p95=max_dd_p95,
            breakeven_mean=breakeven_mean,
            breakeven_rate=breakeven_rate,
            recommendation=recommendation
        )
        
        # === PATH DATA ===
        percentiles = []
        for month in range(time_horizon + 1):
            month_values = equity_curves[:, month]
            percentiles.append(PathPercentile(
                month=month,
                p5=float(np.percentile(month_values, 5)),
                p25=float(np.percentile(month_values, 25)),
                p50=float(np.percentile(month_values, 50)),
                p75=float(np.percentile(month_values, 75)),
                p95=float(np.percentile(month_values, 95))
            ))
        
        # Sample paths for visualization (50 representative paths)
        n_sample = min(50, n_sims)
        sample_indices = np.linspace(0, n_sims - 1, n_sample, dtype=int)
        sorted_by_return = np.argsort(returns)
        sample_paths = [
            equity_curves[sorted_by_return[i]].tolist()
            for i in sample_indices
        ]
        
        median_path = [p.p50 for p in percentiles]
        
        paths = PathData(
            percentiles=percentiles,
            sample_paths=sample_paths,
            median_path=median_path
        )
        
        # === OUTCOME DISTRIBUTION ===
        outcomes = OutcomeDistribution(
            double_plus=int(np.sum(returns >= 100)),
            profitable=int(np.sum((returns > 0) & (returns < 100))),
            loss=int(np.sum((returns <= 0) & ~is_ruin)),
            ruin=int(np.sum(is_ruin)),
            total=n_sims
        )
        
        # === RETURN DISTRIBUTION ===
        bucket_size = 50
        min_ret = int(np.floor(returns.min() / bucket_size) * bucket_size)
        max_ret = int(np.ceil(returns.max() / bucket_size) * bucket_size)
        
        return_buckets = []
        for start in range(min_ret, max_ret, bucket_size):
            count = int(np.sum((returns >= start) & (returns < start + bucket_size)))
            return_buckets.append(ReturnBucket(
                range_start=start,
                range_end=start + bucket_size,
                count=count,
                percentage=count / n_sims * 100
            ))
        
        # === RISK METRICS ===
        # Survival curve
        survival_curve = []
        for month in range(time_horizon + 1):
            survived = np.sum(equity_curves[:, month] > 0) / n_sims
            survival_curve.append(float(survived))
        
        # Months underwater
        underwater = equity_curves < initial_capitals.reshape(-1, 1)
        months_underwater = np.sum(underwater, axis=1)
        
        # Tail loss (worst 5%)
        worst_5pct_idx = returns <= np.percentile(returns, 5)
        tail_loss_mean = float(np.mean(initial_capitals[worst_5pct_idx] - final_capitals[worst_5pct_idx]))
        
        risk_metrics = RiskMetrics(
            var={"1": float(np.percentile(losses, 99)), "5": var_5, "10": float(np.percentile(losses, 90))},
            cvar={"1": float(np.mean(losses[losses >= np.percentile(losses, 99)])),
                  "5": cvar_5,
                  "10": float(np.mean(losses[losses >= np.percentile(losses, 90)]))},
            drawdown_mean=max_dd_mean,
            drawdown_std=float(np.std(max_drawdowns)),
            drawdown_p50=float(np.median(max_drawdowns)),
            drawdown_p95=max_dd_p95,
            drawdown_p99=float(np.percentile(max_drawdowns, 99)),
            months_underwater_mean=float(np.mean(months_underwater)),
            survival_curve=survival_curve,
            tail_loss_mean=tail_loss_mean
        )
        
        # === PREMORTEM (Basic - detailed in analytics module) ===
        # This is a placeholder; full premortem comes from analytics
        premortem = PremortemAnalysis(
            failure_rate=prob_ruin + float(np.mean(returns < -20)),
            failure_count=int(np.sum(is_ruin) + np.sum(returns < -20)),
            primary_causes=[],  # Filled by analytics module
            critical_periods=[],
            failure_timing_distribution=[],
            regime_analysis=None,
            most_sensitive_parameters=[]
        )
        
        # === META ===
        from datetime import datetime
        meta = SimulationMeta(
            n_simulations=n_sims,
            time_horizon=time_horizon,
            seed=self.input.config.seed,
            computation_time_ms=computation_time_ms,
            timestamp=datetime.utcnow().isoformat()
        )
        
        return SimulationResult(
            summary=summary,
            paths=paths,
            outcomes=outcomes,
            return_distribution=return_buckets,
            risk_metrics=risk_metrics,
            premortem=premortem,
            meta=meta
        )