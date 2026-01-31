/**
 * Parameter configuration sidebar
 */

import React from 'react';
import {
  DollarSign,
  Users,
  Percent,
  Activity,
  Shield,
  Play,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Settings,
} from 'lucide-react';
import { Slider } from '../common/Slider';
import { Collapsible } from '../common/Collapsible';

export function ParameterPanel({
  params,
  updateParam,
  presets,
  activePreset,
  applyPreset,
  simConfig,
  setSimConfig,
  onRun,
  onReset,
  isLoading,
  isOpen,
  onToggle,
}) {
  return (
    <>
      {/* Toggle button for mobile */}
      <button
        onClick={onToggle}
        style={{
          position: 'fixed',
          left: isOpen ? '280px' : '0',
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 100,
          width: '24px',
          height: '48px',
          backgroundColor: 'white',
          border: '1px solid var(--gray-200)',
          borderLeft: isOpen ? 'none' : '1px solid var(--gray-200)',
          borderRadius: isOpen ? '0 8px 8px 0' : '0 8px 8px 0',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'left var(--transition-normal)',
          boxShadow: 'var(--shadow-md)',
        }}
      >
        {isOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
      </button>

      {/* Sidebar */}
      <aside
        style={{
          width: isOpen ? '280px' : '0',
          flexShrink: 0,
          backgroundColor: 'white',
          borderRight: '1px solid var(--gray-200)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          transition: 'width var(--transition-normal)',
        }}
      >
        {/* Presets */}
        <div style={{
          padding: '16px',
          borderBottom: '1px solid var(--gray-100)',
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '6px',
          }}>
            {presets.map(preset => (
              <button
                key={preset}
                onClick={() => applyPreset(preset)}
                style={{
                  padding: '8px 4px',
                  fontSize: '11px',
                  fontWeight: 500,
                  border: activePreset === preset 
                    ? '1px solid var(--primary-500)' 
                    : '1px solid var(--gray-200)',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: activePreset === preset 
                    ? 'var(--primary-50)' 
                    : 'white',
                  color: activePreset === preset 
                    ? 'var(--primary-600)' 
                    : 'var(--gray-600)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                }}
              >
                {preset}
              </button>
            ))}
          </div>
        </div>

        {/* Scrollable Parameters */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px',
        }}>
          {/* Capital & Development */}
          <Collapsible title="Capital & Dev" icon={DollarSign} defaultOpen>
            <Slider
              label="Initial Capital"
              value={params.initialCapital}
              onChange={(v) => updateParam('initialCapital', v)}
              min={2000}
              max={12000}
              step={500}
              unit=" M"
            />
            <Slider
              label="Dev Duration"
              value={params.devDuration}
              onChange={(v) => updateParam('devDuration', v)}
              min={3}
              max={18}
              step={1}
              unit=" mo"
            />
            <Slider
              label="Monthly Burn"
              value={params.devBurn}
              onChange={(v) => updateParam('devBurn', v)}
              min={100}
              max={500}
              step={20}
              unit=" M"
            />
          </Collapsible>

          {/* Sales & Conversion */}
          <Collapsible title="Sales & Conversion" icon={Users} defaultOpen>
            <Slider
              label="Leads per Month"
              value={params.leadsPerMonth}
              onChange={(v) => updateParam('leadsPerMonth', v)}
              min={1}
              max={25}
              step={1}
            />
            <Slider
              label="BUMN Win Rate"
              value={params.winRateBumn * 100}
              onChange={(v) => updateParam('winRateBumn', v / 100)}
              min={20}
              max={95}
              step={5}
              unit="%"
              format={(v) => v.toFixed(0)}
            />
            <Slider
              label="Open Win Rate"
              value={params.winRateOpen * 100}
              onChange={(v) => updateParam('winRateOpen', v / 100)}
              min={5}
              max={50}
              step={5}
              unit="%"
              format={(v) => v.toFixed(0)}
            />
          </Collapsible>

          {/* Pricing */}
          <Collapsible title="Pricing (M/yr)" icon={Percent}>
            <Slider
              label="Small PT"
              value={params.contractSmall}
              onChange={(v) => updateParam('contractSmall', v)}
              min={80}
              max={300}
              step={20}
            />
            <Slider
              label="Medium PT"
              value={params.contractMedium}
              onChange={(v) => updateParam('contractMedium', v)}
              min={150}
              max={600}
              step={25}
            />
            <Slider
              label="Large PT"
              value={params.contractLarge}
              onChange={(v) => updateParam('contractLarge', v)}
              min={300}
              max={1000}
              step={50}
            />
          </Collapsible>

          {/* Retention & Costs */}
          <Collapsible title="Retention & Costs" icon={Activity}>
            <Slider
              label="Annual Churn"
              value={params.baseChurn * 100}
              onChange={(v) => updateParam('baseChurn', v / 100)}
              min={3}
              max={30}
              step={1}
              unit="%"
              format={(v) => v.toFixed(0)}
            />
            <Slider
              label="Op Overhead"
              value={params.opOverhead}
              onChange={(v) => updateParam('opOverhead', v)}
              min={50}
              max={300}
              step={10}
              unit=" M/mo"
            />
          </Collapsible>

          {/* Simulation Config */}
          <Collapsible title="Simulation Config" icon={Settings}>
            <div style={{ marginBottom: '12px' }}>
              <label style={{
                display: 'block',
                fontSize: '13px',
                fontWeight: 500,
                color: 'var(--gray-600)',
                marginBottom: '8px',
              }}>
                Number of Simulations
              </label>
              <select
                value={simConfig.nSimulations}
                onChange={(e) => setSimConfig({
                  ...simConfig,
                  nSimulations: parseInt(e.target.value),
                })}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  fontSize: '14px',
                  border: '1px solid var(--gray-300)',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'white',
                  cursor: 'pointer',
                }}
              >
                <option value={200}>200 (Fast)</option>
                <option value={500}>500 (Standard)</option>
                <option value={1000}>1,000 (Detailed)</option>
                <option value={2000}>2,000 (High Precision)</option>
              </select>
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px 0',
            }}>
              <span style={{
                fontSize: '13px',
                color: 'var(--gray-600)',
              }}>
                Regime Switching
              </span>
              <button
                onClick={() => setSimConfig({
                  ...simConfig,
                  enableRegimes: !simConfig.enableRegimes,
                })}
                style={{
                  width: '44px',
                  height: '24px',
                  borderRadius: 'var(--radius-full)',
                  border: 'none',
                  backgroundColor: simConfig.enableRegimes !== false
                    ? 'var(--primary-500)'
                    : 'var(--gray-300)',
                  cursor: 'pointer',
                  position: 'relative',
                  transition: 'background-color var(--transition-fast)',
                }}
              >
                <span style={{
                  position: 'absolute',
                  top: '2px',
                  left: simConfig.enableRegimes !== false ? '22px' : '2px',
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  backgroundColor: 'white',
                  transition: 'left var(--transition-fast)',
                  boxShadow: 'var(--shadow-sm)',
                }} />
              </button>
            </div>
          </Collapsible>
        </div>

        {/* Action Buttons */}
        <div style={{
          padding: '16px',
          borderTop: '1px solid var(--gray-100)',
          display: 'flex',
          gap: '8px',
        }}>
          <button
            onClick={onReset}
            style={{
              padding: '12px',
              border: '1px solid var(--gray-300)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            title="Reset to defaults"
          >
            <RotateCcw size={18} style={{ color: 'var(--gray-600)' }} />
          </button>
          <button
            onClick={onRun}
            disabled={isLoading}
            style={{
              flex: 1,
              padding: '12px 20px',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              backgroundColor: isLoading ? 'var(--gray-300)' : 'var(--primary-500)',
              color: 'white',
              fontWeight: 600,
              fontSize: '14px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'background-color var(--transition-fast)',
            }}
          >
            {isLoading ? (
              <>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid rgba(255,255,255,0.3)',
                  borderTopColor: 'white',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                }} />
                Running...
              </>
            ) : (
              <>
                <Play size={18} />
                Run Simulation
              </>
            )}
          </button>
        </div>
      </aside>
    </>
  );
}