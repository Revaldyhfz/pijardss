"""
Log-Normal Distribution for Positive Right-Skewed Values.

The log-normal distribution is ideal for quantities that:
1. Must be positive (can't have negative revenue)
2. Are right-skewed (occasional large values)
3. Result from multiplicative processes

Why Log-Normal?
--------------
If X = exp(Z) where Z ~ Normal(μ, σ²), then X is log-normal.

This arises naturally when growth is multiplicative:
    X_t = X_{t-1} × (1 + r_t)
    
Taking logs: log(X_t) = log(X_{t-1}) + log(1 + r_t)

This is a random walk in log-space, leading to log-normal distribution.

Parameterization:
----------------
We offer two parameterizations:
1. (μ, σ) - parameters of the underlying normal distribution
2. (mean, cv) - mean and coefficient of variation (intuitive)

The conversion:
    Given desired mean M and CV c:
    σ² = log(1 + c²)
    μ = log(M) - σ²/2

Use Cases in Pijar DSS:
----------------------
- Contract values: "Average 180M, but ranges widely"
- Revenue per customer: Growth compounds multiplicatively
- Costs: Can have occasional large overruns
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from scipy import stats
from typing import Union, Optional

from .base import BaseDistribution


class LogNormalDistribution(BaseDistribution):
    """
    Log-normal distribution for positive, right-skewed values.
    
    Parameters
    ----------
    mu : float
        Mean of the underlying normal distribution (log-space)
    sigma : float
        Std dev of the underlying normal distribution (log-space)
        
    Note
    ----
    mu and sigma are NOT the mean and std of the log-normal itself!
    Use class methods for intuitive parameterization.
    
    Examples
    --------
    >>> # Contract value: mean 180M, CV of 0.3 (moderate variability)
    >>> contract = LogNormalDistribution.from_mean_cv(mean=180, cv=0.3)
    >>> contract.mean
    180.0
    >>> samples = contract.sample(1000)
    >>> samples.min() > 0  # Always positive
    True
    """
    
    def __init__(self, mu: float, sigma: float):
        if sigma <= 0:
            raise ValueError(f"sigma must be > 0, got {sigma}")
        
        self.mu = float(mu)
        self.sigma = float(sigma)
        self._scipy_dist = stats.lognorm(s=sigma, scale=np.exp(mu))
    
    @classmethod
    def from_mean_cv(cls, mean: float, cv: float) -> 'LogNormalDistribution':
        """
        Create from mean and coefficient of variation.
        
        The coefficient of variation (CV) = std / mean is a 
        scale-free measure of dispersion. 
        
        CV interpretation:
        - CV = 0.1: Low variability (tight around mean)
        - CV = 0.3: Moderate variability
        - CV = 0.5: High variability
        - CV = 1.0: Very high (std equals mean)
        
        Parameters
        ----------
        mean : float
            Desired mean of the distribution (> 0)
        cv : float
            Coefficient of variation (> 0)
            
        Returns
        -------
        LogNormalDistribution
        """
        if mean <= 0:
            raise ValueError(f"mean must be > 0, got {mean}")
        if cv <= 0:
            raise ValueError(f"cv must be > 0, got {cv}")
        
        # Derive log-space parameters from mean and CV
        sigma_sq = np.log(1 + cv ** 2)
        sigma = np.sqrt(sigma_sq)
        mu = np.log(mean) - sigma_sq / 2
        
        return cls(mu=mu, sigma=sigma)
    
    @classmethod
    def from_mean_std(cls, mean: float, std: float) -> 'LogNormalDistribution':
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
        LogNormalDistribution
        """
        if mean <= 0:
            raise ValueError(f"mean must be > 0, got {mean}")
        if std <= 0:
            raise ValueError(f"std must be > 0, got {std}")
        
        cv = std / mean
        return cls.from_mean_cv(mean=mean, cv=cv)
    
    @classmethod
    def from_median_range(
        cls, 
        median: float, 
        p10: float, 
        p90: float
    ) -> 'LogNormalDistribution':
        """
        Create from median and 10th/90th percentiles.
        
        This is useful for expert elicitation:
        "The value is probably around X, with 80% chance between Y and Z"
        
        Parameters
        ----------
        median : float
            50th percentile (center of distribution)
        p10 : float
            10th percentile (low end)
        p90 : float
            90th percentile (high end)
            
        Returns
        -------
        LogNormalDistribution
        """
        # For log-normal, median = exp(μ)
        mu = np.log(median)
        
        # 90th percentile: exp(μ + z_{0.9} × σ) = p90
        # So: σ = (log(p90) - μ) / z_{0.9}
        z_90 = stats.norm.ppf(0.9)  # ≈ 1.28
        sigma = (np.log(p90) - mu) / z_90
        
        return cls(mu=mu, sigma=sigma)
    
    def sample(
        self, 
        size: Union[int, tuple] = 1, 
        rng: Optional[Generator] = None
    ) -> NDArray:
        """Draw random samples."""
        if rng is None:
            rng = np.random.default_rng()
        
        # Sample from normal, then exponentiate
        normal_samples = rng.normal(loc=self.mu, scale=self.sigma, size=size)
        return np.exp(normal_samples)
    
    def pdf(self, x: NDArray) -> NDArray:
        """Probability density function."""
        return self._scipy_dist.pdf(x)
    
    def cdf(self, x: NDArray) -> NDArray:
        """Cumulative distribution function."""
        return self._scipy_dist.cdf(x)
    
    @property
    def mean(self) -> float:
        """Expected value: exp(μ + σ²/2)"""
        return np.exp(self.mu + self.sigma ** 2 / 2)
    
    @property
    def std(self) -> float:
        """Standard deviation."""
        variance = (np.exp(self.sigma ** 2) - 1) * np.exp(2 * self.mu + self.sigma ** 2)
        return np.sqrt(variance)
    
    @property
    def median(self) -> float:
        """Median: exp(μ)"""
        return np.exp(self.mu)
    
    @property
    def mode(self) -> float:
        """Mode: exp(μ - σ²)"""
        return np.exp(self.mu - self.sigma ** 2)
    
    @property
    def support(self) -> tuple:
        """Log-normal is defined on (0, ∞)."""
        return (0.0, np.inf)
    
    def __repr__(self) -> str:
        return f"LogNormal(mean={self.mean:.2f}, std={self.std:.2f})"