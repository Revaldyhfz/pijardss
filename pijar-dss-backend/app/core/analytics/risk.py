"""
Risk Analytics Module.

Provides comprehensive risk analysis derived from Monte Carlo simulation
results. This module computes metrics that quantify downside risk and
help stakeholders understand what can go wrong.

Risk Metrics Computed:
---------------------
1. Value at Risk (VaR): Maximum loss at confidence level
2. Conditional VaR (CVaR/ES): Expected loss in tail
3. Drawdown Analysis: Peak-to-trough decline metrics
4. Survival Analysis: Time-dependent ruin probability
5. Underwater Analysis: Time spent below starting capital
6. Tail Decomposition: What drives worst outcomes

Philosophy:
----------
These metrics mirror what a trading desk uses to manage portfolio risk.
We're applying the same rigor to business expansion decisions.
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from scipy import stats

from ..simulation.path import PathResult
from ...utils.math_helpers import compute_drawdown, percentile, empirical_cdf


@dataclass
class VaRResult:
    """
    Value at Risk computation result.
    
    VaR answers: "What is the maximum loss we won't exceed with X% confidence?"
    
    Example: VaR_95 = 1,200M means "There's 95% probability we won't lose
    more than 1,200M IDR"
    """
    confidence_level: float  # e.g., 0.95 for 95%
    var_absolute: float      # Absolute capital loss
    var_relative: float      # Loss as % of initial capital
    threshold_capital: float # Capital level at VaR threshold


@dataclass
class CVaRResult:
    """
    Conditional Value at Risk (Expected Shortfall) result.
    
    CVaR answers: "If we're in the worst X% of scenarios, what's our
    average loss?"
    
    CVaR is always worse than VaR because it averages the tail,
    not just the threshold.
    """
    confidence_level: float
    cvar_absolute: float     # Average loss in tail
    cvar_relative: float     # Average loss % in tail
    n_tail_scenarios: int    # Number of scenarios in tail


@dataclass
class DrawdownAnalysis:
    """
    Comprehensive drawdown statistics.
    
    Drawdown = (Peak - Current) / Peak
    
    This measures the decline from the highest point reached,
    which is psychologically important for stakeholders.
    """
    mean: float
    median: float
    std: float
    p75: float
    p90: float
    p95: float
    p99: float
    max_observed: float
    
    # Time analysis
    avg_time_to_max_dd: float  # Average month when max DD occurs
    avg_recovery_time: float   # Average months to recover from max DD


@dataclass
class SurvivalAnalysis:
    """
    Survival analysis results.
    
    Models the probability of "survival" (capital > 0) over time.
    Uses Kaplan-Meier-style estimation from simulation paths.
    """
    # Survival curve: P(survive to month t)
    survival_curve: List[float]
    
    # Hazard rate: Conditional probability of failure at t given survival to t
    hazard_rates: List[float]
    
    # Key percentiles
    median_survival_time: Optional[float]  # Month when 50% have failed (if applicable)
    p10_survival_time: Optional[float]     # Month when 10% have failed
    
    # Terminal survival
    terminal_survival_rate: float  # P(survive entire horizon)


@dataclass
class UnderwaterAnalysis:
    """
    Analysis of time spent "underwater" (below starting capital).
    
    Even profitable ventures spend time underwater during development
    and early sales phases. This quantifies that experience.
    """
    mean_months_underwater: float
    median_months_underwater: float
    max_months_underwater: float
    
    # Probability of being underwater at each month
    underwater_probability_curve: List[float]
    
    # Consecutive underwater streaks
    mean_max_streak: float
    p95_max_streak: float


@dataclass 
class TailAnalysis:
    """
    Detailed analysis of tail (worst) outcomes.
    
    Examines the worst 5% of scenarios to understand what
    drives catastrophic outcomes.
    """
    tail_threshold_return: float  # Return threshold for tail
    n_tail_paths: int
    
    # Statistics in tail
    tail_mean_return: float
    tail_mean_final_capital: float
    tail_ruin_rate: float  # % of tail that hits ruin
    
    # Parameter analysis in tail
    tail_parameter_means: Dict[str, float]
    tail_vs_population_delta: Dict[str, float]  # How tail differs from population


@dataclass
class RiskAnalysisResult:
    """Complete risk analysis output."""
    var: Dict[str, VaRResult]       # VaR at multiple confidence levels
    cvar: Dict[str, CVaRResult]     # CVaR at multiple confidence levels
    drawdown: DrawdownAnalysis
    survival: SurvivalAnalysis
    underwater: UnderwaterAnalysis
    tail: TailAnalysis


class RiskAnalyzer:
    """
    Comprehensive risk analyzer for Monte Carlo results.
    
    Takes simulation path results and computes all risk metrics
    needed for decision support.
    
    Parameters
    ----------
    path_results : List[PathResult]
        Results from Monte Carlo simulation
    confidence_levels : List[float]
        Confidence levels for VaR/CVaR (e.g., [0.90, 0.95, 0.99])
    """
    
    def __init__(
        self, 
        path_results: List[PathResult],
        confidence_levels: List[float] = None
    ):
        self.paths = path_results
        self.n_paths = len(path_results)
        self.confidence_levels = confidence_levels or [0.90, 0.95, 0.99]
        
        # Pre-extract commonly used arrays
        self._extract_arrays()
    
    def _extract_arrays(self):
        """Pre-extract arrays for efficient computation."""
        self.initial_capitals = np.array([p.initial_capital for p in self.paths])
        self.final_capitals = np.array([p.final_capital for p in self.paths])
        self.returns = np.array([p.total_return for p in self.paths])
        self.max_drawdowns = np.array([p.max_drawdown for p in self.paths])
        self.is_ruin = np.array([p.is_ruin for p in self.paths])
        self.breakeven_months = np.array([p.breakeven_month for p in self.paths])
        
        # Stack equity curves (n_paths × n_months+1)
        self.equity_curves = np.vstack([p.equity_curve for p in self.paths])
        self.time_horizon = self.equity_curves.shape[1] - 1
        
        # Compute losses (positive = loss)
        self.losses = self.initial_capitals - self.final_capitals
    
    def compute_var(self, confidence: float) -> VaRResult:
        """
        Compute Value at Risk at given confidence level.
        
        VaR at confidence α is the (1-α) quantile of the loss distribution.
        Example: VaR_95 is the 95th percentile of losses.
        
        Parameters
        ----------
        confidence : float
            Confidence level (e.g., 0.95 for 95% VaR)
            
        Returns
        -------
        VaRResult
        """
        # VaR is the quantile of the loss distribution
        var_absolute = float(np.percentile(self.losses, confidence * 100))
        
        # Relative to average initial capital
        avg_initial = float(np.mean(self.initial_capitals))
        var_relative = var_absolute / avg_initial * 100
        
        # Threshold capital (what capital corresponds to this loss)
        threshold_capital = avg_initial - var_absolute
        
        return VaRResult(
            confidence_level=confidence,
            var_absolute=var_absolute,
            var_relative=var_relative,
            threshold_capital=threshold_capital
        )
    
    def compute_cvar(self, confidence: float) -> CVaRResult:
        """
        Compute Conditional VaR (Expected Shortfall).
        
        CVaR is the expected loss given that we're in the tail.
        It's the average of losses exceeding VaR.
        
        CVaR is considered superior to VaR because:
        1. It's coherent (satisfies subadditivity)
        2. It captures tail severity, not just threshold
        
        Parameters
        ----------
        confidence : float
            Confidence level
            
        Returns
        -------
        CVaRResult
        """
        # Get VaR threshold
        var_threshold = np.percentile(self.losses, confidence * 100)
        
        # Select tail scenarios
        tail_mask = self.losses >= var_threshold
        tail_losses = self.losses[tail_mask]
        
        # CVaR is mean of tail
        cvar_absolute = float(np.mean(tail_losses))
        
        avg_initial = float(np.mean(self.initial_capitals))
        cvar_relative = cvar_absolute / avg_initial * 100
        
        return CVaRResult(
            confidence_level=confidence,
            cvar_absolute=cvar_absolute,
            cvar_relative=cvar_relative,
            n_tail_scenarios=int(np.sum(tail_mask))
        )
    
    def compute_drawdown_analysis(self) -> DrawdownAnalysis:
        """
        Comprehensive drawdown analysis.
        
        Computes statistics on maximum drawdown across all paths,
        plus timing analysis.
        """
        # Basic statistics on max drawdown
        dd = self.max_drawdowns
        
        # Time to max drawdown for each path
        time_to_max_dd = []
        recovery_times = []
        
        for path in self.paths:
            curve = path.equity_curve
            
            # Find when max drawdown occurred
            running_max = np.maximum.accumulate(curve)
            with np.errstate(divide='ignore', invalid='ignore'):
                dd_series = np.where(running_max > 0, 
                                     (running_max - curve) / running_max, 
                                     0)
            
            max_dd_month = int(np.argmax(dd_series))
            time_to_max_dd.append(max_dd_month)
            
            # Recovery time (months from max DD to recovery)
            if max_dd_month < len(curve) - 1:
                peak_at_max_dd = running_max[max_dd_month]
                recovery_month = None
                for m in range(max_dd_month + 1, len(curve)):
                    if curve[m] >= peak_at_max_dd:
                        recovery_month = m
                        break
                if recovery_month:
                    recovery_times.append(recovery_month - max_dd_month)
        
        return DrawdownAnalysis(
            mean=float(np.mean(dd)),
            median=float(np.median(dd)),
            std=float(np.std(dd)),
            p75=float(np.percentile(dd, 75)),
            p90=float(np.percentile(dd, 90)),
            p95=float(np.percentile(dd, 95)),
            p99=float(np.percentile(dd, 99)),
            max_observed=float(np.max(dd)),
            avg_time_to_max_dd=float(np.mean(time_to_max_dd)),
            avg_recovery_time=float(np.mean(recovery_times)) if recovery_times else -1
        )
    
    def compute_survival_analysis(self) -> SurvivalAnalysis:
        """
        Kaplan-Meier style survival analysis.
        
        Estimates the survival function S(t) = P(survive to time t)
        and hazard function h(t) = P(fail at t | survive to t).
        """
        n_months = self.time_horizon
        
        # Survival curve: fraction with capital > 0 at each month
        survival_curve = []
        for month in range(n_months + 1):
            survived = np.sum(self.equity_curves[:, month] > 0) / self.n_paths
            survival_curve.append(float(survived))
        
        # Hazard rates: conditional failure probability
        # h(t) = [S(t-1) - S(t)] / S(t-1)
        hazard_rates = [0.0]  # No hazard at t=0
        for month in range(1, n_months + 1):
            if survival_curve[month - 1] > 0:
                hazard = (survival_curve[month - 1] - survival_curve[month]) / survival_curve[month - 1]
            else:
                hazard = 0.0
            hazard_rates.append(float(hazard))
        
        # Median survival time (when S(t) drops below 0.5)
        median_survival = None
        for month, surv in enumerate(survival_curve):
            if surv < 0.5:
                median_survival = float(month)
                break
        
        # 10% failure time
        p10_survival = None
        for month, surv in enumerate(survival_curve):
            if surv < 0.9:
                p10_survival = float(month)
                break
        
        return SurvivalAnalysis(
            survival_curve=survival_curve,
            hazard_rates=hazard_rates,
            median_survival_time=median_survival,
            p10_survival_time=p10_survival,
            terminal_survival_rate=survival_curve[-1]
        )
    
    def compute_underwater_analysis(self) -> UnderwaterAnalysis:
        """
        Analyze time spent below starting capital.
        
        Even successful ventures spend time "underwater" during
        development and early growth. This quantifies that experience.
        """
        # Underwater mask: capital < initial
        underwater = self.equity_curves < self.initial_capitals.reshape(-1, 1)
        
        # Total months underwater per path
        months_underwater = np.sum(underwater, axis=1)
        
        # Probability of being underwater at each month
        underwater_prob = np.mean(underwater, axis=0).tolist()
        
        # Maximum consecutive underwater streak per path
        max_streaks = []
        for i in range(self.n_paths):
            path_underwater = underwater[i]
            max_streak = 0
            current_streak = 0
            for is_uw in path_underwater:
                if is_uw:
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 0
            max_streaks.append(max_streak)
        
        return UnderwaterAnalysis(
            mean_months_underwater=float(np.mean(months_underwater)),
            median_months_underwater=float(np.median(months_underwater)),
            max_months_underwater=float(np.max(months_underwater)),
            underwater_probability_curve=underwater_prob,
            mean_max_streak=float(np.mean(max_streaks)),
            p95_max_streak=float(np.percentile(max_streaks, 95))
        )
    
    def compute_tail_analysis(self, tail_percentile: float = 5.0) -> TailAnalysis:
        """
        Detailed analysis of worst outcomes.
        
        Examines the tail of the return distribution to understand
        what characterizes catastrophic scenarios.
        
        Parameters
        ----------
        tail_percentile : float
            Percentile defining the tail (e.g., 5 = worst 5%)
        """
        # Identify tail threshold
        tail_threshold = np.percentile(self.returns, tail_percentile)
        tail_mask = self.returns <= tail_threshold
        n_tail = int(np.sum(tail_mask))
        
        # Tail statistics
        tail_returns = self.returns[tail_mask]
        tail_finals = self.final_capitals[tail_mask]
        tail_ruin = self.is_ruin[tail_mask]
        
        # Parameter analysis in tail
        # Extract realized parameters from tail paths
        tail_paths = [p for p, in_tail in zip(self.paths, tail_mask) if in_tail]
        
        param_names = ['initial_capital', 'dev_duration', 'dev_burn', 
                       'leads_per_month', 'win_rate_bumn', 'win_rate_open',
                       'annual_churn_rate']
        
        tail_param_means = {}
        population_param_means = {}
        tail_vs_pop_delta = {}
        
        for param in param_names:
            # Population mean
            pop_values = [p.realized_params.get(param, 0) for p in self.paths]
            pop_mean = np.mean(pop_values)
            population_param_means[param] = pop_mean
            
            # Tail mean
            tail_values = [p.realized_params.get(param, 0) for p in tail_paths]
            tail_mean = np.mean(tail_values) if tail_values else pop_mean
            tail_param_means[param] = float(tail_mean)
            
            # Delta (how much tail differs from population)
            if pop_mean != 0:
                delta = (tail_mean - pop_mean) / pop_mean * 100
            else:
                delta = 0
            tail_vs_pop_delta[param] = float(delta)
        
        return TailAnalysis(
            tail_threshold_return=float(tail_threshold),
            n_tail_paths=n_tail,
            tail_mean_return=float(np.mean(tail_returns)),
            tail_mean_final_capital=float(np.mean(tail_finals)),
            tail_ruin_rate=float(np.mean(tail_ruin)),
            tail_parameter_means=tail_param_means,
            tail_vs_population_delta=tail_vs_pop_delta
        )
    
    def analyze(self) -> RiskAnalysisResult:
        """
        Run complete risk analysis.
        
        Returns
        -------
        RiskAnalysisResult
            Comprehensive risk analysis
        """
        # VaR at multiple confidence levels
        var_results = {}
        for conf in self.confidence_levels:
            key = f"{int(conf * 100)}"
            var_results[key] = self.compute_var(conf)
        
        # CVaR at multiple confidence levels
        cvar_results = {}
        for conf in self.confidence_levels:
            key = f"{int(conf * 100)}"
            cvar_results[key] = self.compute_cvar(conf)
        
        return RiskAnalysisResult(
            var=var_results,
            cvar=cvar_results,
            drawdown=self.compute_drawdown_analysis(),
            survival=self.compute_survival_analysis(),
            underwater=self.compute_underwater_analysis(),
            tail=self.compute_tail_analysis()
        )