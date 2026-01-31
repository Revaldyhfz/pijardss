/**
 * Collapsible section component
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

export function Collapsible({ 
  title, 
  icon: Icon, 
  children, 
  defaultOpen = false,
  badge,
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: 'var(--radius-md)',
      border: '1px solid var(--gray-200)',
      marginBottom: '12px',
      overflow: 'hidden',
    }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          padding: '14px 16px',
          border: 'none',
          cursor: 'pointer',
          backgroundColor: isOpen ? 'var(--gray-50)' : 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          transition: 'background-color var(--transition-fast)',
        }}
      >
        <span style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontSize: '13px',
          fontWeight: 600,
          color: 'var(--gray-700)',
        }}>
          {Icon && <Icon size={16} style={{ color: 'var(--primary-500)' }} />}
          {title}
          {badge && (
            <span style={{
              fontSize: '11px',
              fontWeight: 500,
              padding: '2px 8px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--primary-100)',
              color: 'var(--primary-600)',
            }}>
              {badge}
            </span>
          )}
        </span>
        {isOpen ? (
          <ChevronUp size={16} style={{ color: 'var(--gray-400)' }} />
        ) : (
          <ChevronDown size={16} style={{ color: 'var(--gray-400)' }} />
        )}
      </button>
      {isOpen && (
        <div style={{ 
          padding: '16px',
          borderTop: '1px solid var(--gray-100)',
        }}>
          {children}
        </div>
      )}
    </div>
  );
}