import React, { useState, useEffect } from 'react';
import TableGenerator from '../tables/TableGenerator'; // Assuming this component exists
import './TableView.css';

/**
 * רכיב להצגת טבלאות שחולצו מהמסמך
 * @param {Object} props - מאפייני הרכיב
 * @param {Array} props.tables - מערך הטבלאות שחולצו (מ-processed_data.tables)
 * @param {boolean} props.loading - האם הנתונים בטעינה (כללי או ספציפי לטבלאות)
 * @param {Function} props.onExport - פונקציה להפעלה בעת ייצוא טבלה (מקבלת tableId, format)
 */
const TableView = ({ tables = [], loading = false, onExport }) => {
  const [activeTableIndex, setActiveTableIndex] = useState(0);

  // Reset active index if tables change and current index is out of bounds
  useEffect(() => {
    if (activeTableIndex >= tables.length) {
      setActiveTableIndex(tables.length > 0 ? 0 : -1); // Set to -1 if no tables
    }
  }, [tables, activeTableIndex]);


  // אם הנתונים בטעינה, הצג אינדיקטור טעינה
  if (loading) {
    return (
      <div className="table-view-loading">
        <div className="loading-spinner"></div>
        <p>טוען טבלאות...</p>
      </div>
    );
  }

  // אם אין טבלאות לאחר הטעינה, הצג הודעה
  if (!loading && (!tables || tables.length === 0)) {
    return (
      <div className="table-view-empty">
        <i className="fas fa-table"></i> {/* Use Font Awesome */}
        <p>לא זוהו טבלאות במסמך זה</p>
      </div>
    );
  }

  // Ensure activeTableIndex is valid
  const currentTableIndex = (activeTableIndex >= 0 && activeTableIndex < tables.length) ? activeTableIndex : 0;
  const activeTable = tables[currentTableIndex];

  // פונקציה לייצוא הטבלה
  const handleExport = (format) => {
    // Use the table's unique identifier if available (e.g., table.id from Textract)
    // Otherwise, might need to pass index or other identifier to backend
    const tableIdToExport = activeTable?.id || `table_${currentTableIndex}`; // Fallback identifier
    if (onExport && activeTable) {
      onExport(tableIdToExport, format);
    } else {
        console.warn("Export function or active table not available.");
        // Optionally show a UI message
    }
  };

  // Handle table selection change
  const handleTableSelect = (e) => {
      const newIndex = Number(e.target.value);
      if (!isNaN(newIndex) && newIndex >= 0 && newIndex < tables.length) {
          setActiveTableIndex(newIndex);
      }
  };

  // Handle pagination
  const handlePrevTable = () => {
      setActiveTableIndex(prev => Math.max(0, prev - 1));
  };
  const handleNextTable = () => {
      setActiveTableIndex(prev => Math.min(tables.length - 1, prev + 1));
  };


  return (
    <div className="table-view">
      <div className="table-view-header">
        <h3>טבלאות שזוהו במסמך</h3>

        <div className="table-actions">
          {tables.length > 1 && ( // Show selector only if multiple tables
            <div className="table-selector">
              <label htmlFor="table-select">בחר טבלה:</label>
              <select
                id="table-select"
                value={currentTableIndex}
                onChange={handleTableSelect}
              >
                {tables.map((table, index) => (
                  <option key={table.id || index} value={index}>
                    {/* Generate a more descriptive name */}
                    טבלה {index + 1} (עמוד {table.pageNum !== undefined ? table.pageNum + 1 : 'לא ידוע'})
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="export-buttons">
            <button
              className="export-button"
              onClick={() => handleExport('csv')}
              title="ייצוא ל-CSV"
              disabled={!activeTable}
            >
              <i className="fas fa-file-csv"></i> CSV
            </button>
            <button
              className="export-button"
              onClick={() => handleExport('xlsx')}
              title="ייצוא ל-Excel"
              disabled={!activeTable}
            >
              <i className="fas fa-file-excel"></i> Excel
            </button>
            {/* JSON export might require different handling/endpoint */}
            {/*
            <button
              className="export-button"
              onClick={() => handleExport('json')}
              title="ייצוא ל-JSON"
              disabled={!activeTable}
            >
              <i className="fas fa-file-code"></i> JSON
            </button>
            */}
          </div>
        </div>
      </div>

      {activeTable && (
          <>
              <div className="table-metadata">
                <div className="metadata-item">
                  <span className="metadata-label">מיקום:</span>
                  <span className="metadata-value">עמוד {activeTable.pageNum !== undefined ? activeTable.pageNum + 1 : 'לא ידוע'}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">מספר שורות:</span>
                  <span className="metadata-value">{activeTable.row_count || activeTable.rows?.length || 0}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">מספר עמודות:</span>
                  <span className="metadata-value">{activeTable.col_count || activeTable.header?.length || 0}</span>
                </div>
                {/* Add other metadata if available, e.g., confidence */}
                {/*
                {activeTable.extraction_method && (
                  <div className="metadata-item">
                    <span className="metadata-label">שיטת חילוץ:</span>
                    <span className="metadata-value">{activeTable.extraction_method}</span>
                  </div>
                )}
                */}
              </div>

              <div className="table-wrapper">
                <TableGenerator
                  headers={activeTable.header || []}
                  rows={activeTable.rows || []}
                />
              </div>
          </>
      )}


      {tables.length > 1 && ( // Show pagination only if multiple tables
        <div className="table-view-footer">
          <div className="pagination">
            <span className="pagination-info">
              טבלה {currentTableIndex + 1} מתוך {tables.length}
            </span>
            <div className="pagination-buttons">
              <button
                className="pagination-button"
                onClick={handlePrevTable}
                disabled={currentTableIndex === 0}
                title="הטבלה הקודמת"
              >
                <i className="fas fa-chevron-right"></i> {/* Icon for previous in RTL */}
              </button>
              <button
                className="pagination-button"
                onClick={handleNextTable}
                disabled={currentTableIndex === tables.length - 1}
                title="הטבלה הבאה"
              >
                <i className="fas fa-chevron-left"></i> {/* Icon for next in RTL */}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TableView;