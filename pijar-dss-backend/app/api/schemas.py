"""
API Request/Response Schemas.

Defines the Pydantic models for API serialization,
separate from internal data models.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# ============== REQUEST SCHEMAS ==============

class DistributionSpec(BaseModel):
    """Distribution specification for input parameters."""
    type: str = Field(..., description="Distribution type: triangular, beta, lognormal, gamma, fixed")
    params: Dict[str, Any] = Field(..., description="Distribution parameters")


class RiskEventInput(BaseModel):
    """Risk event configuration."""
    name: str
    intensity: float = Field(ge=0, description="Annual arrival rate")
    impact_type: str = Field(..., description="adoption, churn, revenue, or cost")
    severity_min: float = Field(ge=0, le=2)
    severity_mode: float = Field(ge=0, le=2)
    severity_max: float = Field(ge=0, le=2)
    recovery_rate: float = Field(ge=0, le=1, default=0.3)
    start_month: int = Field(ge=1, default=1)
    end_month: Optional[int] = None


class SimulationRequest(BaseModel):
    """Request body for /simulate endpoint."""
    # Capital & Development
    initial_capital: DistributionSpec
    dev_duration: DistributionSpec
    dev_burn: DistributionSpec
    
    # Sales
    leads_per_month: DistributionSpec
    win_rate_bumn: DistributionSpec
    win_rate_open: DistributionSpec
    bumn_ratio: float = Field(ge=0, le=1, default=0.35)
    sales_cycle_months: DistributionSpec
    
    # Pricing
    contract_small: DistributionSpec
    contract_medium: DistributionSpec
    contract_large: DistributionSpec
    size_distribution: Dict[str, float] = Field(
        default={"small": 0.5, "medium": 0.35, "large": 0.15}
    )
    
    # Retention & Costs
    churn_rate: DistributionSpec
    op_overhead: float = Field(ge=0, default=120)
    cost_per_customer: float = Field(ge=0, default=5)
    
    # Risk Events
    risk_events: List[RiskEventInput] = Field(default_factory=list)
    
    # Simulation Config
    n_simulations: int = Field(ge=1, le=10000, default=500)
    time_horizon: int = Field(ge=6, le=120, default=36)
    seed: Optional[int] = None
    enable_regime_switching: bool = True
    enable_risk_events: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "initial_capital": {"type": "triangular", "params": {"min": 4000, "mode": 5000, "max": 6000}},
                "dev_duration": {"type": "triangular", "params": {"min": 4, "mode": 6, "max": 9}},
                "dev_burn": {"type": "triangular", "params": {"min": 160, "mode": 200, "max": 250}},
                "leads_per_month": {"type": "triangular", "params": {"min": 4, "mode": 7, "max": 12}},
                "win_rate_bumn": {"type": "beta", "params": {"alpha": 14, "beta": 6}},
                "win_rate_open": {"type": "beta", "params": {"alpha": 4, "beta": 14}},
                "bumn_ratio": 0.35,
                "sales_cycle_months": {"type": "gamma", "params": {"shape": 6.25, "scale": 0.8}},
                "contract_small": {"type": "lognormal", "params": {"mean": 180, "cv": 0.2}},
                "contract_medium": {"type": "lognormal", "params": {"mean": 320, "cv": 0.15}},
                "contract_large": {"type": "lognormal", "params": {"mean": 550, "cv": 0.1}},
                "churn_rate": {"type": "beta", "params": {"alpha": 2, "beta": 18}},
                "n_simulations": 500,
                "time_horizon": 36
            }
        }


class SensitivityRequest(BaseModel):
    """Request for sensitivity analysis."""
    output_metric: str = Field(default="return", description="return, final_capital, max_drawdown, is_profitable")
    variation_pct: float = Field(ge=0.05, le=0.5, default=0.2)


# ============== RESPONSE SCHEMAS ==============

class SummaryStats(BaseModel):
    """Summary statistics response."""
    prob_profit: float
    prob_double: float
    prob_ruin: float
    return_mean: float
    return_median: float
    return_std: float
    return_p5: float
    return_p95: float
    var_5: float
    cvar_5: float
    max_drawdown_mean: float
    max_drawdown_p95: float
    breakeven_mean: Optional[float]
    breakeven_rate: float
    recommendation: str


class PathPercentileResponse(BaseModel):
    """Equity curve percentile at a month."""
    month: int
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float


class PathDataResponse(BaseModel):
    """Path data for visualization."""
    percentiles: List[PathPercentileResponse]
    sample_paths: List[List[float]]
    median_path: List[float]


class OutcomeResponse(BaseModel):
    """Outcome distribution."""
    double_plus: int
    profitable: int
    loss: int
    ruin: int
    total: int


class ReturnBucketResponse(BaseModel):
    """Histogram bucket."""
    range_start: float
    range_end: float
    count: int
    percentage: float


class RiskMetricsResponse(BaseModel):
    """Risk metrics."""
    var: Dict[str, float]
    cvar: Dict[str, float]
    drawdown_mean: float
    drawdown_std: float
    drawdown_p95: float
    drawdown_max: float
    months_underwater_mean: float
    survival_curve: List[float]
    tail_loss_mean: float


class FailureCauseResponse(BaseModel):
    """Failure cause attribution."""
    factor: str
    display_name: str
    failed_mean: float
    success_mean: float
    difference_pct: float
    attribution_score: float
    direction: str
    interpretation: str


class CriticalPeriodResponse(BaseModel):
    """Critical period identification."""
    start_month: int
    end_month: int
    hazard_rate: float
    cumulative_failures: float
    dominant_cause: str


class FailureTrajectoryResponse(BaseModel):
    """Failure trajectory archetype."""
    trajectory_type: str
    prevalence: float
    months_to_failure: float
    peak_capital_reached: float
    warning_signs: List[str]


class RegimeImpactResponse(BaseModel):
    """Regime impact on failure."""
    regime: str
    time_spent_pct: float
    conditional_failure_rate: float
    risk_multiplier: float


class PremortemResponse(BaseModel):
    """Premortem analysis response."""
    failure_definition: str
    failure_rate: float
    failure_count: int
    primary_causes: List[FailureCauseResponse]
    cause_interactions: List[Dict[str, Any]]
    critical_periods: List[CriticalPeriodResponse]
    failure_timing_histogram: List[int]
    median_failure_month: Optional[float]
    failure_trajectories: List[FailureTrajectoryResponse]
    regime_impacts: List[RegimeImpactResponse]
    early_warning_signals: List[str]
    mitigation_priorities: List[str]


class TornadoItemResponse(BaseModel):
    """Tornado diagram item."""
    parameter: str
    display_name: str
    low_value: float
    base_value: float
    high_value: float
    output_at_low: float
    output_at_base: float
    output_at_high: float
    swing: float


class CorrelationResponse(BaseModel):
    """Correlation result."""
    parameter: str
    spearman_corr: float
    is_significant: bool


class SensitivityResponse(BaseModel):
    """Sensitivity analysis response."""
    tornado: List[TornadoItemResponse]
    correlations: List[CorrelationResponse]
    top_positive_drivers: List[str]
    top_negative_drivers: List[str]
    total_r2: float


class SimulationMetaResponse(BaseModel):
    """Simulation metadata."""
    n_simulations: int
    time_horizon: int
    seed: Optional[int]
    computation_time_ms: float
    timestamp: str


class SimulationResponse(BaseModel):
    """Complete simulation response."""
    summary: SummaryStats
    paths: PathDataResponse
    outcomes: OutcomeResponse
    return_distribution: List[ReturnBucketResponse]
    risk_metrics: RiskMetricsResponse
    premortem: PremortemResponse
    sensitivity: SensitivityResponse
    meta: SimulationMetaResponse