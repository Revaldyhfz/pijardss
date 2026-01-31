/**
 * Results display panel with scrollable content
 * Equity curve is prominent and full-width at top
 */

import React from 'react';
import {
  Target,
  Zap,
  TrendingUp,
  Shield,
  Activity,
  Clock,
  Check,
  X,
  AlertTriangle,
  BarChart3,
  PieChart,
  LineChart,
} from 'lucide-react';
import { Card } from '../common/Card';
import { MetricCard } from '../common/MetricCard';
import { EquityCurveChart } from '../charts/EquityCurveChart';
import { ReturnDistChart } from '../charts/ReturnDistChart';
import { OutcomesPieChart } from '../charts/OutcomesPieChart';
import { SurvivalChart } from '../charts/SurvivalChart';
import { TornadoChart } from '../charts/TornadoChart';
import { RiskAnalysisSection } from './RiskAnalysisSection';
import { PremortemSection } from './PremortemSection';
import { formatPercent, formatNumber, formatMonths, getRecommendationStyle, getStatusColor } from '../../utils/format';

export function ResultsPanel({ results, isLoading }) {
  const { summary, paths, outcomes, return_distribution, risk_metrics, premortem, sensitivity } = results;
  const recStyle = getRecommendationStyle(summary.recommendation);

  return (
    <div style={{
      flex: 1,
      overflow: 'auto',
      padding: '20px',
    }}>
      <div style={{
        maxWidth: '1600px',
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
      }}>
        {/* Loading Overlay */}
        {isLoading && (
          <div style={{
            position: 'fixed',
            top: '60px',
            right: '20px',
            backgroundColor: 'white',
            padding: '12px 20px',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-lg)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            zIndex: 50,
          }}>
            <div style={{
              width: '16px',
              height: '16px',
              border: '2px solid var(--gray-200)',
              borderTopColor: 'var(--primary-500)',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }} />
            <span style={{ fontSize: '14px', color: 'var(--gray-600)' }}>
              Updating...
            </span>
          </div>
        )}

        {/* === ROW 1: Recommendation Banner + Key Metrics === */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '280px 1fr',
          gap: '16px',
          alignItems: 'stretch',
        }}>
          {/* Recommendation Badge */}
          <div style={{
            padding: '20px 24px',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: recStyle.bg,
            border: `2px solid ${recStyle.border}`,
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
          }}>
            <div style={{
              width: '52px',
              height: '52px',
              borderRadius: '50%',
              backgroundColor: recStyle.color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              flexShrink: 0,
            }}>
              {summary.recommendation === 'PROCEED' ? (
                <Check size={28} />
              ) : summary.recommendation === 'DO_NOT_PROCEED' ? (
                <X size={28} />
              ) : (
                <AlertTriangle size={28} />
              )}
            </div>
            <div>
              <div style={{
                fontSize: '22px',
                fontWeight: 700,
                color: recStyle.color,
                lineHeight: 1.2,
              }}>
                {recStyle.text}
              </div>
              <div style={{
                fontSize: '13px',
                color: 'var(--gray-600)',
                marginTop: '4px',
              }}>
                {formatPercent(summary.prob_profit)} profit probability
              </div>
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(6, 1fr)',
            gap: '12px',
          }}>
            <MetricCard
              label="P(Profit)"
              value={formatPercent(summary.prob_profit)}
              status={getStatusColor('prob_profit', summary.prob_profit)}
              icon={Target}
              compact
            />
            <MetricCard
              label="P(2x)"
              value={formatPercent(summary.prob_double)}
              status={getStatusColor('prob_double', summary.prob_double)}
              icon={Zap}
              compact
            />
            <MetricCard
              label="Mean Return"
              value={`${summary.return_mean >= 0 ? '+' : ''}${formatNumber(summary.return_mean, 0)}%`}
              status={getStatusColor('return', summary.return_mean)}
              icon={TrendingUp}
              compact
            />
            <MetricCard
              label="P(Ruin)"
              value={formatPercent(summary.prob_ruin)}
              status={getStatusColor('prob_ruin', summary.prob_ruin)}
              icon={Shield}
              compact
            />
            <MetricCard
              label="Max DD"
              value={`${formatNumber(summary.max_drawdown_mean, 0)}%`}
              status={getStatusColor('max_drawdown', summary.max_drawdown_mean)}
              icon={Activity}
              compact
            />
            <MetricCard
              label="Breakeven"
              value={summary.breakeven_mean ? formatMonths(summary.breakeven_mean) : 'N/A'}
              status="neutral"
              icon={Clock}
              compact
            />
          </div>
        </div>

        {/* === ROW 2: EQUITY CURVE - FULL WIDTH, PROMINENT === */}
        <Card 
          title="Monte Carlo Simulation Paths" 
          icon={LineChart} 
          padding="20px"
          style={{
            boxShadow: 'var(--shadow-md)',
          }}
          headerAction={
            <div style={{
              display: 'flex',
              gap: '12px',
              fontSize: '12px',
              color: 'var(--gray-500)',
            }}>
              <span>{results.meta?.n_simulations || 500} simulations</span>
              <span>•</span>
              <span>{results.meta?.time_horizon || 36} months</span>
            </div>
          }
        >
          <EquityCurveChart
            data={paths}
            initialCapital={5000}
            height={420}
          />
        </Card>

        {/* === ROW 3: Secondary Charts === */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          gap: '16px',
        }}>
          {/* Outcomes */}
          <Card title="Outcome Distribution" icon={PieChart} padding="16px">
            <div style={{ height: '320px' }}>
              <OutcomesPieChart data={outcomes} />
            </div>
          </Card>

          {/* Return Distribution */}
          <Card title="Return Distribution" icon={BarChart3} padding="16px">
            <div style={{ height: '320px' }}>
              <ReturnDistChart data={return_distribution} summary={summary} />
            </div>
          </Card>

          {/* Sensitivity Analysis */}
          <Card title="Sensitivity Analysis" icon={Activity} padding="16px">
            <div style={{ height: '320px' }}>
              <TornadoChart data={sensitivity?.tornado || []} />
            </div>
          </Card>
        </div>

        {/* === ROW 4: Risk Analysis === */}
        <RiskAnalysisSection riskMetrics={risk_metrics} summary={summary} />

        {/* === ROW 5: Premortem Analysis === */}
        <PremortemSection premortem={premortem} />
      </div>
    </div>
  );
}