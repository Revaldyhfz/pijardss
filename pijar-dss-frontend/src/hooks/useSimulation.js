/**
 * Custom hook for simulation state management
 */

import { useState, useCallback } from 'react';
import { runSimulation, buildSimulationRequest } from '../services/api';

const DEFAULT_PARAMS = {
  // Capital & Dev
  initialCapital: 5000,
  devDuration: 6,
  devBurn: 200,
  
  // Sales
  leadsPerMonth: 7,
  winRateBumn: 0.70,
  winRateOpen: 0.22,
  bumnRatio: 0.35,
  
  // Pricing
  contractSmall: 180,
  contractMedium: 320,
  contractLarge: 550,
  
  // Retention & Costs
  baseChurn: 0.10,
  opOverhead: 120,
  costPerCustomer: 5,
  
  // Risk Events
  riskEvents: [],
  enableRisks: true,
};

const PRESETS = {
  Base: { ...DEFAULT_PARAMS },
  Conservative: {
    ...DEFAULT_PARAMS,
    initialCapital: 6000,
    devDuration: 8,
    leadsPerMonth: 5,
    winRateBumn: 0.60,
    winRateOpen: 0.18,
    baseChurn: 0.12,
  },
  Aggressive: {
    ...DEFAULT_PARAMS,
    initialCapital: 7000,
    devDuration: 5,
    devBurn: 280,
    leadsPerMonth: 10,
    winRateBumn: 0.78,
    winRateOpen: 0.28,
    baseChurn: 0.08,
  },
  Pessimistic: {
    ...DEFAULT_PARAMS,
    initialCapital: 4000,
    devDuration: 10,
    devBurn: 250,
    leadsPerMonth: 4,
    winRateBumn: 0.55,
    winRateOpen: 0.15,
    baseChurn: 0.15,
  },
};

export function useSimulation() {
  const [params, setParams] = useState(DEFAULT_PARAMS);
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activePreset, setActivePreset] = useState('Base');
  const [simConfig, setSimConfig] = useState({
    nSimulations: 500,
    timeHorizon: 36,
  });

  const updateParam = useCallback((key, value) => {
    setParams(prev => ({ ...prev, [key]: value }));
    setActivePreset(null); // Clear preset when manually editing
  }, []);

  const applyPreset = useCallback((presetName) => {
    if (PRESETS[presetName]) {
      setParams(PRESETS[presetName]);
      setActivePreset(presetName);
    }
  }, []);

  const runSim = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const request = buildSimulationRequest(params, simConfig);
      const data = await runSimulation(request);
      setResults(data);
    } catch (err) {
      setError(err.message);
      console.error('Simulation error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [params, simConfig]);

  const reset = useCallback(() => {
    setParams(DEFAULT_PARAMS);
    setActivePreset('Base');
    setResults(null);
    setError(null);
  }, []);

  return {
    params,
    results,
    isLoading,
    error,
    activePreset,
    simConfig,
    presets: Object.keys(PRESETS),
    updateParam,
    applyPreset,
    runSim,
    reset,
    setSimConfig,
  };
}