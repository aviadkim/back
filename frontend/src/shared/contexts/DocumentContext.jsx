import React, { createContext, useState, useCallback } from 'react';
import axios from 'axios';

// Create the document context
const DocumentContext = createContext();

/**
 * Document Context Provider component
 * Manages document state across the application following Vertical Slice Architecture
 * 
 * Responsibilities:
 * - Loading documents from the API
 * - Uploading new documents
 * - Fetching document details
 * - Deleting documents
 * - Analyzing document content
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 * @returns {JSX.Element} The provider component
 */
export const DocumentContextProvider = ({ children }) => {
  // State for documents
  const [documents, setDocuments] = useState([]);
  const [currentDocument, setCurrentDocument] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Load all documents from the API
   */
  const loadDocuments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('/api/documents');
      setDocuments(response.data);
      
      return response.data;
    } catch (err) {
      console.error('Error loading documents:', err);
      setError(err.message || 'Failed to load documents');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Fetch a single document by ID
   * 
   * @param {string} id - Document ID
   * @returns {Object} Document data
   */
  const getDocumentById = useCallback(async (id) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`/api/documents/${id}`);
      setCurrentDocument(response.data);
      
      return response.data;
    } catch (err) {
      console.error(`Error loading document ${id}:`, err);
      setError(err.message || 'Failed to load document');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Upload a new document
   * 
   * @param {FormData} formData - Form data with document file and metadata
   * @param {Function} onProgress - Progress callback
   * @returns {Object} Uploaded document data
   */
  const uploadDocument = useCallback(async (formData, onProgress) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('/api/documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: onProgress,
      });
      
      // Add the new document to the list
      setDocuments(prev => [...prev, response.data]);
      
      return response.data;
    } catch (err) {
      console.error('Error uploading document:', err);
      setError(err.message || 'Failed to upload document');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Delete a document by ID
   * 
   * @param {string} id - Document ID
   * @returns {boolean} Success status
   */
  const deleteDocument = useCallback(async (id) => {
    try {
      setLoading(true);
      setError(null);
      
      await axios.delete(`/api/documents/${id}`);
      
      // Remove the document from the list
      setDocuments(prev => prev.filter(doc => doc.id !== id));
      
      if (currentDocument && currentDocument.id === id) {
        setCurrentDocument(null);
      }
      
      return true;
    } catch (err) {
      console.error(`Error deleting document ${id}:`, err);
      setError(err.message || 'Failed to delete document');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [currentDocument]);

  /**
   * Analyze a document to extract specific data
   * 
   * @param {string} id - Document ID
   * @param {Object} options - Analysis options
   * @returns {Object} Analysis results
   */
  const analyzeDocument = useCallback(async (id, options = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post(`/api/documents/${id}/analyze`, options);
      
      // Update the current document with analysis results
      if (currentDocument && currentDocument.id === id) {
        setCurrentDocument(prev => ({
          ...prev,
          analysis: response.data,
        }));
      }
      
      return response.data;
    } catch (err) {
      console.error(`Error analyzing document ${id}:`, err);
      setError(err.message || 'Failed to analyze document');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [currentDocument]);

  // Context value
  const contextValue = {
    documents,
    currentDocument,
    loading,
    error,
    loadDocuments,
    getDocumentById,
    uploadDocument,
    deleteDocument,
    analyzeDocument,
  };

  return (
    <DocumentContext.Provider value={contextValue}>
      {children}
    </DocumentContext.Provider>
  );
};

export default DocumentContext;
