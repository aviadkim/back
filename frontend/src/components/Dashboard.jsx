import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col, Card, Button, Alert, Spinner, Table } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import axios from 'axios';
// Assuming DocumentUploader is in the same directory or adjust path
import DocumentUploader from './DocumentUploader';
import './Dashboard.css'; // Assuming this CSS file exists

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Dashboard = () => {
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(true); // Separate loading state for docs
  const [loadingStats, setLoadingStats] = useState(true); // Separate loading state for stats
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalDocuments: 0,
    processedDocuments: 0,
    failedDocuments: 0,
    pendingDocuments: 0, // Added pending
    documentsByType: {},
    financialMetrics: {
      isinCount: 0,
      tableCount: 0
    }
  });
  const [showUploader, setShowUploader] = useState(false);

  // Use useCallback to memoize fetch functions
  const fetchDocuments = useCallback(async () => {
    setLoadingDocs(true);
    // Clear error related to documents before fetching
    // setError(prev => prev?.includes('documents') ? null : prev);
    try {
      // TODO: Replace with actual API endpoint
      // const response = await axios.get('/api/documents');
      // Mock data
      await new Promise(resolve => setTimeout(resolve, 600));
      const response = {
          data: [
              { _id: 'doc1', originalFileName: 'Report_Q1_2024.pdf', uploadDate: new Date(Date.now() - 86400000).toISOString(), processingStatus: 'Completed' },
              { _id: 'doc2', originalFileName: 'Financial_Statement_2023.pdf', uploadDate: new Date(Date.now() - 172800000).toISOString(), processingStatus: 'Completed' },
              { _id: 'doc3', originalFileName: 'Investment_Summary.pdf', uploadDate: new Date().toISOString(), processingStatus: 'Pending' },
              { _id: 'doc4', originalFileName: 'Analysis_Market_Trends.pdf', uploadDate: new Date(Date.now() - 259200000).toISOString(), processingStatus: 'Failed' },
              { _id: 'doc5', originalFileName: 'Old_Report.pdf', uploadDate: new Date(Date.now() - 345600000).toISOString(), processingStatus: 'Completed' },
              { _id: 'doc6', originalFileName: 'Prospectus.pdf', uploadDate: new Date(Date.now() - 432000000).toISOString(), processingStatus: 'Completed' },
          ]
      };
      setDocuments(response.data);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents. Please try again later.');
    } finally {
      setLoadingDocs(false);
    }
  }, []); // Empty dependency array means this function is created once

  const fetchStats = useCallback(async () => {
    setLoadingStats(true);
     // Clear error related to stats before fetching
    // setError(prev => prev?.includes('stats') ? null : prev);
    try {
      // TODO: Replace with actual API endpoint
      // const response = await axios.get('/api/stats');
      // Mock stats
      await new Promise(resolve => setTimeout(resolve, 400));
      const response = {
          data: {
              totalDocuments: 6,
              processedDocuments: 4,
              failedDocuments: 1,
              pendingDocuments: 1,
              documentsByType: { 'PDF': 6, 'DOCX': 0 }, // Example types
              financialMetrics: {
                  isinCount: 15,
                  tableCount: 8
              }
          }
      };
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      // Don't set global error, maybe show a specific stats error?
      // setError('Failed to load dashboard statistics.');
    } finally {
      setLoadingStats(false);
    }
  }, []); // Empty dependency array

  useEffect(() => {
    fetchDocuments();
    fetchStats();
  }, [fetchDocuments, fetchStats]); // Depend on the memoized functions

  const handleUploadSuccess = () => {
    setShowUploader(false);
    // Re-fetch data after successful upload
    fetchDocuments();
    fetchStats();
  };

  const handleDeleteDocument = async (documentId) => {
    // Add confirmation dialog
    if (window.confirm(`Are you sure you want to delete document ${documentId}? This action cannot be undone.`)) {
      try {
        // TODO: Replace with actual API endpoint
        // await axios.delete(`/api/documents/${documentId}`);
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate delete
        console.log(`Simulated delete for document ${documentId}`);
        // Optimistic UI update or re-fetch
        fetchDocuments(); // Re-fetch to update list
        fetchStats(); // Re-fetch stats
      } catch (err) {
        console.error('Error deleting document:', err);
        setError(`Failed to delete document ${documentId}. Please try again later.`);
      }
    }
  };

  // --- Chart Rendering ---

  const renderDocumentTypeChart = () => {
    if (loadingStats) return <Spinner animation="border" size="sm" />;
    if (!stats.documentsByType || Object.keys(stats.documentsByType).length === 0) {
      return <Alert variant="info" size="sm">No document type data available.</Alert>;
    }

    const chartData = {
      labels: Object.keys(stats.documentsByType),
      datasets: [
        {
          label: 'Documents by Type',
          data: Object.values(stats.documentsByType),
          backgroundColor: [ // Add more colors if needed
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(255, 99, 132, 0.7)',
          ],
          borderColor: [
             'rgba(54, 162, 235, 1)',
             'rgba(255, 206, 86, 1)',
             'rgba(75, 192, 192, 1)',
             'rgba(153, 102, 255, 1)',
             'rgba(255, 159, 64, 1)',
             'rgba(255, 99, 132, 1)',
          ],
          borderWidth: 1,
        },
      ],
    };
     const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed !== null) {
                            label += context.parsed;
                        }
                        return label;
                    }
                }
            }
        }
    };

    return <Pie data={chartData} options={options} />;
  };

  const renderProcessingStatusChart = () => {
     if (loadingStats) return <Spinner animation="border" size="sm" />;

    const pendingCount = stats.totalDocuments - stats.processedDocuments - stats.failedDocuments;
    const chartData = {
      labels: ['Processed', 'Failed', 'Pending'],
      datasets: [
        {
          label: 'Document Status',
          data: [
            stats.processedDocuments,
            stats.failedDocuments,
            pendingCount >= 0 ? pendingCount : 0 // Ensure non-negative
          ],
          backgroundColor: [
            'rgba(75, 192, 192, 0.7)', // Processed - Green
            'rgba(255, 99, 132, 0.7)',  // Failed - Red
            'rgba(255, 206, 86, 0.7)', // Pending - Yellow
          ],
           borderColor: [
             'rgba(75, 192, 192, 1)',
             'rgba(255, 99, 132, 1)',
             'rgba(255, 206, 86, 1)',
           ],
          borderWidth: 1,
        },
      ],
    };

    const options = {
      indexAxis: 'y', // Make it a horizontal bar chart for better label readability
      responsive: true,
      plugins: {
         legend: { display: false }, // Hide legend as labels are clear
         title: { display: false }, // Title is in Card Header
      },
      scales: {
        x: {
          beginAtZero: true,
          title: { display: true, text: 'Number of Documents' }
        },
        y: { grid: { display: false } } // Hide y-axis grid lines
      }
    };

    return <Bar data={chartData} options={options} />;
  };

  // --- Recent Documents Table ---

  const renderRecentDocumentsTable = () => {
    if (loadingDocs) {
      return <div className="text-center p-3"><Spinner animation="border" size="sm" /> Loading documents...</div>;
    }

    if (error && error.includes('documents')) { // Show specific error
      return <Alert variant="danger">{error}</Alert>;
    }

    if (documents.length === 0) {
      return <Alert variant="info">No documents found. Upload your first document using the button above.</Alert>;
    }

    // Sort documents by uploadDate (descending)
    const sortedDocuments = [...documents].sort(
      (a, b) => new Date(b.uploadDate) - new Date(a.uploadDate)
    );

    // Take only the 5 most recent
    const recentDocuments = sortedDocuments.slice(0, 5);

    return (
      <Table striped hover responsive size="sm">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Upload Date</th>
            <th>Status</th>
            <th className="text-center">Actions</th>
          </tr>
        </thead>
        <tbody>
          {recentDocuments.map(doc => (
            <tr key={doc._id}>
              <td className="text-truncate" style={{ maxWidth: '250px' }}>
                <Link to={`/documents/${doc._id}`} title={doc.originalFileName}>
                  {doc.originalFileName}
                </Link>
              </td>
              <td>{new Date(doc.uploadDate).toLocaleString()}</td>
              <td>
                {/* Use Bootstrap badges for status */}
                <span className={`badge bg-${doc.processingStatus?.toLowerCase() === 'completed' ? 'success' : doc.processingStatus?.toLowerCase() === 'failed' ? 'danger' : 'warning'}`}>
                  {doc.processingStatus || 'Unknown'}
                </span>
              </td>
              <td className="text-center">
                <div className="action-buttons btn-group btn-group-sm" role="group">
                  <Link to={`/documents/${doc._id}`} className="btn btn-outline-primary" title="View Document">
                    <i className="fas fa-eye"></i>
                  </Link>
                  <Button
                    variant="outline-danger"
                    onClick={() => handleDeleteDocument(doc._id)}
                    title="Delete Document"
                  >
                    <i className="fas fa-trash"></i>
                  </Button>
                  {/* Add more actions if needed, e.g., reprocess */}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    );
  };

  // --- Main Component Return ---

  return (
    <Container fluid className="dashboard-container p-4">
      <Row className="mb-4 align-items-center">
        <Col>
          <h1 className="h2">Financial Documents Dashboard</h1>
        </Col>
        <Col xs="auto">
          <Button
            variant="primary"
            onClick={() => setShowUploader(!showUploader)}
            aria-controls="document-uploader-collapse"
            aria-expanded={showUploader}
          >
            <i className={`fas ${showUploader ? 'fa-times' : 'fa-upload'} me-2`}></i>
            {showUploader ? 'Close Uploader' : 'Upload Document'}
          </Button>
        </Col>
      </Row>

      {/* Collapsible Uploader */}
      {/* Consider using react-bootstrap Collapse component for animation */}
      {showUploader && (
        <Row className="mb-4">
          <Col>
            <Card className="shadow-sm">
              <Card.Body>
                <DocumentUploader onSuccess={handleUploadSuccess} />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Stats Row */}
      <Row className="mb-4 g-3">
        {loadingStats ? (
             <Col xs={12} className="text-center"><Spinner animation="border" size="sm" /> Loading stats...</Col>
        ) : (
            <>
                <Col md={3} sm={6}>
                  <Card className="dashboard-stat-card text-center shadow-sm h-100">
                    <Card.Body>
                      <div className="stat-icon mb-2"><i className="fas fa-file-alt fa-2x text-primary"></i></div>
                      <Card.Title className="text-muted small text-uppercase">Total Docs</Card.Title>
                      <div className="stat-value display-6">{stats.totalDocuments}</div>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3} sm={6}>
                  <Card className="dashboard-stat-card text-center shadow-sm h-100">
                    <Card.Body>
                       <div className="stat-icon mb-2"><i className="fas fa-check-circle fa-2x text-success"></i></div>
                      <Card.Title className="text-muted small text-uppercase">Processed</Card.Title>
                      <div className="stat-value display-6">{stats.processedDocuments}</div>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3} sm={6}>
                  <Card className="dashboard-stat-card text-center shadow-sm h-100">
                    <Card.Body>
                       <div className="stat-icon mb-2"><i className="fas fa-barcode fa-2x text-info"></i></div>
                      <Card.Title className="text-muted small text-uppercase">ISINs Found</Card.Title>
                      <div className="stat-value display-6">{stats.financialMetrics?.isinCount ?? 'N/A'}</div>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3} sm={6}>
                  <Card className="dashboard-stat-card text-center shadow-sm h-100">
                    <Card.Body>
                       <div className="stat-icon mb-2"><i className="fas fa-table fa-2x text-secondary"></i></div>
                      <Card.Title className="text-muted small text-uppercase">Tables Found</Card.Title>
                      <div className="stat-value display-6">{stats.financialMetrics?.tableCount ?? 'N/A'}</div>
                    </Card.Body>
                  </Card>
                </Col>
            </>
        )}
      </Row>

      {/* Charts Row */}
      <Row className="mb-4 g-3">
        <Col lg={6}>
          <Card className="shadow-sm h-100">
            <Card.Header>Processing Status</Card.Header>
            <Card.Body style={{ minHeight: '250px' }}>
              {renderProcessingStatusChart()}
            </Card.Body>
          </Card>
        </Col>
        <Col lg={6}>
          <Card className="shadow-sm h-100">
            <Card.Header>Document Types</Card.Header>
            <Card.Body style={{ minHeight: '250px' }}>
              {renderDocumentTypeChart()}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Recent Documents Row */}
      <Row>
        <Col>
          <Card className="shadow-sm">
            <Card.Header>Recent Documents</Card.Header>
            <Card.Body>
              {renderRecentDocumentsTable()}
              {!loadingDocs && documents.length > 5 && (
                <div className="text-center mt-3">
                  {/* TODO: Update link if using a different route for all documents */}
                  <Link to="/documents" className="btn btn-outline-primary btn-sm">
                    View All Documents
                  </Link>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;