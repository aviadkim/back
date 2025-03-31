import axios from 'axios';

// Create API client with consistent configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api', // Base URL for all API requests
  timeout: 60000, // 60 seconds timeout, adjust as needed for potentially long processing
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

// Request interceptor to add authentication token (if using auth)
apiClient.interceptors.request.use(
  config => {
    // Example: Get token from local storage
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    console.error("API Request Error:", error);
    return Promise.reject(error);
  }
);

// Response interceptor for standardized error handling
apiClient.interceptors.response.use(
  response => {
    // If response is successful, just return it
    return response;
  },
  error => {
    let errorData = {
      message: 'An unknown network error occurred. Please check your connection.',
      status: error.status, // Network error status
      data: null
    };

    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error("API Response Error Data:", error.response.data);
      console.error("API Response Error Status:", error.response.status);
      console.error("API Response Error Headers:", error.response.headers);

      // Use the standardized error format from the backend if available
      errorData = {
        message: error.response.data?.message || `Request failed with status code ${error.response.status}`,
        status: error.response.status,
        data: error.response.data // Contains the full backend error response
      };

      // Handle specific status codes globally if needed
      if (error.response.status === 401) {
        // Example: Unauthorized - redirect to login or refresh token
        console.warn("Unauthorized access detected. Redirecting to login.");
        // Uncomment the line below to redirect
        // window.location.href = '/login';
      } else if (error.response.status === 404) {
          console.warn("Resource not found (404).");
          // Update message for 404
          errorData.message = error.response.data?.message || "The requested resource was not found.";
      }

    } else if (error.request) {
      // The request was made but no response was received
      console.error("API No Response Error:", error.request);
      errorData.message = 'No response received from the server. Please check if the backend is running.';
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Setup Error:', error.message);
      errorData.message = `Error setting up request: ${error.message}`;
    }

    // Reject with a standardized error object
    return Promise.reject(errorData);
  }
);

/**
 * Document API methods using the standardized client
 */
const documentApi = {
  /**
   * Upload and process a document
   * @param {File} file - The document file to upload
   * @param {Object} options - Additional options like language, onProgress callback
   * @returns {Promise<Object>} API response data on success
   */
  uploadDocument: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);

    // Add optional parameters like language
    if (options.language) {
      formData.append('language', options.language);
    }

    // Make the request using the configured apiClient
    return apiClient.post('/document/upload', formData, {
      headers: {
        // Override Content-Type for multipart/form-data
        'Content-Type': 'multipart/form-data'
      },
      // Pass the onUploadProgress callback from options
      onUploadProgress: options.onProgress
    }).then(response => response.data); // Return only the data part of the response
  },

  /**
   * Get all documents for the current user
   * @param {Object} params - Query parameters (e.g., page, limit)
   * @returns {Promise<Object>} API response data on success
   */
  getDocuments: async (params = {}) => {
    // Use the correct endpoint '/document/s'
    return apiClient.get('/document/s', { params })
      .then(response => response.data); // Return only the data part
  },

  /**
   * Get a specific document by ID
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} API response data on success
   */
  getDocument: async (documentId) => {
    return apiClient.get(`/document/${documentId}`)
      .then(response => response.data); // Return only the data part
  },

  /**
   * Get tables extracted from a document
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} API response data on success
   */
  getDocumentTables: async (documentId) => {
    return apiClient.get(`/document/${documentId}/tables`)
      .then(response => response.data); // Return only the data part
  },

  /**
   * Get financial data extracted from a document
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} API response data on success
   */
  getFinancialData: async (documentId) => {
    return apiClient.get(`/document/${documentId}/financial`)
      .then(response => response.data); // Return only the data part
  },

  /**
   * Ask a question about a document
   * @param {string} documentId - Document ID
   * @param {string} question - Question text
   * @returns {Promise<Object>} API response data on success
   */
  askDocumentQuestion: async (documentId, question) => {
    return apiClient.post(`/document/${documentId}/question`, { question })
      .then(response => response.data); // Return only the data part
  }
};

// Export the document API methods
export {
  documentApi
};

// Default export can include multiple API groups if needed later
export default {
  document: documentApi,
  // auth: authApi, // Example if auth API is added later
};