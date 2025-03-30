import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DocumentUploader from './components/DocumentUploader';
import DocumentChat from './components/DocumentChat';
import TableExtractor from './components/TableExtractor';

/**
 * Main App Component
 * 
 * Serves as the main layout and state container for the application
 */
const App = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Fetch documents when component mounts
  useEffect(() => {
    fetchDocuments();
  }, []);
  
  // Fetch documents from the API
  const fetchDocuments = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.get('/api/documents');
      setDocuments(response.data);
      
      // If there are documents and none is selected, select the first one
      if (response.data.length > 0 && !selectedDocument) {
        setSelectedDocument(response.data[0]);
      }
    } catch (error) {
      setError('שגיאה בטעינת המסמכים. אנא נסה שוב.');
      console.error('Error fetching documents:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle document upload success
  const handleUploadSuccess = (data) => {
    // Add the new document to the list
    const newDocument = {
      id: data.document_id,
      filename: data.filename,
      upload_date: new Date().toISOString(),
      status: 'completed',
      page_count: data.details?.chunks_count || 1,
      language: data.details?.metadata?.language || 'he',
      type: data.filename.split('.').pop().toUpperCase()
    };
    
    setDocuments(prev => [newDocument, ...prev]);
    setSelectedDocument(newDocument);
    
    // Switch to the chat tab
    setActiveTab('chat');
  };
  
  // Handle document selection
  const handleDocumentSelect = (document) => {
    setSelectedDocument(document);
    
    // If we're on the upload tab, switch to chat
    if (activeTab === 'upload') {
      setActiveTab('chat');
    }
  };
  
  // Render the sidebar document list
  const renderDocumentList = () => {
    if (documents.length === 0) {
      return (
        <div className="text-center text-gray-500 p-4">
          {isLoading ? 'טוען מסמכים...' : 'אין מסמכים. העלה מסמך חדש.'}
        </div>
      );
    }
    
    return (
      <ul className="document-list space-y-2">
        {documents.map((document) => (
          <li key={document.id}>
            <button
              onClick={() => handleDocumentSelect(document)}
              className={`w-full flex items-center p-3 rounded-lg ${
                selectedDocument?.id === document.id
                  ? 'bg-primary-100 text-primary-800'
                  : 'hover:bg-gray-100'
              }`}
            >
              {/* Document icon based on type */}
              <div className="document-icon mr-3">
                {document.type === 'PDF' ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                  </svg>
                ) : document.type === 'XLSX' || document.type === 'XLS' || document.type === 'CSV' ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5 4a3 3 0 00-3 3v6a3 3 0 003 3h10a3 3 0 003-3V7a3 3 0 00-3-3H5zm0 2a1 1 0 00-1 1v6a1 1 0 001 1h10a1 1 0 001-1V7a1 1 0 00-1-1H5z" clipRule="evenodd" />
                    <path d="M7 9a1 1 0 100-2 1 1 0 000 2zm2 0a1 1 0 100-2 1 1 0 000 2zm2 0a1 1 0 100-2 1 1 0 000 2z" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              
              <div className="document-info text-start overflow-hidden">
                <div className="document-name font-medium truncate">
                  {document.filename}
                </div>
                <div className="document-meta text-xs text-gray-500 flex mt-1">
                  <span className="mr-2">{document.type}</span>
                  <span className="mr-2">•</span>
                  <span>{new Date(document.upload_date).toLocaleDateString()}</span>
                  <span className="mr-2">•</span>
                  <span>{document.page_count} עמודים</span>
                </div>
              </div>
            </button>
          </li>
        ))}
      </ul>
    );
  };
  
  // Render the main content based on the active tab
  const renderContent = () => {
    if (activeTab === 'upload') {
      return <DocumentUploader onUploadSuccess={handleUploadSuccess} />;
    } else if (activeTab === 'chat' && selectedDocument) {
      return <DocumentChat documentId={selectedDocument.id} documentName={selectedDocument.filename} />;
    } else if (activeTab === 'tables' && selectedDocument) {
      return <TableExtractor documentId={selectedDocument.id} documentName={selectedDocument.filename} />;
    } else {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          יש לבחור מסמך כדי להמשיך
        </div>
      );
    }
  };
  
  return (
    <div className="app-container min-h-screen bg-gray-100 text-gray-900 flex flex-col">
      {/* Header */}
      <header className="bg-primary-600 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">FinDoc Analyzer</h1>
          <div className="version text-sm">גרסה 4.1</div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-grow container mx-auto my-6 px-4 flex">
        {/* Sidebar */}
        <div className="sidebar w-1/4 mr-6">
          <div className="bg-white rounded-lg shadow-md p-4 mb-6">
            <h2 className="text-lg font-semibold mb-4">פעולות</h2>
            <div className="actions">
              <button
                onClick={() => setActiveTab('upload')}
                className={`w-full flex items-center p-3 mb-2 rounded-lg ${
                  activeTab === 'upload'
                    ? 'bg-primary-100 text-primary-800'
                    : 'hover:bg-gray-100'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
                העלאת מסמך חדש
              </button>
              
              <button
                onClick={() => setActiveTab('chat')}
                disabled={!selectedDocument}
                className={`w-full flex items-center p-3 mb-2 rounded-lg ${
                  activeTab === 'chat'
                    ? 'bg-primary-100 text-primary-800'
                    : 'hover:bg-gray-100'
                } ${!selectedDocument ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zM7 8H5v2h2V8zm2 0h2v2H9V8zm6 0h-2v2h2V8z" clipRule="evenodd" />
                </svg>
                שיחה עם המסמך
              </button>
              
              <button
                onClick={() => setActiveTab('tables')}
                disabled={!selectedDocument}
                className={`w-full flex items-center p-3 rounded-lg ${
                  activeTab === 'tables'
                    ? 'bg-primary-100 text-primary-800'
                    : 'hover:bg-gray-100'
                } ${!selectedDocument ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5 4a3 3 0 00-3 3v6a3 3 0 003 3h10a3 3 0 003-3V7a3 3 0 00-3-3H5zm-1 9v-1h5v2H5a1 1 0 01-1-1zm7 1h4a1 1 0 001-1v-1h-5v2zm0-4h5V8h-5v2zM9 8H4v2h5V8z" clipRule="evenodd" />
                </svg>
                טבלאות וניתוח נתונים
              </button>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-lg font-semibold mb-4">המסמכים שלי</h2>
            <div className="document-list-container">
              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mb-4 rounded">
                  {error}
                </div>
              )}
              
              {renderDocumentList()}
            </div>
          </div>
        </div>
        
        {/* Main Content Area */}
        <div className="content w-3/4 bg-white rounded-lg shadow-md">
          {renderContent()}
        </div>
      </main>
      
      {/* Footer */}
      <footer className="bg-gray-800 text-white p-4 text-center">
        <div className="container mx-auto">
          <p>FinDoc Analyzer &copy; 2025 - כל הזכויות שמורות</p>
        </div>
      </footer>
    </div>
  );
};

export default App;
