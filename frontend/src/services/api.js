import axios from 'axios';

// API base URL.
// In development the React dev server proxies /api/* to localhost:8000
// (see "proxy" in package.json), so we use a relative base URL.
// In production set REACT_APP_API_URL to the deployed backend URL.
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Service Methods
const apiService = {
  // Health Check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // User Management
  registerUser: async (userData) => {
    const response = await api.post('/api/users/register', userData);
    return response.data;
  },

  getUserProfile: async (userId) => {
    const response = await api.get(`/api/users/${userId}`);
    return response.data;
  },

  // Mood Tracking
  logMood: async (moodData) => {
    const response = await api.post('/api/mood/log', moodData);
    return response.data;
  },

  getMoodHistory: async (userId, days = 7) => {
    const response = await api.get(`/api/mood/history/${userId}`, {
      params: { days },
    });
    return response.data;
  },

  // Journal
  createJournalEntry: async (entryData) => {
    const response = await api.post('/api/journal/entry', entryData);
    return response.data;
  },

  getJournalEntries: async (userId, limit = 10) => {
    const response = await api.get(`/api/journal/entries/${userId}`, {
      params: { limit },
    });
    return response.data;
  },

  // AI Analysis
  analyzeSentiment: async (text) => {
    const response = await api.post('/api/analyze/sentiment', null, {
      params: { text },
    });
    return response.data;
  },

  assessRisk: async (userId) => {
    const response = await api.get(`/api/analyze/risk/${userId}`);
    return response.data;
  },

  // Recommendations
  getRecommendations: async (userId) => {
    const response = await api.get(`/api/recommendations/${userId}`);
    return response.data;
  },

  // Chatbot
  sendChatMessage: async (message, userId) => {
    const response = await api.post('/api/chat', null, {
      params: { message, user_id: userId },
    });
    return response.data;
  },

  // Multimodal Analysis
  // Sends text (required) + optional audio/video files as multipart form data.
  // Returns the full analysis result object from the backend.
  multimodalAnalyze: async (text, audioFile = null, videoFile = null) => {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('user_id', 'react_user');
    if (audioFile) formData.append('audio_file', audioFile);
    if (videoFile) formData.append('video_file', videoFile);

    // The api instance has 'Content-Type: application/json' as a default header.
    // We must DELETE it so the browser can set 'multipart/form-data; boundary=...'
    // automatically — without the boundary FastAPI cannot parse the form fields.
    const response = await api.post('/api/multimodal/analyze', formData, {
      headers: { 'Content-Type': undefined },
    });
    return response.data;
  },

  // Text-only shortcut (JSON body — no file uploads needed)
  multimodalAnalyzeText: async (text) => {
    const response = await api.post('/api/multimodal/analyze/text', { text });
    return response.data;
  },
};

export default apiService;

// Made with Bob
