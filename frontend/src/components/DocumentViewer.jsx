import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Tabs, Tab, Spinner, Alert, Button, Card } from 'react-bootstrap';
import { Document, Page, pdfjs } from 'react-pdf'; // Import pdfjs
import axios from 'axios';
import './DocumentViewer.css';

// Configure PDF.js worker
// You might need to adjust the path depending on your setup or use a CDN
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;


const DocumentViewer = () => {
  const { documentId } = useParams();
  const [documentInfo, setDocumentInfo] = useState(null); // Renamed from 'document' to avoid conflict
  const [extractedData, setExtractedData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [activeTab, setActiveTab] = useState('original');

  useEffect(() => {
    const fetchDocument = async () => {
      setLoading(true);
      setError(null); // Reset error on new fetch
      try {
        // Fetch document metadata and extracted data together
        // Assuming the backend endpoint /api/documents/<id> now returns everything
        const response = await axios.get(`/api/documents/${documentId}`);
        
        if (response.data) {
             setDocumentInfo(response.data.metadata || {}); // Extract metadata
             setExtractedData(response.data.processing_result || {}); // Extract processing results
        } else {
             throw new Error("Document data not found in response");
        }

        setLoading(false);
      } catch (err) {
        console.error('Error fetching document:', err);
        // More specific error messages
        if (err.response && err.response.status === 404) {
             setError(`Document with ID ${documentId} not found.`);
        } else {
             setError('Failed to load document data. Please check the API connection and try again.');
        }
        setLoading(false);
      }
    };

    if (documentId) {
      fetchDocument();
    } else {
         setError("No document ID provided.");
         setLoading(false);
    }
  }, [documentId]);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setPageNumber(1); // Reset to first page on new document load
  };

  const handlePageChange = (offset) => {
    setPageNumber(prevPageNumber => {
      const newPageNumber = prevPageNumber + offset;
      // Ensure newPageNumber stays within bounds [1, numPages]
      return Math.min(Math.max(1, newPageNumber), numPages || 1);
    });
  };

  // --- Rendering Functions ---

  const renderOriginalDocument = () => {
     // Construct the URL to fetch the PDF file itself
     // This might need adjustment based on how files are served
     const pdfFileUrl = `/api/documents/${documentId}/file`; // Assuming an endpoint to serve the file

     return (
          <div className="pdf-container">
          <Document
               file={pdfFileUrl}
               onLoadSuccess={onDocumentLoadSuccess}
               onLoadError={(pdfError) => {
                    console.error("Error loading PDF:", pdfError);
                    setError(`Failed to load PDF document. Check if the file exists at ${pdfFileUrl}. Error: ${pdfError.message}`);
               }}
               loading={<Spinner animation="border" />}
               // Removed error prop here, handled by onLoadError
          >
               <Page
               pageNumber={pageNumber}
               renderTextLayer={true} // Enable text selection
               renderAnnotationLayer={false} // Disable annotations for cleaner view
               scale={1.2} // Adjust scale as needed
               />
          </Document>
          
          {numPages && ( // Only show navigation if numPages is known
               <div className="pdf-navigation">
               <Button 
                    variant="outline-primary" 
                    onClick={() => handlePageChange(-1)} 
                    disabled={pageNumber <= 1}
                    size="sm"
               >
                    Previous
               </Button>
               <span className="page-info">
                    Page {pageNumber} of {numPages}
               </span>
               <Button 
                    variant="outline-primary" 
                    onClick={() => handlePageChange(1)} 
                    disabled={pageNumber >= numPages}
                    size="sm"
               >
                    Next
               </Button>
               </div>
          )}
          </div>
     );
  }

  const renderExtractedText = () => {
    // Assuming extractedData.full_text contains the text, possibly with page markers
    // Or adapt if text is per-page in extractedData.pages
    if (!extractedData || !extractedData.full_text) {
      return <Alert variant="info">No extracted text available for this document.</Alert>;
    }

    // Simple display of full text for now
    // Could be enhanced to show text for the current pageNumber if available
    return (
      <Card className="text-viewer">
        <Card.Header>Full Extracted Text</Card.Header>
        <Card.Body>
          <pre className="extracted-text">{extractedData.full_text}</pre>
        </Card.Body>
      </Card>
    );
  };

  const renderExtractedTables = () => {
     // Assuming extractedData.tables is a dictionary { page_num_str: [table_data] }
     if (!extractedData || !extractedData.tables || Object.keys(extractedData.tables).length === 0) {
       return <Alert variant="info">No tables detected in this document.</Alert>;
     }
 
     // Get tables for the current page (adjust pageNumber to be string key)
     const currentPageTables = extractedData.tables[String(pageNumber)] || [];
 
     if (currentPageTables.length === 0) {
       return <Alert variant="info">No tables detected on page {pageNumber}.</Alert>;
     }
 
     return (
       <div className="tables-container">
         {currentPageTables.map((table, index) => (
           <Card key={table.id || index} className="mb-3">
             <Card.Header>Table {index + 1} (Page {table.page})</Card.Header>
             <Card.Body>
               <div className="table-responsive">
                 <table className="table table-bordered table-striped table-sm">
                   {table.header && table.header.length > 0 && (
                     <thead>
                       <tr>
                         {table.header.map((cell, cellIndex) => (
                           <th key={cellIndex}>{cell}</th>
                         ))}
                       </tr>
                     </thead>
                   )}
                   {table.data && table.data.length > 0 && (
                      <tbody>
                        {table.data.map((row, rowIndex) => (
                          <tr key={rowIndex}>
                            {row.map((cell, cellIndex) => (
                              <td key={cellIndex}>{cell}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                   )}
                 </table>
               </div>
             </Card.Body>
           </Card>
         ))}
       </div>
     );
   };

   const renderFinancialData = () => {
     // Assuming extractedData.entities and extractedData.ratios hold the relevant data
     const entities = extractedData.entities || {};
     const ratios = extractedData.ratios || {};
 
     const hasEntities = Object.values(entities).some(list => list && list.length > 0);
     const hasRatios = Object.keys(ratios).length > 0;
 
     if (!hasEntities && !hasRatios) {
       return <Alert variant="info">No specific financial data (entities or ratios) extracted.</Alert>;
     }
 
     return (
       <div className="financial-data">
         {/* Display Entities */}
         {hasEntities && (
           <Card className="mb-3">
             <Card.Header>Extracted Entities</Card.Header>
             <Card.Body>
               {Object.entries(entities).map(([type, list]) => (
                 list && list.length > 0 && (
                   <div key={type} className="mb-2">
                     <strong>{type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                     <ul className="list-inline">
                       {list.map((item, index) => (
                         <li key={index} className="list-inline-item badge bg-light text-dark m-1">{item}</li>
                       ))}
                     </ul>
                   </div>
                 )
               ))}
             </Card.Body>
           </Card>
         )}
 
         {/* Display Ratios */}
         {hasRatios && (
           <Card>
             <Card.Header>Calculated Financial Ratios</Card.Header>
             <Card.Body>
               <table className="table table-bordered table-sm">
                 <thead>
                   <tr>
                     <th>Ratio</th>
                     <th>Value</th>
                     <th>Interpretation</th>
                   </tr>
                 </thead>
                 <tbody>
                   {Object.entries(ratios).map(([key, ratioData]) => (
                     <tr key={key}>
                       <td>{key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
                       <td>{ratioData.value?.toFixed(4) ?? 'N/A'}</td>
                       <td>{ratioData.interpretation || ratioData.description || 'N/A'}</td>
                     </tr>
                   ))}
                 </tbody>
               </table>
             </Card.Body>
           </Card>
         )}
       </div>
     );
   };

  // --- Main Render ---

  if (loading) {
    return <Spinner animation="border" className="page-spinner" />;
  }

  if (error) {
    // Provide a way to retry or go back
    return (
         <Alert variant="danger">
              <Alert.Heading>Error Loading Document</Alert.Heading>
              <p>{error}</p>
              {/* Optional: Add a retry button or link */}
         </Alert>
    );
  }

  if (!documentInfo) {
    // This case might be covered by error state, but good to have
    return <Alert variant="warning">Document information could not be loaded.</Alert>;
  }

  return (
    <div className="document-viewer container mt-3">
      <h2>{documentInfo.filename || `Document ${documentId}`}</h2>
      <p className="text-muted">
          Uploaded: {documentInfo.upload_date ? new Date(documentInfo.upload_date).toLocaleString() : 'N/A'} |
          Pages: {documentInfo.page_count ?? 'N/A'} |
          Language: {documentInfo.language || 'N/A'} |
          Status: {documentInfo.processing_status || 'N/A'}
      </p>
      
      <Tabs
        id="document-view-tabs"
        activeKey={activeTab}
        onSelect={(key) => setActiveTab(key)}
        className="mb-3"
        fill // Make tabs fill the width
      >
        <Tab eventKey="original" title="Original Document">
          {renderOriginalDocument()}
        </Tab>
        <Tab eventKey="text" title="Extracted Text">
          {/* Simple view for now, split view can be complex */}
          {renderExtractedText()}
        </Tab>
        <Tab eventKey="tables" title="Tables">
           {/* Simple view for now */}
          {renderExtractedTables()}
        </Tab>
        <Tab eventKey="financial" title="Financial Data">
          {renderFinancialData()}
        </Tab>
      </Tabs>
    </div>
  );
};

export default DocumentViewer;