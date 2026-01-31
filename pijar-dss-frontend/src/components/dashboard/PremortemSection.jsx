/**
 * Enhanced Premortem Analysis Section
 * Data-driven failure analysis with bold conclusions
 */

import React from 'react';
import { 
  AlertTriangle, 
  TrendingDown, 
  Clock, 
  AlertCircle,
  ArrowRight,
  CheckCircle,
  XCircle,
  Target,
  Shield,
  Zap,
  Eye,
} from 'lucide-react';
import { Card } from '../common/Card';
import { formatPercent, formatNumber } from '../../utils/format';

export function PremortemSection({ premortem }) {
  // No failures - show success message
  if (!premortem || premortem.failure_count === 0 || premortem.failure_rate < 0.05) {
    return (
      <Card title="Premortem Analysis" icon={AlertTriangle} padding="24px">
        <div style={{
          textAlign: 'center',
          padding: '32px 20px',
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: 'var(--success-50)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
          }}>
            <CheckCircle size={32} style={{ color: 'var(--success-500)' }} />
          </div>
          <h3 style={{
            fontSize: '18px',
            fontWeight: 600,
            color: 'var(--gray-800)',
            marginBottom: '8px',
          }}>
            Low Failure Rate Detected
          </h3>
          <p style={{
            fontSize: '14px',
            color: 'var(--gray-600)',
            maxWidth: '400px',
            margin: '0 auto',
            lineHeight: 1.6,
          }}>
            Less than 5% of simulations resulted in significant loss.
            The current parameters show strong resilience against failure scenarios.
          </p>
        </div>
      </Card>
    );
  }

  // Determine severity level
  const severity = premortem.failure_rate > 0.4 ? 'high' : 
                   premortem.failure_rate > 0.2 ? 'medium' : 'low';
  
  const severityConfig = {
    high: { bg: '#fef2f2', border: '#fecaca', color: '#dc2626', label: 'HIGH RISK' },
    medium: { bg: '#fffbeb', border: '#fde68a', color: '#d97706', label: 'MODERATE RISK' },
    low: { bg: '#fefce8', border: '#fef08a', color: '#ca8a04', label: 'MANAGEABLE RISK' },
  };

  const config = severityConfig[severity];

  // Generate key conclusion based on data
  const topCause = premortem.primary_causes?.[0];
  const dominantTrajectory = premortem.failure_trajectories?.sort((a, b) => b.prevalence - a.prevalence)[0];

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: 'var(--radius-lg)',
      border: `2px solid ${config.border}`,
      overflow: 'hidden',
    }}>
      {/* Header with Key Conclusion */}
      <div style={{
        padding: '20px 24px',
        backgroundColor: config.bg,
        borderBottom: `1px solid ${config.border}`,
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '16px',
        }}>
          <div style={{ flex: 1 }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              marginBottom: '12px',
            }}>
              <AlertTriangle size={22} style={{ color: config.color }} />
              <h3 style={{
                fontSize: '16px',
                fontWeight: 700,
                color: 'var(--gray-900)',
                margin: 0,
              }}>
                Premortem Analysis
              </h3>
              <span style={{
                fontSize: '11px',
                fontWeight: 600,
                padding: '4px 10px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: config.color,
                color: 'white',
              }}>
                {config.label}
              </span>
            </div>

            {/* KEY CONCLUSION - Bold and prominent */}
            <div style={{
              backgroundColor: 'white',
              border: `1px solid ${config.border}`,
              borderRadius: 'var(--radius-md)',
              padding: '16px',
            }}>
              <div style={{
                fontSize: '11px',
                fontWeight: 600,
                color: 'var(--gray-500)',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px',
              }}>
                ⚡ Key Finding
              </div>
              <p style={{
                fontSize: '15px',
                fontWeight: 600,
                color: 'var(--gray-800)',
                margin: 0,
                lineHeight: 1.5,
              }}>
                {generateKeyConclusion(premortem, topCause, dominantTrajectory)}
              </p>
            </div>
          </div>

          {/* Failure Rate Dial */}
          <div style={{
            textAlign: 'center',
            padding: '12px 20px',
            backgroundColor: 'white',
            borderRadius: 'var(--radius-md)',
            border: `1px solid ${config.border}`,
            minWidth: '120px',
          }}>
            <div style={{
              fontSize: '32px',
              fontWeight: 800,
              color: config.color,
              lineHeight: 1,
            }}>
              {(premortem.failure_rate * 100).toFixed(0)}%
            </div>
            <div style={{
              fontSize: '11px',
              color: 'var(--gray-600)',
              fontWeight: 500,
              marginTop: '4px',
            }}>
              Failure Rate
            </div>
            <div style={{
              fontSize: '10px',
              color: 'var(--gray-500)',
              marginTop: '2px',
            }}>
              {premortem.failure_count} of {Math.round(premortem.failure_count / premortem.failure_rate)} sims
            </div>
          </div>
        </div>
      </div>

      {/* Three Column Analysis */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr 1fr',
        gap: '1px',
        backgroundColor: 'var(--gray-100)',
      }}>
        {/* Column 1: Primary Causes */}
        <div style={{ backgroundColor: 'white', padding: '20px' }}>
          <SectionHeader 
            icon={TrendingDown} 
            title="Why Failures Happen" 
            color="#ef4444"
          />
          
          <div style={{ marginTop: '16px' }}>
            {premortem.primary_causes?.slice(0, 4).map((cause, i) => (
              <CauseCard key={i} cause={cause} rank={i + 1} />
            ))}
          </div>

          {/* Cause Interaction Insight */}
          {premortem.cause_interactions?.length > 0 && (
            <div style={{
              marginTop: '16px',
              padding: '12px',
              backgroundColor: 'var(--gray-50)',
              borderRadius: 'var(--radius-md)',
              borderLeft: '3px solid var(--primary-500)',
            }}>
              <div style={{
                fontSize: '11px',
                fontWeight: 600,
                color: 'var(--primary-600)',
                marginBottom: '4px',
              }}>
                💡 Pattern Detected
              </div>
              <div style={{
                fontSize: '12px',
                color: 'var(--gray-700)',
              }}>
                {premortem.cause_interactions[0].cause1} and {premortem.cause_interactions[0].cause2} 
                {' '}appear together in {(premortem.cause_interactions[0].cooccurrence * 100).toFixed(0)}% of failures
              </div>
            </div>
          )}
        </div>

        {/* Column 2: How Failures Unfold */}
        <div style={{ backgroundColor: 'white', padding: '20px' }}>
          <SectionHeader 
            icon={Clock} 
            title="How Failures Unfold" 
            color="#f59e0b"
          />
          
          <div style={{ marginTop: '16px' }}>
            {premortem.failure_trajectories?.map((traj, i) => (
              <TrajectoryCard key={i} trajectory={traj} isTop={i === 0} />
            ))}
          </div>

          {/* Timing insight */}
          {premortem.critical_periods?.length > 0 && (
            <div style={{
              marginTop: '16px',
              padding: '12px',
              backgroundColor: 'var(--warning-50)',
              borderRadius: 'var(--radius-md)',
              borderLeft: '3px solid var(--warning-500)',
            }}>
              <div style={{
                fontSize: '11px',
                fontWeight: 600,
                color: 'var(--warning-600)',
                marginBottom: '4px',
              }}>
                ⏰ Critical Period
              </div>
              <div style={{
                fontSize: '12px',
                color: 'var(--gray-700)',
              }}>
                <strong>Month {premortem.critical_periods[0].start_month}-{premortem.critical_periods[0].end_month}</strong>
                {' '}shows elevated risk ({(premortem.critical_periods[0].cumulative_failures * 100).toFixed(0)}% of failures occur by this point)
              </div>
            </div>
          )}
        </div>

        {/* Column 3: What To Do About It */}
        <div style={{ backgroundColor: 'white', padding: '20px' }}>
          <SectionHeader 
            icon={Shield} 
            title="What To Do About It" 
            color="#10b981"
          />
          
          {/* Early Warning Signals */}
          <div style={{ marginTop: '16px' }}>
            <div style={{
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--gray-700)',
              marginBottom: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}>
              <Eye size={14} style={{ color: 'var(--danger-500)' }} />
              Watch For These Signals
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {premortem.early_warning_signals?.slice(0, 3).map((signal, i) => (
                <WarningSignal key={i} signal={signal} />
              ))}
            </div>
          </div>

          {/* Mitigation Actions */}
          <div style={{ marginTop: '20px' }}>
            <div style={{
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--gray-700)',
              marginBottom: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}>
              <Target size={14} style={{ color: 'var(--success-500)' }} />
              Priority Actions
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {premortem.mitigation_priorities?.slice(0, 3).map((action, i) => (
                <MitigationAction key={i} action={action} priority={i + 1} />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Summary Bar */}
      <div style={{
        padding: '16px 24px',
        backgroundColor: 'var(--gray-50)',
        borderTop: '1px solid var(--gray-200)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{
          fontSize: '12px',
          color: 'var(--gray-600)',
        }}>
          Analysis based on <strong>{premortem.failure_count}</strong> failure scenarios
          {premortem.median_failure_month && (
            <> • Median failure at <strong>month {premortem.median_failure_month}</strong></>
          )}
        </div>
        <div style={{
          fontSize: '11px',
          color: 'var(--gray-500)',
        }}>
          Failure definition: {premortem.failure_definition || 'Ruin (capital ≤ 0) OR return ≤ -20%'}
        </div>
      </div>
    </div>
  );
}

