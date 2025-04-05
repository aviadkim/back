import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Document, Page, pdfjs } from 'react-pdf';
import LoadingSpinner from '../ui/LoadingSpinner'; // Restored with placeholder
import './DocumentViewer.css';

// Initialize PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const DocumentViewer = ({ document }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPdf = async () => {
      if (!document || !document.id) return;
      
      try {
        setLoading(true);
        // Create a blob URL for the PDF
        const response = await axios.get(`/api/documents/${document.id}/file`, {
          responseType: 'blob'
        });
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        setPdfUrl(url);
        setError(null);
      } catch (err) {
        console.error('Error fetching PDF:', err);
        setError('Failed to load PDF file');
      } finally {
        setLoading(false);
      }
    };

    fetchPdf();
    
    // Clean up blob URL on unmount
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [document]);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
  };

  if (loading) {
    return <LoadingSpinner />; // Restored with placeholder
  }

  if (error) {
    return <div className="document-error">{error}</div>;
  }

  if (!pdfUrl) {
    return <div className="document-error">No document available</div>;
  }

  return (
    <div className="document-viewer">
      <div className="pdf-container">
        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={(error) => setError('Error loading PDF: ' + error.message)}
          loading={<LoadingSpinner />}
        >
          <Page 
            pageNumber={pageNumber} 
            renderTextLayer={true}
            renderAnnotationLayer={true}
            scale={1.2}
          />
        </Document>
      </div>
      
      <div className="pdf-controls">
        <button
          disabled={pageNumber <= 1}
          onClick={() => setPageNumber(pageNumber - 1)}
          className="page-button"
        >
          Previous
        </button>
        <span className="page-info">
          Page {pageNumber} of {numPages || '?'}
        </span>
        <button
          disabled={pageNumber >= numPages}
          onClick={() => setPageNumber(pageNumber + 1)}
          className="page-button"
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default DocumentViewer;