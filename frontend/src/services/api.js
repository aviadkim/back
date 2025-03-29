// frontend/src/services/api.js
import axios from 'axios';

// הגדרת API בסיסי
// Use environment variable for flexibility, fallback to localhost
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// יצירת מופע axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Optional: Add interceptors for handling errors or adding auth tokens globally
api.interceptors.response.use(
  response => response,
  error => {
    // Log error or handle specific error statuses
    console.error('API call error:', error.response || error.message || error);
    return Promise.reject(error);
  }
);


export default api;