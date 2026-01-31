/**
 * API Service for Pijar DSS Backend
 */

const API_BASE_URL = '/api/v1';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

/**
 * Health check
 */
export async function checkHealth() {
  return fetchAPI('/health');
}

/**
 * Get parameter presets
 */
export async function getPresets() {
  return fetchAPI('/presets');
}

/**
 * Run Monte Carlo simulation
 */
export async function runSimulation(params) {
  return fetchAPI('/simulate', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * Build simulation request from UI parameters
 */
export function buildSimulationRequest(uiParams, config = {}) {
  return {
    // Capital & Development
    initial_capital: {
      type: 'triangular',
      params: {
        min: uiParams.initialCapital * 0.8,
        mode: uiParams.initialCapital,
        max: uiParams.initialCapital * 1.2,
      },
    },
    dev_duration: {
      type: 'triangular',
      params: {
        min: Math.max(3, uiParams.devDuration - 2),
        mode: uiParams.devDuration,
        max: uiParams.devDuration + 3,
      },
    },
    dev_burn: {
      type: 'triangular',
      params: {
        min: uiParams.devBurn * 0.8,
        mode: uiParams.devBurn,
        max: uiParams.devBurn * 1.25,
      },
    },

    // Sales
    leads_per_month: {
      type: 'triangular',
      params: {
        min: Math.max(1, uiParams.leadsPerMonth - 3),
        mode: uiParams.leadsPerMonth,
        max: uiParams.leadsPerMonth + 5,
      },
    },
    win_rate_bumn: {
      type: 'beta',
      params: {
        alpha: uiParams.winRateBumn * 20,
        beta: (1 - uiParams.winRateBumn) * 20,
      },
    },
    win_rate_open: {
      type: 'beta',
      params: {
        alpha: uiParams.winRateOpen * 20,
        beta: (1 - uiParams.winRateOpen) * 20,
      },
    },
    bumn_ratio: uiParams.bumnRatio || 0.35,
    sales_cycle_months: {
      type: 'gamma',
      params: { shape: 6.25, scale: 0.8 },
    },

    // Pricing
    contract_small: {
      type: 'lognormal',
      params: { mean: uiParams.contractSmall, cv: 0.2 },
    },
    contract_medium: {
      type: 'lognormal',
      params: { mean: uiParams.contractMedium, cv: 0.15 },
    },
    contract_large: {
      type: 'lognormal',
      params: { mean: uiParams.contractLarge, cv: 0.1 },
    },
    size_distribution: { small: 0.5, medium: 0.35, large: 0.15 },

    // Retention & Costs
    churn_rate: {
      type: 'beta',
      params: {
        alpha: uiParams.baseChurn * 20,
        beta: (1 - uiParams.baseChurn) * 20,
      },
    },
    op_overhead: uiParams.opOverhead,
    cost_per_customer: uiParams.costPerCustomer,

    // Risk Events
    risk_events: uiParams.riskEvents || [],

    // Config
    n_simulations: config.nSimulations || 500,
    time_horizon: config.timeHorizon || 36,
    seed: config.seed || null,
    enable_regime_switching: config.enableRegimes !== false,
    enable_risk_events: config.enableRisks !== false,
  };
}