import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { useDashboardStore } from '../../store/dashboardStore';

export default function RatingTrendChart({ data }) {
  const currentInterval = useDashboardStore((state) => state.trendInterval);
  const updateInterval = useDashboardStore((state) => state.updateTrendInterval);

  const formatXAxis = (tickItem) => {
    if (!tickItem) return '';
    try {
      const d = new Date(tickItem);
      if (isNaN(d.getTime())) return tickItem;
      if (currentInterval === 'daily') {
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      }
      if (currentInterval === 'monthly') {
        return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short' });
      }
      // Weekly default
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return tickItem;
    }
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#1e293b] border border-slate-700 px-3 py-2.5 rounded-xl shadow-xl">
          <p className="text-xs text-slate-400 font-semibold mb-1">
            {formatXAxis(payload[0].payload.time_bucket)}
          </p>
          <p className="text-sm font-bold text-indigo-400">
            Rating: {payload[0].value.toFixed(2)} ⭐
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between h-96">
      {/* Chart Header */}
      <div className="flex justify-between items-center mb-6 select-none">
        <div>
          <h4 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Rating Trend Over Time</h4>
          <p className="text-xs text-slate-400">Time-series average satisfaction index</p>
        </div>

        {/* Interval Buttons */}
        <div className="flex bg-slate-850 p-1 rounded-xl border border-slate-800">
          {['daily', 'weekly', 'monthly'].map((interval) => (
            <button
              key={interval}
              onClick={() => updateInterval(interval)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all duration-150 ${
                currentInterval === interval
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-650/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {interval}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Area */}
      <div className="flex-1 w-full min-h-0">
        {data && data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorRating" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis
                dataKey="time_bucket"
                tickFormatter={formatXAxis}
                stroke="#475569"
                fontSize={10}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                domain={[1, 5]}
                ticks={[1, 2, 3, 4, 5]}
                stroke="#475569"
                fontSize={10}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="avg_rating"
                stroke="#6366f1"
                strokeWidth={3}
                dot={{ r: 2, stroke: '#818cf8', strokeWidth: 1 }}
                activeDot={{ r: 6 }}
                connectNulls={true}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-xs text-slate-500">
            No trend data available for selected filter range.
          </div>
        )}
      </div>
    </div>
  );
}
