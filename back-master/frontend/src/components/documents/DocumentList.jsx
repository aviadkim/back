// src/components/documents/DocumentList.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import './DocumentList.css';

function DocumentList({ documents }) {
  // פונקציה לפורמט תאריך
  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A'; // Handle cases where date might be missing
    try {
      const date = new Date(dateStr);
      return new Intl.DateTimeFormat('he-IL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (e) {
      console.error("Error formatting date:", dateStr, e);
      return dateStr; // Return original string if formatting fails
    }
  };

  // פונקציה לקבלת סטטוס בעברית
  const getStatusText = (status) => {
    const statusMap = {
      'processing': 'בעיבוד',
      'completed': 'הושלם',
      'error': 'שגיאה',
      'pending': 'ממתין' // Added pending status
    };
    return statusMap[status] || status || 'לא ידוע'; // Default to 'לא ידוע' if status is null/undefined
  };

  // פונקציה לקבלת צבע סטטוס
  const getStatusClass = (status) => {
    const statusClassMap = {
      'processing': 'status-processing',
      'completed': 'status-completed',
      'error': 'status-error',
      'pending': 'status-pending' // Added pending status class
    };
    return statusClassMap[status] || 'status-unknown'; // Default class
  };

  // Function to get language text
  const getLanguageText = (langCode) => {
    const langMap = {
      'he': 'עברית',
      'en': 'אנגלית',
      'auto': 'אוטומטי',
      'mixed': 'מעורב'
    };
    return langMap[langCode] || langCode || 'לא ידוע';
  }

  return (
    <div className="document-list">
      {documents.map((document) => (
        <Link
          to={`/documents/${document.id}`} // Assuming 'id' is the correct identifier
          className="document-card"
          key={document.id} // Use 'id' as key
        >
          <div className="document-icon">
            {/* Choose icon based on file type if available, otherwise default */}
            <i className="icon-file-document"></i>
          </div>
          <div className="document-info">
            {/* Use 'filename' if available, otherwise a placeholder */}
            <h3 className="document-name">{document.filename || 'Unnamed Document'}</h3>
            <div className="document-meta">
              <span className="document-date">
                <i className="icon-calendar"></i>
                {/* Use 'upload_date' */}
                {formatDate(document.upload_date)}
              </span>
              {/* Display page count if available */}
              {document.page_count && (
                <span className="document-pages">
                  <i className="icon-pages"></i>
                  {document.page_count} עמודים
                </span>
              )}
              {/* Display language if available */}
              {document.language && (
                <span className="document-lang">
                  <i className="icon-language"></i>
                  {getLanguageText(document.language)}
                </span>
              )}
            </div>
          </div>
          {/* Use 'status' */}
          <div className={`document-status ${getStatusClass(document.status)}`}>
            {getStatusText(document.status)}
          </div>
        </Link>
      ))}
    </div>
  );
}

export default DocumentList;