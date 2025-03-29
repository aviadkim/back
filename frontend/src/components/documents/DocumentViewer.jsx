import React, { useState, useEffect } from 'react';
import './DocumentViewer.css';

/**
 * רכיב להצגת המסמך המקורי
 * @param {Object} props - מאפייני הרכיב
 * @param {string} props.documentUrl - כתובת URL למסמך המקורי (pre-signed URL)
 * @param {Object} props.document - אובייקט המסמך עם כל המידע (לגישה ל-metadata ו-processed_data)
 */
const DocumentViewer = ({ documentUrl, document }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pageCount, setPageCount] = useState(0);

  // אפקט לטעינת נתוני המסמך
  useEffect(() => {
    setLoading(true); // Start loading when URL or document changes
    setError(null);
    setPageCount(0); // Reset page count

    // If we have a URL, assume we can try to load it
    if (documentUrl) {
      // Get page count from metadata if available
      if (document?.metadata?.page_count) {
        setPageCount(document.metadata.page_count);
      }

      // Simulate loading completion - in a real app, you might wait for iframe onload
      const timer = setTimeout(() => {
        setLoading(false);
      }, 500); // Short delay to allow iframe to start loading

      return () => clearTimeout(timer);
    }
    // If no URL, check if we have extracted text as fallback
    else if (document?.processed_data?.text_content) {
        setLoading(false); // No URL, but have text, stop loading
    }
    // If no URL and no text, set error
    else {
      setError('לא נמצאה כתובת למסמך המקורי או תוכן שחולץ.');
      setLoading(false);
    }
  }, [documentUrl, document]); // Rerun effect if URL or document object changes

  // אם המסמך בתהליך טעינה, הצג אינדיקטור טעינה
  if (loading) {
    return (
      <div className="document-viewer-loading">
        <div className="loading-spinner"></div>
        <p>טוען את המסמך...</p>
      </div>
    );
  }

  // אם הייתה שגיאה, הצג הודעת שגיאה
  if (error) {
    return (
      <div className="document-viewer-error">
        <i className="fas fa-exclamation-triangle"></i>
        <p>{error}</p>
      </div>
    );
  }

  // אם אין כתובת מסמך אך יש תוכן טקסט שחולץ, הצג את התוכן הטקסטואלי
  if (!documentUrl && document?.processed_data?.text_content) {
    return (
      <div className="document-viewer-text">
        <div className="text-content-header">
          <h3>תוכן מסמך שחולץ:</h3>
        </div>
        <div className="text-content-body">
          {/* Render text content, splitting by newline */}
          {document.processed_data.text_content.split('\n').map((line, i) => (
            <p key={i}>{line || '\u00A0'}</p> // Use non-breaking space for empty lines
          ))}
        </div>
      </div>
    );
  }

  // If we have a documentUrl, try to display it
  if (documentUrl) {
      // Basic check for PDF extension
      const isPdf = documentUrl.toLowerCase().includes('.pdf');

      return (
        <div className="document-viewer">
          <div className="document-viewer-header">
            <h3>מסמך מקורי</h3>
            <a
              href={documentUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="open-in-new-tab"
              title="פתח בכרטיסייה חדשה"
            >
              <i className="fas fa-external-link-alt"></i> פתח בכרטיסייה חדשה
            </a>
          </div>

          <div className="document-viewer-content">
            {isPdf ? (
              // Use iframe for better PDF controls generally
              <iframe
                src={`${documentUrl}#toolbar=1&navpanes=1&scrollbar=1`} // Add parameters for PDF viewer UI
                title="PDF Document Viewer"
                className="pdf-viewer"
                // Optional: Add sandbox attribute for security if URL is untrusted
                // sandbox="allow-scripts allow-same-origin"
              >
                <p>הדפדפן שלך אינו תומך בהצגת PDF מוטמע. <a href={documentUrl} target="_blank" rel="noopener noreferrer">לחץ כאן להורדת הקובץ</a>.</p>
              </iframe>
            ) : (
              // Fallback for non-PDFs or if iframe fails - might not render correctly
              // Consider showing a download link instead for non-PDFs
               <div className="non-pdf-fallback">
                   <p>תצוגה מקדימה אינה זמינה עבור סוג קובץ זה.</p>
                   <a href={documentUrl} target="_blank" rel="noopener noreferrer" className="btn-secondary">
                       <i className="fas fa-download"></i> הורד את הקובץ
                   </a>
               </div>
              // <embed
              //   src={documentUrl}
              //   type={document?.metadata?.content_type || "application/octet-stream"} // Try to get content type
              //   className="pdf-viewer" // Re-use class, might need adjustments
              // />
            )}
          </div>

          {pageCount > 0 && (
            <div className="document-viewer-footer">
              <span>{pageCount} עמודים במסמך זה</span>
            </div>
          )}
        </div>
      );
  }

  // Fallback if no URL and no text content
  return (
       <div className="document-viewer-error">
           <i className="fas fa-file-excel"></i> {/* Generic file icon */}
           <p>לא ניתן להציג את המסמך.</p>
       </div>
   );
};

export default DocumentViewer;