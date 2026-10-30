import axios from 'axios';

// API base URL.
// In development the React dev server proxies /api/* to localhost:8000
// (see "proxy" in package.json), so we use a relative base URL.
// In production set REACT_APP_API_URL to the deployed backend URL.
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error),
);

// Handle 401 â€” remove token and redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

const apiService = {
  // â”€â”€ Health â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  healthCheck: async () => {
    const r = await api.get('/health');
    return r.data;
  },

  // â”€â”€ Config â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  getHelpline: async () => {
    const r = await api.get('/api/config/helpline');
    return r.data;
  },

  // â”€â”€ User management â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  registerUser: async (userData) => {
    const r = await api.post('/api/users/register', userData);
    return r.data;
  },
  getUserProfile: async (userId) => {
    const r = await api.get(`/api/users/${userId}`);
    return r.data;
  },
  deleteUserData: async (userId) => {
    const r = await api.delete(`/api/users/${userId}/data`);
    return r.data;
  },

  // â”€â”€ Journal â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  createJournalEntry: async (entryData) => {
    const r = await api.post('/api/journal/entry', entryData);
    return r.data;
  },
  getJournalEntries: async (userId, limit = 10) => {
    const r = await api.get(`/api/journal/entries/${userId}`, { params: { limit } });
    return r.data;
  },

  // â”€â”€ Chatbot â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  sendChatMessage: async (message, userId) => {
    // Send as JSON body â€” query params break on special characters like ? & #
    const r = await api.post('/api/chat', { message, user_id: userId });
    return r.data;
  },

  // â”€â”€ Assessment â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  /**
   * POST /api/assess/multimodal
   * text required; audioFile optional File object (WAV / MP3 / WebM).
   */
  assess: async (text, audioFile = null) => {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('user_id', localStorage.getItem('mindcare_user_id') || 'user123');
    if (audioFile) formData.append('audio_file', audioFile);
    const r = await api.post('/api/assess/multimodal', formData, {
      headers: { 'Content-Type': undefined }, // let browser set multipart boundary
    });
    return r.data;
  },

  getAssessmentHistory: async (userId, page = 1, pageSize = 20) => {
    const r = await api.get(`/api/assessments/${userId}`, {
      params: { page, page_size: pageSize },
    });
    return r.data;
  },

  // Legacy text-only shortcut (kept for backward compat)
  multimodalAnalyzeText: async (text) => {
    const r = await api.post('/api/multimodal/analyze/text', { text });
    return r.data;
  },

  // â”€â”€ PHQ-8 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  scorePHQ8: async (answers, userId = 'user123') => {
    const r = await api.post('/api/phq8/score', { answers, user_id: userId });
    return r.data;
  },
  getPHQ8History: async (userId) => {
    const r = await api.get(`/api/phq8/history/${userId}`);
    return r.data;
  },

  // â”€â”€ Model metrics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  getModelMetrics: async () => {
    const r = await api.get('/api/model/metrics');
    return r.data;
  },
};

export default apiService;
