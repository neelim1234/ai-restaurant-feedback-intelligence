import React from 'react';
import { useLocation } from 'react-router-dom';
import { useDashboardStore } from '../../store/dashboardStore';
import { RefreshCw, CloudCheck, Loader2 } from 'lucide-react';

export default function Topbar() {
  const location = useLocation();
  const loading = useDashboardStore((state) => state.loading);
  const triggerFetch = useDashboardStore((state) => state.triggerDebouncedFetch);

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/':
        return 'Executive Analytics Dashboard';
      case '/branches':
        return 'Branch Performance Rollup';
      case '/insights':
        return 'Customer Sentiment & Deep Insights';
      default:
        return 'Analytics Console';
    }
  };

  return (
    <header className="h-16 bg-[#0f172a]/40 backdrop-blur-md border-b border-slate-800 flex items-center justify-between px-8 text-slate-200 select-none">
      {/* Title */}
      <div>
        <h1 className="text-lg font-bold text-slate-100 tracking-tight">{getPageTitle()}</h1>
        <p className="text-xs text-slate-400">SpiceHub Foods Pvt Ltd</p>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        {loading ? (
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Loader2 className="h-3.5 w-3.5 animate-spin text-indigo-400" />
            <span>Syncing database...</span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 text-xs text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded-full">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
            <span>Data Synced</span>
          </div>
        )}

        <button
          onClick={triggerFetch}
          disabled={loading}
          className="p-2 hover:bg-slate-800 text-slate-400 hover:text-slate-100 rounded-lg transition-colors border border-slate-800"
          title="Force reload analytics data"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>
    </header>
  );
}
