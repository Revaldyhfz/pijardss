/**
 * Main Dashboard Page
 * Responsive layout with parameter sidebar and results area
 */

import React, { useEffect, useState } from 'react';
import { useSimulation } from '../../hooks/useSimulation';
import { ParameterPanel } from './ParameterPanel';
import { ResultsPanel } from './ResultsPanel';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { AlertTriangle } from 'lucide-react';

export function DashboardPage() {
  const {
    params,
    results,
    isLoading,
    error,
    activePreset,
    simConfig,
    presets,
    updateParam,
    applyPreset,
    runSim,
    reset,
    setSimConfig,
  } = useSimulation();

  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Run initial simulation
  useEffect(() => {
    runSim();
  }, []);

  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      paddingTop: '60px',
      backgroundColor: 'var(--gray-100)',
      overflow: 'hidden',
    }}>
      {/* Parameter Sidebar */}
      <ParameterPanel
        params={params}
        updateParam={updateParam}
        presets={presets}
        activePreset={activePreset}
        applyPreset={applyPreset}
        simConfig={simConfig}
        setSimConfig={setSimConfig}
        onRun={runSim}
        onReset={reset}
        isLoading={isLoading}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* Main Content Area */}
      <main style={{
        flex: 1,
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}>
        {error && (
          <div style={{
            margin: '16px',
            padding: '16px',
            backgroundColor: 'var(--danger-50)',
            border: '1px solid #fecaca',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            color: 'var(--danger-600)',
          }}>
            <AlertTriangle size={20} />
            <span>Error: {error}</span>
          </div>
        )}

        {isLoading && !results ? (
          <div style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <LoadingSpinner message="Running Monte Carlo simulation..." />
          </div>
        ) : results ? (
          <ResultsPanel results={results} isLoading={isLoading} />
        ) : (
          <div style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--gray-400)',
          }}>
            Configure parameters and run simulation
          </div>
        )}
      </main>
    </div>
  );
}