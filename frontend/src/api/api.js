import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Interceptor to add auth token
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

// Interceptor to handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================
// AUTH ENDPOINTS
// ============================================

export const authAPI = {
  // Student
  studentLogin: (emailOrId, password) =>
    api.post('/auth/student/login', { email_or_id: emailOrId, password }),

  studentRegister: (data) =>
    api.post('/auth/student/register', data),

  forgotPassword: (email) =>
    api.post('/auth/student/forgot-password', { email }),

  resetPassword: (token, password) =>
    api.post('/auth/student/reset-password', { token, password }),

  // Admin
  adminLogin: (username, password) =>
    api.post('/auth/admin/login', { username, password }),
};

// ============================================
// STUDENT ENDPOINTS
// ============================================

export const studentAPI = {
  getDashboard: () =>
    api.get('/student/dashboard'),

  getPrediction: (studentData) =>
    api.post('/student/predict', studentData),

  getPredictionHistory: () =>
    api.get('/student/predictions'),

  uploadResume: (formData) =>
    api.post('/student/upload-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  getEligibleCompanies: (studentData) =>
    api.post('/student/eligible-companies', studentData),

  updateProfile: (data) =>
    api.put('/student/profile', data),

  getProfile: () =>
    api.get('/student/profile'),
};

// ============================================
// ADMIN ENDPOINTS
// ============================================

export const adminAPI = {
  getDashboard: () =>
    api.get('/admin/dashboard'),

  getStudents: (params) =>
    api.get('/admin/students', { params }),

  addStudent: (data) =>
    api.post('/admin/add-student', data),

  updateStudent: (id, data) =>
    api.put(`/admin/update-student/${id}`, data),

  deleteStudent: (id) =>
    api.delete(`/admin/delete-student/${id}`),

  uploadDataset: (formData) =>
    api.post('/admin/upload-dataset', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  trainModel: () =>
    api.post('/admin/train-model'),

  getPredictions: (params) =>
    api.get('/admin/predictions', { params }),

  getAnalytics: () =>
    api.get('/admin/analytics'),

  getCompanies: () =>
    api.get('/admin/companies'),

  addCompany: (data) =>
    api.post('/admin/add-company', data),

  updateCompany: (id, data) =>
    api.put(`/admin/update-company/${id}`, data),

  deleteCompany: (id) =>
    api.delete(`/admin/delete-company/${id}`),

  sendAlerts: () =>
    api.post('/admin/send-alerts'),

  getMentorAlerts: (params) =>
    api.get('/admin/mentor-alerts', { params }),
};

// ============================================
// ML ENDPOINTS
// ============================================

export const mlAPI = {
  getModelInfo: () =>
    api.get('/ml/model-info'),

  getModelAccuracy: () =>
    api.get('/ml/model-accuracy'),

  predict: (data) =>
    api.post('/ml/predict', data),

  batchPredict: (data) =>
    api.post('/ml/batch-predict', data),
};

// ============================================
// RESUME ANALYSIS ENDPOINTS
// ============================================

export const resumeAPI = {
  analyzeResume: (formData) =>
    api.post('/resume/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  getResumeHistory: () =>
    api.get('/resume/history'),
};

// ============================================
// COMPANY ELIGIBILITY ENDPOINTS
// ============================================

export const companyAPI = {
  checkEligibility: (studentData) =>
    api.post('/company/check-eligibility', studentData),

  getCompanies: () =>
    api.get('/company/list'),

  getCompanyDetails: (name) =>
    api.get(`/company/${name}`),

  compareCompanies: () =>
    api.get('/company/compare'),
};

export default api;
