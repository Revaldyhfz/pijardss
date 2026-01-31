"""
Abstract Base Class for Stochastic Processes.

Stochastic processes model how quantities evolve over time with
randomness. Unlike static distributions (which give a single draw),
processes generate paths: sequences of values indexed by time.

Key Concepts:
------------
- State: Current value of the process
- Transition: How state changes from t to t+1
- Path: Complete trajectory over time horizon

Process Types in This Module:
----------------------------
1. Poisson: Discrete event arrivals (leads, deals, churns)
2. GBM: Continuous growth with random fluctuations
3. Jump-Diffusion: GBM + sudden jumps
4. Regime Switching: Different dynamics in different states
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any
import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray


class BaseProcess(ABC):
    """
    Abstract base class for stochastic processes.
    
    All time evolution models must inherit from this class.
    """
    
    @abstractmethod
    def step(
        self, 
        current_state: float, 
        t: int, 
        rng: Generator,
        **context
    ) -> float:
        """
        Evolve the process by one time step.
        
        Parameters
        ----------
        current_state : float
            Current value of the process
        t : int
            Current time index
        rng : Generator
            Random number generator
        **context : dict
            Additional context (e.g., regime, external factors)
            
        Returns
        -------
        float
            New state after one time step
        """
        pass
    
    @abstractmethod
    def simulate_path(
        self, 
        initial_state: float, 
        n_steps: int, 
        rng: Generator,
        **context
    ) -> NDArray:
        """
        Generate a complete path.
        
        Parameters
        ----------
        initial_state : float
            Starting value
        n_steps : int
            Number of time steps to simulate
        rng : Generator
            Random number generator
        **context : dict
            Additional context
            
        Returns
        -------
        NDArray
            Array of shape (n_steps + 1,) with full path
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"