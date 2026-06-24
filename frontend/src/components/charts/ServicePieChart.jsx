import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';

const COLORS = {
  delivery: '#6366f1', // Indigo
  'dine-in': '#06b6d4',  // Cyan
  takeaway: '#3b82f6',  // Blue
};

const LABEL_MAP = {
  delivery: 'Delivery',
  'dine-in': 'Dine-in',
  takeaway: 'Takeaway',
};

export default function ServicePieChart({ data }) {
  const formatData = () => {
    if (!data) return [];
    return Object.entries(data).map(([key, val]) => ({
      name: LABEL_MAP[key] || key,
      value: val,
      color: COLORS[key] || '#94a3b8',
    }));
  };

  const formattedData = formatData();
  const total = formattedData.reduce((acc, curr) => acc + curr.value, 0);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const percentage = total > 0 ? ((payload[0].value / total) * 100).toFixed(1) : 0;
      return (
        <div className="bg-[#1e293b] border border-slate-700 px-3 py-1.5 rounded-xl shadow-xl">
          <p className="text-xs font-bold text-slate-100">{payload[0].name}</p>
          <p className="text-sm font-semibold text-slate-300 mt-0.5">
            Orders: {payload[0].value.toLocaleString()} ({percentage}%)
          </p>
        </div>
      );
    }
    return null;
  };

  const renderLegend = (value, entry) => {
    return <span className="text-xs text-slate-300 font-medium capitalize">{value}</span>;
  };

  return (
    <div className="bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between h-96">
      {/* Header */}
      <div className="mb-4 select-none">
        <h4 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Service Channels</h4>
        <p className="text-xs text-slate-400">Order distribution across service methods</p>
      </div>

      {/* Donut Chart Area */}
      <div className="flex-1 w-full min-h-0 flex items-center justify-center">
        {total > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={formattedData}
                cx="50%"
                cy="45%"
                innerRadius={55}
                outerRadius={80}
                paddingAngle={4}
                dataKey="value"
              >
                {formattedData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="bottom" 
                align="center" 
                formatter={renderLegend}
                iconType="circle"
                iconSize={8}
                wrapperStyle={{ bottom: 0 }}
              />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-xs text-slate-500">No order channel data available.</div>
        )}
      </div>
    </div>
  );
}
