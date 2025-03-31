import axios from 'axios';

// Create API client with consistent configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  timeout: 30000, // 30 seconds timeout for document processing
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

// Request interceptor to add authentication token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }

    // Return proper error message
    return Promise.reject({
      message: error.response?.data?.message || 'An unknown error occurred',
      status: error.response?.status,
      data: error.response?.data
    });
  }
);

/**
 * Document API methods
 */
const documentApi = {
  /**
   * Upload and process a document
   * @param {File} file - The document file to upload
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Processing result
   */
  uploadDocument: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);

    // Add optional parameters
    if (options.language) {
      formData.append('language', options.language);
    }

    return apiClient.post('/document/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: options.onProgress
    }).then(response => response.data);
  },

  /**
   * Get all documents for the current user
   * @param {Object} params - Query parameters (page, limit)
   * @returns {Promise<Object>} Documents list
   */
  getDocuments: async (params = {}) => {
    return apiClient.get('/documents', { params })
      .then(response => response.data);
  },

  /**
   * Get a specific document by ID
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} Document data
   */
  getDocument: async (documentId) => {
    return apiClient.get(`/document/${documentId}`)
      .then(response => response.data);
  },

  /**
   * Get tables extracted from a document
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} Table data
   */
  getDocumentTables: async (documentId) => {
    return apiClient.get(`/document/${documentId}/tables`)
      .then(response => response.data);
  },

  /**
   * Get financial data extracted from a document
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} Financial data
   */
  getFinancialData: async (documentId) => {
    return apiClient.get(`/document/${documentId}/financial`)
      .then(response => response.data);
  },

  /**
   * Ask a question about a document
   * @param {string} documentId - Document ID
   * @param {string} question - Question text
   * @returns {Promise<Object>} Answer data
   */
  askDocumentQuestion: async (documentId, question) => {
    return apiClient.post(`/document/${documentId}/question`, { question })
      .then(response => response.data);
  }
};

/**
 * Authentication API methods
 */
const authApi = {
  /**
   * Login with username and password
   * @param {string} username - Username
   * @param {string} password - Password
   * @returns {Promise<Object>} Authentication result
   */
  login: async (username, password) => {
    return apiClient.post('/auth/login', { username, password })
      .then(response => {
        // Store token in localStorage
        if (response.data.data?.token) {
          localStorage.setItem('auth_token', response.data.data.token);
        }
        return response.data;
      });
  },

  /**
   * Logout current user
   * @returns {Promise<Object>} Logout result
   */
  logout: async () => {
    return apiClient.post('/auth/logout')
      .then(response => {
        // Remove token from localStorage
        localStorage.removeItem('auth_token');
        return response.data;
      });
  },

  /**
   * Check if user is authenticated
   * @returns {Promise<Object>} Authentication status
   */
  checkAuth: async () => {
    return apiClient.get('/auth/check')
      .then(response => response.data);
  }
};

// Export all API endpoints
export {
  documentApi,
  authApi
};

// Default export
export default {
  document: documentApi,
  auth: authApi
};