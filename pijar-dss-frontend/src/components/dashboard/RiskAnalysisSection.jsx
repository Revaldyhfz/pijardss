/**
 * Risk analysis section with key metrics
 */

import React from 'react';
import { Shield, TrendingDown, AlertCircle, Clock } from 'lucide-react';
import { Card } from '../common/Card';
import { SurvivalChart } from '../charts/SurvivalChart';
import { formatNumber, formatPercent } from '../../utils/format';

export function RiskAnalysisSection({ riskMetrics, summary }) {
  if (!riskMetrics) return null;

  const riskItems = [
    {
      label: 'Value at Risk (95%)',
      value: `IDR ${formatNumber(riskMetrics.var?.['95'] || summary.var_5, 0)}M`,
      description: '95% confidence max loss',
      icon: TrendingDown,
      color: 'var(--danger-600)',
    },
    {
      label: 'Conditional VaR (95%)',
      value: `IDR ${formatNumber(riskMetrics.cvar?.['95'] || summary.cvar_5, 0)}M`,
      description: 'Expected loss in worst 5%',
      icon: AlertCircle,
      color: 'var(--danger-600)',
    },
    {
      label: 'Max Drawdown (95th)',
      value: `${formatNumber(riskMetrics.drawdown_p95 || summary.max_drawdown_p95, 0)}%`,
      description: 'Worst expected peak-to-trough',
      icon: TrendingDown,
      color: 'var(--warning-600)',
    },
    {
      label: 'Months Underwater',
      value: `${formatNumber(riskMetrics.months_underwater_mean, 1)} avg`,
      description: 'Time below starting capital',
      icon: Clock,
      color: 'var(--primary-600)',
    },
  ];

  return (
    <Card title="Risk Analysis" icon={Shield} padding="0">
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
      }}>
        {/* Risk Metrics */}
        <div style={{ padding: '16px' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px',
          }}>
            {riskItems.map((item, i) => {
              const Icon = item.icon;
              return (
                <div
                  key={i}
                  style={{
                    padding: '14px',
                    backgroundColor: 'var(--gray-50)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--gray-100)',
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '8px',
                  }}>
                    <Icon size={16} style={{ color: item.color }} />
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: 'var(--gray-500)',
                      textTransform: 'uppercase',
                    }}>
                      {item.label}
                    </span>
                  </div>
                  <div style={{
                    fontSize: '18px',
                    fontWeight: 700,
                    color: 'var(--gray-900)',
                  }}>
                    {item.value}
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: 'var(--gray-500)',
                    marginTop: '2px',
                  }}>
                    {item.description}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Survival Curve */}
        <div style={{
          borderLeft: '1px solid var(--gray-100)',
          padding: '16px',
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--gray-600)',
            marginBottom: '12px',
          }}>
            Survival Curve
          </div>
          <div style={{ height: '200px' }}>
            <SurvivalChart data={riskMetrics.survival_curve} />
          </div>
        </div>
      </div>
    </Card>
  );
}