import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Tabs, Tab, Spinner, Alert, Button, Card, Pagination, Table, Container, Row, Col, ListGroup } from 'react-bootstrap'; // Added Container, Row, Col, ListGroup
import { Document, Page, pdfjs } from 'react-pdf';
import axios from 'axios';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'; // Import default annotation layer CSS
import 'react-pdf/dist/esm/Page/TextLayer.css'; // Import default text layer CSS
import './DocumentViewer.css'; // Assuming this CSS file exists

// Set worker source for react-pdf
// You might need to copy the pdf.worker.min.js file to your public folder
// Option 1: Using CDN (easier for setup)
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;
// Option 2: Local file (requires setup)
// pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';


const DocumentViewer = () => {
  const { documentId } = useParams();
  const [documentInfo, setDocumentInfo] = useState(null); // Renamed from 'document' to avoid conflict
  const [extractedData, setExtractedData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [activeTab, setActiveTab] = useState('original');
  const [pdfFileUrl, setPdfFileUrl] = useState(null);

  const fetchDocumentData = useCallback(async () => {
    if (!documentId) return;
    setLoading(true);
    setError(null); // Clear previous errors
    try {
      // Fetch document metadata
      // TODO: Replace with actual API endpoint
      // const metadataResponse = await axios.get(`/api/documents/${documentId}`);
      // Mock metadata
      await new Promise(resolve => setTimeout(resolve, 300));
      const metadataResponse = {
          data: {
              _id: documentId,
              originalFileName: `Document_${documentId}.pdf`,
              uploadDate: new Date().toISOString(),
              processingStatus: 'completed',
              // Add other relevant metadata
          }
      };
      setDocumentInfo(metadataResponse.data);

      // Set PDF file URL (assuming API serves the file)
      // TODO: Replace with actual API endpoint
      setPdfFileUrl(`/api/documents/${documentId}/file`); // Or a direct URL if available

      // Fetch extracted data
      // TODO: Replace with actual API endpoint
      // const dataResponse = await axios.get(`/api/documents/${documentId}/data`);
      // Mock extracted data
      await new Promise(resolve => setTimeout(resolve, 500));
      const mockExtractedData = {
          filename: `Document_${documentId}.pdf`,
          processing_time: 15.3,
          pages: Array.from({ length: 5 }, (_, i) => ({ // Mock 5 pages
              pageNumber: i + 1,
              textLength: Math.floor(Math.random() * 1000) + 500,
              dimensions: { width: 612, height: 792 },
              text: `This is the extracted text for page ${i + 1}. Lorem ipsum dolor sit amet... ` + " Sample text ".repeat(50)
          })),
          tables: [
              { pageNumber: 0, tableId: 'page1-table0', rowCount: 5, colCount: 3, header: ['Header 1', 'Header 2', 'Header 3'], rows: Array.from({ length: 4 }, (_, r) => [`Row ${r+1} Col 1`, `Row ${r+1} Col 2`, Math.random() > 0.5 ? 123 : 456]), tableType: 'Financial', analysis: { summary: 'Sample analysis' }, extractionMethod: 'cv2' },
              { pageNumber: 2, tableId: 'page3-table0', rowCount: 4, colCount: 2, header: ['Key', 'Value'], rows: [['Key A', 'Val A'], ['Key B', 'Val B'], ['Key C', 'Val C']], tableType: 'Generic', analysis: {}, extractionMethod: 'text' }
          ],
          financialData: {
              isinNumbers: [
                  { code: 'US0378331005', description: 'Apple Inc.', confidence: 'high', context: '... ISIN: US0378331005 ...', pageNumber: 1 },
                  { code: 'IL0010811143', description: 'Teva Pharma', confidence: 'medium', context: '... נייר IL0010811143 ...', pageNumber: 3 }
              ],
              financialMetrics: {
                  'Total Assets': ['$1,234,567.89'],
                  'Net Income': ['$50,000'],
                  'Portfolio Yield': ['3.5%']
              }
          },
          metadata: { author: 'System', creationDate: new Date().toISOString() },
          error: null
      };
      setExtractedData(mockExtractedData);

    } catch (err) {
      console.error('Error fetching document:', err);
      setError(`Failed to load document data (ID: ${documentId}). Please check the console and try again.`);
      setDocumentInfo(null); // Clear info on error
      setExtractedData(null);
      setPdfFileUrl(null);
    } finally {
      setLoading(false);
    }
  }, [documentId]);


  useEffect(() => {
    fetchDocumentData();
  }, [fetchDocumentData]); // Depend on the memoized fetch function

  const onDocumentLoadSuccess = ({ numPages: nextNumPages }) => {
    setNumPages(nextNumPages);
    // Reset to page 1 if the document changes or loads for the first time
    if (pageNumber !== 1) {
        setPageNumber(1);
    }
  };

  const onDocumentLoadError = (error) => {
      console.error("Error loading PDF:", error);
      setError(`Failed to load PDF file. ${error.message}`);
  };


  const handlePageChange = (newPageNumber) => {
      // Ensure newPageNumber is within valid range
      const validPageNumber = Math.min(Math.max(1, newPageNumber), numPages || 1);
      setPageNumber(validPageNumber);
  };

  // --- Render Functions ---

  const renderOriginalDocument = () => {
      if (!pdfFileUrl) {
          return <Alert variant="warning">PDF file URL not available.</Alert>;
      }
      return (
          <div className="pdf-container">
              <Document
                  file={pdfFileUrl}
                  onLoadSuccess={onDocumentLoadSuccess}
                  onLoadError={onDocumentLoadError}
                  loading={<div className="text-center p-4"><Spinner animation="border" /> Loading PDF...</div>}
                  error={<Alert variant="danger">Error loading PDF. Check console for details.</Alert>}
                  options={{
                      cMapUrl: `//cdn.jsdelivr.net/npm/pdfjs-dist@${pdfjs.version}/cmaps/`,
                      cMapPacked: true,
                      standardFontDataUrl: `//cdn.jsdelivr.net/npm/pdfjs-dist@${pdfjs.version}/standard_fonts/`
                  }}
              >
                  <Page
                      pageNumber={pageNumber}
                      renderTextLayer={true} // Enable text layer for selection/search
                      renderAnnotationLayer={true} // Enable annotation layer
                      scale={1.5} // Adjust scale as needed
                      className="pdf-page"
                  />
              </Document>

              {numPages && numPages > 1 && (
                  <Pagination className="pdf-pagination justify-content-center mt-3">
                      <Pagination.First onClick={() => handlePageChange(1)} disabled={pageNumber <= 1} />
                      <Pagination.Prev onClick={() => handlePageChange(pageNumber - 1)} disabled={pageNumber <= 1} />
                      {/* Simple page number display - could be enhanced */}
                      <Pagination.Item active>{pageNumber}</Pagination.Item>
                      <Pagination.Ellipsis disabled />
                      <Pagination.Item disabled>{numPages}</Pagination.Item>
                      <Pagination.Next onClick={() => handlePageChange(pageNumber + 1)} disabled={pageNumber >= numPages} />
                      <Pagination.Last onClick={() => handlePageChange(numPages)} disabled={pageNumber >= numPages} />
                  </Pagination>
              )}
          </div>
      );
  };


  const renderExtractedText = () => {
    if (!extractedData || !extractedData.pages || extractedData.pages.length < pageNumber) {
      return <Alert variant="info" size="sm">No extracted text available for this page.</Alert>;
    }

    const pageData = extractedData.pages[pageNumber - 1]; // 0-based index
    if (!pageData || !pageData.text) {
      return <Alert variant="info" size="sm">No extracted text content for page {pageNumber}.</Alert>;
    }

    return (
      <Card className="text-viewer h-100">
        <Card.Header>Extracted Text - Page {pageNumber}</Card.Header>
        <Card.Body style={{ overflowY: 'auto', maxHeight: '70vh' }}>
          <pre className="extracted-text">{pageData.text}</pre>
        </Card.Body>
      </Card>
    );
  };

  const renderExtractedTables = () => {
    if (!extractedData || !extractedData.tables || extractedData.tables.length === 0) {
      return <Alert variant="info" size="sm">No tables detected in this document.</Alert>;
    }

    // Filter tables for the current page (using 1-based pageNumber from state)
    const pageTables = extractedData.tables.filter(
      table => table.pageNumber === pageNumber
    );

    if (pageTables.length === 0) {
      return <Alert variant="info" size="sm">No tables detected on page {pageNumber}.</Alert>;
    }

    return (
      <div className="tables-container" style={{ overflowY: 'auto', maxHeight: '70vh' }}>
        <h5 className="mb-3">Tables on Page {pageNumber}</h5>
        {pageTables.map((table, index) => (
          <Card key={table.tableId || index} className="mb-3 shadow-sm">
            <Card.Header>
                Table {index + 1} (ID: {table.tableId || 'N/A'})
                <small className="text-muted float-end">Type: {table.tableType || 'Unknown'} | Method: {table.extractionMethod || 'N/A'}</small>
            </Card.Header>
            <Card.Body>
              <div className="table-responsive">
                <Table striped bordered hover size="sm">
                  {table.header && table.header.length > 0 && (
                    <thead>
                      <tr>{table.header.map((cell, i) => <th key={i}>{cell}</th>)}</tr>
                    </thead>
                  )}
                  <tbody>
                    {table.rows && table.rows.map((row, i) => (
                      <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>
                    ))}
                    {(!table.rows || table.rows.length === 0) && (
                        <tr><td colSpan={table.header?.length || 1} className="text-center text-muted">No rows found</td></tr>
                    )}
                  </tbody>
                </Table>
              </div>
              {table.analysis && Object.keys(table.analysis).length > 0 && (
                  <div className="mt-2 p-2 bg-light border rounded">
                      <h6>Analysis:</h6>
                      <pre className="small">{JSON.stringify(table.analysis, null, 2)}</pre>
                  </div>
              )}
            </Card.Body>
          </Card>
        ))}
      </div>
    );
  };

  const renderFinancialData = () => {
    if (!extractedData || !extractedData.financialData) {
      return <Alert variant="info" size="sm">No financial data extracted.</Alert>;
    }

    const { isinNumbers, financialMetrics } = extractedData.financialData;
    const hasIsin = isinNumbers && isinNumbers.length > 0;
    const hasMetrics = financialMetrics && Object.keys(financialMetrics).length > 0;

    if (!hasIsin && !hasMetrics) {
        return <Alert variant="info" size="sm">No specific financial data points found.</Alert>;
    }

    return (
      <div className="financial-data p-3" style={{ overflowY: 'auto', maxHeight: '80vh' }}>
        {hasIsin && (
          <Card className="mb-3 shadow-sm">
            <Card.Header as="h5">ISIN Numbers Found</Card.Header>
            <ListGroup variant="flush">
              {isinNumbers.map((isin, index) => (
                <ListGroup.Item key={index} className="d-flex justify-content-between align-items-start">
                  <div>
                    <strong>{isin.code}</strong>
                    <small className="d-block text-muted">{isin.description || 'No description'}</small>
                    {isin.context && <small className="d-block text-muted fst-italic">Context: ...{isin.context}...</small>}
                  </div>
                  <span className="badge bg-secondary rounded-pill">Page {isin.pageNumber}</span>
                </ListGroup.Item>
              ))}
            </ListGroup>
          </Card>
        )}

        {hasMetrics && (
          <Card className="shadow-sm">
            <Card.Header as="h5">Financial Metrics Found</Card.Header>
            <Card.Body>
              <Table striped bordered hover size="sm">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Value(s)</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(financialMetrics).map(([key, values], index) => (
                    <tr key={index}>
                      <td>{key}</td>
                      {/* Ensure values is always an array and join */}
                      <td>{Array.isArray(values) ? values.join(', ') : values}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        )}
      </div>
    );
  };

  // --- Main Render ---

  if (loading) {
    return <div className="text-center p-5"><Spinner animation="border" /> Loading document data...</div>;
  }

  if (error) {
    return <Alert variant="danger" className="m-3">{error}</Alert>;
  }

  if (!documentInfo) {
    return <Alert variant="warning" className="m-3">Document information not available.</Alert>;
  }

  return (
    <Container fluid className="document-viewer p-3">
      <h3 className="mb-1">{documentInfo.originalFileName}</h3>
      <p className="text-muted mb-3">
          Uploaded: {new Date(documentInfo.uploadDate).toLocaleString()} | Status: {documentInfo.processingStatus}
      </p>

      <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)} id="document-view-tabs" className="mb-3" fill>
        <Tab eventKey="original" title={<><i className="fas fa-file-pdf me-2"></i>Original</>}>
          {renderOriginalDocument()}
        </Tab>
        <Tab eventKey="text" title={<><i className="fas fa-file-alt me-2"></i>Text</>}>
          <Row>
            <Col md={6} className="panel">{renderOriginalDocument()}</Col>
            <Col md={6} className="panel">{renderExtractedText()}</Col>
          </Row>
        </Tab>
        <Tab eventKey="tables" title={<><i className="fas fa-table me-2"></i>Tables</>}>
           <Row>
            <Col md={6} className="panel">{renderOriginalDocument()}</Col>
            <Col md={6} className="panel">{renderExtractedTables()}</Col>
          </Row>
        </Tab>
        <Tab eventKey="financial" title={<><i className="fas fa-chart-line me-2"></i>Financial Data</>}>
          {renderFinancialData()}
        </Tab>
      </Tabs>
    </Container>
  );
};

export default DocumentViewer;