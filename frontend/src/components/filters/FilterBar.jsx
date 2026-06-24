import React, { useEffect } from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { X, Filter } from 'lucide-react';

export default function FilterBar() {
  const store = useDashboardStore();

  useEffect(() => {
    // Load metadata lookups once on filter mount
    if (store.cities.length === 0) {
      store.fetchMetadata();
    }
  }, []);

  const {
    filters,
    cities,
    brands,
    branches,
    cuisines,
    updateFilters,
    resetFilters,
  } = store;

  // Filter branches locally based on selected city/brand to provide correct contextual selections
  const filteredBranches = branches.filter((branch) => {
    if (filters.city_id && branch.city_id !== filters.city_id) return false;
    if (filters.brand_id && branch.brand_id !== filters.brand_id) return false;
    return true;
  });

  const handleSelectChange = (key, value, isInt = false) => {
    const val = value === '' ? undefined : (isInt ? parseInt(value, 10) : value);
    updateFilters({ [key]: val });
  };

  const handleDateChange = (key, value) => {
    updateFilters({ [key]: value || undefined });
  };

  const hasActiveFilters = Object.values(filters).some(v => v !== undefined && v !== null && v !== '');

  return (
    <div className="bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-6 select-none">
      {/* Header */}
      <div className="flex justify-between items-center mb-5 border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <Filter className="h-4.5 w-4.5 text-indigo-400" />
          <h4 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Analytics Query Filters</h4>
        </div>
        {hasActiveFilters && (
          <button
            onClick={resetFilters}
            className="flex items-center gap-1.5 px-3 py-1 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-semibold rounded-lg transition-colors border border-rose-500/20"
          >
            <X className="h-3.5 w-3.5" />
            <span>Reset Filters</span>
          </button>
        )}
      </div>

      {/* Grid Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
        {/* City Filter */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">City</label>
          <select
            value={filters.city_id || ''}
            onChange={(e) => handleSelectChange('city_id', e.target.value, true)}
            className="bg-[#1e293b] border border-slate-800 text-slate-200 text-sm px-3 py-2 rounded-xl focus:border-indigo-500 outline-none w-full"
          >
            <option value="">All Cities</option>
            {cities.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        {/* Brand Filter */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Brand</label>
          <select
            value={filters.brand_id || ''}
            onChange={(e) => handleSelectChange('brand_id', e.target.value, true)}
            className="bg-[#1e293b] border border-slate-800 text-slate-200 text-sm px-3 py-2 rounded-xl focus:border-indigo-500 outline-none w-full"
          >
            <option value="">All Brands</option>
            {brands.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>
        </div>

        {/* Branch Filter */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Branch</label>
          <select
            value={filters.branch_id || ''}
            onChange={(e) => handleSelectChange('branch_id', e.target.value, true)}
            className="bg-[#1e293b] border border-slate-800 text-slate-200 text-sm px-3 py-2 rounded-xl focus:border-indigo-500 outline-none w-full"
          >
            <option value="">All Branches</option>
            {filteredBranches.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>
        </div>

        {/* Cuisine Filter */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Cuisine Ordered</label>
          <select
            value={filters.ordered_cuisine || ''}
            onChange={(e) => handleSelectChange('ordered_cuisine', e.target.value)}
            className="bg-[#1e293b] border border-slate-800 text-slate-200 text-sm px-3 py-2 rounded-xl focus:border-indigo-500 outline-none w-full"
          >
            <option value="">All Cuisines</option>
            {cuisines.map((c) => (
              <option key={c.name} value={c.name}>{c.name}</option>
            ))}
          </select>
        </div>

        {/* Service Type */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Service Channel</label>
          <select
            value={filters.service_type || ''}
            onChange={(e) => handleSelectChange('service_type', e.target.value)}
            className="bg-[#1e293b] border border-slate-800 text-slate-200 text-sm px-3 py-2 rounded-xl focus:border-indigo-500 outline-none w-full"
          >
            <option value="">All Channels</option>
            <option value="delivery">Delivery</option>
            <option value="dine-in">Dine-in</option>
            <option value="takeaway">Takeaway</option>
          </select>
        </div>

        {/* Price Segment */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Price Segment</label>
          <select
            value={filters.price_segment || ''}
            onChange={(e) => handleSelectChange('price_segment', e.target.value)}
            className="bg-[#1e293b] border border-slate-800 text-slate-200 text-sm px-3 py-2 rounded-xl focus:border-indigo-500 outline-none w-full"
          >
            <option value="">All Segments</option>
            <option value="budget">Budget</option>
            <option value="mid-range">Mid-range</option>
            <option value="premium">Premium</option>
          </select>
        </div>

        {/* Rating Clamps */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Min Rating</label>
          <select
            value={filters.min_rating || ''}
            onChange={(e) => handleSelectChange('min_rating', e.target.value, true)}
            className="bg-[#1e293b] border border-slate-800 text-slate-200 text-sm px-3 py-2 rounded-xl focus:border-indigo-500 outline-none w-full"
          >
            <option value="">1 Star</option>
            {[2, 3, 4, 5].map(r => (
              <option key={r} value={r}>{r} Stars</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Max Rating</label>
          <select
            value={filters.max_rating || ''}
            onChange={(e) => handleSelectChange('max_rating', e.target.value, true)}
            className="bg-[#1e293b] border border-slate-800 text-slate-200 text-sm px-3 py-2 rounded-xl focus:border-indigo-500 outline-none w-full"
          >
            <option value="">5 Stars</option>
            {[4, 3, 2, 1].map(r => (
              <option key={r} value={r}>{r} Stars</option>
            ))}
          </select>
        </div>

        {/* Start Date */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Start Date</label>
          <input
            type="date"
            value={filters.start_date || ''}
            onChange={(e) => handleDateChange('start_date', e.target.value)}
            className="bg-[#1e293b] border border-slate-800 text-slate-200 text-sm px-3 py-2 rounded-xl focus:border-indigo-500 outline-none w-full cursor-pointer"
          />
        </div>

        {/* End Date */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">End Date</label>
          <input
            type="date"
            value={filters.end_date || ''}
            onChange={(e) => handleDateChange('end_date', e.target.value)}
            className="bg-[#1e293b] border border-slate-800 text-slate-200 text-sm px-3 py-2 rounded-xl focus:border-indigo-500 outline-none w-full cursor-pointer"
          />
        </div>
      </div>
    </div>
  );
}
