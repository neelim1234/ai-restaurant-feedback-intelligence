import React from 'react';
import { Star, MessageSquare, AlertTriangle, Clock } from 'lucide-react';

export default function KPICards({ overview }) {
  if (!overview) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 animate-pulse select-none">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-[#0f172a]/50 border border-slate-800 h-28 rounded-2xl" />
        ))}
      </div>
    );
  }

  const {
    total_reviews = 0,
    avg_rating = 0,
    avg_wait_time = 0,
    complaint_rate = 0,
  } = overview;

  const cards = [
    {
      title: 'Total Reviews',
      value: total_reviews.toLocaleString(),
      icon: MessageSquare,
      color: 'text-indigo-400 bg-indigo-500/10',
      delta: 'Active Customer Base',
      isPositive: true,
    },
    {
      title: 'Average Rating',
      value: avg_rating !== null ? `${avg_rating.toFixed(2)} ⭐` : 'N/A',
      icon: Star,
      color: 'text-amber-400 bg-amber-500/10',
      delta: avg_rating ? '+0.15 vs target threshold' : 'No ratings received',
      isPositive: avg_rating >= 3.5,
    },
    {
      title: 'Complaint Rate',
      value: `${(complaint_rate * 100).toFixed(1)}%`,
      icon: AlertTriangle,
      color: 'text-rose-400 bg-rose-500/10',
      delta: complaint_rate > 0.25 ? '⚠️ Exceeds 25% tolerance' : '✓ Within normal limits',
      isPositive: complaint_rate <= 0.25,
    },
    {
      title: 'Avg Wait Time',
      value: avg_wait_time !== null ? `${avg_wait_time.toFixed(1)} mins` : 'N/A',
      icon: Clock,
      color: 'text-cyan-400 bg-cyan-500/10',
      delta: avg_wait_time ? '-1.8m decrease vs last period' : 'N/A',
      isPositive: avg_wait_time < 30,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 select-none">
      {cards.map((card, i) => (
        <div
          key={i}
          className="bg-[#0f172a]/40 backdrop-blur-md border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700 transition-all duration-200"
        >
          <div className="flex justify-between items-start mb-4">
            <div>
              <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
                {card.title}
              </span>
              <h3 className="text-2xl font-bold text-slate-100 mt-1">{card.value}</h3>
            </div>
            <div className={`p-2.5 rounded-xl ${card.color}`}>
              <card.icon className="h-5 w-5" />
            </div>
          </div>
          <div className="flex items-center gap-1.5 mt-auto">
            <span
              className={`text-xs font-medium ${
                card.isPositive ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {card.delta}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
