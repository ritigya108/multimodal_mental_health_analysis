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

// Handle 401 — remove token and redirect to login
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
  // ── Health ──────────────────────────────────────────────────────────────────
  healthCheck: async () => {
    const r = await api.get('/health');
    return r.data;
  },

  // ── Auth ────────────────────────────────────────────────────────────────────
  /**
   * POST /auth/token
   * Returns { access_token, token_type, expires_in_seconds, user_id }
   */
  login: async (username, password) => {
    const r = await api.post('/auth/token', { username, password });
    if (r.data.access_token) {
      localStorage.setItem('token', r.data.access_token);
      localStorage.setItem('mindcare_user_id', r.data.user_id);
    }
    return r.data;
  },

  // ── Config ──────────────────────────────────────────────────────────────────
  getHelpline: async () => {
    const r = await api.get('/api/config/helpline');
    return r.data;
  },

  // ── User management ─────────────────────────────────────────────────────────
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

  // ── Journal ─────────────────────────────────────────────────────────────────
  createJournalEntry: async (entryData) => {
    const r = await api.post('/api/journal/entry', entryData);
    return r.data;
  },
  getJournalEntries: async (userId, limit = 10) => {
    const r = await api.get(`/api/journal/entries/${userId}`, { params: { limit } });
    return r.data;
  },

  // ── Chatbot ─────────────────────────────────────────────────────────────────
  sendChatMessage: async (message, userId) => {
    const r = await api.post('/api/chat', { message, user_id: userId });
    return r.data;
  },

  // ── Assessment ──────────────────────────────────────────────────────────────
  /**
   * POST /api/assess/multimodal — EATD three-question endpoint.
   *
   * @param {Object} texts  — { positive: string, neutral: string, negative: string }
   * @param {Array}  blobs  — [positiveFile|null, neutralFile|null, negativeFile|null]
   *                          Each item is a File object (WebM/WAV/MP3) or null.
   */
  assessEATD: async (texts, blobs = [null, null, null]) => {
    const formData = new FormData();
    formData.append('positive_text', texts.positive || '');
    formData.append('neutral_text',  texts.neutral  || '');
    formData.append('negative_text', texts.negative || '');

    const audioKeys = ['positive_audio', 'neutral_audio', 'negative_audio'];
    blobs.forEach((b, i) => { if (b) formData.append(audioKeys[i], b); });

    const r = await api.post('/api/assess/multimodal', formData, {
      headers: { 'Content-Type': undefined }, // let browser set multipart boundary
    });
    return r.data;
  },

  /** Legacy single-text shortcut (kept for backward compat). */
  assess: async (text, audioFile = null) => {
    const formData = new FormData();
    formData.append('positive_text', text);
    if (audioFile) formData.append('positive_audio', audioFile);
    const r = await api.post('/api/assess/multimodal', formData, {
      headers: { 'Content-Type': undefined },
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

  // ── PHQ-8 ───────────────────────────────────────────────────────────────────
  scorePHQ8: async (answers, userId = 'user123') => {
    const r = await api.post('/api/phq8/score', { answers, user_id: userId });
    return r.data;
  },
  getPHQ8History: async (userId) => {
    const r = await api.get(`/api/phq8/history/${userId}`);
    return r.data;
  },

  // ── Model metrics ───────────────────────────────────────────────────────────
  getModelMetrics: async () => {
    const r = await api.get('/api/model/metrics');
    return r.data;
  },
};

export default apiService;
