// src/components/tables/CustomTableGenerator.jsx
import React, { useState, useEffect } from 'react';
import TableGenerator from './TableGenerator'; // Import the display component
import './CustomTableGenerator.css';

function CustomTableGenerator({ documentId }) {
  const [documentData, setDocumentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tableName, setTableName] = useState('טבלה מותאמת אישית');
  const [availableColumns, setAvailableColumns] = useState([]);
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [filters, setFilters] = useState([]);
  const [filterType, setFilterType] = useState('simple'); // 'simple' or 'advanced'
  const [generatedTable, setGeneratedTable] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState(null); // Specific error for generation

  // טעינת פרטי המסמך
  useEffect(() => {
    const fetchDocumentData = async () => {
      setLoading(true);
      setError(null);
      setAvailableColumns([]); // Reset columns on new document ID
      setSelectedColumns([]);
      setFilters([]);
      setGeneratedTable(null);
      setGenerationError(null);

      try {
        // Use the AWS endpoint to get full document details
        const response = await fetch(`/api/aws/documents/${documentId}`);

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'שגיאה בטעינת נתוני המסמך');
        }

        const data = await response.json();
        setDocumentData(data);

        // חילוץ עמודות זמינות only if processing is complete
        if (data?.metadata?.status === 'completed' && data.processed_data) {
             extractAvailableColumns(data.processed_data);
        } else if (data?.metadata?.status === 'processing') {
            setError("המסמך עדיין בעיבוד. לא ניתן ליצור טבלה מותאמת כעת.");
        } else if (data?.metadata?.status === 'error') {
            setError(`שגיאה בעיבוד המסמך המקורי: ${data.metadata.error_message || 'שגיאה לא ידועה'}`);
        } else {
            setError("לא נמצאו נתונים מעובדים עבור מסמך זה.");
        }

      } catch (error) {
        console.error('Error fetching document data:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    if (documentId) {
        fetchDocumentData();
    } else {
        setLoading(false); // No document ID, nothing to load
    }

  }, [documentId]); // Rerun when documentId changes

  // פונקציה לחילוץ עמודות זמינות לבחירה
  const extractAvailableColumns = (data) => {
    const columns = new Map(); // Use Map to avoid duplicates by ID

    const addColumn = (col) => {
        if (!columns.has(col.id)) {
            columns.set(col.id, col);
        }
    };

    // עמודות מקודי ISIN (assuming ai_analysis structure)
    if (data.ai_analysis?.isin_codes && Array.isArray(data.ai_analysis.isin_codes)) {
        // Assuming isin_codes is an array of strings for now
        // If it's an array of objects, adapt this part
        addColumn({
            id: `isin_code`,
            name: 'ISIN Code',
            group: 'AI Analysis',
            type: 'string'
        });
        // Example if it were objects:
        // data.ai_analysis.isin_codes.forEach(item => {
        //     if (typeof item === 'object' && item !== null) {
        //         Object.keys(item).forEach(key => {
        //             addColumn({ id: `isin_${key}`, name: key, group: 'ISIN', type: typeof item[key] });
        //         });
        //     }
        // });
    }

    // עמודות ממדדים פיננסיים (assuming ai_analysis structure)
     if (data.ai_analysis?.financial_metrics && typeof data.ai_analysis.financial_metrics === 'object') {
         Object.keys(data.ai_analysis.financial_metrics).forEach(key => {
             addColumn({
                 id: `metric_${key}`,
                 name: key, // Use the metric key as name
                 group: 'Financial Metrics (AI)',
                 type: typeof data.ai_analysis.financial_metrics[key]
             });
         });
     }

    // עמודות מטבלאות
    if (data.tables && typeof data.tables === 'object') {
      Object.entries(data.tables).forEach(([pageNum, pageTables]) => {
        if (Array.isArray(pageTables)) {
            pageTables.forEach((table, tableIndex) => {
              // Use uniqueId if available, otherwise generate one
              const tableUniqueId = table.uniqueId || table.id || `page-${pageNum}-table-${tableIndex}`;
              if (table.header && Array.isArray(table.header)) {
                table.header.forEach((header, colIndex) => {
                  if (header && typeof header === 'string' && header.trim() !== '') { // Ensure header is valid
                      addColumn({
                        id: `table_${tableUniqueId}_col_${colIndex}`, // More robust ID
                        name: header.trim(),
                        group: `טבלה (עמ' ${parseInt(pageNum) + 1})`,
                        type: 'string', // Assume string initially
                        tableId: tableUniqueId,
                        columnIndex: colIndex
                      });
                  }
                });
              }
            });
        }
      });
    }

    setAvailableColumns(Array.from(columns.values()));
  };

  // הוספת עמודה
  const addColumn = (column) => {
    // Avoid adding duplicates
    if (!selectedColumns.some(sc => sc.id === column.id)) {
        setSelectedColumns(prev => [...prev, column]);
    }
  };

  // הסרת עמודה
  const removeColumn = (columnId) => {
    setSelectedColumns(prev => prev.filter(col => col.id !== columnId));
  };

  // הוספת פילטר
  const addFilter = () => {
    const newFilter = {
      id: Date.now().toString(),
      column: availableColumns.length > 0 ? availableColumns[0].id : '',
      operator: 'equals',
      value: ''
    };
    setFilters(prev => [...prev, newFilter]);
  };

  // הסרת פילטר
  const removeFilter = (filterId) => {
    setFilters(prev => prev.filter(filter => filter.id !== filterId));
  };

  // עדכון פילטר
  const updateFilter = (filterId, field, value) => {
    setFilters(prev => prev.map(filter =>
      filter.id === filterId ? { ...filter, [field]: value } : filter
    ));
  };

  // שליחת בקשה ליצירת טבלה מותאמת אישית
  const generateTable = async () => {
    if (selectedColumns.length === 0) {
      alert('יש לבחור לפחות עמודה אחת');
      return;
    }

    setIsGenerating(true);
    setGenerationError(null); // Reset previous errors
    setGeneratedTable(null); // Clear previous results

    try {
      const requestData = {
        name: tableName,
        // Send only the IDs of selected columns
        columns: selectedColumns.map(col => ({ id: col.id, name: col.name, group: col.group })), // Send more info if needed by backend
        filter: {
          type: filterType,
          conditions: filters.map(filter => ({
            column_id: filter.column, // Match backend expectation (e.g., column_id)
            operator: filter.operator,
            value: filter.value
          }))
        }
      };

      // *** IMPORTANT: This endpoint `/api/documents/${documentId}/custom-table`
      // *** does not exist in the backend code provided earlier.
      // *** You will need to implement this endpoint in Flask (e.g., in aws_routes.py or a new file).
      // *** The backend logic will need to interpret the column IDs and filters
      // *** to query/process data from DynamoDB or S3/Textract results.
      const response = await fetch(`/api/aws/documents/${documentId}/custom-table`, { // Using AWS prefix tentatively
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'שגיאה ביצירת הטבלה');
      }

      const data = await response.json();
      // Assuming the backend returns data in the format { table_id: '...', table_name: '...', data: { columns: [...], data: [...] } }
      setGeneratedTable(data);
    } catch (error) {
      console.error('Error generating custom table:', error);
      setGenerationError(`שגיאה ביצירת הטבלה: ${error.message}. ודא שנקודת הקצה /api/aws/documents/${documentId}/custom-table קיימת ומטפלת בבקשה.`);
    } finally {
      setIsGenerating(false);
    }
  };

  // ייצוא הטבלה (Needs backend endpoint)
  const exportTable = (format) => {
    if (!generatedTable || !generatedTable.table_id) {
        alert("אין טבלה שנוצרה לייצא.");
        return;
    }
    // *** IMPORTANT: This endpoint `/api/tables/${generatedTable.table_id}/export`
    // *** likely needs to be implemented on the backend as well.
    window.location.href = `/api/aws/tables/${generatedTable.table_id}/export?format=${format}`; // Using AWS prefix tentatively
  };

  if (loading) {
    return (
      <div className="custom-table-generator loading">
        <div className="loading-indicator">
          <i className="icon-loading spin"></i>
          <span>טוען נתוני מסמך...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="custom-table-generator error">
        <div className="error-message">
          <i className="icon-error"></i>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="custom-table-generator">
      <div className="generator-options">
        {/* Table Name Input */}
        <div className="generator-section">
          <h3>שם הטבלה</h3>
          <input
            type="text"
            value={tableName}
            onChange={(e) => setTableName(e.target.value)}
            placeholder="הזן שם לטבלה"
            className="table-name-input"
          />
        </div>

        {/* Column Selection */}
        <div className="generator-section">
          <h3>בחירת עמודות</h3>
          <div className="columns-container">
            <div className="available-columns">
              <h4>עמודות זמינות ({availableColumns.length})</h4>
              <div className="columns-list scrollable">
                {availableColumns.length > 0 ? availableColumns.map((column) => (
                  <div
                    key={column.id}
                    className={`column-item ${selectedColumns.some(sc => sc.id === column.id) ? 'disabled' : ''}`} // Disable if already selected
                    onClick={() => addColumn(column)}
                    title={`Group: ${column.group}\nType: ${column.type}`} // Add tooltip
                  >
                    <div className="column-name">{column.name}</div>
                    <div className="column-group">{column.group}</div>
                    <button className="btn-add" disabled={selectedColumns.some(sc => sc.id === column.id)}>
                      <i className="icon-plus"></i>
                    </button>
                  </div>
                )) : <p>אין עמודות זמינות.</p>}
              </div>
            </div>

            <div className="selected-columns">
              <h4>עמודות נבחרות ({selectedColumns.length})</h4>
              {selectedColumns.length === 0 ? (
                <div className="empty-selection">
                  <p>גרור עמודות לכאן או לחץ על '+'</p>
                </div>
              ) : (
                <div className="columns-list scrollable">
                  {selectedColumns.map((column) => (
                    <div key={column.id} className="column-item selected">
                      <div className="column-name">{column.name}</div>
                      <div className="column-group">{column.group}</div>
                      <button
                        className="btn-remove"
                        onClick={() => removeColumn(column.id)}
                      >
                        <i className="icon-minus"></i>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Filters Section */}
        <div className="generator-section">
          <h3>פילטרים (אופציונלי)</h3>
          {/* Filter Type Selector (Optional) */}
          {/*
          <div className="filter-type-selector">
             <label><input type="radio" name="filterType" value="simple" checked={filterType === 'simple'} onChange={() => setFilterType('simple')}/> פילטר פשוט</label>
             <label><input type="radio" name="filterType" value="advanced" checked={filterType === 'advanced'} onChange={() => setFilterType('advanced')}/> פילטר מתקדם</label>
          </div>
          */}
          <div className="filters-list">
            {filters.map((filter) => (
              <div key={filter.id} className="filter-item">
                <select
                  value={filter.column}
                  onChange={(e) => updateFilter(filter.id, 'column', e.target.value)}
                  className="filter-select"
                >
                  <option value="">-- בחר עמודה --</option>
                  {/* Populate options from selected columns or available columns */}
                  {availableColumns.map((column) => (
                    <option key={column.id} value={column.id}>
                      {column.name} ({column.group})
                    </option>
                  ))}
                </select>

                <select
                  value={filter.operator}
                  onChange={(e) => updateFilter(filter.id, 'operator', e.target.value)}
                   className="filter-select"
                >
                  <option value="equals">שווה ל</option>
                  <option value="not_equals">לא שווה ל</option>
                  <option value="contains">מכיל</option>
                  <option value="greater_than">גדול מ</option>
                  <option value="less_than">קטן מ</option>
                  {/* Add more operators as needed */}
                </select>

                <input
                  type="text"
                  value={filter.value}
                  onChange={(e) => updateFilter(filter.id, 'value', e.target.value)}
                  placeholder="ערך לסינון"
                  className="filter-input"
                />

                <button
                  className="btn-remove-filter"
                  onClick={() => removeFilter(filter.id)}
                  title="הסר פילטר"
                >
                  <i className="icon-trash"></i>
                </button>
              </div>
            ))}

            <button className="btn-add-filter" onClick={addFilter} disabled={availableColumns.length === 0}>
              <i className="icon-plus"></i> הוסף פילטר
            </button>
          </div>
        </div>

        {/* Action Button */}
        <div className="generator-actions">
          <button
            className="btn-primary generate-btn"
            onClick={generateTable}
            disabled={isGenerating || selectedColumns.length === 0}
          >
            {isGenerating ? (
              <>
                <i className="icon-loading spin"></i> מייצר טבלה...
              </>
            ) : (
              <>
                <i className="icon-table-generate"></i> צור טבלה מותאמת
              </>
            )}
          </button>
        </div>
      </div>

      {/* Display Generation Error */}
       {generationError && (
           <div className="generator-error error-message">
               <i className="icon-error"></i>
               <p>{generationError}</p>
           </div>
       )}


      {/* Display Generated Table */}
      {generatedTable && generatedTable.data && (
        <div className="generator-result">
          <div className="result-header">
            <h3>תוצאה: {generatedTable.table_name || tableName}</h3>
            <div className="export-options">
              <div className="dropdown">
                <button className="btn-secondary dropdown-toggle">
                  <i className="icon-export"></i> ייצוא
                </button>
                <div className="dropdown-menu">
                  <button onClick={() => exportTable('csv')}>CSV</button>
                  <button onClick={() => exportTable('excel')}>Excel</button>
                  <button onClick={() => exportTable('json')}>JSON</button>
                </div>
              </div>
            </div>
          </div>

          <div className="table-container">
            {/* Use the TableGenerator component to display the result */}
            <TableGenerator
                headers={generatedTable.data.columns || []}
                rows={generatedTable.data.data || []}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default CustomTableGenerator;