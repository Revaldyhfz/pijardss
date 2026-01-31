"""
Gamma Distribution for Duration and Waiting Time Uncertainty.

The Gamma distribution is the natural choice for modeling:
1. Waiting times (time until k events occur)
2. Durations (development time, sales cycle length)
3. Aggregate of exponential processes

Why Gamma?
----------
If you're waiting for k independent events, each with exponential
waiting time, the total wait is Gamma-distributed. This matches
many business processes: "time to close deal" is the sum of
"time to qualify", "time to proposal", "time to negotiation", etc.

Parameterization:
----------------
We use shape (k) and scale (θ):
- k (shape): "equivalent number of stages"
- θ (scale): "average time per stage"

Mean = k × θ
Variance = k × θ²

Use Cases in Pijar DSS:
----------------------
- Sales cycle duration: "Typically 4-6 months with some variation"
- Development delays: "Could extend by 0-4 months"
- Time to churn: "Customers typically stay 2-3 years"
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from scipy import stats
from typing import Union, Optional

from .base import BaseDistribution


class GammaDistribution(BaseDistribution):
    """
    Gamma distribution for positive durations and waiting times.
    
    Parameters
    ----------
    shape : float
        Shape parameter k (> 0)
        Interpretation: "number of stages" or "concentration"
    scale : float
        Scale parameter θ (> 0)
        Interpretation: "average time per stage"
        
    Note
    ----
    scipy uses shape and scale; some sources use shape and rate (1/scale).
    
    Examples
    --------
    >>> # Sales cycle: mean 5 months, moderate variability
    >>> cycle = GammaDistribution.from_mean_cv(mean=5, cv=0.4)
    >>> cycle.mean
    5.0
    """
    
    def __init__(self, shape: float, scale: float):
        if shape <= 0:
            raise ValueError(f"shape must be > 0, got {shape}")
        if scale <= 0:
            raise ValueError(f"scale must be > 0, got {scale}")
        
        self.shape = float(shape)
        self.scale = float(scale)
        self._scipy_dist = stats.gamma(a=shape, scale=scale)
    
    @classmethod
    def from_mean_cv(cls, mean: float, cv: float) -> 'GammaDistribution':
        """
        Create from mean and coefficient of variation.
        
        For Gamma: CV = 1/sqrt(k), so k = 1/CV²
        
        Parameters
        ----------
        mean : float
            Desired mean (> 0)
        cv : float
            Coefficient of variation (> 0)
            
        Returns
        -------
        GammaDistribution
        """
        if mean <= 0:
            raise ValueError(f"mean must be > 0, got {mean}")
        if cv <= 0:
            raise ValueError(f"cv must be > 0, got {cv}")
        
        # k = 1/CV², θ = mean/k = mean × CV²
        shape = 1 / (cv ** 2)
        scale = mean * cv ** 2
        
        return cls(shape=shape, scale=scale)
    
    @classmethod
    def from_mean_std(cls, mean: float, std: float) -> 'GammaDistribution':
        """
        Create from mean and standard deviation.
        
        Parameters
        ----------
        mean : float
            Desired mean (> 0)
        std : float  
            Desired standard deviation (> 0)
            
        Returns
        -------
        GammaDistribution
        """
        cv = std / mean
        return cls.from_mean_cv(mean=mean, cv=cv)
    
    @classmethod
    def from_percentiles(
        cls, 
        p50: float, 
        p90: float
    ) -> 'GammaDistribution':
        """
        Create from median and 90th percentile.
        
        Useful for elicitation: "Usually takes about X, but can take up to Y"
        
        Parameters
        ----------
        p50 : float
            Median (50th percentile)
        p90 : float
            90th percentile
            
        Returns
        -------
        GammaDistribution
        """
        # This requires numerical solving; we use a simple approximation
        # based on the ratio p90/p50
        ratio = p90 / p50
        
        # For Gamma, the ratio of percentiles depends on shape
        # We use a lookup/interpolation approach
        # Approximate: shape ≈ 1.5 / (log(ratio))^2 for typical ratios
        log_ratio = np.log(ratio)
        shape = max(0.5, 2.0 / (log_ratio ** 2))
        
        # Given shape, solve for scale from median
        scale = p50 / stats.gamma.ppf(0.5, a=shape)
        
        return cls(shape=shape, scale=scale)
    
    def sample(
        self, 
        size: Union[int, tuple] = 1, 
        rng: Optional[Generator] = None
    ) -> NDArray:
        """Draw random samples."""
        if rng is None:
            rng = np.random.default_rng()
        
        return rng.gamma(shape=self.shape, scale=self.scale, size=size)
    
    def pdf(self, x: NDArray) -> NDArray:
        """Probability density function."""
        return self._scipy_dist.pdf(x)
    
    def cdf(self, x: NDArray) -> NDArray:
        """Cumulative distribution function."""
        return self._scipy_dist.cdf(x)
    
    @property
    def mean(self) -> float:
        """Expected value: k × θ"""
        return self.shape * self.scale
    
    @property
    def std(self) -> float:
        """Standard deviation: sqrt(k) × θ"""
        return np.sqrt(self.shape) * self.scale
    
    @property
    def mode(self) -> Optional[float]:
        """Mode: (k-1) × θ for k ≥ 1, else 0"""
        if self.shape >= 1:
            return (self.shape - 1) * self.scale
        return 0.0
    
    @property
    def support(self) -> tuple:
        """Gamma is defined on (0, ∞)."""
        return (0.0, np.inf)
    
    def __repr__(self) -> str:
        return f"Gamma(shape={self.shape:.2f}, scale={self.scale:.2f}, mean={self.mean:.2f})"