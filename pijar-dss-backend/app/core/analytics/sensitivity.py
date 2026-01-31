"""
Sensitivity Analysis Module.

Determines which input parameters have the greatest impact on outcomes.
This is critical for understanding where to focus efforts and what
assumptions matter most.

Methods Implemented:
-------------------
1. Tornado Analysis: One-at-a-time variation, visual impact ranking
2. Correlation Analysis: Which inputs correlate with outputs
3. Contribution to Variance: Decompose output variance by input

Why Sensitivity Matters:
-----------------------
If P(profit) is highly sensitive to win_rate_bumn but insensitive to
dev_duration, then:
- Invest in improving BUMN relationships (high leverage)
- Don't stress about exact dev timeline (low impact)
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from scipy import stats

from ..simulation.path import PathResult


@dataclass
class TornadoItem:
    """
    Single parameter's tornado analysis result.
    
    Shows how output changes when this parameter varies from
    low to high while others stay at base values.
    """
    parameter: str
    display_name: str
    
    # Input values tested
    low_value: float
    base_value: float
    high_value: float
    
    # Output at each input level
    output_at_low: float
    output_at_base: float
    output_at_high: float
    
    # Impact metrics
    swing: float           # |high - low| output change
    asymmetry: float       # How asymmetric is the impact
    
    @property
    def downside_impact(self) -> float:
        """Impact of moving to pessimistic value."""
        return self.output_at_low - self.output_at_base
    
    @property
    def upside_impact(self) -> float:
        """Impact of moving to optimistic value."""
        return self.output_at_high - self.output_at_base


@dataclass
class CorrelationResult:
    """
    Correlation between an input parameter and output metric.
    
    Uses both Pearson (linear) and Spearman (rank) correlation
    to capture different relationship types.
    """
    parameter: str
    output_metric: str
    
    pearson_corr: float
    pearson_pvalue: float
    
    spearman_corr: float
    spearman_pvalue: float
    
    @property
    def is_significant(self) -> bool:
        """Is correlation statistically significant at 5% level?"""
        return self.spearman_pvalue < 0.05


@dataclass
class VarianceContribution:
    """
    Contribution of each parameter to output variance.
    
    Uses linear regression R² decomposition to estimate
    how much of output variance is "explained" by each input.
    """
    parameter: str
    marginal_r2: float      # R² from this parameter alone
    contribution_pct: float  # % of total explained variance


@dataclass
class SensitivityResult:
    """Complete sensitivity analysis results."""
    tornado: List[TornadoItem]
    correlations: List[CorrelationResult]
    variance_contributions: List[VarianceContribution]
    
    # Top drivers
    top_positive_drivers: List[str]  # Parameters that most improve outcome
    top_negative_drivers: List[str]  # Parameters that most hurt outcome
    
    # Overall explanatory power
    total_r2: float  # How much variance is explained by all inputs


class SensitivityAnalyzer:
    """
    Sensitivity analyzer for Monte Carlo results.
    
    Analyzes how simulation outputs depend on input parameters
    by examining the correlation structure in the simulation data.
    
    Parameters
    ----------
    path_results : List[PathResult]
        Results from Monte Carlo simulation
    output_metric : str
        Which output to analyze ('return', 'prob_profit', 'max_drawdown')
    """
    
    PARAMETER_NAMES = {
        'initial_capital': 'Initial Capital',
        'dev_duration': 'Dev Duration',
        'dev_burn': 'Monthly Burn Rate',
        'leads_per_month': 'Leads per Month',
        'win_rate_bumn': 'BUMN Win Rate',
        'win_rate_open': 'Open Win Rate',
        'annual_churn_rate': 'Annual Churn Rate',
    }
    
    def __init__(
        self, 
        path_results: List[PathResult],
        output_metric: str = 'return'
    ):
        self.paths = path_results
        self.n_paths = len(path_results)
        self.output_metric = output_metric
        
        # Extract data
        self._extract_data()
    
    def _extract_data(self):
        """Extract input parameters and outputs into arrays."""
        # Outputs
        if self.output_metric == 'return':
            self.outputs = np.array([p.total_return for p in self.paths])
        elif self.output_metric == 'final_capital':
            self.outputs = np.array([p.final_capital for p in self.paths])
        elif self.output_metric == 'max_drawdown':
            self.outputs = np.array([p.max_drawdown for p in self.paths])
        elif self.output_metric == 'is_profitable':
            self.outputs = np.array([1 if p.total_return > 0 else 0 for p in self.paths])
        else:
            self.outputs = np.array([p.total_return for p in self.paths])
        
        # Inputs (from realized_params)
        self.input_names = list(self.PARAMETER_NAMES.keys())
        self.inputs = {}
        
        for param in self.input_names:
            values = [p.realized_params.get(param, 0) for p in self.paths]
            self.inputs[param] = np.array(values)
    
    def compute_correlations(self) -> List[CorrelationResult]:
        """
        Compute correlation between each input and the output.
        
        Uses both Pearson (linear) and Spearman (rank) correlation.
        Spearman is more robust to outliers and non-linear relationships.
        """
        results = []
        
        for param in self.input_names:
            x = self.inputs[param]
            y = self.outputs
            
            # Skip if no variation
            if np.std(x) < 1e-10:
                continue
            
            # Pearson correlation
            pearson_r, pearson_p = stats.pearsonr(x, y)
            
            # Spearman rank correlation
            spearman_r, spearman_p = stats.spearmanr(x, y)
            
            results.append(CorrelationResult(
                parameter=param,
                output_metric=self.output_metric,
                pearson_corr=float(pearson_r),
                pearson_pvalue=float(pearson_p),
                spearman_corr=float(spearman_r),
                spearman_pvalue=float(spearman_p)
            ))
        
        # Sort by absolute Spearman correlation
        results.sort(key=lambda x: abs(x.spearman_corr), reverse=True)
        
        return results
    
    def compute_variance_contributions(self) -> Tuple[List[VarianceContribution], float]:
        """
        Decompose output variance by input parameters.
        
        Uses marginal R² from simple linear regression to estimate
        each parameter's contribution to output variance.
        
        Note: Contributions may not sum to 100% due to:
        1. Non-linear relationships
        2. Interaction effects
        3. Unexplained variance
        """
        contributions = []
        total_var = np.var(self.outputs)
        
        if total_var < 1e-10:
            return [], 0.0
        
        # Compute marginal R² for each parameter
        for param in self.input_names:
            x = self.inputs[param]
            
            if np.std(x) < 1e-10:
                continue
            
            # Simple linear regression: y = a + b*x
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, self.outputs)
            
            marginal_r2 = r_value ** 2
            
            contributions.append(VarianceContribution(
                parameter=param,
                marginal_r2=float(marginal_r2),
                contribution_pct=float(marginal_r2 * 100)
            ))
        
        # Sort by contribution
        contributions.sort(key=lambda x: x.marginal_r2, reverse=True)
        
        # Total R² from multiple regression
        # Build design matrix
        X = np.column_stack([self.inputs[p] for p in self.input_names if np.std(self.inputs[p]) > 1e-10])
        
        if X.shape[1] > 0:
            # Add intercept
            X = np.column_stack([np.ones(self.n_paths), X])
            
            # OLS: β = (X'X)^(-1) X'y
            try:
                beta = np.linalg.lstsq(X, self.outputs, rcond=None)[0]
                y_pred = X @ beta
                ss_res = np.sum((self.outputs - y_pred) ** 2)
                ss_tot = np.sum((self.outputs - np.mean(self.outputs)) ** 2)
                total_r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            except:
                total_r2 = sum(c.marginal_r2 for c in contributions)
        else:
            total_r2 = 0.0
        
        return contributions, float(total_r2)
    
    def compute_tornado(self, variation_pct: float = 0.20) -> List[TornadoItem]:
        """
        Compute tornado diagram data.
        
        For each parameter, estimates the output change when that
        parameter moves from its low to high value.
        
        This uses the correlation structure from the simulation data
        rather than re-running simulations.
        
        Parameters
        ----------
        variation_pct : float
            Percentage variation to consider (e.g., 0.20 = ±20%)
        """
        tornado_items = []
        
        # Base output (median)
        base_output = float(np.median(self.outputs))
        
        for param in self.input_names:
            x = self.inputs[param]
            
            if np.std(x) < 1e-10:
                continue
            
            # Parameter statistics
            base_value = float(np.median(x))
            low_value = float(np.percentile(x, 10))
            high_value = float(np.percentile(x, 90))
            
            # Estimate output at low/high using linear regression
            slope, intercept, r_value, _, _ = stats.linregress(x, self.outputs)
            
            output_at_low = intercept + slope * low_value
            output_at_high = intercept + slope * high_value
            output_at_base = intercept + slope * base_value
            
            swing = abs(output_at_high - output_at_low)
            
            # Asymmetry: is upside bigger than downside?
            upside = output_at_high - output_at_base
            downside = output_at_base - output_at_low
            asymmetry = (upside - downside) / (swing + 1e-10)
            
            tornado_items.append(TornadoItem(
                parameter=param,
                display_name=self.PARAMETER_NAMES.get(param, param),
                low_value=low_value,
                base_value=base_value,
                high_value=high_value,
                output_at_low=float(output_at_low),
                output_at_base=float(output_at_base),
                output_at_high=float(output_at_high),
                swing=float(swing),
                asymmetry=float(asymmetry)
            ))
        
        # Sort by swing (impact)
        tornado_items.sort(key=lambda x: x.swing, reverse=True)
        
        return tornado_items
    
    def analyze(self) -> SensitivityResult:
        """
        Run complete sensitivity analysis.
        
        Returns
        -------
        SensitivityResult
        """
        correlations = self.compute_correlations()
        variance_contributions, total_r2 = self.compute_variance_contributions()
        tornado = self.compute_tornado()
        
        # Identify top drivers
        top_positive = [
            c.parameter for c in correlations 
            if c.spearman_corr > 0 and c.is_significant
        ][:3]
        
        top_negative = [
            c.parameter for c in correlations 
            if c.spearman_corr < 0 and c.is_significant
        ][:3]
        
        return SensitivityResult(
            tornado=tornado,
            correlations=correlations,
            variance_contributions=variance_contributions,
            top_positive_drivers=top_positive,
            top_negative_drivers=top_negative,
            total_r2=total_r2
        )