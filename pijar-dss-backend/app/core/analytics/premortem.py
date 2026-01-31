"""
Premortem Analytics Module.

Data-driven premortem analysis derived from Monte Carlo simulation.
Unlike checklist-based approaches, this identifies failure causes
empirically from the simulation data.

Key Questions Answered:
----------------------
1. Why do failures happen? (Cause attribution)
2. When do failures happen? (Temporal analysis)
3. What conditions lead to failure? (Conditional analysis)
4. How do failures unfold? (Trajectory analysis)

Methodology:
-----------
1. Identify "failure" paths (ruin or severe loss)
2. Compare failed paths to successful paths
3. Identify distinguishing characteristics
4. Quantify cause attribution through conditional analysis

This is NOT a checklist. It's empirical failure forensics.
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from scipy import stats
from collections import defaultdict

from ..simulation.path import PathResult
from ..processes import RegimeType


@dataclass
class FailureCause:
    """
    Attribution of a failure cause.
    
    Identifies a factor that distinguishes failed paths from
    successful paths, quantifying its contribution to failure.
    """
    factor: str                    # Parameter or condition name
    display_name: str              # Human-readable name
    
    # Statistical comparison
    failed_mean: float             # Mean value in failed paths
    success_mean: float            # Mean value in successful paths
    population_mean: float         # Mean value across all paths
    
    # Effect size
    difference_pct: float          # (failed - success) / success as %
    cohens_d: float                # Standardized effect size
    
    # Attribution
    attribution_score: float       # 0-1, contribution to failure
    confidence: float              # Statistical confidence
    
    # Interpretation
    direction: str                 # 'higher' or 'lower' in failures
    interpretation: str            # Plain English explanation


@dataclass
class CriticalPeriod:
    """
    A time period with elevated failure risk.
    
    Identifies when failures typically occur and what
    characterizes those periods.
    """
    start_month: int
    end_month: int
    
    # Risk metrics for this period
    hazard_rate: float            # Conditional failure probability
    cumulative_failures: float    # % of all failures by end of period
    
    # Characteristics
    typical_capital_level: float  # Average capital at start
    typical_burn_rate: float      # Average monthly burn
    dominant_cause: str           # Primary failure driver


@dataclass
class FailureTrajectory:
    """
    Common pattern in how failures unfold.
    
    Identifies archetypal failure paths to help stakeholders
    visualize what failure looks like.
    """
    trajectory_type: str          # 'slow_bleed', 'sudden_collapse', 'recovery_failure'
    prevalence: float             # % of failures following this pattern
    
    # Trajectory characteristics
    months_to_failure: float      # Average time to failure
    peak_capital_reached: float   # Highest capital before decline
    warning_signs: List[str]      # Early indicators


@dataclass
class RegimeImpact:
    """
    Impact of economic regimes on failure probability.
    """
    regime: str
    time_spent_pct: float          # % of time in this regime
    conditional_failure_rate: float # P(failure | spent time in regime)
    risk_multiplier: float          # How much worse than baseline


@dataclass
class PremortemResult:
    """
    Complete premortem analysis results.
    
    Provides a data-driven answer to "If this fails, why?"
    """
    # Failure definition and rate
    failure_definition: str        # How we define "failure"
    failure_rate: float            # % of paths that failed
    failure_count: int             # Absolute count
    
    # Cause analysis
    primary_causes: List[FailureCause]
    cause_interactions: List[Tuple[str, str, float]]  # Pairs that co-occur
    
    # Temporal analysis
    critical_periods: List[CriticalPeriod]
    failure_timing_histogram: List[int]  # Count by month
    median_failure_month: Optional[float]
    
    # Trajectory analysis
    failure_trajectories: List[FailureTrajectory]
    
    # Regime analysis
    regime_impacts: List[RegimeImpact]
    
    # Actionable insights
    early_warning_signals: List[str]
    mitigation_priorities: List[str]


class PremortemAnalyzer:
    """
    Data-driven premortem analyzer.
    
    Examines simulation paths to understand failure patterns
    and provide actionable insights.
    
    Parameters
    ----------
    path_results : List[PathResult]
        Results from Monte Carlo simulation
    failure_threshold : float
        Return below which a path is considered "failed"
        Default: -20% (significant loss)
    """
    
    PARAMETER_DISPLAY_NAMES = {
        'initial_capital': 'Starting Capital',
        'dev_duration': 'Development Duration',
        'dev_burn': 'Development Burn Rate',
        'leads_per_month': 'Lead Generation',
        'win_rate_bumn': 'BUMN Win Rate',
        'win_rate_open': 'Open Market Win Rate',
        'annual_churn_rate': 'Customer Churn',
    }
    
    def __init__(
        self,
        path_results: List[PathResult],
        failure_threshold: float = -20.0
    ):
        self.paths = path_results
        self.n_paths = len(path_results)
        self.failure_threshold = failure_threshold
        
        # Classify paths
        self._classify_paths()
    
    def _classify_paths(self):
        """Classify paths into failed and successful."""
        self.returns = np.array([p.total_return for p in self.paths])
        self.is_ruin = np.array([p.is_ruin for p in self.paths])
        
        # Failure = ruin OR return below threshold
        self.is_failed = self.is_ruin | (self.returns <= self.failure_threshold)
        
        self.failed_paths = [p for p, f in zip(self.paths, self.is_failed) if f]
        self.success_paths = [p for p, f in zip(self.paths, self.is_failed) if not f]
        
        self.n_failed = len(self.failed_paths)
        self.n_success = len(self.success_paths)
    
    def analyze_causes(self) -> List[FailureCause]:
        """
        Identify factors that distinguish failed paths from successful ones.
        
        Uses statistical comparison of parameter distributions between
        failed and successful paths.
        """
        if self.n_failed == 0 or self.n_success == 0:
            return []
        
        causes = []
        params = list(self.PARAMETER_DISPLAY_NAMES.keys())
        
        for param in params:
            # Extract values
            failed_values = np.array([
                p.realized_params.get(param, 0) for p in self.failed_paths
            ])
            success_values = np.array([
                p.realized_params.get(param, 0) for p in self.success_paths
            ])
            all_values = np.array([
                p.realized_params.get(param, 0) for p in self.paths
            ])
            
            # Skip if no variation
            if np.std(all_values) < 1e-10:
                continue
            
            # Compute statistics
            failed_mean = float(np.mean(failed_values))
            success_mean = float(np.mean(success_values))
            pop_mean = float(np.mean(all_values))
            pop_std = float(np.std(all_values))
            
            # Effect size: Cohen's d
            pooled_std = np.sqrt(
                (np.var(failed_values) + np.var(success_values)) / 2
            )
            cohens_d = (failed_mean - success_mean) / (pooled_std + 1e-10)
            
            # Percentage difference
            if success_mean != 0:
                diff_pct = (failed_mean - success_mean) / abs(success_mean) * 100
            else:
                diff_pct = 0
            
            # Statistical test
            t_stat, p_value = stats.ttest_ind(failed_values, success_values)
            
            # Attribution score (normalized effect size)
            attribution = min(1.0, abs(cohens_d) / 2)
            
            # Direction and interpretation
            if cohens_d > 0.1:
                direction = 'higher'
                interpretation = f"Failed paths had higher {self.PARAMETER_DISPLAY_NAMES[param]}"
            elif cohens_d < -0.1:
                direction = 'lower'
                interpretation = f"Failed paths had lower {self.PARAMETER_DISPLAY_NAMES[param]}"
            else:
                direction = 'similar'
                interpretation = f"{self.PARAMETER_DISPLAY_NAMES[param]} was similar in failed and successful paths"
            
            causes.append(FailureCause(
                factor=param,
                display_name=self.PARAMETER_DISPLAY_NAMES[param],
                failed_mean=failed_mean,
                success_mean=success_mean,
                population_mean=pop_mean,
                difference_pct=float(diff_pct),
                cohens_d=float(cohens_d),
                attribution_score=float(attribution),
                confidence=float(1 - p_value),
                direction=direction,
                interpretation=interpretation
            ))
        
        # Sort by attribution score
        causes.sort(key=lambda x: x.attribution_score, reverse=True)
        
        return causes
    
    def analyze_timing(self) -> Tuple[List[CriticalPeriod], List[int], Optional[float]]:
        """
        Analyze when failures occur.
        
        Identifies critical periods with elevated failure risk
        and builds a histogram of failure timing.
        """
        if self.n_failed == 0:
            return [], [], None
        
        # Get failure months from equity curves
        failure_months = []
        for path in self.failed_paths:
            curve = path.equity_curve
            for month, capital in enumerate(curve):
                if capital <= 0:
                    failure_months.append(month)
                    break
            else:
                # Didn't hit zero, but still "failed" by return threshold
                # Assign to final month
                failure_months.append(len(curve) - 1)
        
        failure_months = np.array(failure_months)
        
        # Histogram
        max_month = int(np.max(failure_months)) + 1
        histogram = [0] * max_month
        for m in failure_months:
            histogram[m] += 1
        
        # Median failure month
        median_month = float(np.median(failure_months)) if len(failure_months) > 0 else None
        
        # Identify critical periods (consecutive months with high failures)
        periods = []
        
        # Find peaks in failure histogram
        total_failures = len(failure_months)
        cumulative = 0
        
        # Simple approach: identify windows with above-average failure rates
        window_size = 3
        avg_rate = total_failures / max_month if max_month > 0 else 0
        
        i = 0
        while i < max_month - window_size:
            window_failures = sum(histogram[i:i+window_size])
            window_rate = window_failures / window_size
            
            if window_rate > avg_rate * 1.5:  # 50% above average
                # Found a critical period
                cumulative += window_failures
                
                # Identify dominant cause for this period
                period_paths = [
                    p for p, m in zip(self.failed_paths, failure_months)
                    if i <= m < i + window_size
                ]
                dominant_cause = self._identify_dominant_cause(period_paths)
                
                periods.append(CriticalPeriod(
                    start_month=i,
                    end_month=i + window_size - 1,
                    hazard_rate=float(window_rate / max(1, self.n_paths - cumulative + window_failures)),
                    cumulative_failures=float(cumulative / total_failures),
                    typical_capital_level=self._avg_capital_at_month(period_paths, i),
                    typical_burn_rate=self._estimate_burn_rate(period_paths, i),
                    dominant_cause=dominant_cause
                ))
                
                i += window_size
            else:
                i += 1
        
        return periods, histogram, median_month
    
    def _identify_dominant_cause(self, paths: List[PathResult]) -> str:
        """Identify the most distinctive parameter for a set of paths."""
        if not paths:
            return "unknown"
        
        max_effect = 0
        dominant = "multiple_factors"
        
        for param in self.PARAMETER_DISPLAY_NAMES.keys():
            path_values = [p.realized_params.get(param, 0) for p in paths]
            all_values = [p.realized_params.get(param, 0) for p in self.paths]
            
            if np.std(all_values) < 1e-10:
                continue
            
            path_mean = np.mean(path_values)
            all_mean = np.mean(all_values)
            all_std = np.std(all_values)
            
            effect = abs(path_mean - all_mean) / (all_std + 1e-10)
            
            if effect > max_effect:
                max_effect = effect
                dominant = param
        
        return self.PARAMETER_DISPLAY_NAMES.get(dominant, dominant)
    
    def _avg_capital_at_month(self, paths: List[PathResult], month: int) -> float:
        """Get average capital at a specific month."""
        capitals = [p.equity_curve[month] if month < len(p.equity_curve) else 0 
                   for p in paths]
        return float(np.mean(capitals)) if capitals else 0
    
    def _estimate_burn_rate(self, paths: List[PathResult], month: int) -> float:
        """Estimate average burn rate at a specific month."""
        burns = []
        for p in paths:
            if month > 0 and month < len(p.equity_curve):
                burn = p.equity_curve[month - 1] - p.equity_curve[month]
                burns.append(burn)
        return float(np.mean(burns)) if burns else 0
    
    def analyze_trajectories(self) -> List[FailureTrajectory]:
        """
        Classify failure paths into trajectory archetypes.
        
        Identifies common patterns in how failures unfold:
        - Slow bleed: Gradual decline over many months
        - Sudden collapse: Rapid decline from a peak
        - Recovery failure: Initial recovery followed by collapse
        """
        if self.n_failed == 0:
            return []
        
        trajectories = defaultdict(list)
        
        for path in self.failed_paths:
            curve = path.equity_curve
            initial = curve[0]
            
            # Find peak
            peak_idx = np.argmax(curve)
            peak_val = curve[peak_idx]
            
            # Find failure point
            failure_idx = len(curve) - 1
            for i, val in enumerate(curve):
                if val <= 0:
                    failure_idx = i
                    break
            
            # Classify trajectory
            if peak_val > initial * 1.1 and peak_idx < failure_idx - 3:
                # Had a recovery then failed
                trajectories['recovery_failure'].append(path)
            elif failure_idx - peak_idx < 6:
                # Rapid collapse (less than 6 months from peak to failure)
                trajectories['sudden_collapse'].append(path)
            else:
                # Slow decline
                trajectories['slow_bleed'].append(path)
        
        results = []
        
        for traj_type, paths in trajectories.items():
            if not paths:
                continue
            
            # Compute characteristics
            months_to_fail = []
            peaks = []
            
            for p in paths:
                curve = p.equity_curve
                peak = max(curve)
                peaks.append(peak)
                
                for i, val in enumerate(curve):
                    if val <= 0:
                        months_to_fail.append(i)
                        break
                else:
                    months_to_fail.append(len(curve) - 1)
            
            # Warning signs based on trajectory type
            if traj_type == 'slow_bleed':
                warnings = [
                    "Consistent monthly losses",
                    "Customer acquisition below target",
                    "High burn rate relative to revenue"
                ]
            elif traj_type == 'sudden_collapse':
                warnings = [
                    "Over-reliance on few large customers",
                    "High customer concentration risk",
                    "Insufficient cash buffer"
                ]
            else:  # recovery_failure
                warnings = [
                    "Premature scaling",
                    "Unsustainable growth rate",
                    "Market conditions changed post-recovery"
                ]
            
            results.append(FailureTrajectory(
                trajectory_type=traj_type,
                prevalence=len(paths) / self.n_failed,
                months_to_failure=float(np.mean(months_to_fail)),
                peak_capital_reached=float(np.mean(peaks)),
                warning_signs=warnings
            ))
        
        # Sort by prevalence
        results.sort(key=lambda x: x.prevalence, reverse=True)
        
        return results
    
    def analyze_regimes(self) -> List[RegimeImpact]:
        """
        Analyze impact of economic regimes on failure.
        
        Computes how time spent in different regimes correlates
        with failure probability.
        """
        regime_impacts = []
        
        # Count time in each regime for failed vs successful paths
        regimes = ['normal', 'stress', 'boom']
        
        for regime in regimes:
            failed_time = []
            success_time = []
            
            for path in self.failed_paths:
                time_in_regime = sum(1 for r in path.regime_path if r == regime)
                failed_time.append(time_in_regime / len(path.regime_path))
            
            for path in self.success_paths:
                time_in_regime = sum(1 for r in path.regime_path if r == regime)
                success_time.append(time_in_regime / len(path.regime_path))
            
            if not failed_time or not success_time:
                continue
            
            failed_avg = np.mean(failed_time)
            success_avg = np.mean(success_time)
            pop_avg = (failed_avg * self.n_failed + success_avg * self.n_success) / self.n_paths
            
            # Conditional failure rate given high exposure to regime
            high_exposure_threshold = np.percentile(
                [sum(1 for r in p.regime_path if r == regime) / len(p.regime_path) 
                 for p in self.paths], 75
            )
            
            high_exposure_paths = [
                p for p in self.paths
                if sum(1 for r in p.regime_path if r == regime) / len(p.regime_path) > high_exposure_threshold
            ]
            
            if high_exposure_paths:
                conditional_failure = sum(
                    1 for p in high_exposure_paths
                    if p.is_ruin or p.total_return <= self.failure_threshold
                ) / len(high_exposure_paths)
            else:
                conditional_failure = self.n_failed / self.n_paths
            
            baseline_failure = self.n_failed / self.n_paths
            risk_mult = conditional_failure / baseline_failure if baseline_failure > 0 else 1.0
            
            regime_impacts.append(RegimeImpact(
                regime=regime,
                time_spent_pct=float(pop_avg * 100),
                conditional_failure_rate=float(conditional_failure),
                risk_multiplier=float(risk_mult)
            ))
        
        # Sort by risk multiplier
        regime_impacts.sort(key=lambda x: x.risk_multiplier, reverse=True)
        
        return regime_impacts
    
    def generate_insights(
        self, 
        causes: List[FailureCause],
        trajectories: List[FailureTrajectory]
    ) -> Tuple[List[str], List[str]]:
        """
        Generate actionable insights from analysis.
        
        Returns early warning signals and mitigation priorities.
        """
        early_warnings = []
        mitigations = []
        
        # From causes
        for cause in causes[:3]:  # Top 3 causes
            if cause.attribution_score > 0.3:
                if cause.direction == 'lower' and 'rate' in cause.factor.lower():
                    early_warnings.append(
                        f"Monitor {cause.display_name} closely - "
                        f"failed paths averaged {cause.failed_mean:.1%} vs {cause.success_mean:.1%}"
                    )
                    mitigations.append(
                        f"Improve {cause.display_name} through targeted interventions"
                    )
                elif cause.direction == 'higher' and 'churn' in cause.factor.lower():
                    early_warnings.append(
                        f"Watch for rising churn - "
                        f"failed paths had {cause.failed_mean:.1%} vs {cause.success_mean:.1%}"
                    )
                    mitigations.append(
                        "Invest in customer success and retention programs"
                    )
                elif cause.direction == 'higher' and 'burn' in cause.factor.lower():
                    early_warnings.append(
                        f"Control burn rate - "
                        f"failed paths burned {cause.failed_mean:.0f}M vs {cause.success_mean:.0f}M"
                    )
                    mitigations.append(
                        "Maintain strict cost discipline during development"
                    )
        
        # From trajectories
        if trajectories:
            dominant = trajectories[0]
            if dominant.trajectory_type == 'slow_bleed':
                early_warnings.append(
                    "Set monthly revenue targets and trigger review if missed 2+ months"
                )
                mitigations.append(
                    "Build monthly performance dashboards with automatic alerts"
                )
            elif dominant.trajectory_type == 'sudden_collapse':
                early_warnings.append(
                    "Monitor customer concentration - no single customer > 20% revenue"
                )
                mitigations.append(
                    "Diversify customer base and maintain cash reserves"
                )
        
        # Generic insights if lists are empty
        if not early_warnings:
            early_warnings = [
                "Track capital runway monthly",
                "Monitor customer acquisition vs plan",
                "Review burn rate against milestones"
            ]
        
        if not mitigations:
            mitigations = [
                "Maintain 6+ months runway buffer",
                "Set clear go/no-go decision points",
                "Prepare contingency cost reduction plans"
            ]
        
        return early_warnings, mitigations
    
    def analyze(self) -> PremortemResult:
        """
        Run complete premortem analysis.
        
        Returns
        -------
        PremortemResult
            Data-driven premortem analysis
        """
        # Define failure
        failure_def = f"Ruin (capital ≤ 0) OR return ≤ {self.failure_threshold}%"
        
        # Cause analysis
        causes = self.analyze_causes()
        
        # Identify cause interactions (pairs that co-occur in failures)
        interactions = self._find_interactions(causes)
        
        # Timing analysis
        critical_periods, histogram, median_month = self.analyze_timing()
        
        # Trajectory analysis
        trajectories = self.analyze_trajectories()
        
        # Regime analysis
        regime_impacts = self.analyze_regimes()
        
        # Generate insights
        warnings, mitigations = self.generate_insights(causes, trajectories)
        
        return PremortemResult(
            failure_definition=failure_def,
            failure_rate=self.n_failed / self.n_paths,
            failure_count=self.n_failed,
            primary_causes=causes,
            cause_interactions=interactions,
            critical_periods=critical_periods,
            failure_timing_histogram=histogram,
            median_failure_month=median_month,
            failure_trajectories=trajectories,
            regime_impacts=regime_impacts,
            early_warning_signals=warnings,
            mitigation_priorities=mitigations
        )
    
    def _find_interactions(
        self, 
        causes: List[FailureCause]
    ) -> List[Tuple[str, str, float]]:
        """Find pairs of causes that frequently co-occur in failures."""
        if self.n_failed < 10 or len(causes) < 2:
            return []
        
        interactions = []
        top_causes = causes[:5]  # Look at top 5 causes
        
        for i, cause1 in enumerate(top_causes):
            for cause2 in top_causes[i+1:]:
                # Check if both are extreme in same failure paths
                param1 = cause1.factor
                param2 = cause2.factor
                
                # Count co-occurrences of both being "bad"
                cooccur = 0
                for path in self.failed_paths:
                    val1 = path.realized_params.get(param1, 0)
                    val2 = path.realized_params.get(param2, 0)
                    
                    # "Bad" means in direction of failure
                    bad1 = (cause1.direction == 'lower' and val1 < cause1.population_mean) or \
                           (cause1.direction == 'higher' and val1 > cause1.population_mean)
                    bad2 = (cause2.direction == 'lower' and val2 < cause2.population_mean) or \
                           (cause2.direction == 'higher' and val2 > cause2.population_mean)
                    
                    if bad1 and bad2:
                        cooccur += 1
                
                cooccur_rate = cooccur / self.n_failed
                
                if cooccur_rate > 0.5:  # More than 50% co-occurrence
                    interactions.append((
                        cause1.display_name,
                        cause2.display_name,
                        cooccur_rate
                    ))
        
        # Sort by co-occurrence rate
        interactions.sort(key=lambda x: x[2], reverse=True)
        
        return interactions[:5]  # Top 5 interactions