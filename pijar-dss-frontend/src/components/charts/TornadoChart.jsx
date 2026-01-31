/**
 * Tornado diagram for sensitivity analysis
 * Shows impact of each parameter on outcome
 */

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
} from 'recharts';

export function TornadoChart({ data, baseValue = 0 }) {
  if (!data || data.length === 0) {
    return (
      <div style={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--gray-400)',
        fontSize: '14px',
      }}>
        No sensitivity data available
      </div>
    );
  }

  // Transform and sort data by swing (impact)
  const chartData = data
    .slice(0, 8)
    .map(item => ({
      name: item.display_name || item.parameter,
      parameter: item.parameter,
      low: item.output_at_low - item.output_at_base,
      high: item.output_at_high - item.output_at_base,
      swing: Math.abs(item.swing || (item.output_at_high - item.output_at_low)),
      lowLabel: `${item.low_value}`,
      highLabel: `${item.high_value}`,
      baseValue: item.output_at_base,
    }))
    .sort((a, b) => b.swing - a.swing);

  // Find max range for symmetric axis
  const maxRange = Math.max(
    ...chartData.map(d => Math.max(Math.abs(d.low), Math.abs(d.high)))
  );

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Chart */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 10, right: 10, left: 10, bottom: 10 }}
          >
            <XAxis
              type="number"
              domain={[-maxRange * 1.1, maxRange * 1.1]}
              tick={{ fontSize: 10, fill: 'var(--gray-500)' }}
              tickLine={false}
              axisLine={{ stroke: 'var(--gray-300)' }}
              tickFormatter={(v) => `${v > 0 ? '+' : ''}${v.toFixed(0)}%`}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fontSize: 11, fill: 'var(--gray-700)', fontWeight: 500 }}
              tickLine={false}
              axisLine={false}
              width={105}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload[0]) return null;
                const data = payload[0].payload;
                return (
                  <div style={{
                    backgroundColor: 'white',
                    border: '1px solid var(--gray-200)',
                    borderRadius: '8px',
                    padding: '12px',
                    boxShadow: 'var(--shadow-lg)',
                    fontSize: '12px',
                  }}>
                    <div style={{ fontWeight: 600, marginBottom: '8px', color: 'var(--gray-800)' }}>
                      {data.name}
                    </div>
                    <div style={{ display: 'grid', gap: '4px' }}>
                      <div style={{ color: '#ef4444' }}>
                        ↓ Pessimistic: {data.low > 0 ? '+' : ''}{data.low.toFixed(1)}% impact
                      </div>
                      <div style={{ color: '#10b981' }}>
                        ↑ Optimistic: {data.high > 0 ? '+' : ''}{data.high.toFixed(1)}% impact
                      </div>
                      <div style={{ color: 'var(--gray-500)', marginTop: '4px', borderTop: '1px solid var(--gray-100)', paddingTop: '4px' }}>
                        Total swing: {data.swing.toFixed(0)}% range
                      </div>
                    </div>
                  </div>
                );
              }}
            />
            
            {/* Center reference line */}
            <ReferenceLine x={0} stroke="var(--gray-400)" strokeWidth={1.5} />

            {/* Negative impact bar */}
            <Bar 
              dataKey="low" 
              fill="#ef4444"
              radius={[4, 0, 0, 4]}
              barSize={20}
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`low-${index}`}
                  fill={entry.low < 0 ? '#ef4444' : '#10b981'}
                  fillOpacity={0.85}
                />
              ))}
            </Bar>

            {/* Positive impact bar */}
            <Bar 
              dataKey="high" 
              fill="#10b981"
              radius={[0, 4, 4, 0]}
              barSize={20}
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`high-${index}`}
                  fill={entry.high > 0 ? '#10b981' : '#ef4444'}
                  fillOpacity={0.85}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '24px',
        marginTop: '8px',
        paddingTop: '8px',
        borderTop: '1px solid var(--gray-100)',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '11px',
          color: 'var(--gray-600)',
        }}>
          <div style={{
            width: '14px',
            height: '10px',
            backgroundColor: '#ef4444',
            borderRadius: '2px',
          }} />
          Pessimistic scenario
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '11px',
          color: 'var(--gray-600)',
        }}>
          <div style={{
            width: '14px',
            height: '10px',
            backgroundColor: '#10b981',
            borderRadius: '2px',
          }} />
          Optimistic scenario
        </div>
      </div>
    </div>
  );
}