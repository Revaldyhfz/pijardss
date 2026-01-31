/**
 * Custom slider input component
 */

import React from 'react';

export function Slider({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  unit = '',
  format = (v) => v.toLocaleString(),
}) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px',
      }}>
        <label style={{
          fontSize: '13px',
          fontWeight: 500,
          color: 'var(--gray-600)',
        }}>
          {label}
        </label>
        <span style={{
          fontSize: '13px',
          fontWeight: 600,
          color: 'var(--primary-600)',
          backgroundColor: 'var(--primary-50)',
          padding: '2px 8px',
          borderRadius: 'var(--radius-sm)',
        }}>
          {format(value)}{unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{
          width: '100%',
          height: '6px',
          borderRadius: 'var(--radius-full)',
          appearance: 'none',
          background: `linear-gradient(to right, var(--primary-500) 0%, var(--primary-500) ${((value - min) / (max - min)) * 100}%, var(--gray-200) ${((value - min) / (max - min)) * 100}%, var(--gray-200) 100%)`,
          cursor: 'pointer',
          outline: 'none',
        }}
      />
    </div>
  );
}