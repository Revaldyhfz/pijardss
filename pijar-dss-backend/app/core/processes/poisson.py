"""
Poisson Process for Discrete Event Arrivals.

The Poisson process is fundamental for modeling discrete events
occurring randomly in time: lead arrivals, deal closings, customer
churns, risk events.

Mathematical Background:
-----------------------
A Poisson process with rate λ has the property that:
- Number of events in interval [0, t] follows Poisson(λt)
- Inter-arrival times are Exponential(λ)
- Events are independent

For monthly simulation:
- If annual rate is λ, monthly rate is λ/12
- Number of events in a month ~ Poisson(λ/12)

Extensions:
----------
1. Non-homogeneous: λ(t) varies with time
2. State-dependent: λ depends on current state
3. Regime-dependent: λ differs by economic regime

Use Cases in Pijar DSS:
----------------------
- Lead arrivals: λ = 7 leads/month
- Deal closings: λ = leads × win_rate
- Churn events: λ = customers × churn_rate
- Risk shocks: λ = 0.08/year for policy changes
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from typing import Optional, Callable, Union

from .base import BaseProcess


class PoissonProcess(BaseProcess):
    """
    Poisson process for discrete event arrivals.
    
    Parameters
    ----------
    base_rate : float
        Base arrival rate (events per time unit)
    rate_modifier : callable, optional
        Function (t, state, context) -> multiplier
        Allows for non-homogeneous or state-dependent rates
        
    Examples
    --------
    >>> # Constant rate: 7 leads per month
    >>> leads = PoissonProcess(base_rate=7)
    >>> leads.sample_count(rng)
    6  # Approximately 7, with random variation
    
    >>> # Rate that varies with regime
    >>> def regime_modifier(t, state, context):
    ...     return 0.7 if context.get('regime') == 'stress' else 1.0
    >>> leads = PoissonProcess(base_rate=7, rate_modifier=regime_modifier)
    """
    
    def __init__(
        self, 
        base_rate: float,
        rate_modifier: Optional[Callable] = None
    ):
        if base_rate < 0:
            raise ValueError(f"base_rate must be >= 0, got {base_rate}")
        
        self.base_rate = base_rate
        self.rate_modifier = rate_modifier or (lambda t, s, c: 1.0)
    
    def get_effective_rate(
        self, 
        t: int = 0, 
        state: float = 0, 
        context: dict = None
    ) -> float:
        """
        Compute the effective rate after applying modifiers.
        
        Parameters
        ----------
        t : int
            Current time
        state : float
            Current state value
        context : dict
            Additional context (regime, etc.)
            
        Returns
        -------
        float
            Effective arrival rate
        """
        context = context or {}
        modifier = self.rate_modifier(t, state, context)
        return max(0, self.base_rate * modifier)
    
    def sample_count(
        self, 
        rng: Generator,
        t: int = 0,
        state: float = 0,
        context: dict = None
    ) -> int:
        """
        Sample the number of events in one time period.
        
        Parameters
        ----------
        rng : Generator
            Random number generator
        t : int
            Current time
        state : float
            Current state
        context : dict
            Additional context
            
        Returns
        -------
        int
            Number of events (non-negative integer)
        """
        rate = self.get_effective_rate(t, state, context)
        
        if rate <= 0:
            return 0
        
        return int(rng.poisson(rate))
    
    def step(
        self, 
        current_state: float, 
        t: int, 
        rng: Generator,
        **context
    ) -> float:
        """
        For Poisson, 'step' returns the count of events.
        
        This differs from continuous processes where step returns
        the new value of a continuous state variable.
        """
        return float(self.sample_count(rng, t, current_state, context))
    
    def simulate_path(
        self, 
        initial_state: float, 
        n_steps: int, 
        rng: Generator,
        **context
    ) -> NDArray:
        """
        Generate a path of event counts.
        
        Returns
        -------
        NDArray
            Array of shape (n_steps,) with event count at each step
        """
        counts = np.zeros(n_steps, dtype=np.int64)
        
        for t in range(n_steps):
            counts[t] = self.sample_count(rng, t, initial_state, context)
        
        return counts
    
    def simulate_cumulative_path(
        self, 
        n_steps: int, 
        rng: Generator,
        **context
    ) -> NDArray:
        """
        Generate cumulative count path (total events up to time t).
        
        Returns
        -------
        NDArray
            Array of shape (n_steps + 1,) starting from 0
        """
        counts = self.simulate_path(0, n_steps, rng, **context)
        cumulative = np.zeros(n_steps + 1, dtype=np.int64)
        cumulative[1:] = np.cumsum(counts)
        
        return cumulative
    
    def __repr__(self) -> str:
        return f"PoissonProcess(rate={self.base_rate})"


class CompoundPoissonProcess(BaseProcess):
    """
    Compound Poisson process: Poisson arrivals with random magnitudes.
    
    Useful for modeling:
    - Total revenue from random number of deals with random sizes
    - Aggregate losses from random number of risk events
    
    X(t) = Σᵢ Yᵢ  where N(t) ~ Poisson(λt), Yᵢ ~ F
    
    Parameters
    ----------
    arrival_rate : float
        Rate of the underlying Poisson process
    magnitude_sampler : callable
        Function (rng) -> magnitude for each arrival
    """
    
    def __init__(
        self, 
        arrival_rate: float,
        magnitude_sampler: Callable[[Generator], float]
    ):
        self.arrival_process = PoissonProcess(base_rate=arrival_rate)
        self.magnitude_sampler = magnitude_sampler
    
    def step(
        self, 
        current_state: float, 
        t: int, 
        rng: Generator,
        **context
    ) -> float:
        """
        Compute the sum of magnitudes for arrivals in this period.
        """
        n_arrivals = self.arrival_process.sample_count(rng, t, current_state, context)
        
        if n_arrivals == 0:
            return 0.0
        
        total = sum(self.magnitude_sampler(rng) for _ in range(n_arrivals))
        return total
    
    def simulate_path(
        self, 
        initial_state: float, 
        n_steps: int, 
        rng: Generator,
        **context
    ) -> NDArray:
        """Generate path of aggregate magnitudes per period."""
        path = np.zeros(n_steps + 1)
        path[0] = initial_state
        
        cumulative = initial_state
        for t in range(n_steps):
            increment = self.step(cumulative, t, rng, **context)
            cumulative += increment
            path[t + 1] = cumulative
        
        return path