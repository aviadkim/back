import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom'; // Keep Link if needed elsewhere
import DocumentList from '../components/documents/DocumentList';
import UploadWidget from '../components/documents/UploadWidget';
import documentService from '../services/documentService'; // Use the service
import './DocumentsPage.css'; // Ensure CSS is imported

/**
 * דף רשימת המסמכים
 */
const DocumentsPage = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadSuccessMessage, setUploadSuccessMessage] = useState(''); // For success message
  const [uploadErrorMessage, setUploadErrorMessage] = useState(''); // For upload error message
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'upload_date', direction: 'desc' }); // Default sort by date desc
  const [filterStatus, setFilterStatus] = useState('all');

  // טעינת המסמכים בעת טעינת הדף
  useEffect(() => {
    fetchDocuments();
  }, []); // Run once on mount

  // פונקציה לטעינת המסמכים מהשרת
  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError(null); // Clear previous errors
      const response = await documentService.getDocuments();
      // Ensure response is always an array
      setDocuments(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError(`אירעה שגיאה בטעינת המסמכים: ${error.message}. נסה לרענן את הדף.`);
      setDocuments([]); // Clear documents on error
    } finally {
      setLoading(false);
    }
  };

  // טיפול בהעלאת מסמך מוצלחת
  const handleUploadSuccess = (response) => {
    const filename = response?.filename || 'המסמך'; // Use filename from response if available
    setUploadSuccessMessage(`${filename} הועלה בהצלחה! העיבוד החל.`);
    // Add the new document optimistically or refetch
    fetchDocuments(); // Refetch the list to include the new document and its status
    // Clear message after a few seconds
    setTimeout(() => setUploadSuccessMessage(''), 4000);
  };

  // טיפול בשגיאת העלאה
  const handleUploadError = (errorMessage) => {
    setUploadErrorMessage(`שגיאה בהעלאת המסמך: ${errorMessage}`);
    // Clear message after a few seconds
    setTimeout(() => setUploadErrorMessage(''), 5000);
  };

  // Memoized calculation for filtered and sorted documents
  const processedDocuments = useMemo(() => {
    let filtered = documents.filter(doc => {
      // Ensure doc and filename exist before searching
      const matchesSearch = !searchTerm || (doc.filename && doc.filename.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesStatus = filterStatus === 'all' || doc.status === filterStatus;
      return matchesSearch && matchesStatus;
    });

    // Sorting logic
    filtered.sort((a, b) => {
      const { key, direction } = sortConfig;
      const valA = a[key];
      const valB = b[key];

      // Handle missing values
      if (valA === undefined || valA === null) return 1;
      if (valB === undefined || valB === null) return -1;

      let comparison = 0;
      if (key === 'upload_date') {
        // Compare dates
        comparison = new Date(valA) - new Date(valB);
      } else if (typeof valA === 'string' && typeof valB === 'string') {
        // Compare strings (case-insensitive)
        comparison = valA.toLowerCase().localeCompare(valB.toLowerCase(), 'he');
      } else if (typeof valA === 'number' && typeof valB === 'number') {
        // Compare numbers
        comparison = valA - valB;
      } else {
         // Fallback comparison
         comparison = String(valA).localeCompare(String(valB), 'he');
      }

      return direction === 'desc' ? comparison * -1 : comparison;
    });

    return filtered;
  }, [documents, searchTerm, filterStatus, sortConfig]);


  // שינוי הגדרות המיון
  const handleSort = (key) => {
    setSortConfig(prevConfig => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Function to clear filters and search
  const clearFilters = () => {
      setSearchTerm('');
      setFilterStatus('all');
      // Optionally reset sort?
      // setSortConfig({ key: 'upload_date', direction: 'desc' });
  };


  return (
    <div className="documents-page">
      <div className="container"> {/* Ensure container class is used */}
        <div className="page-header">
          <h1>המסמכים שלי</h1>
          <p className="page-description">העלה, צפה ונתח את המסמכים הפיננסיים שלך</p>
        </div>

        <div className="page-content">
          <div className="documents-grid">
            {/* Upload Section */}
            <div className="upload-section">
              <UploadWidget
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
              />
              {/* Display Success/Error Messages */}
              {uploadSuccessMessage && (
                <div className="alert success-message">
                  <i className="fas fa-check-circle"></i>
                  <span>{uploadSuccessMessage}</span>
                </div>
              )}
              {uploadErrorMessage && (
                <div className="alert error-message">
                  <i className="fas fa-exclamation-triangle"></i>
                  <span>{uploadErrorMessage}</span>
                </div>
              )}
            </div>

            {/* Document List Section */}
            <div className="document-list-section">
              <div className="list-controls">
                {/* Search Box */}
                <div className="search-box">
                  <i className="fas fa-search search-icon"></i>
                  <input
                    type="text"
                    placeholder="חיפוש לפי שם מסמך..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                   {searchTerm && (
                       <button className="clear-search-icon" onClick={() => setSearchTerm('')} title="נקה חיפוש">
                           <i className="fas fa-times"></i>
                       </button>
                   )}
                </div>

                {/* Filter Box */}
                <div className="filter-box">
                  <label htmlFor="status-filter">סנן לפי סטטוס:</label>
                  <select
                    id="status-filter"
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                  >
                    <option value="all">הכל</option>
                    <option value="completed">הושלם</option>
                    <option value="processing">בתהליך</option>
                    <option value="error">שגיאה</option>
                  </select>
                </div>
                 {/* Optional: Clear Filters Button */}
                 {(searchTerm || filterStatus !== 'all') && (
                     <button className="clear-filters-button btn-link" onClick={clearFilters}>
                         נקה סינון וחיפוש
                     </button>
                 )}
              </div>

              {/* Loading State */}
              {loading && (
                  <div className="loading-indicator list-loading">
                      <div className="loading-spinner"></div>
                      <span>טוען מסמכים...</span>
                  </div>
              )}

              {/* Error State */}
              {!loading && error && (
                  <div className="error-message list-error">
                      <i className="fas fa-exclamation-circle"></i>
                      <p>{error}</p>
                      <button className="btn-secondary" onClick={fetchDocuments}>נסה שוב</button>
                  </div>
              )}

              {/* Document List or No Documents Message */}
              {!loading && !error && (
                processedDocuments.length > 0 ? (
                  <DocumentList
                    documents={processedDocuments}
                    // Pass sort handlers if DocumentList implements clickable headers
                    // onSort={handleSort}
                    // sortConfig={sortConfig}
                  />
                ) : (
                  <div className="no-documents">
                    {searchTerm || filterStatus !== 'all' ? (
                      <>
                        <i className="fas fa-search"></i>
                        <p>לא נמצאו מסמכים התואמים את הסינון או החיפוש.</p>
                        <button
                          className="clear-filters-button btn-link"
                          onClick={clearFilters}
                        >
                          נקה סינון וחיפוש
                        </button>
                      </>
                    ) : (
                      <>
                        <i className="fas fa-file-alt"></i> {/* Changed icon */}
                        <p>אין לך מסמכים עדיין. העלה את המסמך הראשון שלך באמצעות הטופס למעלה!</p>
                      </>
                    )}
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentsPage;