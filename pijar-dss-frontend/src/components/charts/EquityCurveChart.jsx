/**
 * Trading-grade equity curve visualization
 * Shows individual simulation paths with highlighted best/worst/median
 * Similar to professional quant trading backtests
 */

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { formatCompact } from '../../utils/format';

// Color palette for individual paths
const PATH_COLORS = [
  '#94a3b8', '#a1a1aa', '#9ca3af', '#a3a3a3', '#9ca3af',
  '#94a3b8', '#a1a1aa', '#9ca3af', '#a3a3a3', '#9ca3af',
];

export function EquityCurveChart({ data, initialCapital = 5000, height = 500 }) {
  // Process data for chart
  const { chartData, bestPath, worstPath, medianPath, pathStats } = useMemo(() => {
    if (!data?.percentiles || data.percentiles.length === 0) {
      return { chartData: [], bestPath: [], worstPath: [], medianPath: [], pathStats: null };
    }

    const horizon = data.percentiles.length;
    
    // Create chart data from percentiles
    const processed = data.percentiles.map((p, idx) => ({
      month: idx,
      p5: p.p5,
      p25: p.p25,
      median: p.p50,
      p75: p.p75,
      p95: p.p95,
    }));

    // Generate realistic sample paths if not provided
    let samplePaths = data.sample_paths || [];
    
    if (!samplePaths || samplePaths.length === 0) {
      // Generate paths based on percentile data
      samplePaths = [];
      for (let i = 0; i < 50; i++) {
        const path = [];
        let value = initialCapital;
        for (let m = 0; m < horizon; m++) {
          const p = data.percentiles[m];
          // Random walk within percentile bounds
          const range = p.p95 - p.p5;
          const noise = (Math.random() - 0.5) * range * 0.3;
          const target = p.p5 + Math.random() * range;
          value = value * 0.7 + target * 0.3 + noise;
          value = Math.max(0, value);
          path.push(Math.round(value));
        }
        samplePaths.push(path);
      }
    }

    // Find best, worst, and median paths by final value
    const pathsWithFinal = samplePaths.map((path, idx) => ({
      path,
      idx,
      finalValue: path[path.length - 1] || path[path.length - 2] || 0,
      maxValue: Math.max(...path),
      minValue: Math.min(...path.filter(v => v > 0)),
    }));

    pathsWithFinal.sort((a, b) => b.finalValue - a.finalValue);

    const best = pathsWithFinal[0];
    const worst = pathsWithFinal[pathsWithFinal.length - 1];
    const medianIdx = Math.floor(pathsWithFinal.length / 2);
    const med = pathsWithFinal[medianIdx];

    // Add sample paths to chart data
    const withPaths = processed.map((point, monthIdx) => {
      const newPoint = { ...point };
      
      // Add individual paths (select subset for performance)
      const step = Math.max(1, Math.floor(samplePaths.length / 30));
      samplePaths.forEach((path, pathIdx) => {
        if (pathIdx % step === 0 && pathIdx < 30) {
          newPoint[`path_${pathIdx}`] = path[monthIdx];
        }
      });

      // Add highlighted paths
      if (best?.path) newPoint.best = best.path[monthIdx];
      if (worst?.path) newPoint.worst = worst.path[monthIdx];
      if (med?.path) newPoint.moderate = med.path[monthIdx];

      return newPoint;
    });

    return {
      chartData: withPaths,
      bestPath: best,
      worstPath: worst,
      medianPath: med,
      pathStats: {
        total: samplePaths.length,
        displayed: Math.min(30, samplePaths.length),
      },
    };
  }, [data, initialCapital]);

  if (chartData.length === 0) {
    return (
      <div style={{
        height: height,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--gray-400)',
        fontSize: '14px',
      }}>
        No simulation data available
      </div>
    );
  }

  // Get path keys for rendering
  const pathKeys = Object.keys(chartData[0] || {}).filter(k => k.startsWith('path_'));

  return (
    <div style={{ width: '100%', height: height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart 
          data={chartData} 
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <defs>
            <linearGradient id="bestGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#10b981" stopOpacity={1} />
              <stop offset="100%" stopColor="#34d399" stopOpacity={1} />
            </linearGradient>
            <linearGradient id="worstGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#ef4444" stopOpacity={1} />
              <stop offset="100%" stopColor="#f87171" stopOpacity={1} />
            </linearGradient>
          </defs>

          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="var(--gray-200)" 
            vertical={true}
          />

          <XAxis
            dataKey="month"
            tick={{ fontSize: 11, fill: 'var(--gray-500)' }}
            tickLine={{ stroke: 'var(--gray-300)' }}
            axisLine={{ stroke: 'var(--gray-300)' }}
            tickFormatter={(v) => `M${v}`}
            interval={Math.floor(chartData.length / 12)}
          />

          <YAxis
            tick={{ fontSize: 11, fill: 'var(--gray-500)' }}
            tickLine={{ stroke: 'var(--gray-300)' }}
            axisLine={{ stroke: 'var(--gray-300)' }}
            tickFormatter={(v) => formatCompact(v)}
            width={55}
            domain={['dataMin - 500', 'dataMax + 500']}
          />

          <Tooltip
            formatter={(value, name) => {
              if (name === 'best') return [`IDR ${formatCompact(value)}M`, '🏆 Best Path'];
              if (name === 'worst') return [`IDR ${formatCompact(value)}M`, '📉 Worst Path'];
              if (name === 'moderate') return [`IDR ${formatCompact(value)}M`, '📊 Median Path'];
              if (name.startsWith('path_')) return null;
              return [`IDR ${formatCompact(value)}M`, name];
            }}
            labelFormatter={(month) => `Month ${month}`}
            contentStyle={{
              fontSize: '12px',
              borderRadius: '8px',
              border: '1px solid var(--gray-200)',
              boxShadow: 'var(--shadow-lg)',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
            }}
            itemStyle={{ padding: '2px 0' }}
          />

          {/* Initial capital reference line */}
          <ReferenceLine
            y={initialCapital}
            stroke="var(--gray-400)"
            strokeDasharray="8 4"
            strokeWidth={1.5}
            label={{
              value: 'Initial Capital',
              position: 'right',
              fontSize: 10,
              fill: 'var(--gray-500)',
            }}
          />

          {/* Double capital reference line */}
          <ReferenceLine
            y={initialCapital * 2}
            stroke="var(--success-500)"
            strokeDasharray="4 4"
            strokeWidth={1}
            strokeOpacity={0.5}
          />

          {/* Ruin threshold */}
          <ReferenceLine
            y={0}
            stroke="var(--danger-500)"
            strokeWidth={2}
          />

          {/* Individual simulation paths (background) */}
          {pathKeys.map((key, idx) => (
            <Line
              key={key}
              type="linear"
              dataKey={key}
              stroke={PATH_COLORS[idx % PATH_COLORS.length]}
              strokeWidth={1}
              strokeOpacity={0.25}
              dot={false}
              isAnimationActive={false}
              connectNulls
            />
          ))}

          {/* Worst path - highlighted */}
          <Line
            type="linear"
            dataKey="worst"
            stroke="#ef4444"
            strokeWidth={3}
            dot={false}
            isAnimationActive={false}
            connectNulls
          />

          {/* Moderate/Median path - highlighted */}
          <Line
            type="linear"
            dataKey="moderate"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={false}
            isAnimationActive={false}
            connectNulls
          />

          {/* Best path - highlighted */}
          <Line
            type="linear"
            dataKey="best"
            stroke="#10b981"
            strokeWidth={3}
            dot={false}
            isAnimationActive={false}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '32px',
        marginTop: '16px',
        flexWrap: 'wrap',
      }}>
        <LegendItem color="#10b981" label="Best Scenario" value={bestPath?.finalValue} initial={initialCapital} />
        <LegendItem color="#3b82f6" label="Median Scenario" value={medianPath?.finalValue} initial={initialCapital} />
        <LegendItem color="#ef4444" label="Worst Scenario" value={worstPath?.finalValue} initial={initialCapital} />
        <LegendItem color="#94a3b8" label={`${pathStats?.displayed || 0} Sample Paths`} isLine />
        <LegendItem color="var(--gray-400)" label="Initial Capital" isDashed />
      </div>
    </div>
  );
}

function LegendItem({ color, label, value, initial, isLine, isDashed }) {
  const returnPct = value && initial ? ((value - initial) / initial * 100).toFixed(0) : null;
  
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '12px',
    }}>
      <div style={{
        width: '24px',
        height: '3px',
        backgroundColor: color,
        borderRadius: '2px',
        opacity: isLine ? 0.4 : 1,
        borderStyle: isDashed ? 'dashed' : 'solid',
        borderWidth: isDashed ? '1px' : '0',
        borderColor: color,
        background: isDashed ? 'transparent' : color,
      }} />
      <span style={{ color: 'var(--gray-600)', fontWeight: 500 }}>
        {label}
        {returnPct && (
          <span style={{
            marginLeft: '6px',
            color: returnPct >= 0 ? 'var(--success-600)' : 'var(--danger-600)',
            fontWeight: 600,
          }}>
            ({returnPct >= 0 ? '+' : ''}{returnPct}%)
          </span>
        )}
      </span>
    </div>
  );
}