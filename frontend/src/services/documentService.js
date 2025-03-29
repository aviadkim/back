// frontend/src/services/documentService.js
import api from './api';

// שירות לניהול מסמכים
const documentService = {
  // קבלת רשימת מסמכים
  getDocuments: async () => {
    try {
      // Using the AWS endpoint as specified in the instructions
      const response = await api.get('/aws/documents');
      // Ensure data is an array, default to empty array if not
      return Array.isArray(response.data) ? response.data : [];
    } catch (error) {
      console.error('Error fetching documents:', error.response?.data?.error || error.message);
      // Re-throw a more specific error or return an empty array/null
      throw new Error(error.response?.data?.error || 'Failed to fetch documents');
    }
  },

  // קבלת פרטי מסמך
  getDocument: async (documentId) => {
    if (!documentId) {
        throw new Error("Document ID is required");
    }
    try {
      // Using the AWS endpoint
      const response = await api.get(`/aws/documents/${documentId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching document ${documentId}:`, error.response?.data?.error || error.message);
      throw new Error(error.response?.data?.error || `Failed to fetch document ${documentId}`);
    }
  },

  // העלאת מסמך חדש
  uploadDocument: async (file, language = 'auto') => {
    if (!file) {
        throw new Error("File is required for upload");
    }
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('language', language);

      // Using the AWS endpoint
      const response = await api.post('/aws/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        // Optional: Add progress tracking here if needed
        // onUploadProgress: progressEvent => { ... }
      });
      return response.data; // Expects { document_id: '...', status: '...' }
    } catch (error) {
      console.error('Error uploading document:', error.response?.data?.error || error.message);
      throw new Error(error.response?.data?.error || 'Failed to upload document');
    }
  },

  // שאילת שאלה על מסמך
  askQuestion: async (documentId, question) => {
     if (!documentId || !question) {
        throw new Error("Document ID and question are required");
     }
    try {
      // Using the AWS endpoint
      const response = await api.post(`/aws/documents/${documentId}/ask`, { question });
      return response.data; // Expects { answer: '...' }
    } catch (error) {
      console.error('Error asking question:', error.response?.data?.error || error.message);
      throw new Error(error.response?.data?.error || 'Failed to get answer');
    }
  }
};

export default documentService;