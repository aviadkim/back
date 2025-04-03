import React, { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * Table Extractor Component
 * 
 * Displays and provides tools for interacting with tables extracted from documents
 */
const TableExtractor = ({ documentId, documentName }) => {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [viewMode, setViewMode] = useState('default');
  const [generatedView, setGeneratedView] = useState(null);
  const [selectedTableIds, setSelectedTableIds] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Fetch tables when document ID changes
  useEffect(() => {
    if (documentId) {
      fetchTables();
    }
  }, [documentId]);
  
  // Fetch tables from the API
  const fetchTables = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`/api/tables/document/${documentId}`);
      setTables(response.data.tables || []);
      
      // Select the first table by default if available
      if (response.data.tables && response.data.tables.length > 0) {
        setSelectedTable(response.data.tables[0]);
        setSelectedTableIds([response.data.tables[0].id]);
      }
    } catch (error) {
      setError('שגיאה בטעינת הטבלאות. אנא נסה שוב.');
      console.error('Error fetching tables:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle table selection
  const handleTableSelect = (table) => {
    setSelectedTable(table);
    
    // Update selected table IDs as well
    if (!selectedTableIds.includes(table.id)) {
      setSelectedTableIds([...selectedTableIds, table.id]);
    }
  };
  
  // Handle table selection for comparison view
  const handleTableSelectToggle = (tableId) => {
    setSelectedTableIds(prev => {
      if (prev.includes(tableId)) {
        return prev.filter(id => id !== tableId);
      } else {
        return [...prev, tableId];
      }
    });
  };
  
  // Generate a specialized view
  const generateView = async () => {
    if (!selectedTableIds.length) return;
    
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.post('/api/tables/generate', {
        documentId,
        tableIds: selectedTableIds,
        format: viewMode,
        options: {
          name: viewMode === 'summary' ? 'תקציר מסמך' : 'השוואת נתונים'
        }
      });
      
      setGeneratedView(response.data.table);
    } catch (error) {
      setError('שגיאה ביצירת המבט. אנא נסה שוב.');
      console.error('Error generating view:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Export table in different formats
  const exportTable = async (format) => {
    if (!selectedTable) return;
    
    setIsLoading(true);
    
    try {
      const response = await axios.post('/api/tables/export', {
        documentId,
        tableId: selectedTable.id,
        format
      }, {
        responseType: format === 'xlsx' ? 'blob' : 'text'
      });
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${selectedTable.name || 'table'}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      setError(`שגיאה ביצוא הטבלה בפורמט ${format}. אנא נסה שוב.`);
      console.error('Error exporting table:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Render table selection sidebar
  const renderTableSelector = () => {
    if (!tables.length) {
      return (
        <div className="p-3 text-gray-500 text-center">
          {isLoading ? 'טוען טבלאות...' : 'לא נמצאו טבלאות במסמך זה'}
        </div>
      );
    }
    
    return (
      <div className="table-list">
        <h3 className="font-medium mb-2 text-gray-700">טבלאות במסמך:</h3>
        <ul className="space-y-1">
          {tables.map((table) => (
            <li key={table.id}>
              <button
                onClick={() => handleTableSelect(table)}
                className={`w-full text-start p-2 rounded text-sm ${
                  selectedTable?.id === table.id
                    ? 'bg-primary-100 text-primary-700'
                    : 'hover:bg-gray-100'
                }`}
              >
                <div className="font-medium">{table.name || `טבלה ${table.id}`}</div>
                <div className="text-xs text-gray-500">עמוד {table.page}</div>
              </button>
            </li>
          ))}
        </ul>
        
        {tables.length > 1 && (
          <div className="mt-6">
            <h3 className="font-medium mb-2 text-gray-700">מבטים מיוחדים:</h3>
            <div className="flex space-x-2">
              <button
                onClick={() => setViewMode('summary')}
                className={`px-3 py-1 rounded text-sm ${
                  viewMode === 'summary' ? 'bg-primary-600 text-white' : 'bg-gray-200'
                }`}
              >
                תקציר
              </button>
              <button
                onClick={() => setViewMode('comparison')}
                className={`px-3 py-1 rounded text-sm ${
                  viewMode === 'comparison' ? 'bg-primary-600 text-white' : 'bg-gray-200'
                }`}
              >
                השוואה
              </button>
            </div>
            
            {(viewMode === 'summary' || viewMode === 'comparison') && (
              <div className="mt-3">
                <p className="text-sm text-gray-600 mb-2">
                  {viewMode === 'summary' 
                    ? 'בחר טבלאות לתקציר:' 
                    : 'בחר טבלאות להשוואה:'}
                </p>
                <div className="space-y-1">
                  {tables.map((table) => (
                    <div key={table.id} className="flex items-center">
                      <input
                        type="checkbox"
                        id={`table-check-${table.id}`}
                        checked={selectedTableIds.includes(table.id)}
                        onChange={() => handleTableSelectToggle(table.id)}
                        className="mx-2"
                      />
                      <label htmlFor={`table-check-${table.id}`} className="text-sm">
                        {table.name || `טבלה ${table.id}`}
                      </label>
                    </div>
                  ))}
                </div>
                <button
                  onClick={generateView}
                  disabled={selectedTableIds.length === 0 || isLoading}
                  className="mt-3 px-3 py-1 bg-primary-600 text-white rounded text-sm disabled:opacity-50"
                >
                  {isLoading ? 'מעבד...' : 'יצירת מבט'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };
  
  // Render the main table view
  const renderTableView = () => {
    if (!selectedTable && !generatedView) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          {isLoading ? 'טוען נתונים...' : 'יש לבחור טבלה כדי להציגה'}
        </div>
      );
    }
    
    if (generatedView) {
      if (generatedView.type === 'summary') {
        return renderSummaryView();
      } else if (generatedView.type === 'comparison') {
        return renderComparisonView();
      }
    }
    
    // Render the standard table
    return (
      <div className="standard-table-view">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-primary-700">
            {selectedTable.name || `טבלה ${selectedTable.id}`}
          </h2>
          <div className="export-buttons flex space-x-2">
            <button
              onClick={() => exportTable('csv')}
              className="px-3 py-1 bg-gray-200 rounded text-sm hover:bg-gray-300"
            >
              יצוא ל-CSV
            </button>
            <button
              onClick={() => exportTable('json')}
              className="px-3 py-1 bg-gray-200 rounded text-sm hover:bg-gray-300"
            >
              יצוא ל-JSON
            </button>
          </div>
        </div>
        
        <div className="table-container overflow-x-auto border rounded">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {selectedTable.header.map((header, index) => (
                  <th
                    key={index}
                    className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {selectedTable.rows.map((row, rowIndex) => (
                <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };
  
  // Render summary view
  const renderSummaryView = () => {
    return (
      <div className="summary-view">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-primary-700">
            {generatedView.name}
          </h2>
          <button
            onClick={() => setGeneratedView(null)}
            className="px-3 py-1 bg-gray-200 rounded text-sm hover:bg-gray-300"
          >
            חזרה לטבלה
          </button>
        </div>
        
        <div className="metrics-grid grid grid-cols-1 md:grid-cols-2 gap-4">
          {generatedView.metrics.map((metric, index) => (
            <div key={index} className="metric-card p-4 border rounded-lg bg-white shadow-sm">
              <div className="text-xs text-gray-500 uppercase">{metric.category}</div>
              <div className="flex justify-between items-center mt-1">
                <div className="font-medium">{metric.name}</div>
                <div className="text-lg font-bold text-primary-700">{metric.value}</div>
              </div>
              {metric.additional && (
                <div className="text-sm text-gray-600 mt-1">{metric.additional}</div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  // Render comparison view
  const renderComparisonView = () => {
    return (
      <div className="comparison-view">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-primary-700">
            {generatedView.name}
          </h2>
          <button
            onClick={() => setGeneratedView(null)}
            className="px-3 py-1 bg-gray-200 rounded text-sm hover:bg-gray-300"
          >
            חזרה לטבלה
          </button>
        </div>
        
        {generatedView.error ? (
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
            {generatedView.error}
          </div>
        ) : (
          <div className="comparison-table-container overflow-x-auto border rounded">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    קטגוריה
                  </th>
                  {generatedView.tables.map((table) => (
                    <th
                      key={table.id}
                      className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {table.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {generatedView.comparison_data.map((row, rowIndex) => (
                  <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {row.category}
                    </td>
                    {row.values.map((value, valueIndex) => (
                      <td key={valueIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div>{value.value}</div>
                        {value.additional && (
                          <div className="text-xs text-gray-500">{value.additional}</div>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className="table-extractor-container bg-white rounded-lg shadow-md h-full">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 m-4 rounded">
          {error}
          <button 
            onClick={() => setError('')}
            className="float-left text-red-700 font-bold"
          >
            &times;
          </button>
        </div>
      )}
      
      <div className="p-4 border-b">
        <h2 className="text-xl font-semibold text-primary-700">
          טבלאות במסמך: {documentName || documentId}
        </h2>
      </div>
      
      <div className="flex h-[calc(100%-4rem)]">
        <div className="table-sidebar w-1/4 p-4 border-l overflow-y-auto">
          {renderTableSelector()}
        </div>
        
        <div className="table-content w-3/4 p-4 overflow-y-auto">
          {renderTableView()}
        </div>
      </div>
    </div>
  );
};

export default TableExtractor;
