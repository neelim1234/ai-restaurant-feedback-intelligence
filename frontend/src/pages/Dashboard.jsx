import React, { useEffect, useState } from 'react';
import { useDashboardStore } from '../store/dashboardStore';
import KPICards from '../components/charts/KPICards';
import RatingTrendChart from '../components/charts/RatingTrendChart';
import ServicePieChart from '../components/charts/ServicePieChart';
import ComplaintBarChart from '../components/charts/ComplaintBarChart';
import AlertsBanner from '../components/dashboard/AlertsBanner';
import { Loader2, Sparkles } from 'lucide-react';

export default function Dashboard() {
  const store = useDashboardStore();
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const handleGenerateInsights = () => {
    store.fetchAIInsights();
    setCooldown(5); // Start 5-second cooldown
  };

  useEffect(() => {
    // Load metadata and analytics on dashboard load
    if (store.cities.length === 0) {
      store.fetchMetadata();
    }
    store.fetchAnalyticsData();
  }, []);

  const { overview, ratingTrend, complaints, distributions, loading, error, filters, aiInsights, aiLoading, aiError } = store;

  if (error) {
    return (
      <div className="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-6 text-center max-w-xl mx-auto my-12">
        <h3 className="text-lg font-bold text-rose-400 mb-2">Operational Sync Failure</h3>
        <p className="text-sm text-slate-300">{error}</p>
        <button
          onClick={() => store.fetchAnalyticsData()}
          className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-slate-100 text-xs font-bold rounded-lg transition-colors"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Alerts Notice */}
      <AlertsBanner overview={overview} filters={filters} />

      {/* KPI Cards */}
      <KPICards overview={overview} />

      {/* Main Charts Block */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RatingTrendChart data={ratingTrend} />
        <ServicePieChart data={distributions?.service_type_distribution} />
      </div>

      {/* Secondary Charts Block */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ComplaintBarChart data={complaints} />
        </div>
        
        {/* AI Insights Panel */}
        <div className="bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between select-none">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="text-sm font-bold text-slate-100 uppercase tracking-wider">AI Executive Insights</h4>
              {aiInsights && (
                <span className={`text-[10px] px-2.5 py-1 rounded-full font-bold uppercase tracking-wider ${
                  aiInsights.priority_level === 'critical' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                  aiInsights.priority_level === 'high' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                  aiInsights.priority_level === 'medium' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
                  'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                }`}>
                  Priority: {aiInsights.priority_level}
                </span>
              )}
            </div>

            {aiError && (
              <div className="bg-rose-500/10 border border-rose-500/25 p-4 rounded-xl">
                <p className="text-xs text-rose-400 font-medium">{aiError}</p>
              </div>
            )}

            {aiLoading ? (
              <div className="flex flex-col items-center justify-center py-12 space-y-3">
                <Loader2 className="h-8 w-8 text-indigo-400 animate-spin" />
                <p className="text-xs text-slate-400">Synthesizing SQL metrics via Gemini...</p>
              </div>
            ) : aiInsights ? (
              <div className="space-y-4 text-xs">
                {/* Summary */}
                <div className="bg-slate-900/60 border border-slate-850 p-4 rounded-xl">
                  <span className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider block mb-1">Executive Summary</span>
                  <p className="text-slate-300 leading-relaxed">{aiInsights.summary}</p>
                </div>

                {/* Root Causes */}
                <div className="space-y-1.5">
                  <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block">Root Causes</span>
                  <ul className="list-disc pl-4 space-y-1 text-slate-400 leading-relaxed">
                    {aiInsights.root_causes.map((rc, i) => (
                      <li key={i}>{rc}</li>
                    ))}
                  </ul>
                </div>

                {/* Recommendations */}
                <div className="space-y-1.5 pt-1.5 border-t border-slate-850">
                  <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider block">Action Plan</span>
                  <ul className="list-disc pl-4 space-y-1 text-slate-400 leading-relaxed">
                    {aiInsights.recommendations.map((rec, i) => (
                      <li key={i} className="text-slate-300">{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-center space-y-4">
                <div className="bg-indigo-500/10 p-3 rounded-2xl">
                  <Sparkles className="h-6 w-6 text-indigo-400" />
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-slate-300 font-semibold">Gemini Diagnostics Ready</p>
                  <p className="text-[11px] text-slate-500 max-w-[200px] mx-auto">Click below to generate context-aware summary and action plan.</p>
                </div>
                <button
                  onClick={handleGenerateInsights}
                  disabled={cooldown > 0}
                  className={`w-full py-2.5 rounded-xl font-bold text-xs transition-all duration-200 cursor-pointer ${
                    cooldown > 0
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-850'
                      : 'bg-indigo-600 hover:bg-indigo-700 text-slate-100 shadow-lg shadow-indigo-600/15'
                  }`}
                >
                  {cooldown > 0 ? `Rate Limited (${cooldown}s)` : 'Generate AI Insights'}
                </button>
              </div>
            )}
          </div>
          
          {aiInsights && (
            <button
              onClick={handleGenerateInsights}
              disabled={cooldown > 0 || aiLoading}
              className={`mt-4 w-full py-2 rounded-xl font-bold text-xs transition-all duration-200 cursor-pointer ${
                cooldown > 0
                  ? 'bg-slate-850 text-slate-500 cursor-not-allowed border border-slate-850'
                  : 'bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300'
              }`}
            >
              {cooldown > 0 ? `Cooldown (${cooldown}s)` : 'Recalculate Insights'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
