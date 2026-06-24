import React, { useEffect, useState } from 'react';
import { useDashboardStore } from '../store/dashboardStore';
import FilterBar from '../components/filters/FilterBar';
import KPICards from '../components/charts/KPICards';
import RatingTrendChart from '../components/charts/RatingTrendChart';
import ComplaintBarChart from '../components/charts/ComplaintBarChart';
import { api } from '../services/api';
import { Loader2, Copy, Check, MessageSquare } from 'lucide-react';

export default function Insights() {
  const store = useDashboardStore();

  useEffect(() => {
    // Sync metadata lookups and execute analytics fetch
    if (store.cities.length === 0) {
      store.fetchMetadata();
    }
    store.fetchAnalyticsData();
  }, []);

  const { overview, ratingTrend, complaints, loading, error } = store;

  // Responder State
  const [reviewText, setReviewText] = useState('');
  const [rating, setRating] = useState(5);
  const [draftResponse, setDraftResponse] = useState('');
  const [responderLoading, setResponderLoading] = useState(false);
  const [responderError, setResponderError] = useState('');
  const [cooldown, setCooldown] = useState(0);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const handleGenerateResponse = async () => {
    if (!reviewText.trim()) return;
    setResponderLoading(true);
    setResponderError('');
    setDraftResponse('');
    setCooldown(5); // Start 5-second cooldown

    try {
      const result = await api.generateAIResponse(reviewText, rating);
      setDraftResponse(result.response);
    } catch (err) {
      console.error("Error generating draft response:", err);
      const msg = err.response?.data?.detail || "Failed to generate draft response. Please try again.";
      setResponderError(msg);
    } finally {
      setResponderLoading(false);
    }
  };

  const handleCopy = () => {
    if (!draftResponse) return;
    navigator.clipboard.writeText(draftResponse);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Global Filter Bar */}
      <FilterBar />

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-6 text-center max-w-xl mx-auto">
          <p className="text-sm text-rose-400 font-semibold">{error}</p>
        </div>
      )}

      {/* Main Results Container */}
      <div className={`space-y-6 transition-opacity duration-300 ${loading ? 'opacity-40 pointer-events-none' : 'opacity-100'}`}>
        {/* KPI metrics */}
        <KPICards overview={overview} />

        {/* AI Review Response Generator Card */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-6 select-none flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4.5 w-4.5 text-indigo-400" />
                <h4 className="text-sm font-bold text-slate-100 uppercase tracking-wider">AI Review Responder</h4>
              </div>
              <p className="text-xs text-slate-400">Generate empathy-focused guest relations drafts adaptive to customer ratings.</p>
              
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="sm:col-span-3 flex flex-col gap-1.5">
                  <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Review Content</label>
                  <textarea
                    placeholder="Paste customer review here... (e.g., 'Delivery took 55 minutes and food was cold')"
                    value={reviewText}
                    onChange={(e) => setReviewText(e.target.value)}
                    className="bg-[#1e293b] border border-slate-800 text-slate-200 text-xs px-3.5 py-3 rounded-xl focus:border-indigo-500 outline-none h-20 resize-none placeholder:text-slate-500"
                  />
                </div>
                <div className="flex flex-col gap-1.5 justify-between">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Rating</label>
                    <select
                      value={rating}
                      onChange={(e) => setRating(parseInt(e.target.value, 10))}
                      className="bg-[#1e293b] border border-slate-800 text-slate-200 text-xs px-3 py-3 rounded-xl focus:border-indigo-500 outline-none w-full cursor-pointer"
                    >
                      {[5, 4, 3, 2, 1].map(r => (
                        <option key={r} value={r}>{r} Star{r !== 1 ? 's' : ''}</option>
                      ))}
                    </select>
                  </div>
                  <button
                    onClick={handleGenerateResponse}
                    disabled={cooldown > 0 || !reviewText.trim()}
                    className={`w-full py-3 rounded-xl font-bold text-xs transition-all duration-200 cursor-pointer ${
                      cooldown > 0 || !reviewText.trim()
                        ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-850'
                        : 'bg-indigo-600 hover:bg-indigo-700 text-slate-100 shadow-lg shadow-indigo-600/15'
                    }`}
                  >
                    {cooldown > 0 ? `Rate Limit (${cooldown}s)` : 'Draft Reply'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between select-none">
            <div className="flex justify-between items-center mb-3">
              <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Draft Output</h5>
              {draftResponse && (
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 text-[10px] text-slate-400 hover:text-slate-100 transition-colors border border-slate-800 px-2 py-1 rounded-lg hover:border-slate-700 cursor-pointer"
                >
                  {copied ? (
                    <>
                      <Check className="h-3 w-3 text-emerald-400" />
                      <span className="text-emerald-400">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              )}
            </div>

            {responderError && (
              <div className="bg-rose-500/10 border border-rose-500/20 p-3 rounded-xl flex-1 flex items-center justify-center">
                <p className="text-[11px] text-rose-400 text-center">{responderError}</p>
              </div>
            )}

            {responderLoading ? (
              <div className="flex flex-col items-center justify-center flex-1 py-6 space-y-2">
                <Loader2 className="h-6 w-6 text-indigo-400 animate-spin" />
                <p className="text-[11px] text-slate-400">Consulting Guest Relations Advisor...</p>
              </div>
            ) : draftResponse ? (
              <div className="bg-slate-900/60 border border-slate-850 p-4 rounded-xl flex-1 flex flex-col justify-center">
                <p className="text-xs text-slate-300 italic leading-relaxed font-serif">"{draftResponse}"</p>
              </div>
            ) : !responderError && (
              <div className="flex items-center justify-center flex-1 border border-dashed border-slate-850 rounded-xl py-8">
                <p className="text-[11px] text-slate-500 max-w-[150px] text-center leading-relaxed">Generated reply will appear here after clicking Draft Reply.</p>
              </div>
            )}
          </div>
        </div>

        {/* Dynamic Aggregations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RatingTrendChart data={ratingTrend} />
          <ComplaintBarChart data={complaints} />
        </div>
      </div>
    </div>
  );
}

