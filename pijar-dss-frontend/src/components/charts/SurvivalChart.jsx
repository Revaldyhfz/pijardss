/**
 * Survival curve visualization
 */

import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from 'recharts';

export function SurvivalChart({ data }) {
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

  const chartData = data.map((survival, month) => ({
    month,
    survival: survival * 100,
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="survivalGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#10b981" stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--gray-200)" />
        <XAxis
          dataKey="month"
          tick={{ fontSize: 10, fill: 'var(--gray-500)' }}
          tickLine={false}
          axisLine={{ stroke: 'var(--gray-300)' }}
          tickFormatter={(v) => `M${v}`}
        />
        <YAxis
          domain={[0, 100]}
          tick={{ fontSize: 10, fill: 'var(--gray-500)' }}
          tickLine={false}
          axisLine={{ stroke: 'var(--gray-300)' }}
          tickFormatter={(v) => `${v}%`}
          width={40}
        />
        <Tooltip
          formatter={(value) => [`${value.toFixed(1)}%`, 'Survival Rate']}
          labelFormatter={(month) => `Month ${month}`}
          contentStyle={{
            fontSize: '12px',
            borderRadius: '8px',
            border: '1px solid var(--gray-200)',
          }}
        />
        <ReferenceLine y={50} stroke="var(--gray-400)" strokeDasharray="4 4" />
        <Area
          type="monotone"
          dataKey="survival"
          stroke="#10b981"
          strokeWidth={2}
          fill="url(#survivalGradient)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}