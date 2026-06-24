import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';

const CATEGORY_MAP = {
  delivery_delay: 'Delivery Delay',
  food_quality: 'Food Quality',
  pricing: 'Pricing',
  packaging: 'Packaging',
  hygiene: 'Hygiene',
  staff_behavior: 'Staff Behavior',
  ambience: 'Ambience',
  portion_size: 'Portion Size',
};

// Vibrant color palette for complaints
const COLORS = [
  '#f87171', // red-405
  '#fb923c', // orange-400
  '#facc15', // yellow-400
  '#2dd4bf', // teal-400
  '#38bdf8', // sky-400
  '#818cf8', // indigo-400
  '#c084fc', // purple-400
  '#f472b6', // pink-400
];

export default function ComplaintBarChart({ data }) {
  // Format object {delivery_delay: 100, ...} to sorted list [{name: 'Delivery Delay', count: 100}]
  const formatData = () => {
    if (!data) return [];
    return Object.entries(data)
      .map(([key, val]) => ({
        key,
        name: CATEGORY_MAP[key] || key,
        count: val,
      }))
      .sort((a, b) => b.count - a.count); // sort descending
  };

  const formattedData = formatData();

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#1e293b] border border-slate-700 px-3 py-1.5 rounded-xl shadow-xl">
          <p className="text-xs font-bold text-slate-100">{payload[0].payload.name}</p>
          <p className="text-sm font-semibold text-rose-400 mt-0.5">
            Mentions: {payload[0].value.toLocaleString()}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between h-96">
      {/* Chart Header */}
      <div className="mb-4 select-none">
        <h4 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Complaint Breakdown (Pre-AI)</h4>
        <p className="text-xs text-slate-400">Heuristic keyword occurrence counts in review text</p>
      </div>

      {/* Chart Area */}
      <div className="flex-1 w-full min-h-0">
        {formattedData.length > 0 && formattedData.some(d => d.count > 0) ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={formattedData}
              layout="vertical"
              margin={{ top: 5, right: 10, left: 35, bottom: 5 }}
            >
              <XAxis type="number" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis
                type="category"
                dataKey="name"
                stroke="#94a3b8"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                width={85}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {formattedData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-xs text-slate-500">
            No complaints detected for the selected filter range.
          </div>
        )}
      </div>
    </div>
  );
}
