"""
Risk Event Modeling.

Models discrete shock events that can impact business performance.
Uses jump process framework with recovery dynamics.

Risk Event Lifecycle:
--------------------
1. Arrival: Poisson process with state-dependent intensity
2. Impact: Immediate multiplicative effect on a parameter
3. Recovery: Gradual return to baseline (geometric decay)

Types of Impacts:
----------------
- Adoption: Reduces lead flow and conversion
- Churn: Increases customer attrition
- Revenue: Reduces revenue per customer
- Cost: Increases operating costs
"""

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from ..distributions import TriangularDistribution
from ..processes import PoissonProcess


@dataclass
class ActiveShock:
    """
    An active shock affecting the business.
    
    Attributes
    ----------
    event_name : str
        Name of the risk event
    impact_type : str
        Type of impact (adoption, churn, revenue, cost)
    severity : float
        Current severity multiplier (< 1 for negative, > 1 for positive)
    recovery_rate : float
        Monthly probability of full recovery
    start_month : int
        Month when shock occurred
    """
    event_name: str
    impact_type: str
    severity: float
    recovery_rate: float
    start_month: int


@dataclass
class RiskEventConfig:
    """Configuration for a risk event type."""
    name: str
    intensity: float  # Annual arrival rate
    impact_type: str
    severity_dist: TriangularDistribution
    recovery_rate: float
    start_month: int = 1
    end_month: Optional[int] = None


class RiskEventManager:
    """
    Manages risk event arrivals and their effects.
    
    Maintains state of active shocks and computes aggregate
    multipliers for each impact type.
    
    Parameters
    ----------
    events : List[RiskEventConfig]
        List of risk event configurations
    """
    
    def __init__(self, events: List[RiskEventConfig]):
        self.events = events
        self.active_shocks: List[ActiveShock] = []
        
        # Create Poisson processes for each event
        self._arrival_processes = {
            e.name: PoissonProcess(base_rate=e.intensity / 12)  # Monthly rate
            for e in events
        }
    
    def check_for_arrivals(
        self,
        month: int,
        rng: Generator,
        regime_multiplier: float = 1.0
    ) -> List[ActiveShock]:
        """
        Check for new risk event arrivals this month.
        
        Parameters
        ----------
        month : int
            Current month
        rng : Generator
            Random number generator
        regime_multiplier : float
            Multiplier on arrival intensity from regime
            
        Returns
        -------
        List[ActiveShock]
            New shocks that occurred this month
        """
        new_shocks = []
        
        for event in self.events:
            # Check if event is active in this period
            if month < event.start_month - 1:
                continue
            if event.end_month and month > event.end_month - 1:
                continue
            
            # Sample arrivals with regime adjustment
            process = self._arrival_processes[event.name]
            effective_rate = process.base_rate * regime_multiplier
            
            n_arrivals = rng.poisson(effective_rate)
            
            for _ in range(n_arrivals):
                # Sample severity
                severity = event.severity_dist.sample(rng=rng)[0]
                
                shock = ActiveShock(
                    event_name=event.name,
                    impact_type=event.impact_type,
                    severity=severity,
                    recovery_rate=event.recovery_rate,
                    start_month=month
                )
                new_shocks.append(shock)
                self.active_shocks.append(shock)
        
        return new_shocks
    
    def process_recoveries(self, rng: Generator) -> int:
        """
        Process recovery of active shocks.
        
        Each shock has a probability of fully recovering each month.
        
        Returns
        -------
        int
            Number of shocks that recovered
        """
        recovered = 0
        remaining = []
        
        for shock in self.active_shocks:
            if rng.random() < shock.recovery_rate:
                recovered += 1
            else:
                # Partial recovery: move severity toward 1.0
                shock.severity = shock.severity + (1.0 - shock.severity) * 0.2
                remaining.append(shock)
        
        self.active_shocks = remaining
        return recovered
    
    def get_multipliers(self) -> Dict[str, float]:
        """
        Compute aggregate multipliers from all active shocks.
        
        Multipliers are combined multiplicatively:
        If two shocks have severity 0.9 and 0.8 on adoption,
        the combined multiplier is 0.9 × 0.8 = 0.72
        
        Returns
        -------
        Dict[str, float]
            Mapping from impact type to aggregate multiplier
        """
        multipliers = {
            'adoption': 1.0,
            'churn': 1.0,
            'revenue': 1.0,
            'cost': 1.0
        }
        
        for shock in self.active_shocks:
            if shock.impact_type in multipliers:
                multipliers[shock.impact_type] *= shock.severity
        
        return multipliers
    
    def reset(self):
        """Clear all active shocks."""
        self.active_shocks = []
    
    def get_active_count(self) -> int:
        """Get number of currently active shocks."""
        return len(self.active_shocks)
    
    def get_active_by_type(self) -> Dict[str, int]:
        """Get count of active shocks by impact type."""
        counts = {'adoption': 0, 'churn': 0, 'revenue': 0, 'cost': 0}
        for shock in self.active_shocks:
            if shock.impact_type in counts:
                counts[shock.impact_type] += 1
        return counts