// Helper function to generate key conclusion
function generateKeyConclusion(premortem, topCause, dominantTrajectory) {
  if (!topCause) {
    return `${(premortem.failure_rate * 100).toFixed(0)}% of scenarios end in failure. Review parameters carefully.`;
  }

  const trajectoryText = dominantTrajectory 
    ? `, typically through ${formatTrajectoryName(dominantTrajectory.trajectory_type)} over ~${dominantTrajectory.months_to_failure} months`
    : '';

  if (topCause.attribution_score > 0.4) {
    return `${topCause.display_name} is the dominant failure driver (${(topCause.attribution_score * 100).toFixed(0)}% attribution). In failed scenarios, this metric was ${Math.abs(topCause.difference_pct).toFixed(0)}% ${topCause.direction} than successful ones${trajectoryText}.`;
  } else if (premortem.primary_causes?.length >= 2) {
    const cause2 = premortem.primary_causes[1];
    return `Failures are driven by a combination of ${topCause.display_name} and ${cause2.display_name}. No single factor dominates, suggesting systemic rather than isolated risk${trajectoryText}.`;
  } else {
    return `${topCause.display_name} contributes most to failures, with failed scenarios showing ${Math.abs(topCause.difference_pct).toFixed(0)}% ${topCause.direction} values${trajectoryText}.`;
  }
}

