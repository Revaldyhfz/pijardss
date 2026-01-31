/**
 * Return distribution histogram with context and annotations
 */

import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
} from 'recharts';

export function ReturnDistChart({ data, summary }) {
  // Calculate statistics for context
  const stats = useMemo(() => {
    if (!data || data.length === 0) return null;
    
    const totalCount = data.reduce((sum, d) => sum + (d.count || 0), 0);
    const profitableCount = data
      .filter(d => d.range_start >= 0)
      .reduce((sum, d) => sum + (d.count || 0), 0);
    const lossCount = totalCount - profitableCount;
    
    return {
      total: totalCount,
      profitable: profitableCount,
      loss: lossCount,
      profitPct: (profitableCount / totalCount * 100).toFixed(0),
      lossPct: (lossCount / totalCount * 100).toFixed(0),
    };
  }, [data]);

  if (!data || data.length === 0) {
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

  // Find key percentiles for annotation
  const meanReturn = summary?.return_mean || 0;
  const medianReturn = summary?.return_median || 0;

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Context Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        marginBottom: '12px',
        padding: '10px 12px',
        backgroundColor: 'var(--gray-50)',
        borderRadius: 'var(--radius-md)',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontSize: '16px',
            fontWeight: 700,
            color: meanReturn >= 0 ? 'var(--success-600)' : 'var(--danger-600)',
          }}>
            {meanReturn >= 0 ? '+' : ''}{meanReturn?.toFixed(0)}%
          </div>
          <div style={{ fontSize: '10px', color: 'var(--gray-500)' }}>Mean</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontSize: '16px',
            fontWeight: 700,
            color: medianReturn >= 0 ? 'var(--success-600)' : 'var(--danger-600)',
          }}>
            {medianReturn >= 0 ? '+' : ''}{medianReturn?.toFixed(0)}%
          </div>
          <div style={{ fontSize: '10px', color: 'var(--gray-500)' }}>Median</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontSize: '16px',
            fontWeight: 700,
            color: 'var(--success-600)',
          }}>
            {stats?.profitPct}%
          </div>
          <div style={{ fontSize: '10px', color: 'var(--gray-500)' }}>Win Rate</div>
        </div>
      </div>

      {/* Chart */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="var(--gray-200)" 
              vertical={false}
            />
            <XAxis
              dataKey="range_start"
              tick={{ fontSize: 10, fill: 'var(--gray-500)' }}
              tickLine={false}
              axisLine={{ stroke: 'var(--gray-300)' }}
              tickFormatter={(v) => `${v}%`}
              interval={1}
            />
            <YAxis
              tick={{ fontSize: 10, fill: 'var(--gray-500)' }}
              tickLine={false}
              axisLine={{ stroke: 'var(--gray-300)' }}
              tickFormatter={(v) => `${v.toFixed(0)}%`}
              width={35}
            />
            <Tooltip
              formatter={(value, name, props) => {
                const start = props.payload.range_start;
                const end = start + 50;
                return [
                  `${value.toFixed(1)}% of simulations`,
                  `Return: ${start}% to ${end}%`
                ];
              }}
              contentStyle={{
                fontSize: '12px',
                borderRadius: '8px',
                border: '1px solid var(--gray-200)',
                boxShadow: 'var(--shadow-md)',
              }}
            />
            
            {/* Break-even reference line */}
            <ReferenceLine 
              x={0} 
              stroke="var(--gray-500)" 
              strokeDasharray="4 4"
              strokeWidth={2}
              label={{
                value: 'Break-even',
                position: 'top',
                fontSize: 10,
                fill: 'var(--gray-500)',
              }}
            />
            
            {/* 2x return reference */}
            <ReferenceLine 
              x={100} 
              stroke="var(--success-400)" 
              strokeDasharray="4 4"
              strokeWidth={1}
              label={{
                value: '2x',
                position: 'top',
                fontSize: 9,
                fill: 'var(--success-500)',
              }}
            />

            <Bar dataKey="percentage" radius={[4, 4, 0, 0]} maxBarSize={40}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.range_start >= 0 ? '#10b981' : '#ef4444'}
                  fillOpacity={entry.range_start >= 100 ? 1 : 0.75}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend/Interpretation */}
      <div style={{
        marginTop: '8px',
        padding: '8px 10px',
        backgroundColor: meanReturn >= 50 ? 'var(--success-50)' : meanReturn >= 0 ? 'var(--primary-50)' : 'var(--warning-50)',
        borderRadius: 'var(--radius-sm)',
        fontSize: '11px',
        color: 'var(--gray-600)',
        textAlign: 'center',
      }}>
        {meanReturn >= 100 ? (
          <span><strong>Strong outlook:</strong> Average return exceeds 2x investment</span>
        ) : meanReturn >= 50 ? (
          <span><strong>Positive outlook:</strong> Most scenarios end profitably</span>
        ) : meanReturn >= 0 ? (
          <span><strong>Moderate outlook:</strong> Roughly balanced risk/reward</span>
        ) : (
          <span><strong>Caution:</strong> Negative expected return indicates high risk</span>
        )}
      </div>
    </div>
  );
}