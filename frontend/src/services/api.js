import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Lookups
  getCities: () => client.get('/lookup/cities').then(res => res.data),
  getBrands: () => client.get('/lookup/brands').then(res => res.data),
  getCuisines: () => client.get('/lookup/cuisines').then(res => res.data),
  getBranches: (cityId, brandId) => {
    const params = {};
    if (cityId) params.city_id = cityId;
    if (brandId) params.brand_id = brandId;
    return client.get('/lookup/branches', { params }).then(res => res.data);
  },

  // Analytics (Passes the FilterParams object directly)
  getOverview: (params, options) => client.get('/analytics/overview', { params, ...options }).then(res => res.data),
  getRatingTrend: (interval, params, options) => 
    client.get('/analytics/rating-trend', { params: { ...params, interval }, ...options }).then(res => res.data),
  getBranchPerformance: (params, options) => client.get('/analytics/branch-performance', { params, ...options }).then(res => res.data),
  getComplaints: (params, options) => client.get('/analytics/complaints', { params, ...options }).then(res => res.data),
  getDistributions: (params, options) => client.get('/analytics/distributions', { params, ...options }).then(res => res.data),

  // AI Integration (Passes filter context payload or individual review bodies)
  getAIInsights: (filters) => client.post('/ai/insights', filters).then(res => res.data),
  generateAIResponse: (reviewText, rating) => client.post('/ai/respond', { review_text: reviewText, rating }).then(res => res.data),
};


