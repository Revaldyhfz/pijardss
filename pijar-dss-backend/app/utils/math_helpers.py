"""
Mathematical and Statistical Helper Functions.

This module provides common statistical computations used throughout
the simulation and analytics modules. All functions are designed to
be numerically stable and handle edge cases gracefully.
"""

import numpy as np
from numpy.typing import NDArray
from typing import Tuple, List, Optional


def percentile(data: NDArray, q: float) -> float:
    """
    Compute the q-th percentile of data using linear interpolation.
    
    Parameters
    ----------
    data : array-like
        Input data (will be sorted internally)
    q : float
        Percentile to compute, in range [0, 100]
        
    Returns
    -------
    float
        The q-th percentile value
        
    Notes
    -----
    Uses linear interpolation between data points, which is the
    standard method for continuous distributions. This matches
    Excel's PERCENTILE.INC function.
    """
    return float(np.percentile(data, q))


def compute_quantiles(data: NDArray, quantiles: List[float]) -> dict:
    """
    Compute multiple quantiles efficiently in a single pass.
    
    Parameters
    ----------
    data : array-like
        Input data
    quantiles : list of float
        Quantiles to compute (as percentages, e.g., [5, 25, 50, 75, 95])
        
    Returns
    -------
    dict
        Mapping from quantile to value
    """
    sorted_data = np.sort(data)
    return {q: percentile(sorted_data, q) for q in quantiles}


def compute_drawdown(equity_curve: NDArray) -> Tuple[NDArray, float]:
    """
    Compute the drawdown series and maximum drawdown.
    
    Drawdown at time t is defined as:
        DD(t) = (Peak(t) - Equity(t)) / Peak(t)
    
    where Peak(t) = max(Equity[0:t])
    
    This measures the percentage decline from the highest point
    reached so far, which is the standard risk metric in trading.
    
    Parameters
    ----------
    equity_curve : array-like
        Time series of portfolio/capital values
        
    Returns
    -------
    tuple
        (drawdown_series, max_drawdown)
        - drawdown_series: Array of drawdown values at each time
        - max_drawdown: Maximum drawdown observed (as decimal, e.g., 0.25 = 25%)
        
    Example
    -------
    >>> equity = np.array([100, 110, 105, 120, 90, 115])
    >>> dd_series, max_dd = compute_drawdown(equity)
    >>> max_dd
    0.25  # 25% drawdown from peak of 120 to trough of 90
    """
    equity_curve = np.asarray(equity_curve, dtype=np.float64)
    
    # Running maximum (peak)
    running_max = np.maximum.accumulate(equity_curve)
    
    # Drawdown as fraction of peak
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        drawdown = np.where(
            running_max > 0,
            (running_max - equity_curve) / running_max,
            0.0
        )
    
    max_drawdown = float(np.max(drawdown))
    
    return drawdown, max_drawdown


def compute_rolling_volatility(
    returns: NDArray, 
    window: int = 12
) -> NDArray:
    """
    Compute rolling volatility (standard deviation of returns).
    
    Volatility is the standard deviation of returns, typically
    annualized. For monthly returns:
        Annual Vol = Monthly Vol × sqrt(12)
    
    Parameters
    ----------
    returns : array-like
        Time series of returns (not prices)
    window : int
        Rolling window size
        
    Returns
    -------
    NDArray
        Rolling volatility series
    """
    returns = np.asarray(returns)
    n = len(returns)
    
    if n < window:
        return np.full(n, np.nan)
    
    result = np.full(n, np.nan)
    for i in range(window - 1, n):
        result[i] = np.std(returns[i - window + 1:i + 1], ddof=1)
    
    return result


def safe_divide(
    numerator: NDArray, 
    denominator: NDArray, 
    fill_value: float = 0.0
) -> NDArray:
    """
    Safe division that handles zeros and infinities.
    
    Parameters
    ----------
    numerator : array-like
        Numerator values
    denominator : array-like
        Denominator values
    fill_value : float
        Value to use where division is undefined
        
    Returns
    -------
    NDArray
        Result of division with safe handling
    """
    numerator = np.asarray(numerator, dtype=np.float64)
    denominator = np.asarray(denominator, dtype=np.float64)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.where(
            np.abs(denominator) > 1e-10,
            numerator / denominator,
            fill_value
        )
    
    return result


def weighted_average(
    values: NDArray, 
    weights: NDArray
) -> float:
    """
    Compute weighted average.
    
    Parameters
    ----------
    values : array-like
        Values to average
    weights : array-like
        Weights for each value
        
    Returns
    -------
    float
        Weighted average
    """
    values = np.asarray(values)
    weights = np.asarray(weights)
    
    total_weight = np.sum(weights)
    if total_weight == 0:
        return 0.0
    
    return float(np.sum(values * weights) / total_weight)


def empirical_cdf(data: NDArray) -> Tuple[NDArray, NDArray]:
    """
    Compute the empirical cumulative distribution function.
    
    The empirical CDF at value x is the proportion of observations
    less than or equal to x:
        F_n(x) = (1/n) × #{i : X_i ≤ x}
    
    Parameters
    ----------
    data : array-like
        Sample data
        
    Returns
    -------
    tuple
        (sorted_values, cumulative_probabilities)
    """
    sorted_data = np.sort(data)
    n = len(sorted_data)
    cumprob = np.arange(1, n + 1) / n
    
    return sorted_data, cumprob