/**
 * Loading spinner component
 */

import React from 'react';

export function LoadingSpinner({ size = 40, message = 'Running simulation...' }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px',
      gap: '16px',
    }}>
      <div style={{
        width: size,
        height: size,
        border: '3px solid var(--gray-200)',
        borderTopColor: 'var(--primary-500)',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
      }} />
      {message && (
        <span style={{
          fontSize: '14px',
          color: 'var(--gray-500)',
        }}>
          {message}
        </span>
      )}
    </div>
  );
}