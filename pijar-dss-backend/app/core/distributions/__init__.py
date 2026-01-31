"""
Probability Distribution Module.

This module provides probability distributions for modeling
input uncertainty in Monte Carlo simulations.

Available Distributions
-----------------------
- TriangularDistribution: Bounded uncertainty with min/mode/max
- BetaDistribution: Rates and proportions in [0, 1]
- LogNormalDistribution: Positive right-skewed values
- GammaDistribution: Durations and waiting times

Usage
-----
>>> from app.core.distributions import TriangularDistribution, BetaDistribution
>>> 
>>> # Development duration: 4-9 months, most likely 6
>>> dev_time = TriangularDistribution(min_val=4, mode=6, max_val=9)
>>> 
>>> # Win rate: 70% based on ~20 deals
>>> win_rate = BetaDistribution.from_mean_sample_size(mean=0.7, sample_size=20)
"""

from .base import BaseDistribution
from .triangular import TriangularDistribution
from .beta import BetaDistribution
from .lognormal import LogNormalDistribution
from .gamma import GammaDistribution

__all__ = [
    'BaseDistribution',
    'TriangularDistribution',
    'BetaDistribution',
    'LogNormalDistribution',
    'GammaDistribution',
]