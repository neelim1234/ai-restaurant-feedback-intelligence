import React from 'react';
import { AlertCircle, TrendingDown, Clock, ShieldAlert } from 'lucide-react';

export default function AlertsBanner({ overview, filters }) {
  if (!overview) return null;

  const { avg_rating = 0, avg_wait_time = 0, complaint_rate = 0 } = overview;
  const alerts = [];

  // Check filters context to customize alert titles
  const locationLabel = filters?.city_id === 1 ? 'Mumbai' : 'Global';

  // 1. Mumbai satisfaction alert (Specific requirement!)
  if (filters?.city_id === 1 && avg_rating < 3.5) {
    alerts.push({
      id: 'mumbai-sat',
      type: 'critical',
      message: '⚠️ Mumbai satisfaction below target: High concentration of late delivery complaints.',
      icon: ShieldAlert,
      color: 'bg-rose-500/10 border-rose-500/20 text-rose-400',
    });
  }

  // 2. Rating Threshold
  if (avg_rating !== null && avg_rating < 3.4) {
    alerts.push({
      id: 'low-sat',
      type: 'warning',
      message: `Satisfaction drop: ${locationLabel} average rating has dipped to ${avg_rating.toFixed(2)} ⭐.`,
      icon: TrendingDown,
      color: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
    });
  }

  // 3. Complaint threshold
  if (complaint_rate > 0.25) {
    alerts.push({
      id: 'high-complaints',
      type: 'critical',
      message: `Operational alert: ${locationLabel} customer complaint rate is elevated at ${(complaint_rate * 100).toFixed(1)}%.`,
      icon: ShieldAlert,
      color: 'bg-rose-500/10 border-rose-500/20 text-rose-400',
    });
  }

  // 4. Wait time threshold
  if (avg_wait_time !== null && avg_wait_time > 35) {
    alerts.push({
      id: 'slow-delivery',
      type: 'warning',
      message: `Service bottleneck: Average customer wait time is high at ${avg_wait_time.toFixed(1)} mins.`,
      icon: Clock,
      color: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
    });
  }

  if (alerts.length === 0) {
    return (
      <div className="bg-emerald-500/5 border border-emerald-500/10 px-4 py-3.5 rounded-2xl flex items-center gap-3 text-emerald-400 text-sm select-none">
        <AlertCircle className="h-4.5 w-4.5 shrink-0" />
        <span>All system metrics are operational. Satisfaction benchmarks are on target.</span>
      </div>
    );
  }

  return (
    <div className="space-y-3 select-none">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`px-4 py-3.5 rounded-2xl border flex items-center gap-3 text-sm transition-all duration-200 ${alert.color}`}
        >
          <alert.icon className="h-4.5 w-4.5 shrink-0" />
          <span className="font-medium">{alert.message}</span>
        </div>
      ))}
    </div>
  );
}
