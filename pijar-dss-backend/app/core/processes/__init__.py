"""
Stochastic Process Module.

This module provides stochastic processes for modeling time evolution
of uncertain quantities in Monte Carlo simulations.

Available Processes
-------------------
- PoissonProcess: Discrete event arrivals
- CompoundPoissonProcess: Poisson arrivals with random magnitudes
- GeometricBrownianMotion: Continuous proportional growth
- JumpDiffusionProcess: GBM with sudden jumps
- RegimeSwitchingModel: Markov state transitions

Usage
-----
>>> from app.core.processes import PoissonProcess, GeometricBrownianMotion
>>> 
>>> # Lead arrivals
>>> leads = PoissonProcess(base_rate=7)
>>> n_leads = leads.sample_count(rng)
>>> 
>>> # Customer growth
>>> customers = GeometricBrownianMotion(drift=0.02, volatility=0.05)
>>> path = customers.simulate_path(initial_state=10, n_steps=36, rng=rng)
"""

from .base import BaseProcess
from .poisson import PoissonProcess, CompoundPoissonProcess
from .gbm import GeometricBrownianMotion
from .jump_diffusion import JumpDiffusionProcess
from .regime import (
    RegimeType,
    RegimeParameters,
    RegimeSwitchingModel,
    DEFAULT_REGIMES
)

__all__ = [
    'BaseProcess',
    'PoissonProcess',
    'CompoundPoissonProcess',
    'GeometricBrownianMotion',
    'JumpDiffusionProcess',
    'RegimeType',
    'RegimeParameters',
    'RegimeSwitchingModel',
    'DEFAULT_REGIMES',
]