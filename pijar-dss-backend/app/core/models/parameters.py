"""
Parameter Data Models.

Defines the structure for simulation inputs, ensuring type safety
and validation through Pydantic models.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Literal
from enum import Enum


class DistributionType(str, Enum):
    """Types of probability distributions for input parameters."""
    TRIANGULAR = "triangular"
    BETA = "beta"
    LOGNORMAL = "lognormal"
    GAMMA = "gamma"
    FIXED = "fixed"


class TriangularParams(BaseModel):
    """Parameters for triangular distribution."""
    min_val: float = Field(..., alias="min")
    mode: float
    max_val: float = Field(..., alias="max")
    
    class Config:
        populate_by_name = True


class BetaParams(BaseModel):
    """Parameters for beta distribution."""
    alpha: float = Field(gt=0)
    beta: float = Field(gt=0)
    
    @classmethod
    def from_mean_sample_size(cls, mean: float, sample_size: float):
        return cls(alpha=mean * sample_size, beta=(1 - mean) * sample_size)


class LogNormalParams(BaseModel):
    """Parameters for log-normal distribution."""
    mu: Optional[float] = None
    sigma: Optional[float] = None
    mean: Optional[float] = None
    cv: Optional[float] = None
    
    @field_validator('sigma')
    @classmethod
    def sigma_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('sigma must be positive')
        return v


class GammaParams(BaseModel):
    """Parameters for gamma distribution."""
    shape: float = Field(gt=0)
    scale: float = Field(gt=0)


class DistributionSpec(BaseModel):
    """
    Specification for an uncertain parameter.
    
    Allows different distribution types with their respective parameters.
    """
    type: DistributionType
    params: Dict[str, Any]
    
    def get_triangular(self) -> TriangularParams:
        return TriangularParams(**self.params)
    
    def get_beta(self) -> BetaParams:
        return BetaParams(**self.params)


class RiskEventConfig(BaseModel):
    """
    Configuration for a risk event.
    
    Defines the arrival rate, impact type, and severity distribution
    for a specific risk factor.
    """
    name: str
    intensity: float = Field(ge=0, description="Annual arrival rate")
    impact_type: Literal["adoption", "churn", "revenue", "cost"]
    severity_min: float = Field(ge=0, le=2, description="Min multiplier")
    severity_mode: float = Field(ge=0, le=2, description="Mode multiplier")
    severity_max: float = Field(ge=0, le=2, description="Max multiplier")
    recovery_rate: float = Field(ge=0, le=1, default=0.3, 
                                  description="Monthly recovery probability")
    start_month: int = Field(ge=1, default=1)
    end_month: Optional[int] = None


class CapitalDevParams(BaseModel):
    """Capital and development phase parameters."""
    initial_capital: DistributionSpec
    dev_duration: DistributionSpec
    dev_burn: DistributionSpec


class SalesParams(BaseModel):
    """Sales and conversion parameters."""
    leads_per_month: DistributionSpec
    win_rate_bumn: DistributionSpec
    win_rate_open: DistributionSpec
    bumn_ratio: float = Field(ge=0, le=1)
    sales_cycle_months: DistributionSpec


class PricingParams(BaseModel):
    """Contract pricing parameters."""
    contract_small: DistributionSpec
    contract_medium: DistributionSpec
    contract_large: DistributionSpec
    size_distribution: Dict[str, float] = Field(
        default={"small": 0.5, "medium": 0.35, "large": 0.15}
    )


class RetentionCostParams(BaseModel):
    """Retention and cost parameters."""
    churn_rate: DistributionSpec
    op_overhead: float
    cost_per_customer: float


class SimulationConfig(BaseModel):
    """Configuration for the simulation run."""
    n_simulations: int = Field(default=500, ge=1, le=10000)
    time_horizon: int = Field(default=36, ge=6, le=120)
    seed: Optional[int] = None
    enable_regime_switching: bool = True
    enable_risk_events: bool = True


class SimulationInput(BaseModel):
    """
    Complete input specification for a simulation run.
    
    This is the top-level model that the API accepts.
    """
    capital_dev: CapitalDevParams
    sales: SalesParams
    pricing: PricingParams
    retention_costs: RetentionCostParams
    risk_events: List[RiskEventConfig] = Field(default_factory=list)
    config: SimulationConfig = Field(default_factory=SimulationConfig)
    
    class Config:
        json_schema_extra = {
            "example": {
                "capital_dev": {
                    "initial_capital": {
                        "type": "triangular",
                        "params": {"min": 4000, "mode": 5000, "max": 6000}
                    },
                    "dev_duration": {
                        "type": "triangular", 
                        "params": {"min": 4, "mode": 6, "max": 9}
                    },
                    "dev_burn": {
                        "type": "triangular",
                        "params": {"min": 160, "mode": 200, "max": 250}
                    }
                },
                "sales": {
                    "leads_per_month": {
                        "type": "triangular",
                        "params": {"min": 4, "mode": 7, "max": 12}
                    },
                    "win_rate_bumn": {
                        "type": "beta",
                        "params": {"alpha": 14, "beta": 6}
                    },
                    "win_rate_open": {
                        "type": "beta",
                        "params": {"alpha": 4, "beta": 14}
                    },
                    "bumn_ratio": 0.35,
                    "sales_cycle_months": {
                        "type": "gamma",
                        "params": {"shape": 6.25, "scale": 0.8}
                    }
                },
                "pricing": {
                    "contract_small": {
                        "type": "lognormal",
                        "params": {"mean": 180, "cv": 0.2}
                    },
                    "contract_medium": {
                        "type": "lognormal",
                        "params": {"mean": 320, "cv": 0.15}
                    },
                    "contract_large": {
                        "type": "lognormal",
                        "params": {"mean": 550, "cv": 0.1}
                    }
                },
                "retention_costs": {
                    "churn_rate": {
                        "type": "beta",
                        "params": {"alpha": 2, "beta": 18}
                    },
                    "op_overhead": 120,
                    "cost_per_customer": 5
                },
                "config": {
                    "n_simulations": 500,
                    "time_horizon": 36
                }
            }
        }