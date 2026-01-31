/**
 * Reusable card component
 */

import React from 'react';

export function Card({ 
  children, 
  title, 
  icon: Icon,
  padding = '20px',
  className = '',
  style = {},
  headerAction,
}) {
  return (
    <div 
      className={className}
      style={{
        backgroundColor: 'white',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--gray-200)',
        boxShadow: 'var(--shadow-sm)',
        overflow: 'hidden',
        ...style,
      }}
    >
      {title && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 20px',
          borderBottom: '1px solid var(--gray-100)',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '14px',
            fontWeight: 600,
            color: 'var(--gray-800)',
          }}>
            {Icon && <Icon size={18} style={{ color: 'var(--primary-500)' }} />}
            {title}
          </div>
          {headerAction}
        </div>
      )}
      <div style={{ padding }}>
        {children}
      </div>
    </div>
  );
}