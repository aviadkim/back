import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const DocumentContext = createContext();

export const useDocuments = () => useContext(DocumentContext);

export const DocumentProvider = ({ children }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/documents');
      setDocuments(response.data.documents);
      setError(null);
    } catch (err) {
      setError('Failed to load documents');
      console.error('Error fetching documents:', err);
      toast.error('Error loading documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const uploadDocument = async (formData) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setDocuments([...documents, response.data]);
      toast.success('Document uploaded successfully');
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to upload document';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (id) => {
    try {
      await axios.delete(`/api/documents/${id}`);
      setDocuments(documents.filter(doc => doc.id !== id));
      toast.success('Document deleted successfully');
    } catch (err) {
      toast.error('Failed to delete document');
      throw err;
    }
  };

  const value = {
    documents,
    loading,
    error,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
  };

  return (
    <DocumentContext.Provider value={value}>
      {children}
    </DocumentContext.Provider>
  );
};