function formatTrajectoryName(type) {
  const names = {
    'slow_bleed': 'gradual decline',
    'sudden_collapse': 'sudden collapse',
    'recovery_failure': 'failed recovery',
  };
  return names[type] || type.replace('_', ' ');
}

function SectionHeader({ icon: Icon, title, color }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
    }}>
      <div style={{
        width: '28px',
        height: '28px',
        borderRadius: 'var(--radius-md)',
        backgroundColor: `${color}15`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <Icon size={16} style={{ color }} />
      </div>
      <h4 style={{
        fontSize: '13px',
        fontWeight: 700,
        color: 'var(--gray-800)',
        margin: 0,
      }}>
        {title}
      </h4>
    </div>
  );
}

function CauseCard({ cause, rank }) {
  const impactLevel = cause.attribution_score > 0.35 ? 'high' : 
                      cause.attribution_score > 0.2 ? 'medium' : 'low';
  
  const impactColors = {
    high: { bg: '#fef2f2', border: '#fecaca', text: '#dc2626' },
    medium: { bg: '#fffbeb', border: '#fde68a', text: '#d97706' },
    low: { bg: '#f8fafc', border: '#e2e8f0', text: '#64748b' },
  };

  const colors = impactColors[impactLevel];

  return (
    <div style={{
      padding: '12px',
      backgroundColor: colors.bg,
      borderRadius: 'var(--radius-md)',
      borderLeft: `3px solid ${colors.text}`,
      marginBottom: '10px',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '6px',
      }}>
        <span style={{
          fontSize: '13px',
          fontWeight: 700,
          color: 'var(--gray-800)',
        }}>
          {cause.display_name}
        </span>
        <span style={{
          fontSize: '12px',
          fontWeight: 700,
          color: colors.text,
        }}>
          {(cause.attribution_score * 100).toFixed(0)}%
        </span>
      </div>
      <div style={{
        fontSize: '11px',
        color: 'var(--gray-600)',
        lineHeight: 1.4,
      }}>
        {cause.direction === 'lower' ? '↓' : '↑'} {Math.abs(cause.difference_pct).toFixed(0)}% {cause.direction} in failed scenarios
      </div>
    </div>
  );
}

