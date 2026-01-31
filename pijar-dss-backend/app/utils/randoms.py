"""
Reproducible Random Number Generator Management.

In Monte Carlo simulation, reproducibility is critical for:
1. Debugging: Same seed → same results → easier to trace issues
2. Validation: Stakeholders can verify results independently
3. Sensitivity analysis: Isolate parameter effects from random noise

This module provides a centralized RNG management system using
NumPy's modern Generator API with SeedSequence for proper
parallel stream management.
"""

import numpy as np
from numpy.random import Generator, PCG64, SeedSequence
from typing import Optional, List


class RNGManager:
    """
    Manages random number generation for Monte Carlo simulations.
    
    Uses NumPy's PCG64 generator (Permuted Congruential Generator),
    which is the current recommended generator for:
    - Statistical quality (passes all TestU01 BigCrush tests)
    - Speed (faster than Mersenne Twister)
    - Jumpable streams for parallel applications
    
    Statistical Background:
    ----------------------
    PCG64 has a period of 2^128, meaning it can generate 2^128 numbers
    before repeating. For a simulation with 10,000 paths × 36 months × 
    100 random draws per month = 36 million draws, we use approximately
    2^25 numbers, well within the generator's capacity.
    
    The SeedSequence ensures that even with similar base seeds,
    spawned streams are statistically independent (no correlation
    between parallel workers).
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the RNG manager.
        
        Parameters
        ----------
        seed : int, optional
            Base seed for reproducibility. If None, uses system entropy
            for true randomness (non-reproducible).
        """
        self.base_seed = seed
        self.seed_sequence = SeedSequence(seed)
        self._rng = Generator(PCG64(self.seed_sequence))
    
    @property
    def rng(self) -> Generator:
        """Get the primary random number generator."""
        return self._rng
    
    def spawn_generators(self, n: int) -> List[Generator]:
        """
        Spawn n independent random number generators for parallel use.
        
        This is critical for parallel Monte Carlo: each worker needs
        its own RNG stream that is:
        1. Independent of other streams (no correlation)
        2. Reproducible given the base seed
        
        Parameters
        ----------
        n : int
            Number of independent generators to create
            
        Returns
        -------
        List[Generator]
            List of independent Generator objects
            
        Example
        -------
        >>> manager = RNGManager(seed=42)
        >>> generators = manager.spawn_generators(4)  # For 4 parallel workers
        >>> # Each generator produces independent streams
        >>> [g.random() for g in generators]
        [0.7739..., 0.4388..., 0.0596..., 0.8650...]
        """
        child_sequences = self.seed_sequence.spawn(n)
        return [Generator(PCG64(seq)) for seq in child_sequences]
    
    def reset(self) -> None:
        """
        Reset the RNG to initial state.
        
        Useful for running multiple simulations with identical
        random sequences (e.g., for A/B comparison of parameters).
        """
        self.seed_sequence = SeedSequence(self.base_seed)
        self._rng = Generator(PCG64(self.seed_sequence))


def get_rng(seed: Optional[int] = None) -> Generator:
    """
    Convenience function to get a configured RNG.
    
    Parameters
    ----------
    seed : int, optional
        Seed for reproducibility
        
    Returns
    -------
    Generator
        Configured NumPy random generator
    """
    return RNGManager(seed).rng