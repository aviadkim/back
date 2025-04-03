import React from 'react';
import './DocumentTabs.css';

/**
 * רכיב לשוניות המסמך שמאפשר ניווט בין חלקים שונים של תצוגת המסמך
 * @param {Object} props - מאפייני הרכיב
 * @param {string} props.activeTab - הלשונית הפעילה כרגע
 * @param {Function} props.onTabChange - פונקציה שמופעלת כאשר משתמש בוחר לשונית אחרת
 * @param {string} props.documentStatus - סטטוס עיבוד המסמך ('processing', 'completed', 'error')
 */
const DocumentTabs = ({ activeTab, onTabChange, documentStatus }) => {
  // Define tabs and potentially disable some based on status
  const tabs = [
    { id: 'overview', label: 'סקירה כללית', icon: 'fa-file-alt', disabled: documentStatus === 'processing' },
    { id: 'tables', label: 'טבלאות', icon: 'fa-table', disabled: documentStatus === 'processing' },
    // Assuming 'entities' and 'metrics' might come from ai_analysis which happens after processing
    // { id: 'entities', label: 'ישויות פיננסיות', icon: 'fa-tags', disabled: documentStatus !== 'completed' },
    // { id: 'metrics', label: 'מדדים פיננסיים', icon: 'fa-chart-line', disabled: documentStatus !== 'completed' },
    { id: 'chat', label: 'שאל את המסמך', icon: 'fa-comments', disabled: documentStatus !== 'completed' }, // Enable chat only when complete
    { id: 'original', label: 'מסמך מקורי', icon: 'fa-eye', disabled: false } // Always allow viewing original if available
  ];

  // Filter out tabs that should not be shown (e.g., based on available data later)
  const visibleTabs = tabs; // For now, show all defined tabs

  return (
    <div className="document-tabs">
      <div className="tabs-container">
        {visibleTabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => !tab.disabled && onTabChange(tab.id)} // Prevent changing to disabled tabs
            disabled={tab.disabled} // Disable the button visually and functionally
            title={tab.disabled ? "הנתונים עדיין לא זמינים" : ""} // Tooltip for disabled tabs
          >
            <i className={`fas ${tab.icon}`}></i>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default DocumentTabs;