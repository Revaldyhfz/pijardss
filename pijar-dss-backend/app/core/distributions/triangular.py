"""
Triangular Distribution for Bounded Uncertainty.

The triangular distribution is ideal for expert elicitation scenarios
where we can specify:
- Minimum plausible value (a)
- Most likely value / mode (c)  
- Maximum plausible value (b)

This matches the common "best case / most likely / worst case" format
used in business planning and risk assessment.

Mathematical Definition:
-----------------------
PDF:
    f(x) = 2(x-a) / [(b-a)(c-a)]     for a ≤ x ≤ c
    f(x) = 2(b-x) / [(b-a)(b-c)]     for c < x ≤ b

Mean: (a + b + c) / 3
Mode: c
Variance: (a² + b² + c² - ab - ac - bc) / 18

Use Cases in Pijar DSS:
----------------------
- Initial capital: "We'll invest between 4B and 6B, probably around 5B"
- Development duration: "Could take 4-9 months, most likely 6"
- Burn rate: "Expect 180-250 M/month, planning for 200"
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from scipy import stats
from typing import Union, Optional

from .base import BaseDistribution


class TriangularDistribution(BaseDistribution):
    """
    Triangular distribution for bounded uncertain parameters.
    
    Parameters
    ----------
    min_val : float
        Minimum value (lower bound a)
    mode : float
        Most likely value (mode c)
    max_val : float
        Maximum value (upper bound b)
        
    Raises
    ------
    ValueError
        If min_val > mode or mode > max_val
        
    Examples
    --------
    >>> # Development duration: 4-9 months, most likely 6
    >>> dev_duration = TriangularDistribution(min_val=4, mode=6, max_val=9)
    >>> dev_duration.mean
    6.333...
    >>> samples = dev_duration.sample(1000)
    >>> samples.min() >= 4 and samples.max() <= 9
    True
    """
    
    def __init__(self, min_val: float, mode: float, max_val: float):
        # Validate inputs
        if min_val > mode:
            raise ValueError(f"min_val ({min_val}) must be <= mode ({mode})")
        if mode > max_val:
            raise ValueError(f"mode ({mode}) must be <= max_val ({max_val})")
        
        self.min_val = float(min_val)
        self.mode = float(mode)
        self.max_val = float(max_val)
        
        # Handle degenerate case where min == max
        self._is_degenerate = (max_val - min_val) < 1e-10
        
        if not self._is_degenerate:
            # Compute shape parameter for scipy (location of mode as fraction)
            # scipy uses c = (mode - min) / (max - min)
            self._c = (mode - min_val) / (max_val - min_val)
            self._scipy_dist = stats.triang(
                c=self._c, 
                loc=min_val, 
                scale=max_val - min_val
            )
    
    def sample(
        self, 
        size: Union[int, tuple] = 1, 
        rng: Optional[Generator] = None
    ) -> NDArray:
        """
        Draw random samples using inverse transform sampling.
        
        The triangular distribution has a closed-form inverse CDF,
        making sampling very efficient.
        """
        if self._is_degenerate:
            # All mass at a single point
            if isinstance(size, int):
                return np.full(size, self.mode)
            return np.full(size, self.mode)
        
        if rng is None:
            rng = np.random.default_rng()
        
        # Use numpy's built-in triangular (more efficient than scipy)
        return rng.triangular(
            left=self.min_val,
            mode=self.mode,
            right=self.max_val,
            size=size
        )
    
    def pdf(self, x: NDArray) -> NDArray:
        """Probability density function."""
        if self._is_degenerate:
            return np.where(np.abs(x - self.mode) < 1e-10, np.inf, 0.0)
        return self._scipy_dist.pdf(x)
    
    def cdf(self, x: NDArray) -> NDArray:
        """Cumulative distribution function."""
        if self._is_degenerate:
            return np.where(x < self.mode, 0.0, 1.0)
        return self._scipy_dist.cdf(x)
    
    @property
    def mean(self) -> float:
        """
        Expected value: (a + b + c) / 3
        
        Note: This is NOT equal to the mode unless the distribution
        is symmetric (mode at midpoint).
        """
        return (self.min_val + self.mode + self.max_val) / 3
    
    @property
    def std(self) -> float:
        """
        Standard deviation.
        
        Variance = (a² + b² + c² - ab - ac - bc) / 18
        """
        a, c, b = self.min_val, self.mode, self.max_val
        variance = (a**2 + b**2 + c**2 - a*b - a*c - b*c) / 18
        return np.sqrt(variance)
    
    @property
    def support(self) -> tuple:
        """The distribution is bounded on [min_val, max_val]."""
        return (self.min_val, self.max_val)
    
    def __repr__(self) -> str:
        return f"Triangular(min={self.min_val}, mode={self.mode}, max={self.max_val})"