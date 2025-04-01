import React from 'react';
import './DocumentsPage.css';

function DocumentsPage() {
  return (
    <div className="documents-page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">המסמכים שלי</h1>
          <p className="page-description">צפייה, ניהול וניתוח המסמכים הפיננסיים שלך</p>
        </div>
        
        <div className="upload-section">
          <h2 className="section-title">העלאת מסמך חדש</h2>
          <div className="upload-widget">
            <div className="dropzone">
              <div className="dropzone-content">
                <i className="icon-upload-cloud"></i>
                <p>גרור ושחרר קובץ כאן או לחץ לבחירת קובץ</p>
                <span className="dropzone-hint">(PDF, Excel, CSV) בגודל עד 50MB</span>
              </div>
            </div>
            <div className="upload-options">
              <div className="language-selector">
                <label htmlFor="language-select">שפת המסמך:</label>
                <select id="language-select">
                  <option value="auto">זיהוי אוטומטי</option>
                  <option value="he">עברית</option>
                  <option value="en">אנגלית</option>
                  <option value="mixed">מעורב</option>
                </select>
              </div>
              <button className="btn-primary upload-button">
                <i className="icon-upload"></i> העלאה
              </button>
            </div>
          </div>
        </div>
        
        <div className="documents-section">
          <h2 className="section-title">המסמכים שלי</h2>
          <div className="empty-state">
            <i className="icon-documents"></i>
            <h3>אין מסמכים עדיין</h3>
            <p>העלה את המסמך הפיננסי הראשון שלך כדי להתחיל</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DocumentsPage;
