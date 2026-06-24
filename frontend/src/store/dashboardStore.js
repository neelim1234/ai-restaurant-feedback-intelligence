import { create } from 'zustand';
import { api } from '../services/api';

const parseFiltersFromUrl = () => {
  const searchParams = new URLSearchParams(window.location.search);
  
  const getInt = (key) => {
    const val = searchParams.get(key);
    return val ? parseInt(val, 10) : undefined;
  };
  
  const getStr = (key) => {
    const val = searchParams.get(key);
    return val || undefined;
  };
  
  return {
    city_id: getInt('city_id'),
    branch_id: getInt('branch_id'),
    brand_id: getInt('brand_id'),
    ordered_cuisine: getStr('ordered_cuisine'),
    service_type: getStr('service_type'),
    min_rating: getInt('min_rating'),
    max_rating: getInt('max_rating'),
    start_date: getStr('start_date'),
    end_date: getStr('end_date'),
    price_segment: getStr('price_segment'),
  };
};

const syncFiltersToUrl = (filters) => {
  const url = new URL(window.location.href);
  const searchParams = url.searchParams;
  
  // Sync each filter to URL query parameters
  Object.entries(filters).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== '') {
      searchParams.set(key, val.toString());
    } else {
      searchParams.delete(key);
    }
  });
  
  window.history.replaceState({}, '', `${url.pathname}${url.search}`);
};

let debounceTimeout = null;
let activeAbortController = null;

export const useDashboardStore = create((set, get) => ({
  // State
  filters: parseFiltersFromUrl(),
  
  cities: [],
  brands: [],
  branches: [],
  cuisines: [],
  
  overview: null,
  ratingTrend: [],
  branchPerformance: [],
  complaints: null,
  distributions: null,
  
  trendInterval: 'weekly', // daily, weekly, monthly
  
  loading: false,
  metadataLoading: false,
  error: null,

  // AI Insights State
  aiInsights: null,
  aiLoading: false,
  aiError: null,


  // Actions
  updateFilters: (newFilters) => {
    const currentFilters = get().filters;
    const updated = { ...currentFilters, ...newFilters };
    
    // Clean up empty keys
    Object.keys(updated).forEach(k => {
      if (updated[k] === '' || updated[k] === null || updated[k] === undefined) {
        delete updated[k];
      }
    });

    set({ filters: updated, aiInsights: null, aiError: null });
    syncFiltersToUrl(updated);
    
    // Trigger debounced analytics fetch
    get().triggerDebouncedFetch();
  },
  
  resetFilters: () => {
    set({ filters: {}, aiInsights: null, aiError: null });
    syncFiltersToUrl({});
    get().triggerDebouncedFetch();
  },

  updateTrendInterval: (interval) => {
    set({ trendInterval: interval });
    get().triggerDebouncedFetch();
  },

  triggerDebouncedFetch: () => {
    if (debounceTimeout) {
      clearTimeout(debounceTimeout);
    }
    debounceTimeout = setTimeout(() => {
      get().fetchAnalyticsData();
    }, 300); // 300ms debounce
  },

  fetchMetadata: async () => {
    set({ metadataLoading: true });
    try {
      const [cities, brands, cuisines] = await Promise.all([
        api.getCities(),
        api.getBrands(),
        api.getCuisines(),
      ]);
      
      // Load all branches initially for dropdown selectors
      const branches = await api.getBranches();
      
      set({ 
        cities, 
        brands, 
        cuisines, 
        branches,
        metadataLoading: false 
      });
    } catch (err) {
      console.error("Error loading lookup metadata:", err);
      set({ metadataLoading: false });
    }
  },

  fetchAnalyticsData: async () => {
    // Abort any in-flight requests to prevent race conditions
    if (activeAbortController) {
      activeAbortController.abort();
    }
    activeAbortController = new AbortController();
    const signal = activeAbortController.signal;

    set({ loading: true, error: null });
    try {
      const filters = get().filters;
      const interval = get().trendInterval;
      
      // Filter out undefined and null values
      const cleanedParams = {};
      Object.entries(filters).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') {
          cleanedParams[k] = v;
        }
      });

      // Concurrent fetch for all analytics endpoints passing the signal
      const [overview, ratingTrend, branchPerformance, complaints, distributions] = await Promise.all([
        api.getOverview(cleanedParams, { signal }),
        api.getRatingTrend(interval, cleanedParams, { signal }),
        api.getBranchPerformance(cleanedParams, { signal }),
        api.getComplaints(cleanedParams, { signal }),
        api.getDistributions(cleanedParams, { signal }),
      ]);

      set({
        overview,
        ratingTrend,
        branchPerformance,
        complaints,
        distributions,
        loading: false,
      });
    } catch (err) {
      // Check if it is a cancel/abort error and ignore it
      if (err.name === 'CanceledError' || err.name === 'AbortError' || (err.message && err.message.includes('canceled'))) {
        return;
      }
      console.error("Error fetching analytics data:", err);
      set({ 
        error: "Failed to load dashboard data. Please make sure the backend server is running at http://localhost:8000.",
        loading: false 
      });
    }
  },

  fetchAIInsights: async () => {
    set({ aiLoading: true, aiError: null });
    try {
      const filters = get().filters;
      const cleanedParams = {};
      Object.entries(filters).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') {
          cleanedParams[k] = v;
        }
      });
      
      const insights = await api.getAIInsights(cleanedParams);
      set({ aiInsights: insights, aiLoading: false });
    } catch (err) {
      console.error("Error generating AI insights:", err);
      const errorMsg = err.response?.data?.detail || "Failed to generate AI insights. Please retry in a moment.";
      set({ aiError: errorMsg, aiLoading: false });
    }
  },

  clearAIInsights: () => {
    set({ aiInsights: null, aiError: null });
  }
}));
