/**
 * Outcome distribution visualization
 * Horizontal bar chart for better readability than pie chart
 */

import React from 'react';

const OUTCOME_CONFIG = {
  double_plus: {
    label: '2x+ Return',
    color: '#059669',
    bgColor: '#ecfdf5',
    description: 'Doubled investment or more',
  },
  profitable: {
    label: 'Profitable',
    color: '#3b82f6',
    bgColor: '#eff6ff',
    description: 'Positive return, less than 2x',
  },
  loss: {
    label: 'Loss',
    color: '#f59e0b',
    bgColor: '#fffbeb',
    description: 'Lost money but still solvent',
  },
  ruin: {
    label: 'Ruin',
    color: '#dc2626',
    bgColor: '#fef2f2',
    description: 'Complete capital depletion',
  },
};

export function OutcomesPieChart({ data }) {
  if (!data) {
    return (
      <div style={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--gray-400)',
      }}>
        No data available
      </div>
    );
  }

  const total = data.total || (data.double_plus + data.profitable + data.loss + data.ruin);
  
  const outcomeData = [
    { key: 'double_plus', ...OUTCOME_CONFIG.double_plus, count: data.double_plus, pct: data.double_plus / total },
    { key: 'profitable', ...OUTCOME_CONFIG.profitable, count: data.profitable, pct: data.profitable / total },
    { key: 'loss', ...OUTCOME_CONFIG.loss, count: data.loss, pct: data.loss / total },
    { key: 'ruin', ...OUTCOME_CONFIG.ruin, count: data.ruin, pct: data.ruin / total },
  ].filter(d => d.count > 0);

  // Calculate success rate
  const successRate = ((data.double_plus + data.profitable) / total * 100).toFixed(0);
  const ruinRate = (data.ruin / total * 100).toFixed(1);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Summary Stats */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginBottom: '16px',
      }}>
        <div style={{
          padding: '12px',
          backgroundColor: 'var(--success-50)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid #a7f3d0',
          textAlign: 'center',
        }}>
          <div style={{
            fontSize: '24px',
            fontWeight: 700,
            color: 'var(--success-600)',
          }}>
            {successRate}%
          </div>
          <div style={{
            fontSize: '11px',
            color: 'var(--gray-600)',
            fontWeight: 500,
          }}>
            Profitable
          </div>
        </div>
        <div style={{
          padding: '12px',
          backgroundColor: 'var(--danger-50)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid #fecaca',
          textAlign: 'center',
        }}>
          <div style={{
            fontSize: '24px',
            fontWeight: 700,
            color: 'var(--danger-600)',
          }}>
            {ruinRate}%
          </div>
          <div style={{
            fontSize: '11px',
            color: 'var(--gray-600)',
            fontWeight: 500,
          }}>
            Ruin Risk
          </div>
        </div>
      </div>

      {/* Outcome Bars */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {outcomeData.map((item) => (
          <OutcomeBar key={item.key} item={item} total={total} />
        ))}
      </div>

      {/* Total simulations */}
      <div style={{
        marginTop: '12px',
        paddingTop: '12px',
        borderTop: '1px solid var(--gray-100)',
        fontSize: '11px',
        color: 'var(--gray-500)',
        textAlign: 'center',
      }}>
        Based on {total.toLocaleString()} Monte Carlo simulations
      </div>
    </div>
  );
}

function OutcomeBar({ item, total }) {
  const percentage = (item.count / total * 100).toFixed(1);
  
  return (
    <div style={{
      padding: '10px 12px',
      backgroundColor: item.bgColor,
      borderRadius: 'var(--radius-md)',
      border: `1px solid ${item.color}20`,
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '6px',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: item.color,
          }} />
          <span style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--gray-800)',
          }}>
            {item.label}
          </span>
        </div>
        <span style={{
          fontSize: '14px',
          fontWeight: 700,
          color: item.color,
        }}>
          {percentage}%
        </span>
      </div>
      
      {/* Progress bar */}
      <div style={{
        height: '6px',
        backgroundColor: `${item.color}20`,
        borderRadius: 'var(--radius-full)',
        overflow: 'hidden',
      }}>
        <div style={{
          height: '100%',
          width: `${percentage}%`,
          backgroundColor: item.color,
          borderRadius: 'var(--radius-full)',
          transition: 'width 0.5s ease',
        }} />
      </div>
      
      <div style={{
        marginTop: '4px',
        fontSize: '10px',
        color: 'var(--gray-500)',
      }}>
        {item.count.toLocaleString()} scenarios • {item.description}
      </div>
    </div>
  );
}