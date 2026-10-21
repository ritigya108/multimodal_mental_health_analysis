import axios from 'axios';
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const apiService = {
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  registerUser: async (userData) => {
    const response = await api.post('/api/users/register', userData);
    return response.data;
  },

  getUserProfile: async (userId) => {
    const response = await api.get(`/api/users/${userId}`);
    return response.data;
  },

  logMood: async (moodData) => {
    const response = await api.post('/api/mood/log', moodData);
    return response.data;
  },

  getMoodHistory: async (userId, days = 7) => {
    const response = await api.get(`/api/mood/history/${userId}`, { params: { days } });
    return response.data;
  },

  createJournalEntry: async (entryData) => {
    const response = await api.post('/api/journal/entry', entryData);
    return response.data;
  },

  getJournalEntries: async (userId, limit = 10) => {
    const response = await api.get(`/api/journal/entries/${userId}`, { params: { limit } });
    return response.data;
  },

  analyzeSentiment: async (text) => {
    const response = await api.post('/api/analyze/sentiment', null, { params: { text } });
    return response.data;
  },

  assessRisk: async (userId) => {
    const response = await api.get(`/api/analyze/risk/${userId}`);
    return response.data;
  },

  getRecommendations: async (userId) => {
    const response = await api.get(`/api/recommendations/${userId}`);
    return response.data;
  },

  sendChatMessage: async (message, userId) => {
    const response = await api.post('/api/chat', null, { params: { message, user_id: userId } });
    return response.data;
  },

  // Multimodal Analysis — uses relative URL so the React proxy forwards to port 8000
  multimodalAnalyze: async (text, audioFile = null, videoFile = null) => {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('user_id', 'react_user');
    if (audioFile) formData.append('audio_file', audioFile);
    if (videoFile) formData.append('video_file', videoFile);
    // Do NOT set Content-Type — browser sets multipart/form-data with boundary automatically
    const response = await axios.post(
      API_BASE_URL + '/api/multimodal/analyze',
      formData
    );
    return response.data;
  },

  multimodalAnalyzeText: async (text) => {
    const response = await api.post('/api/multimodal/analyze/text', { text });
    return response.data;
  },
};

export default apiService;
