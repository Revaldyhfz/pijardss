"""
Abstract Base Class for Probability Distributions.

All input uncertainty in the simulation is modeled through probability
distributions. This module defines the interface that all distribution
classes must implement, ensuring consistency and interoperability.

Design Philosophy:
-----------------
Each distribution represents epistemic uncertainty about a parameter.
We don't know the exact value, but we can characterize our beliefs
about plausible values through a probability distribution.

Key methods:
- sample(): Draw random values (for Monte Carlo)
- pdf(): Probability density (for visualization/debugging)
- mean/std: Summary statistics for quick analysis
"""

from abc import ABC, abstractmethod
from typing import Union, Optional
import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray


class BaseDistribution(ABC):
    """
    Abstract base class for all probability distributions.
    
    All distributions used for input uncertainty modeling must
    inherit from this class and implement the required methods.
    """
    
    @abstractmethod
    def sample(
        self, 
        size: Union[int, tuple] = 1, 
        rng: Optional[Generator] = None
    ) -> NDArray:
        """
        Draw random samples from the distribution.
        
        Parameters
        ----------
        size : int or tuple
            Number of samples to draw, or shape of output array
        rng : Generator, optional
            NumPy random generator for reproducibility.
            If None, uses numpy's default generator.
            
        Returns
        -------
        NDArray
            Array of random samples
        """
        pass
    
    @abstractmethod
    def pdf(self, x: NDArray) -> NDArray:
        """
        Compute the probability density function at x.
        
        Parameters
        ----------
        x : array-like
            Points at which to evaluate the PDF
            
        Returns
        -------
        NDArray
            PDF values at each point
        """
        pass
    
    @abstractmethod
    def cdf(self, x: NDArray) -> NDArray:
        """
        Compute the cumulative distribution function at x.
        
        Parameters
        ----------
        x : array-like
            Points at which to evaluate the CDF
            
        Returns
        -------
        NDArray
            CDF values at each point (probabilities in [0, 1])
        """
        pass
    
    @property
    @abstractmethod
    def mean(self) -> float:
        """Expected value of the distribution."""
        pass
    
    @property
    @abstractmethod
    def std(self) -> float:
        """Standard deviation of the distribution."""
        pass
    
    @property
    @abstractmethod
    def support(self) -> tuple:
        """
        Support of the distribution (min, max).
        
        Returns
        -------
        tuple
            (lower_bound, upper_bound) where the distribution has
            non-zero probability density
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(mean={self.mean:.4f}, std={self.std:.4f})"