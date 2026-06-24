import React, { useEffect } from 'react';
import { useDashboardStore } from '../store/dashboardStore';
import BranchPerformanceTable from '../components/tables/BranchPerformanceTable';

export default function BranchAnalytics() {
  const store = useDashboardStore();

  useEffect(() => {
    // Refresh data on mount
    store.fetchAnalyticsData();
  }, []);

  const { branchPerformance, loading, error } = store;

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
    <div className="h-full flex flex-col space-y-6">
      <div className="flex-1 min-h-[500px]">
        <BranchPerformanceTable data={branchPerformance} />
      </div>
    </div>
  );
}
