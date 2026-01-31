/**
 * Compact metric display card
 */

import React from 'react';

const STATUS_STYLES = {
  good: {
    bg: 'var(--success-50)',
    color: 'var(--success-600)',
    border: '#a7f3d0',
  },
  warning: {
    bg: 'var(--warning-50)',
    color: 'var(--warning-600)',
    border: '#fde68a',
  },
  bad: {
    bg: 'var(--danger-50)',
    color: 'var(--danger-600)',
    border: '#fecaca',
  },
  neutral: {
    bg: 'var(--primary-50)',
    color: 'var(--primary-600)',
    border: 'var(--primary-200)',
  },
};

export function MetricCard({ 
  label, 
  value, 
  subValue,
  status = 'neutral', 
  icon: Icon,
  compact = false,
}) {
  const style = STATUS_STYLES[status] || STATUS_STYLES.neutral;

  if (compact) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: 'var(--radius-md)',
        padding: '12px 16px',
        border: '1px solid var(--gray-200)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}>
        {Icon && (
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: style.bg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: style.color,
            flexShrink: 0,
          }}>
            <Icon size={18} />
          </div>
        )}
        <div style={{ minWidth: 0 }}>
          <div style={{
            fontSize: '11px',
            fontWeight: 500,
            color: 'var(--gray-500)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '2px',
          }}>
            {label}
          </div>
          <div style={{
            fontSize: '18px',
            fontWeight: 700,
            color: style.color,
            lineHeight: 1.2,
          }}>
            {value}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: style.bg,
      borderRadius: 'var(--radius-lg)',
      padding: '20px',
      border: `1px solid ${style.border}`,
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        marginBottom: '12px',
      }}>
        <span style={{
          fontSize: '12px',
          fontWeight: 600,
          color: 'var(--gray-600)',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
        }}>
          {label}
        </span>
        {Icon && (
          <div style={{ color: style.color }}>
            <Icon size={20} />
          </div>
        )}
      </div>
      <div style={{
        fontSize: '28px',
        fontWeight: 700,
        color: style.color,
        lineHeight: 1.1,
      }}>
        {value}
      </div>
      {subValue && (
        <div style={{
          fontSize: '12px',
          color: 'var(--gray-500)',
          marginTop: '4px',
        }}>
          {subValue}
        </div>
      )}
    </div>
  );
}