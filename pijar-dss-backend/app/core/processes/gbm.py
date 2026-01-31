"""
Geometric Brownian Motion (GBM) for Continuous Growth Processes.

GBM is the workhorse model for quantities that:
1. Grow or decay proportionally (percentage changes)
2. Have continuous random fluctuations
3. Cannot go negative

Mathematical Definition:
-----------------------
dS = μS dt + σS dW

where:
- S: Process value
- μ: Drift (expected growth rate)
- σ: Volatility (standard deviation of returns)
- W: Wiener process (Brownian motion)

Solution:
S(t) = S(0) × exp[(μ - σ²/2)t + σW(t)]

For discrete simulation (monthly steps):
S(t+1) = S(t) × exp[(μ - σ²/2)Δt + σ√Δt × Z]

where Z ~ N(0, 1)

Use Cases in Pijar DSS:
----------------------
- Customer growth trajectory (with random fluctuations)
- Market size evolution
- Revenue growth with volatility
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from typing import Optional, Callable

from .base import BaseProcess


class GeometricBrownianMotion(BaseProcess):
    """
    Geometric Brownian Motion for proportional growth.
    
    Parameters
    ----------
    drift : float
        Expected growth rate per time unit (μ)
        E.g., 0.05 for 5% growth per period
    volatility : float
        Volatility (σ) - standard deviation of returns
        E.g., 0.1 for 10% monthly volatility
    dt : float
        Time step size (default 1.0 for monthly)
        
    Examples
    --------
    >>> # Customer base grows 3% monthly with 10% volatility
    >>> customers = GeometricBrownianMotion(drift=0.03, volatility=0.10)
    >>> path = customers.simulate_path(initial_state=10, n_steps=24, rng=rng)
    >>> path[0]  # Initial customers
    10
    >>> path[-1]  # After 24 months (random)
    18.5  # Approximately 10 × exp(0.03 × 24) with noise
    """
    
    def __init__(
        self, 
        drift: float, 
        volatility: float,
        dt: float = 1.0
    ):
        if volatility < 0:
            raise ValueError(f"volatility must be >= 0, got {volatility}")
        
        self.drift = drift
        self.volatility = volatility
        self.dt = dt
        
        # Precompute constants for efficiency
        # For log-space: increment = (μ - σ²/2)dt + σ√dt × Z
        self._drift_term = (drift - 0.5 * volatility ** 2) * dt
        self._vol_term = volatility * np.sqrt(dt)
    
    def step(
        self, 
        current_state: float, 
        t: int, 
        rng: Generator,
        **context
    ) -> float:
        """
        Evolve by one time step.
        
        Uses the exact solution rather than Euler discretization
        for better accuracy.
        """
        if current_state <= 0:
            return 0.0
        
        # Sample standard normal
        z = rng.standard_normal()
        
        # Compute log-return
        log_return = self._drift_term + self._vol_term * z
        
        # Apply multiplicatively
        return current_state * np.exp(log_return)
    
    def simulate_path(
        self, 
        initial_state: float, 
        n_steps: int, 
        rng: Generator,
        **context
    ) -> NDArray:
        """
        Generate a complete GBM path.
        
        Vectorized for efficiency: generates all random draws at once.
        """
        if initial_state <= 0:
            return np.zeros(n_steps + 1)
        
        # Generate all random innovations at once
        z = rng.standard_normal(n_steps)
        
        # Compute log-returns
        log_returns = self._drift_term + self._vol_term * z
        
        # Cumulative sum in log space, then exponentiate
        cumulative_log_returns = np.concatenate([[0], np.cumsum(log_returns)])
        
        path = initial_state * np.exp(cumulative_log_returns)
        
        return path
    
    def expected_value(self, initial_state: float, t: float) -> float:
        """
        Expected value at time t.
        
        E[S(t)] = S(0) × exp(μt)
        
        Note: Due to Jensen's inequality, this is NOT the same as
        exp(E[log S(t)]). The expected value is higher than the
        median for GBM.
        """
        return initial_state * np.exp(self.drift * t)
    
    def median_value(self, initial_state: float, t: float) -> float:
        """
        Median value at time t.
        
        Median = S(0) × exp[(μ - σ²/2)t]
        
        The median is more robust than mean for skewed distributions.
        """
        return initial_state * np.exp((self.drift - 0.5 * self.volatility ** 2) * t)
    
    def quantile(
        self, 
        initial_state: float, 
        t: float, 
        q: float
    ) -> float:
        """
        Compute the q-th quantile at time t.
        
        Parameters
        ----------
        initial_state : float
            Starting value
        t : float
            Time horizon
        q : float
            Quantile (e.g., 0.05 for 5th percentile)
            
        Returns
        -------
        float
            Value such that P(S(t) ≤ value) = q
        """
        from scipy import stats
        
        # log S(t) ~ N(log S(0) + (μ - σ²/2)t, σ²t)
        log_mean = np.log(initial_state) + (self.drift - 0.5 * self.volatility ** 2) * t
        log_std = self.volatility * np.sqrt(t)
        
        log_quantile = stats.norm.ppf(q, loc=log_mean, scale=log_std)
        
        return np.exp(log_quantile)
    
    def __repr__(self) -> str:
        return f"GBM(drift={self.drift:.3f}, vol={self.volatility:.3f})"