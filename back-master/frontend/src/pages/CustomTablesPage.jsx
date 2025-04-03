// src/pages/CustomTablesPage.jsx
import React, { useState, useEffect } from 'react';
import CustomTableGenerator from '../components/tables/CustomTableGenerator';
import './CustomTablesPage.css';

function CustomTablesPage() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // פונקציה לטעינת רשימת המסמכים
    const fetchDocuments = async () => {
      setLoading(true);
      setError(null);
      try {
        // Use the new AWS endpoint
        const response = await fetch('/api/aws/documents'); // Changed endpoint

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'שגיאה בטעינת המסמכים');
        }

        const data = await response.json();
        // סינון מסמכים שעיבודם הושלם
        const completedDocuments = data.filter(doc => doc.status === 'completed');
        setDocuments(completedDocuments);

        // Select the first completed document by default if available
        if (completedDocuments.length > 0) {
            setSelectedDocument(completedDocuments[0]);
        }

      } catch (error) {
        console.error('Error fetching documents:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []); // Run once on mount

  // Function to format date
  const formatDate = (dateStr) => {
      if (!dateStr) return 'N/A';
      try {
          return new Date(dateStr).toLocaleDateString('he-IL');
      } catch (e) {
          return dateStr;
      }
  };

  if (loading) {
    return (
      <div className="custom-tables-page loading">
        <div className="container">
          <div className="loading-indicator">
            <i className="icon-loading spin"></i>
            <span>טוען נתונים...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="custom-tables-page error">
        <div className="container">
          <div className="error-message">
            <i className="icon-error"></i>
            <h2>שגיאה בטעינת נתונים</h2>
            <p>{error}</p>
            <button className="btn-secondary" onClick={() => window.location.reload()}>
              נסה שוב
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="custom-tables-page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">יצירת טבלאות מותאמות אישית</h1>
          <p className="page-description">צור טבלאות מותאמות אישית מהנתונים במסמכים שלך</p>
        </div>

        <div className="document-selector">
          <h2>בחר מסמך ליצירת טבלה</h2>
          {documents.length === 0 ? (
            <div className="empty-state">
              <i className="icon-documents"></i>
              <h3>אין מסמכים זמינים</h3>
              <p>העלה מסמכים והמתן להשלמת העיבוד שלהם כדי ליצור טבלאות מותאמות.</p>
            </div>
          ) : (
            <div className="document-list-horizontal"> {/* Changed class for potential horizontal layout */}
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className={`document-card-small ${selectedDocument?.id === doc.id ? 'selected' : ''}`} // Smaller card style
                  onClick={() => setSelectedDocument(doc)}
                  title={doc.filename} // Add tooltip
                >
                  <div className="document-icon">
                    <i className="icon-file-document"></i>
                  </div>
                  <div className="document-info">
                    <h3 className="document-name">{doc.filename}</h3>
                    <div className="document-meta">
                      {/* Use more concise meta info */}
                      <span>{formatDate(doc.upload_date)}</span>
                      {doc.page_count && <span>{doc.page_count} עמ'</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedDocument ? (
          <div className="custom-table-generator-section">
            <h2>יצירת טבלה מותאמת אישית עבור: {selectedDocument.filename}</h2>
            {/* Pass documentId to the generator */}
            <CustomTableGenerator documentId={selectedDocument.id} />
          </div>
        ) : (
           documents.length > 0 && ( // Show placeholder only if there are documents but none selected
             <div className="generator-placeholder">
                <i className="icon-table-select"></i>
                <h3>בחר מסמך</h3>
                <p>בחר מסמך מהרשימה למעלה כדי להתחיל ליצור טבלה מותאמת אישית.</p>
             </div>
           )
        )}
      </div>
    </div>
  );
}

export default CustomTablesPage;