"""
Beta Distribution for Rate and Proportion Uncertainty.

The Beta distribution is the natural choice for modeling uncertainty
about probabilities and proportions (values constrained to [0, 1]).

Why Beta for Rates?
------------------
1. Support is exactly [0, 1] - can't generate impossible values
2. Conjugate prior for binomial - has Bayesian interpretation
3. Extremely flexible shape via α and β parameters
4. Can represent: uniform, U-shaped, J-shaped, symmetric, skewed

Parameterization:
----------------
We offer two parameterizations:
1. Shape parameters (α, β) - standard statistical form
2. Mean and sample size (μ, n) - intuitive for business users

The conversion is:
    α = μ × n
    β = (1 - μ) × n

where n can be thought of as "equivalent sample size" representing
confidence in the estimate.

Use Cases in Pijar DSS:
----------------------
- Win rates: "We estimate 70% BUMN win rate based on 20 historical deals"
  → Beta(α=14, β=6) which has mean=0.7, std≈0.1
- Churn rate: "Expect ~10% annual churn, moderate uncertainty"
  → Beta(α=2, β=18) which has mean=0.1
- BUMN ratio: "About 35% of leads are BUMN"
  → Beta(α=7, β=13)
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from scipy import stats
from typing import Union, Optional

from .base import BaseDistribution


class BetaDistribution(BaseDistribution):
    """
    Beta distribution for proportions and probabilities.
    
    Parameters
    ----------
    alpha : float
        First shape parameter (α > 0)
    beta : float
        Second shape parameter (β > 0)
        
    Alternative Construction
    ------------------------
    Use class methods for intuitive parameterization:
    - from_mean_sample_size(mean, sample_size)
    - from_mean_std(mean, std)
    
    Examples
    --------
    >>> # Win rate: 70% with moderate confidence
    >>> win_rate = BetaDistribution(alpha=14, beta=6)
    >>> win_rate.mean
    0.7
    >>> 
    >>> # From business intuition: "70% based on ~20 deals"
    >>> win_rate = BetaDistribution.from_mean_sample_size(mean=0.7, sample_size=20)
    """
    
    def __init__(self, alpha: float, beta: float):
        if alpha <= 0:
            raise ValueError(f"alpha must be > 0, got {alpha}")
        if beta <= 0:
            raise ValueError(f"beta must be > 0, got {beta}")
        
        self.alpha = float(alpha)
        self.beta = float(beta)
        self._scipy_dist = stats.beta(a=alpha, b=beta)
    
    @classmethod
    def from_mean_sample_size(
        cls, 
        mean: float, 
        sample_size: float
    ) -> 'BetaDistribution':
        """
        Create Beta distribution from mean and effective sample size.
        
        This parameterization is intuitive for business users:
        - mean: Your point estimate (e.g., "70% win rate")
        - sample_size: Confidence level as equivalent observations
          (larger = more confident = tighter distribution)
        
        Parameters
        ----------
        mean : float
            Expected value, must be in (0, 1)
        sample_size : float
            Effective sample size (n > 0)
            
        Returns
        -------
        BetaDistribution
            Configured distribution
            
        Examples
        --------
        >>> # "70% win rate based on 20 deals"
        >>> dist = BetaDistribution.from_mean_sample_size(0.7, 20)
        >>> dist.alpha, dist.beta
        (14.0, 6.0)
        """
        if not 0 < mean < 1:
            raise ValueError(f"mean must be in (0, 1), got {mean}")
        if sample_size <= 0:
            raise ValueError(f"sample_size must be > 0, got {sample_size}")
        
        alpha = mean * sample_size
        beta = (1 - mean) * sample_size
        
        return cls(alpha=alpha, beta=beta)
    
    @classmethod
    def from_mean_std(cls, mean: float, std: float) -> 'BetaDistribution':
        """
        Create Beta distribution from mean and standard deviation.
        
        Useful when you have a point estimate and uncertainty range.
        
        Parameters
        ----------
        mean : float
            Expected value, in (0, 1)
        std : float
            Standard deviation (must be feasible for given mean)
            
        Returns
        -------
        BetaDistribution
        """
        if not 0 < mean < 1:
            raise ValueError(f"mean must be in (0, 1), got {mean}")
        
        # Maximum possible variance for Beta is mean*(1-mean)
        max_std = np.sqrt(mean * (1 - mean))
        if std >= max_std:
            raise ValueError(
                f"std ({std}) too large for mean ({mean}). "
                f"Maximum feasible std is {max_std:.4f}"
            )
        
        # Solve for alpha + beta from variance formula
        # Var = α*β / [(α+β)²(α+β+1)] = μ(1-μ)/(α+β+1)
        # So: α+β = μ(1-μ)/Var - 1
        variance = std ** 2
        sum_params = mean * (1 - mean) / variance - 1
        
        alpha = mean * sum_params
        beta = (1 - mean) * sum_params
        
        return cls(alpha=alpha, beta=beta)
    
    def sample(
        self, 
        size: Union[int, tuple] = 1, 
        rng: Optional[Generator] = None
    ) -> NDArray:
        """Draw random samples from Beta distribution."""
        if rng is None:
            rng = np.random.default_rng()
        
        return rng.beta(a=self.alpha, b=self.beta, size=size)
    
    def pdf(self, x: NDArray) -> NDArray:
        """Probability density function."""
        return self._scipy_dist.pdf(x)
    
    def cdf(self, x: NDArray) -> NDArray:
        """Cumulative distribution function."""
        return self._scipy_dist.cdf(x)
    
    @property
    def mean(self) -> float:
        """Expected value: α / (α + β)"""
        return self.alpha / (self.alpha + self.beta)
    
    @property
    def std(self) -> float:
        """Standard deviation."""
        a, b = self.alpha, self.beta
        variance = (a * b) / ((a + b) ** 2 * (a + b + 1))
        return np.sqrt(variance)
    
    @property
    def support(self) -> tuple:
        """Beta is defined on [0, 1]."""
        return (0.0, 1.0)
    
    @property
    def mode(self) -> Optional[float]:
        """
        Mode of the distribution.
        
        Only exists when α > 1 and β > 1.
        Mode = (α - 1) / (α + β - 2)
        """
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return None
    
    def __repr__(self) -> str:
        return f"Beta(α={self.alpha:.2f}, β={self.beta:.2f}, mean={self.mean:.3f})"