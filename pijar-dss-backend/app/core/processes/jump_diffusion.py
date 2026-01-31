"""
Merton Jump-Diffusion Process for Regime Shocks.

The jump-diffusion model extends GBM by adding sudden jumps,
capturing "black swan" events that simple diffusion models miss.

Why Jump-Diffusion?
------------------
Pure GBM has continuous paths - no sudden jumps. But real business
faces discrete shocks:
- Policy changes (sudden adoption drop)
- Competitor actions (price war)
- Economic crises (demand collapse)

These shocks are not well-modeled by volatility alone.

Mathematical Definition:
-----------------------
dS = μS dt + σS dW + S dJ

where J is a compound Poisson process with:
- Jump arrivals: Poisson(λ)
- Jump sizes: typically log-normal

For each jump, S multiplies by (1 + Y) where Y ~ some distribution.

Use Cases in Pijar DSS:
----------------------
- Policy risk: λ = 0.08/year, mean impact = -20%
- Competitor entry: λ = 0.15/year, mean impact = -15%
- Economic boom: λ = 0.05/year, mean impact = +30%
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from typing import Optional, Callable, Tuple

from .base import BaseProcess
from .gbm import GeometricBrownianMotion
from .poisson import PoissonProcess


class JumpDiffusionProcess(BaseProcess):
    """
    Merton jump-diffusion: GBM + Poisson jumps.
    
    Parameters
    ----------
    drift : float
        GBM drift parameter
    volatility : float
        GBM volatility parameter
    jump_intensity : float
        Average number of jumps per time unit (λ)
    jump_mean : float
        Mean of jump size in log terms
        E.g., -0.2 means jumps reduce value by ~20% on average
    jump_std : float
        Std dev of jump size in log terms
    dt : float
        Time step size
        
    Examples
    --------
    >>> # Growth with occasional negative shocks
    >>> process = JumpDiffusionProcess(
    ...     drift=0.02,
    ...     volatility=0.08,
    ...     jump_intensity=0.1,  # ~1 jump per 10 periods
    ...     jump_mean=-0.15,     # Jumps reduce by 15% on average
    ...     jump_std=0.05
    ... )
    """
    
    def __init__(
        self,
        drift: float,
        volatility: float,
        jump_intensity: float,
        jump_mean: float,
        jump_std: float,
        dt: float = 1.0
    ):
        self.drift = drift
        self.volatility = volatility
        self.jump_intensity = jump_intensity
        self.jump_mean = jump_mean
        self.jump_std = jump_std
        self.dt = dt
        
        # Underlying GBM (with drift adjusted for jump compensation)
        # To keep expected growth at drift, we adjust for average jump impact
        # E[e^J] = exp(jump_mean + jump_std²/2)
        # Compensation: μ_adj = μ - λ(E[e^J] - 1)
        expected_jump_factor = np.exp(jump_mean + 0.5 * jump_std ** 2)
        drift_adjustment = jump_intensity * (expected_jump_factor - 1)
        adjusted_drift = drift - drift_adjustment
        
        self._gbm = GeometricBrownianMotion(
            drift=adjusted_drift,
            volatility=volatility,
            dt=dt
        )
        
        self._jump_process = PoissonProcess(base_rate=jump_intensity * dt)
    
    def _sample_jump_size(self, rng: Generator) -> float:
        """
        Sample a single jump size.
        
        Returns multiplicative factor: new_value = old_value × factor
        """
        log_jump = rng.normal(self.jump_mean, self.jump_std)
        return np.exp(log_jump)
    
    def step(
        self, 
        current_state: float, 
        t: int, 
        rng: Generator,
        **context
    ) -> float:
        """
        Evolve by one step: diffusion + potential jumps.
        """
        if current_state <= 0:
            return 0.0
        
        # 1. Apply GBM diffusion
        new_state = self._gbm.step(current_state, t, rng, **context)
        
        # 2. Check for jumps
        n_jumps = self._jump_process.sample_count(rng, t, current_state, context)
        
        # 3. Apply jumps multiplicatively
        for _ in range(n_jumps):
            jump_factor = self._sample_jump_size(rng)
            new_state *= jump_factor
        
        return max(0, new_state)
    
    def simulate_path(
        self, 
        initial_state: float, 
        n_steps: int, 
        rng: Generator,
        **context
    ) -> NDArray:
        """
        Generate a complete path with potential jumps.
        """
        path = np.zeros(n_steps + 1)
        path[0] = initial_state
        
        current = initial_state
        for t in range(n_steps):
            current = self.step(current, t, rng, **context)
            path[t + 1] = current
        
        return path
    
    def decompose_path(
        self, 
        initial_state: float, 
        n_steps: int, 
        rng: Generator
    ) -> Tuple[NDArray, NDArray, NDArray]:
        """
        Generate path with decomposition into diffusion and jump components.
        
        Useful for analysis: understanding how much variation comes
        from continuous noise vs discrete jumps.
        
        Returns
        -------
        tuple
            (full_path, diffusion_only_path, jump_times)
        """
        path = np.zeros(n_steps + 1)
        diffusion_path = np.zeros(n_steps + 1)
        jump_times = []
        
        path[0] = initial_state
        diffusion_path[0] = initial_state
        
        current = initial_state
        current_diffusion = initial_state
        
        for t in range(n_steps):
            # Diffusion component
            z = rng.standard_normal()
            log_return = self._gbm._drift_term + self._gbm._vol_term * z
            
            current_diffusion *= np.exp(log_return)
            diffusion_path[t + 1] = current_diffusion
            
            # Full path with jumps
            current *= np.exp(log_return)
            
            n_jumps = self._jump_process.sample_count(rng, t, current, {})
            for _ in range(n_jumps):
                jump_times.append(t)
                current *= self._sample_jump_size(rng)
            
            path[t + 1] = max(0, current)
        
        return path, diffusion_path, np.array(jump_times)
    
    def __repr__(self) -> str:
        return (f"JumpDiffusion(drift={self.drift:.3f}, vol={self.volatility:.3f}, "
                f"λ={self.jump_intensity:.3f}, jump_μ={self.jump_mean:.3f})")