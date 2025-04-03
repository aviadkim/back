import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DocumentHeader from '../components/documents/DocumentHeader';
import DocumentTabs from '../components/documents/DocumentTabs';
import DocumentViewer from '../components/documents/DocumentViewer';
import TableView from '../components/documents/TableView';
import ISINTable from '../components/documents/ISINTable';
import FinancialMetrics from '../components/documents/FinancialMetrics';
import DocumentChat from '../components/documents/DocumentChat';
import ExtractedDataView from '../components/documents/ExtractedDataView'; // Assuming this combines ISIN/Metrics/etc.
import documentService from '../services/documentService';
import tableService from '../services/tableService'; // Assuming this exists for export
import './DocumentDetailPage.css';

/**
 * דף פרטי מסמך ספציפי
 */
const DocumentDetailPage = () => {
  const { documentId } = useParams();
  const navigate = useNavigate();
  const [document, setDocument] = useState(null); // Holds the entire document object { metadata, processed_data, document_url }
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // Default tab
  // Removed separate tables state, assuming tables are within document.processed_data.tables
  // const [tables, setTables] = useState([]);
  // const [tablesLoading, setTablesLoading] = useState(false);

  // Fetch document data function
  const fetchDocument = useCallback(async () => {
    if (!documentId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await documentService.getDocument(documentId);
      setDocument(data);

      // Optional: Add polling logic if status is 'processing'
      if (data?.metadata?.status === 'processing') {
        // Example: setTimeout(fetchDocument, 5000); // Poll again after 5s
        console.log("Document processing, consider implementing polling...");
      }

    } catch (err) {
      console.error('Error fetching document:', err);
      setError(`אירעה שגיאה בטעינת המסמך: ${err.message}.`);
      setDocument(null); // Clear document data on error
    } finally {
      setLoading(false);
    }
  }, [documentId]); // Dependency on documentId

  // טעינת פרטי המסמך בעת טעינת הדף או שינוי ID
  useEffect(() => {
    fetchDocument();
    // Add cleanup for polling if implemented
    // return () => clearTimeout(pollingTimeoutId);
  }, [fetchDocument]); // Use the memoized fetchDocument function


  // טיפול בלחיצה על כפתור "חזרה לרשימה"
  const handleBackClick = () => {
    navigate('/documents');
  };

  // טיפול בייצוא טבלה
  const handleExportTable = async (tableId, format) => {
    // Note: tableId might need adjustment based on how tables are identified (e.g., index or actual ID from data)
    try {
      // Assuming tableService.exportTable handles the download directly
      tableService.exportTable(tableId, format);
    } catch (err) {
      console.error('Error exporting table:', err);
      // Show error message to the user (e.g., using a toast notification library)
      alert(`שגיאה בייצוא הטבלה: ${err.message}`);
    }
  };

  // תצוגת טעינה ראשונית
  if (loading && !document) {
    return (
      <div className="document-detail-page loading">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>טוען נתוני מסמך...</p>
        </div>
      </div>
    );
  }

  // תצוגת שגיאה אם הטעינה הראשונית נכשלה
  if (error && !document) {
    return (
      <div className="document-detail-page error">
        <div className="error-container">
          <i className="fas fa-exclamation-circle"></i>
          <h2>שגיאה בטעינת המסמך</h2>
          <p>{error}</p>
          <button className="back-button btn-secondary" onClick={handleBackClick}> {/* Added btn class */}
            חזרה לרשימת המסמכים
          </button>
        </div>
      </div>
    );
  }

  // If document data exists (even if processing or error status)
  const { metadata = {}, processed_data = {}, document_url } = document || {};
  const { text_content = "", tables = [], financial_metrics = {}, isin_data = [] } = processed_data; // Use defaults
  const isProcessing = metadata?.status === 'processing';
  const hasErrorStatus = metadata?.status === 'error';

  // Function to render tab content
  const renderTabContent = () => {
      if (isProcessing && activeTab !== 'original') { // Show processing message for most tabs
          return (
              <div className="processing-notice tab-processing">
                  <i className="fas fa-spinner fa-spin"></i>
                  <p>המסמך עדיין בעיבוד. נתונים עבור לשונית זו יוצגו בסיום העיבוד.</p>
              </div>
          );
      }
      if (hasErrorStatus && activeTab !== 'original') { // Show error message for most tabs
           return (
               <div className="error-message tab-error">
                   <i className="fas fa-exclamation-triangle"></i>
                   <p>אירעה שגיאה בעיבוד מסמך זה: {metadata.error_message || 'שגיאה לא ידועה'}</p>
               </div>
           );
       }

      // Render content based on active tab
      switch (activeTab) {
          case 'overview':
              // ExtractedDataView now likely handles ISIN/Metrics internally based on props
              return <ExtractedDataView document={document} />;
          case 'tables':
              // Pass the tables array directly from processed_data
              return <TableView tables={tables} loading={false} onExport={handleExportTable} />;
          case 'entities': // Assuming ISIN is the primary entity for now
              return <ISINTable isinData={isin_data} loading={false} />;
          case 'metrics':
              // Pass the financial_metrics object
              return <FinancialMetrics data={financial_metrics} loading={false} />;
          case 'chat':
              return <DocumentChat documentId={documentId} />;
          case 'original':
              // Pass URL and the full document object for context (like page count)
              return <DocumentViewer documentUrl={document_url} document={document} />;
          default:
              return <ExtractedDataView document={document} />; // Fallback to overview
      }
  };


  return (
    <div className="document-detail-page">
      {/* Pass only metadata to header */}
      <DocumentHeader document={metadata} onBack={handleBackClick} />

      {/* Pass status to tabs for potential disabling */}
      <DocumentTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
          documentStatus={metadata?.status}
      />

      <div className="document-content">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default DocumentDetailPage;