function TrajectoryCard({ trajectory, isTop }) {
  return (
    <div style={{
      padding: '14px',
      backgroundColor: isTop ? 'var(--warning-50)' : 'var(--gray-50)',
      borderRadius: 'var(--radius-md)',
      border: isTop ? '1px solid var(--warning-200)' : '1px solid var(--gray-200)',
      marginBottom: '10px',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px',
      }}>
        <span style={{
          fontSize: '13px',
          fontWeight: 700,
          color: 'var(--gray-800)',
          textTransform: 'capitalize',
        }}>
          {trajectory.trajectory_type.replace('_', ' ')}
          {isTop && <span style={{ marginLeft: '6px', fontSize: '10px' }}>👈 Most Common</span>}
        </span>
        <span style={{
          fontSize: '11px',
          fontWeight: 600,
          padding: '2px 8px',
          borderRadius: 'var(--radius-full)',
          backgroundColor: isTop ? 'var(--warning-500)' : 'var(--gray-400)',
          color: 'white',
        }}>
          {(trajectory.prevalence * 100).toFixed(0)}%
        </span>
      </div>
      
      <div style={{
        fontSize: '12px',
        color: 'var(--gray-700)',
        marginBottom: '8px',
      }}>
        <strong>Timeline:</strong> ~{trajectory.months_to_failure} months to failure
      </div>

      {trajectory.warning_signs?.length > 0 && (
        <div style={{
          fontSize: '11px',
          color: 'var(--gray-600)',
        }}>
          <div style={{ fontWeight: 600, marginBottom: '4px' }}>Warning signs:</div>
          <ul style={{ margin: 0, paddingLeft: '16px' }}>
            {trajectory.warning_signs.slice(0, 2).map((sign, i) => (
              <li key={i} style={{ marginBottom: '2px' }}>{sign}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function WarningSignal({ signal }) {
  return (
    <div style={{
      padding: '10px 12px',
      backgroundColor: 'var(--danger-50)',
      borderRadius: 'var(--radius-md)',
      borderLeft: '2px solid var(--danger-400)',
      fontSize: '12px',
      color: 'var(--gray-700)',
      lineHeight: 1.4,
    }}>
      {signal}
    </div>
  );
}

function MitigationAction({ action, priority }) {
  return (
    <div style={{
      padding: '10px 12px',
      backgroundColor: 'var(--success-50)',
      borderRadius: 'var(--radius-md)',
      borderLeft: '2px solid var(--success-400)',
      fontSize: '12px',
      color: 'var(--gray-700)',
      lineHeight: 1.4,
      display: 'flex',
      alignItems: 'flex-start',
      gap: '8px',
    }}>
      <span style={{
        width: '18px',
        height: '18px',
        borderRadius: '50%',
        backgroundColor: 'var(--success-500)',
        color: 'white',
        fontSize: '10px',
        fontWeight: 700,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}>
        {priority}
      </span>
      {action}
    </div>
  );
}