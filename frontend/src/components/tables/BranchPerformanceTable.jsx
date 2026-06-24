import React, { useState } from 'react';
import { Search, ArrowUpDown, ChevronUp, ChevronDown } from 'lucide-react';

export default function BranchPerformanceTable({ data }) {
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState('avg_rating');
  const [sortAsc, setSortAsc] = useState(false); // Default: descending for ratings

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      // default ratings/reviews desc, names asc
      setSortAsc(field === 'branch_name' || field === 'brand_name' || field === 'city');
    }
  };

  // Filter local data based on search bar
  const getFilteredData = () => {
    if (!data) return [];
    
    let result = [...data];

    // Apply Search
    if (search.trim() !== '') {
      const q = search.toLowerCase();
      result = result.filter(
        (r) =>
          r.branch_name.toLowerCase().includes(q) ||
          r.brand_name.toLowerCase().includes(q) ||
          r.city.toLowerCase().includes(q)
      );
    }

    // Apply Sort
    result.sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];

      // Handle nulls
      if (valA === null || valA === undefined) return sortAsc ? -1 : 1;
      if (valB === null || valB === undefined) return sortAsc ? 1 : -1;

      if (typeof valA === 'string') {
        return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      } else {
        return sortAsc ? valA - valB : valB - valA;
      }
    });

    return result;
  };

  const filteredData = getFilteredData();

  const SortHeader = ({ field, label }) => {
    const isActive = sortField === field;
    return (
      <th
        onClick={() => handleSort(field)}
        className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-400 cursor-pointer hover:bg-slate-800/40 select-none transition-colors"
      >
        <div className="flex items-center gap-1.5">
          <span>{label}</span>
          {isActive ? (
            sortAsc ? (
              <ChevronUp className="h-3.5 w-3.5 text-indigo-400" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5 text-indigo-400" />
            )
          ) : (
            <ArrowUpDown className="h-3 w-3 text-slate-600" />
          )}
        </div>
      </th>
    );
  };

  return (
    <div className="bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-6 flex flex-col h-full">
      {/* Header and Search Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 select-none">
        <div>
          <h4 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Branch Performance League</h4>
          <p className="text-xs text-slate-400">Ranked listing of store performances across locations</p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-72">
          <input
            type="text"
            placeholder="Search branches, brands, cities..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#1e293b] border border-slate-800 text-slate-200 text-xs px-9 py-2.5 rounded-xl focus:border-indigo-500 outline-none placeholder:text-slate-500"
          />
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
        </div>
      </div>

      {/* Table Container */}
      <div className="flex-1 overflow-x-auto min-h-0 border border-slate-850 rounded-xl">
        <table className="min-w-full divide-y divide-slate-850">
          <thead className="bg-[#0b0f19]/80 backdrop-blur-sm sticky top-0 z-10">
            <tr>
              <SortHeader field="branch_name" label="Branch" />
              <SortHeader field="brand_name" label="Brand" />
              <SortHeader field="city" label="City" />
              <SortHeader field="avg_rating" label="Avg Rating" />
              <SortHeader field="review_count" label="Reviews" />
              <SortHeader field="avg_wait_time" label="Avg Wait" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-850/60 bg-transparent text-sm text-slate-300">
            {filteredData.length > 0 ? (
              filteredData.map((row, index) => (
                <tr key={index} className="hover:bg-slate-800/10 transition-colors">
                  <td className="px-6 py-4 font-semibold text-slate-200">{row.branch_name}</td>
                  <td className="px-6 py-4">{row.brand_name}</td>
                  <td className="px-6 py-4">{row.city}</td>
                  <td className="px-6 py-4 font-semibold text-indigo-400">
                    {row.avg_rating !== null ? `${row.avg_rating.toFixed(2)} ⭐` : 'N/A'}
                  </td>
                  <td className="px-6 py-4">{row.review_count.toLocaleString()}</td>
                  <td className="px-6 py-4 text-cyan-400">
                    {row.avg_wait_time !== null ? `${row.avg_wait_time.toFixed(1)} mins` : 'N/A'}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-xs text-slate-500">
                  No matching branches found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
