/**
 * Formatting utilities
 */

/**
 * Format number with thousand separators
 */
export function formatNumber(value, decimals = 0) {
  if (value === null || value === undefined) return '-';
  return Number(value).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Format as percentage
 */
export function formatPercent(value, decimals = 0) {
  if (value === null || value === undefined) return '-';
  // If value is already 0-100 range
  if (Math.abs(value) > 1) {
    return `${formatNumber(value, decimals)}%`;
  }
  // If value is 0-1 range
  return `${formatNumber(value * 100, decimals)}%`;
}

/**
 * Format as currency (IDR)
 */
export function formatCurrency(value, unit = 'M') {
  if (value === null || value === undefined) return '-';
  const formatted = formatNumber(value, 0);
  return `IDR ${formatted}${unit}`;
}

/**
 * Format as compact number
 */
export function formatCompact(value) {
  if (value === null || value === undefined) return '-';
  if (Math.abs(value) >= 1e9) {
    return `${(value / 1e9).toFixed(1)}B`;
  }
  if (Math.abs(value) >= 1e6) {
    return `${(value / 1e6).toFixed(1)}M`;
  }
  if (Math.abs(value) >= 1e3) {
    return `${(value / 1e3).toFixed(1)}K`;
  }
  return value.toFixed(0);
}

/**
 * Format duration in months
 */
export function formatMonths(value) {
  if (value === null || value === undefined || value < 0) return '-';
  return `${Math.round(value)} mo`;
}

/**
 * Get status color based on metric type and value
 */
export function getStatusColor(metric, value) {
  const thresholds = {
    prob_profit: { good: 0.7, warning: 0.5 },
    prob_double: { good: 0.5, warning: 0.3 },
    prob_ruin: { good: 0.05, warning: 0.15, inverse: true },
    max_drawdown: { good: 30, warning: 50, inverse: true },
    return: { good: 50, warning: 0 },
  };

  const t = thresholds[metric];
  if (!t) return 'neutral';

  if (t.inverse) {
    if (value <= t.good) return 'good';
    if (value <= t.warning) return 'warning';
    return 'bad';
  } else {
    if (value >= t.good) return 'good';
    if (value >= t.warning) return 'warning';
    return 'bad';
  }
}

/**
 * Get recommendation styling
 */
export function getRecommendationStyle(recommendation) {
  const styles = {
    PROCEED: {
      bg: 'var(--success-50)',
      border: '#a7f3d0',
      color: 'var(--success-600)',
      text: 'PROCEED',
    },
    CAUTION: {
      bg: 'var(--warning-50)',
      border: '#fde68a',
      color: 'var(--warning-600)',
      text: 'CAUTION',
    },
    REASSESS: {
      bg: '#fff7ed',
      border: '#fed7aa',
      color: '#c2410c',
      text: 'REASSESS',
    },
    DO_NOT_PROCEED: {
      bg: 'var(--danger-50)',
      border: '#fecaca',
      color: 'var(--danger-600)',
      text: 'DO NOT PROCEED',
    },
  };

  return styles[recommendation] || styles.CAUTION;
}