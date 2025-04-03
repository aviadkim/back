import React from 'react';
import './DocumentHeader.css';
import { Link, useNavigate } from 'react-router-dom'; // Import useNavigate

const DocumentHeader = ({ document }) => { // Removed onBack prop, using useNavigate instead
  const navigate = useNavigate(); // Hook for navigation

  // Use metadata directly if document structure is { metadata: {...}, ... }
  const metadata = document || {};

  if (!metadata || !metadata.id) { // Check for a valid identifier like id
    // Render a placeholder or skeleton if no valid data
    return <div className="document-header-skeleton">Loading Header...</div>;
  }

  const { filename, upload_date, status, language, s3_path } = metadata; // Destructure metadata
  const document_url = metadata.document_url; // Get pre-signed URL if available directly

  // Function to navigate back
  const handleBack = () => {
    navigate('/documents'); // Navigate to the documents list page
  };


  // המרת תאריך למבנה קריא אם קיים
  const formattedDate = upload_date
    ? new Date(upload_date).toLocaleDateString('he-IL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    : 'לא זמין';

  // זיהוי סוג המסמך לפי שם הקובץ
  const getDocumentType = (filename) => {
    if (!filename) return 'מסמך';

    const lowerName = filename.toLowerCase();
    if (lowerName.includes('דוח') || lowerName.includes('report')) return 'דוח';
    if (lowerName.includes('statement') || lowerName.includes('חשבון')) return 'דף חשבון';
    if (lowerName.includes('invoice') || lowerName.includes('חשבונית')) return 'חשבונית';
    if (lowerName.includes('letter') || lowerName.includes('מכתב')) return 'מכתב';

    return 'מסמך';
  };

  // סטטוס עם צבע מתאים
  const getStatusClass = (status) => {
    switch (status) {
      case 'completed': return 'status-success';
      case 'processing': return 'status-warning';
      case 'error': return 'status-error';
      default: return 'status-unknown'; // Added default
    }
  };

  // טקסט סטטוס בעברית
  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return 'עיבוד הושלם';
      case 'processing': return 'בתהליך עיבוד';
      case 'error': return 'שגיאה בעיבוד';
      default: return 'לא ידוע';
    }
  };

  // שפת המסמך בעברית
  const getLanguageText = (language) => {
    switch (language) {
      case 'he': return 'עברית';
      case 'en': return 'אנגלית';
      case 'auto': return 'זיהוי אוטומטי';
      case 'mixed': return 'מעורב'; // Added mixed
      default: return language || 'לא ידוע';
    }
  };

  return (
    <div className="document-header">
      <div className="document-header-top">
        {/* Use the handleBack function */}
        <button className="back-button" onClick={handleBack}>
          <i className="fas fa-arrow-right"></i> חזרה לרשימה
        </button>
        <div className={`document-status ${getStatusClass(status)}`}>
          <span className="status-dot"></span>
          <span className="status-text">{getStatusText(status)}</span>
        </div>
      </div>

      <h1 className="document-title">
        {/* Display filename safely */}
        {getDocumentType(filename)}: {filename || 'טוען שם...'}
      </h1>

      <div className="document-meta">
        <div className="meta-item">
          <i className="far fa-calendar-alt"></i>
          <span>תאריך העלאה: {formattedDate}</span>
        </div>
        <div className="meta-item">
          <i className="fas fa-language"></i>
          <span>שפת מסמך: {getLanguageText(language)}</span>
        </div>
        {/* Use the pre-signed document_url if available */}
        {document_url && (
          <div className="meta-item">
            <i className="far fa-file-pdf"></i>
            <a href={document_url} target="_blank" rel="noopener noreferrer">
              הצג מסמך מקורי
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentHeader;