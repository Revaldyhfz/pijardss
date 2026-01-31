"""
Analytics Module.

Provides post-simulation analysis:
- Risk analysis (VaR, CVaR, drawdown, survival)
- Sensitivity analysis (tornado, correlation, variance decomposition)
- Premortem analysis (failure attribution, timing, trajectories)
"""

from .risk import (
    RiskAnalyzer,
    RiskAnalysisResult,
    VaRResult,
    CVaRResult,
    DrawdownAnalysis,
    SurvivalAnalysis,
    UnderwaterAnalysis,
    TailAnalysis,
)

from .sensitivity import (
    SensitivityAnalyzer,
    SensitivityResult,
    TornadoItem,
    CorrelationResult,
    VarianceContribution,
)

from .premortem import (
    PremortemAnalyzer,
    PremortemResult,
    FailureCause,
    CriticalPeriod,
    FailureTrajectory,
    RegimeImpact,
)

__all__ = [
    # Risk
    'RiskAnalyzer',
    'RiskAnalysisResult',
    'VaRResult',
    'CVaRResult',
    'DrawdownAnalysis',
    'SurvivalAnalysis',
    'UnderwaterAnalysis',
    'TailAnalysis',
    # Sensitivity
    'SensitivityAnalyzer',
    'SensitivityResult',
    'TornadoItem',
    'CorrelationResult',
    'VarianceContribution',
    # Premortem
    'PremortemAnalyzer',
    'PremortemResult',
    'FailureCause',
    'CriticalPeriod',
    'FailureTrajectory',
    'RegimeImpact',
]