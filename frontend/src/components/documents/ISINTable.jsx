import React, { useState, useEffect, useMemo } from 'react';
import './ISINTable.css';

/**
 * רכיב להצגת טבלת קודי ISIN שזוהו במסמך
 * @param {Object} props - מאפייני הרכיב
 * @param {Array} props.data - מערך של אובייקטי ISIN שזוהו (או מחרוזות ISIN)
 * @param {boolean} props.loading - האם נתוני ה-ISIN בטעינה
 * @param {boolean} props.isPreview - האם זו תצוגה מקדימה (מציגה פחות שורות)
 */
const ISINTable = ({ data = [], loading = false, isPreview = false }) => {
  const [filteredData, setFilteredData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({
    key: 'confidence', // Default sort key
    direction: 'desc'  // Default sort direction
  });

  // Normalize data to ensure it's an array of objects
  const normalizedIsinData = useMemo(() => {
    return data.map(item => {
      if (typeof item === 'string') {
        // If it's just a string, create a basic object
        return { isin: item, name: 'לא זמין', type: 'לא מוגדר', page: 'לא זמין', confidence: null };
      }
      // Ensure default values for missing properties
      return {
        isin: item.isin || 'לא זמין',
        name: item.name || 'לא זמין',
        type: item.type || 'לא מוגדר',
        page: item.page !== undefined ? item.page + 1 : 'לא זמין', // Adjust page index if needed (assuming 0-based)
        confidence: item.confidence !== undefined ? item.confidence : null
      };
    });
  }, [data]);


  // עדכון המידע המסונן כאשר הנתונים, חיפוש או מיון משתנים
  useEffect(() => {
    let result = [...normalizedIsinData];

    // סינון לפי מונח חיפוש
    if (searchTerm && !isPreview) { // Don't filter in preview mode
      const lowerSearchTerm = searchTerm.toLowerCase();
      result = result.filter(item =>
        item.isin.toLowerCase().includes(lowerSearchTerm) ||
        item.name.toLowerCase().includes(lowerSearchTerm) ||
        item.type.toLowerCase().includes(lowerSearchTerm)
      );
    }

    // מיון הנתונים (only if not preview)
    if (sortConfig.key && !isPreview) {
      result.sort((a, b) => {
        const valA = a[sortConfig.key];
        const valB = b[sortConfig.key];

        // Handle null or undefined values during sort
        if (valA === null || valA === undefined) return 1;
        if (valB === null || valB === undefined) return -1;

        // Sort logic
        let comparison = 0;
        if (typeof valA === 'string' && typeof valB === 'string') {
          comparison = valA.localeCompare(valB, 'he'); // Locale compare for Hebrew strings
        } else if (typeof valA === 'number' && typeof valB === 'number') {
          comparison = valA - valB;
        } else {
          // Fallback comparison if types differ or are not string/number
          comparison = String(valA).localeCompare(String(valB), 'he');
        }

        return sortConfig.direction === 'asc' ? comparison : comparison * -1;
      });
    }

    setFilteredData(isPreview ? result.slice(0, 5) : result); // Limit rows in preview mode

  }, [normalizedIsinData, searchTerm, sortConfig, isPreview]);

  // פונקציה לשינוי הגדרות המיון
  const requestSort = (key) => {
    if (isPreview) return; // Disable sorting in preview
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // יצירת איקון מיון מתאים לעמודה
  const getSortIcon = (columnName) => {
    if (isPreview || sortConfig.key !== columnName) {
      return <i className="fas fa-sort sort-icon"></i>; // Default sort icon
    }
    return sortConfig.direction === 'asc'
      ? <i className="fas fa-sort-up sort-icon active"></i>
      : <i className="fas fa-sort-down sort-icon active"></i>;
  };

  // אם הנתונים בטעינה, הצג אינדיקטור טעינה
  if (loading) {
    return (
      <div className="isin-table-loading">
        <div className="loading-spinner"></div>
        <p>טוען נתוני ISIN...</p>
      </div>
    );
  }

  // אם אין נתונים לאחר הטעינה, הצג הודעה
  if (!loading && (!normalizedIsinData || normalizedIsinData.length === 0)) {
    return (
      <div className="isin-table-empty">
        <i className="fas fa-info-circle"></i>
        <p>לא זוהו קודי ISIN במסמך זה</p>
      </div>
    );
  }

  return (
    <div className={`isin-table-container ${isPreview ? 'preview-mode' : ''}`}>
      {!isPreview && (
        <div className="isin-table-header">
          <h3>קודי ISIN שזוהו ({normalizedIsinData.length})</h3>
          <div className="isin-table-search">
            <i className="fas fa-search search-icon"></i>
            <input
              type="text"
              placeholder="חיפוש קוד, שם או סוג..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
             {searchTerm && (
                 <button className="clear-search-icon" onClick={() => setSearchTerm('')} title="נקה חיפוש">
                     <i className="fas fa-times"></i>
                 </button>
             )}
          </div>
        </div>
      )}

      <div className="isin-table-wrapper">
        <table className="isin-table">
          <thead>
            <tr>
              <th onClick={() => requestSort('isin')} className={!isPreview ? 'sortable' : ''}>
                קוד ISIN {!isPreview && getSortIcon('isin')}
              </th>
              <th onClick={() => requestSort('name')} className={!isPreview ? 'sortable' : ''}>
                שם {!isPreview && getSortIcon('name')}
              </th>
              <th onClick={() => requestSort('type')} className={!isPreview ? 'sortable' : ''}>
                סוג {!isPreview && getSortIcon('type')}
              </th>
              {!isPreview && ( // Show page only in full view
                <th onClick={() => requestSort('page')} className="sortable">
                  עמוד {getSortIcon('page')}
                </th>
              )}
              <th onClick={() => requestSort('confidence')} className={!isPreview ? 'sortable' : ''}>
                רמת ביטחון {!isPreview && getSortIcon('confidence')}
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map((item, index) => (
              <tr key={item.isin + '-' + index} className={item.confidence !== null && item.confidence >= 0.8 ? 'high-confidence' : item.confidence !== null ? 'low-confidence' : ''}>
                <td className="isin-code">{item.isin}</td>
                <td>{item.name}</td>
                <td>{item.type}</td>
                {!isPreview && (
                    <td>{item.page}</td>
                )}
                <td className="confidence-cell">
                  {item.confidence !== null ? (
                    <>
                      <div className="confidence-value">
                        {`${Math.round(item.confidence * 100)}%`}
                      </div>
                      <div className="confidence-bar-container">
                        <div
                          className="confidence-bar"
                          style={{ width: `${item.confidence * 100}%` }}
                        ></div>
                      </div>
                    </>
                  ) : (
                    <span className="confidence-na">לא זמין</span>
                  )}
                </td>
              </tr>
            ))}
             {/* Show message if search yields no results */}
             {!isPreview && searchTerm && filteredData.length === 0 && (
                 <tr>
                     <td colSpan={5} className="no-results-message">לא נמצאו תוצאות התואמות לחיפוש.</td>
                 </tr>
             )}
          </tbody>
        </table>
      </div>

      {!isPreview && (
        <div className="isin-table-footer">
          <span>
            מציג {filteredData.length} מתוך {normalizedIsinData.length} קודי ISIN
            {searchTerm && ` (מסונן לפי "${searchTerm}")`}
          </span>
          {searchTerm && (
            <button
              className="clear-search-button"
              onClick={() => setSearchTerm('')}
            >
              נקה חיפוש
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default ISINTable;