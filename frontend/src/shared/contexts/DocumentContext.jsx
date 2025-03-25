import React, { createContext, useState, useEffect } from 'react';

/**
 * DocumentContext provides state management for active documents across the application
 * 
 * This context:
 * - Stores information about documents the user is currently working with
 * - Maintains a document selection across different features
 * - Persists active documents in localStorage
 * - Provides methods to add/remove documents from the active set
 */
export const DocumentContext = createContext({
  activeDocuments: [],
  setActiveDocuments: () => {},
  addActiveDocument: () => {},
  removeActiveDocument: () => {},
  clearActiveDocuments: () => {},
  isDocumentActive: () => false
});

/**
 * Provider component for the DocumentContext
 */
const DocumentContextProvider = ({ children }) => {
  // Initialize state from localStorage if available
  const [activeDocuments, setActiveDocuments] = useState(() => {
    const savedDocuments = localStorage.getItem('activeDocuments');
    return savedDocuments ? JSON.parse(savedDocuments) : [];
  });
  
  // Save to localStorage when active documents change
  useEffect(() => {
    localStorage.setItem('activeDocuments', JSON.stringify(activeDocuments));
  }, [activeDocuments]);
  
  /**
   * Adds a document to the active documents list
   * 
   * @param {Object} document The document to add
   * @param {string} document.id Unique ID of the document
   * @param {string} document.title Optional display title
   * @param {Object} document.metadata Optional metadata for the document
   */
  const addActiveDocument = (document) => {
    if (!document || !document.id) return;
    
    // Don't add if already in the list
    if (activeDocuments.some(doc => doc.id === document.id)) return;
    
    setActiveDocuments(prev => [...prev, document]);
  };
  
  /**
   * Removes a document from the active documents list
   * 
   * @param {string} documentId ID of the document to remove
   */
  const removeActiveDocument = (documentId) => {
    setActiveDocuments(prev => prev.filter(doc => doc.id !== documentId));
  };
  
  /**
   * Clears all active documents
   */
  const clearActiveDocuments = () => {
    setActiveDocuments([]);
  };
  
  /**
   * Checks if a document is in the active documents list
   * 
   * @param {string} documentId ID of the document to check
   * @returns {boolean} True if the document is active
   */
  const isDocumentActive = (documentId) => {
    return activeDocuments.some(doc => doc.id === documentId);
  };
  
  // Context value
  const contextValue = {
    activeDocuments,
    setActiveDocuments,
    addActiveDocument,
    removeActiveDocument,
    clearActiveDocuments,
    isDocumentActive
  };
  
  return (
    <DocumentContext.Provider value={contextValue}>
      {children}
    </DocumentContext.Provider>
  );
};

export default DocumentContextProvider;
