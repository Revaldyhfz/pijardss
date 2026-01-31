"""
Data Models Module.

Provides Pydantic models for simulation inputs and outputs.
"""

from .parameters import (
    DistributionType,
    TriangularParams,
    BetaParams,
    LogNormalParams,
    GammaParams,
    DistributionSpec,
    RiskEventConfig,
    CapitalDevParams,
    SalesParams,
    PricingParams,
    RetentionCostParams,
    SimulationConfig,
    SimulationInput,
)

from .results import (
    RecommendationType,
    SummaryStatistics,
    PathPercentile,
    PathData,
    OutcomeDistribution,
    ReturnBucket,
    RiskMetrics,
    FailureCause,
    CriticalPeriod,
    RegimeAnalysis,
    PremortemAnalysis,
    SimulationMeta,
    SimulationResult,
)

__all__ = [
    # Parameter models
    'DistributionType',
    'TriangularParams',
    'BetaParams',
    'LogNormalParams',
    'GammaParams',
    'DistributionSpec',
    'RiskEventConfig',
    'CapitalDevParams',
    'SalesParams',
    'PricingParams',
    'RetentionCostParams',
    'SimulationConfig',
    'SimulationInput',
    # Result models
    'RecommendationType',
    'SummaryStatistics',
    'PathPercentile',
    'PathData',
    'OutcomeDistribution',
    'ReturnBucket',
    'RiskMetrics',
    'FailureCause',
    'CriticalPeriod',
    'RegimeAnalysis',
    'PremortemAnalysis',
    'SimulationMeta',
    'SimulationResult',
]