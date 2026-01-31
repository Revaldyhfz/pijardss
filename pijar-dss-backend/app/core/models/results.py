"""
Result Data Models.

Defines the structure for simulation outputs, including summary
statistics, paths, risk metrics, and premortem analysis.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class RecommendationType(str, Enum):
    """Decision recommendation categories."""
    PROCEED = "PROCEED"
    CAUTION = "CAUTION"
    REASSESS = "REASSESS"
    DO_NOT_PROCEED = "DO_NOT_PROCEED"


class SummaryStatistics(BaseModel):
    """
    Summary statistics from the Monte Carlo simulation.
    
    These are the key decision metrics displayed in the dashboard header.
    """
    # Probability metrics
    prob_profit: float = Field(..., ge=0, le=1, description="P(final > initial)")
    prob_double: float = Field(..., ge=0, le=1, description="P(return >= 100%)")
    prob_ruin: float = Field(..., ge=0, le=1, description="P(capital <= 0)")
    
    # Return metrics
    return_mean: float = Field(..., description="Mean return %")
    return_median: float = Field(..., description="Median return %")
    return_std: float = Field(..., description="Std dev of returns %")
    return_p5: float = Field(..., description="5th percentile return %")
    return_p95: float = Field(..., description="95th percentile return %")
    
    # Risk metrics
    var_5: float = Field(..., description="5% Value at Risk (capital loss)")
    cvar_5: float = Field(..., description="5% Conditional VaR")
    max_drawdown_mean: float = Field(..., description="Mean max drawdown %")
    max_drawdown_p95: float = Field(..., description="95th percentile max DD %")
    
    # Time metrics
    breakeven_mean: Optional[float] = Field(None, description="Mean months to breakeven")
    breakeven_rate: float = Field(..., ge=0, le=1, description="P(breakeven achieved)")
    
    # Recommendation
    recommendation: RecommendationType


class PathPercentile(BaseModel):
    """Equity curve percentiles at a single time point."""
    month: int
    p5: float
    p25: float
    p50: float  # Median
    p75: float
    p95: float


class PathData(BaseModel):
    """
    Path-level simulation data.
    
    Contains percentile bands for visualization and optionally
    sample paths for the fan chart.
    """
    percentiles: List[PathPercentile]
    sample_paths: Optional[List[List[float]]] = Field(
        None, 
        description="Sampled individual paths for fan visualization"
    )
    median_path: List[float]


class OutcomeDistribution(BaseModel):
    """Distribution of outcome categories."""
    double_plus: int = Field(..., description="Count: return >= 100%")
    profitable: int = Field(..., description="Count: 0% < return < 100%")
    loss: int = Field(..., description="Count: return <= 0%, not ruined")
    ruin: int = Field(..., description="Count: capital <= 0")
    total: int


class ReturnBucket(BaseModel):
    """Histogram bucket for return distribution."""
    range_start: float
    range_end: float
    count: int
    percentage: float


class RiskMetrics(BaseModel):
    """
    Comprehensive risk metrics.
    
    Provides detailed risk analysis beyond summary statistics.
    """
    # Value at Risk at multiple confidence levels
    var: Dict[str, float] = Field(..., description="VaR by confidence level")
    cvar: Dict[str, float] = Field(..., description="CVaR by confidence level")
    
    # Drawdown analysis
    drawdown_mean: float
    drawdown_std: float
    drawdown_p50: float
    drawdown_p95: float
    drawdown_p99: float
    
    # Time-based risk
    months_underwater_mean: float = Field(
        ..., 
        description="Average months below starting capital"
    )
    
    # Survival analysis
    survival_curve: List[float] = Field(
        ...,
        description="Probability of survival at each month"
    )
    
    # Tail analysis
    tail_loss_mean: float = Field(
        ...,
        description="Mean loss in worst 5% of scenarios"
    )


class FailureCause(BaseModel):
    """Attribution of a failure cause."""
    factor: str
    attribution: float = Field(..., ge=0, le=1)
    conditional_mean: float
    conditional_std: float
    description: str


class CriticalPeriod(BaseModel):
    """Identification of high-risk time periods."""
    start_month: int
    end_month: int
    risk_concentration: float
    dominant_risks: List[str]


class RegimeAnalysis(BaseModel):
    """Analysis of regime effects on outcomes."""
    regime_probabilities: Dict[str, float]
    conditional_failure_rates: Dict[str, float]
    regime_impact_on_return: Dict[str, float]


class PremortemAnalysis(BaseModel):
    """
    Data-driven premortem analysis.
    
    Identifies why failures happen and what causes them,
    derived from simulation data rather than checklists.
    """
    # Overall failure characterization
    failure_rate: float
    failure_count: int
    
    # Cause attribution
    primary_causes: List[FailureCause]
    
    # Temporal analysis
    critical_periods: List[CriticalPeriod]
    failure_timing_distribution: List[float] = Field(
        ...,
        description="Distribution of failure months"
    )
    
    # Regime analysis
    regime_analysis: Optional[RegimeAnalysis]
    
    # Sensitivity
    most_sensitive_parameters: List[Dict[str, Any]]


class SimulationMeta(BaseModel):
    """Metadata about the simulation run."""
    n_simulations: int
    time_horizon: int
    seed: Optional[int]
    computation_time_ms: float
    timestamp: str


class SimulationResult(BaseModel):
    """
    Complete simulation result.
    
    This is the top-level response from the /simulate endpoint.
    """
    summary: SummaryStatistics
    paths: PathData
    outcomes: OutcomeDistribution
    return_distribution: List[ReturnBucket]
    risk_metrics: RiskMetrics
    premortem: PremortemAnalysis
    meta: SimulationMeta
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": {
                    "prob_profit": 0.847,
                    "prob_double": 0.623,
                    "prob_ruin": 0.012,
                    "return_mean": 185.3,
                    "return_median": 156.2,
                    "return_std": 120.5,
                    "return_p5": -15.2,
                    "return_p95": 420.8,
                    "var_5": 1250.0,
                    "cvar_5": 890.0,
                    "max_drawdown_mean": 32.1,
                    "max_drawdown_p95": 58.3,
                    "breakeven_mean": 18.5,
                    "breakeven_rate": 0.91,
                    "recommendation": "PROCEED"
                }
            }
        }