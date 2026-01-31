"""
Markov Regime-Switching Model for Economic States.

Real business environments alternate between different "regimes":
- Normal: Steady growth, predictable dynamics
- Stressed: Slower growth, higher uncertainty, more risk events
- Boom: Accelerated adoption, favorable conditions

The regime-switching model captures this by:
1. Defining discrete states with different parameters
2. Modeling transitions between states via Markov chain

Mathematical Background:
-----------------------
Let S(t) ∈ {1, 2, ..., K} be the regime at time t.
Transition probabilities: P[S(t+1) = j | S(t) = i] = p_ij

In each regime k, the business dynamics follow:
- Lead rate: λ_k
- Win rate: w_k
- Churn rate: c_k
- etc.

This allows the simulation to capture "bad years" and "good years"
systematically rather than treating all time periods identically.

Use Cases in Pijar DSS:
----------------------
Typical 3-regime setup:
- Normal (70% of time): Base case parameters
- Stress (20% of time): 30% fewer leads, 10% lower win rates, 20% higher churn
- Boom (10% of time): 50% more leads, 10% higher win rates, 20% lower churn
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class RegimeType(Enum):
    """Enumeration of possible economic regimes."""
    NORMAL = "normal"
    STRESS = "stress"
    BOOM = "boom"


@dataclass
class RegimeParameters:
    """
    Parameters that apply in a specific regime.
    
    All values are multipliers relative to base case:
    - 1.0 = no change from base
    - 0.8 = 20% reduction
    - 1.2 = 20% increase
    """
    lead_multiplier: float = 1.0
    win_rate_multiplier: float = 1.0
    churn_multiplier: float = 1.0
    revenue_multiplier: float = 1.0
    cost_multiplier: float = 1.0
    risk_intensity_multiplier: float = 1.0
    
    def to_dict(self) -> dict:
        return {
            'lead_multiplier': self.lead_multiplier,
            'win_rate_multiplier': self.win_rate_multiplier,
            'churn_multiplier': self.churn_multiplier,
            'revenue_multiplier': self.revenue_multiplier,
            'cost_multiplier': self.cost_multiplier,
            'risk_intensity_multiplier': self.risk_intensity_multiplier,
        }


# Default regime configurations
DEFAULT_REGIMES: Dict[RegimeType, RegimeParameters] = {
    RegimeType.NORMAL: RegimeParameters(
        lead_multiplier=1.0,
        win_rate_multiplier=1.0,
        churn_multiplier=1.0,
        revenue_multiplier=1.0,
        cost_multiplier=1.0,
        risk_intensity_multiplier=1.0
    ),
    RegimeType.STRESS: RegimeParameters(
        lead_multiplier=0.7,       # 30% fewer leads
        win_rate_multiplier=0.85,  # 15% lower win rates
        churn_multiplier=1.3,      # 30% higher churn
        revenue_multiplier=0.95,   # 5% price pressure
        cost_multiplier=1.1,       # 10% cost inflation
        risk_intensity_multiplier=2.0  # 2x risk event frequency
    ),
    RegimeType.BOOM: RegimeParameters(
        lead_multiplier=1.4,       # 40% more leads
        win_rate_multiplier=1.15,  # 15% higher win rates
        churn_multiplier=0.8,      # 20% lower churn
        revenue_multiplier=1.1,    # 10% pricing power
        cost_multiplier=0.95,      # 5% efficiency gains
        risk_intensity_multiplier=0.5  # Half the risk events
    )
}


@dataclass
class RegimeSwitchingModel:
    """
    Markov regime-switching model.
    
    Parameters
    ----------
    transition_matrix : NDArray
        K×K matrix where entry (i,j) = P[regime j | current regime i]
        Rows must sum to 1.
    regime_params : Dict[RegimeType, RegimeParameters]
        Parameters for each regime
    regime_order : List[RegimeType]
        Ordering of regimes corresponding to matrix indices
    initial_regime : RegimeType
        Starting regime
        
    Examples
    --------
    >>> # 3-state model: Normal (70%), Stress (20%), Boom (10%)
    >>> # With sticky transitions (high diagonal)
    >>> transition = np.array([
    ...     [0.85, 0.10, 0.05],  # From Normal
    ...     [0.25, 0.70, 0.05],  # From Stress
    ...     [0.30, 0.05, 0.65],  # From Boom
    ... ])
    >>> model = RegimeSwitchingModel(
    ...     transition_matrix=transition,
    ...     regime_params=DEFAULT_REGIMES,
    ...     regime_order=[RegimeType.NORMAL, RegimeType.STRESS, RegimeType.BOOM]
    ... )
    """
    transition_matrix: NDArray
    regime_params: Dict[RegimeType, RegimeParameters] = field(
        default_factory=lambda: DEFAULT_REGIMES.copy()
    )
    regime_order: List[RegimeType] = field(
        default_factory=lambda: [RegimeType.NORMAL, RegimeType.STRESS, RegimeType.BOOM]
    )
    initial_regime: RegimeType = RegimeType.NORMAL
    
    def __post_init__(self):
        """Validate the transition matrix."""
        n = len(self.regime_order)
        
        if self.transition_matrix.shape != (n, n):
            raise ValueError(
                f"Transition matrix shape {self.transition_matrix.shape} "
                f"doesn't match number of regimes {n}"
            )
        
        # Check rows sum to 1
        row_sums = self.transition_matrix.sum(axis=1)
        if not np.allclose(row_sums, 1.0):
            raise ValueError(
                f"Transition matrix rows must sum to 1, got {row_sums}"
            )
        
        # Build index lookups
        self._regime_to_idx = {r: i for i, r in enumerate(self.regime_order)}
        self._idx_to_regime = {i: r for i, r in enumerate(self.regime_order)}
    
    def get_regime_index(self, regime: RegimeType) -> int:
        """Get the matrix index for a regime."""
        return self._regime_to_idx[regime]
    
    def get_regime_from_index(self, idx: int) -> RegimeType:
        """Get the regime from a matrix index."""
        return self._idx_to_regime[idx]
    
    def sample_next_regime(
        self, 
        current_regime: RegimeType, 
        rng: Generator
    ) -> RegimeType:
        """
        Sample the next regime given current regime.
        
        Parameters
        ----------
        current_regime : RegimeType
            Current regime state
        rng : Generator
            Random number generator
            
        Returns
        -------
        RegimeType
            Sampled next regime
        """
        current_idx = self.get_regime_index(current_regime)
        probs = self.transition_matrix[current_idx]
        
        next_idx = rng.choice(len(probs), p=probs)
        return self.get_regime_from_index(next_idx)
    
    def get_parameters(self, regime: RegimeType) -> RegimeParameters:
        """Get the parameters for a specific regime."""
        return self.regime_params.get(regime, self.regime_params[RegimeType.NORMAL])
    
    def simulate_regime_path(
        self, 
        n_steps: int, 
        rng: Generator,
        initial: Optional[RegimeType] = None
    ) -> List[RegimeType]:
        """
        Simulate a path of regimes over time.
        
        Parameters
        ----------
        n_steps : int
            Number of time steps
        rng : Generator
            Random number generator
        initial : RegimeType, optional
            Starting regime (uses self.initial_regime if None)
            
        Returns
        -------
        List[RegimeType]
            Sequence of regimes, length n_steps + 1 (includes initial)
        """
        current = initial or self.initial_regime
        path = [current]
        
        for _ in range(n_steps):
            current = self.sample_next_regime(current, rng)
            path.append(current)
        
        return path
    
    def compute_stationary_distribution(self) -> Dict[RegimeType, float]:
        """
        Compute the stationary (long-run) distribution of regimes.
        
        The stationary distribution π satisfies: π = π × P
        where P is the transition matrix.
        
        This gives the expected fraction of time spent in each regime
        over a long simulation.
        
        Returns
        -------
        Dict[RegimeType, float]
            Mapping from regime to long-run probability
        """
        # Solve π(P - I) = 0 subject to Σπ = 1
        # Equivalent to finding left eigenvector with eigenvalue 1
        n = len(self.regime_order)
        
        # Add constraint that probabilities sum to 1
        A = np.vstack([
            self.transition_matrix.T - np.eye(n),
            np.ones(n)
        ])
        b = np.zeros(n + 1)
        b[-1] = 1
        
        # Least squares solution
        pi, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        pi = np.maximum(pi, 0)  # Ensure non-negative
        pi = pi / pi.sum()  # Normalize
        
        return {regime: pi[i] for i, regime in enumerate(self.regime_order)}
    
    @classmethod
    def create_default(
        cls,
        stress_probability: float = 0.20,
        boom_probability: float = 0.10,
        persistence: float = 0.80
    ) -> 'RegimeSwitchingModel':
        """
        Create a regime model with specified stationary probabilities.
        
        Parameters
        ----------
        stress_probability : float
            Long-run probability of stress regime
        boom_probability : float
            Long-run probability of boom regime
        persistence : float
            Probability of staying in current regime
            
        Returns
        -------
        RegimeSwitchingModel
            Configured model
        """
        normal_prob = 1 - stress_probability - boom_probability
        
        # Construct transition matrix to achieve target stationary distribution
        # with specified persistence (diagonal elements)
        # This is approximate; exact matching requires solving nonlinear equations
        
        p_stay = persistence
        p_leave = 1 - persistence
        
        # Transition matrix
        transition = np.array([
            # From Normal: stay or go to Stress/Boom proportionally
            [p_stay, p_leave * stress_probability / (1 - normal_prob + 1e-10), 
             p_leave * boom_probability / (1 - normal_prob + 1e-10)],
            # From Stress: higher chance to return to Normal
            [p_leave * 0.8, p_stay, p_leave * 0.2],
            # From Boom: higher chance to return to Normal
            [p_leave * 0.8, p_leave * 0.2, p_stay],
        ])
        
        # Normalize rows
        transition = transition / transition.sum(axis=1, keepdims=True)
        
        return cls(
            transition_matrix=transition,
            regime_params=DEFAULT_REGIMES.copy(),
            regime_order=[RegimeType.NORMAL, RegimeType.STRESS, RegimeType.BOOM],
            initial_regime=RegimeType.NORMAL
        )
    
    def __repr__(self) -> str:
        stationary = self.compute_stationary_distribution()
        probs_str = ", ".join(f"{r.value}={p:.1%}" for r, p in stationary.items())
        return f"RegimeSwitchingModel(stationary=[{probs_str}])"