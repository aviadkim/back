import React, { useState, useEffect } from 'react';
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
import DocumentUploader from './DocumentUploader'; // Assuming this component exists
import './Dashboard.css';

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalDocuments: 0,
    processedDocuments: 0,
    failedDocuments: 0,
    documentsByType: {},
    financialMetrics: {
      isinCount: 0,
      tableCount: 0
    }
  });
  const [showUploader, setShowUploader] = useState(false);

  // Fetch initial data
  useEffect(() => {
    fetchDocuments();
    fetchStats();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null); // Clear previous errors
    try {
      // Use the /api/documents endpoint which should return summary data
      const response = await axios.get('/api/documents'); 
      // Ensure the response data is an array
      setDocuments(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents. Please check the API connection.');
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats');
      // Update stats, providing defaults if parts are missing
      setStats(prevStats => ({
         ...prevStats, // Keep existing stats
         ...response.data, // Overwrite with new data
         financialMetrics: { // Ensure financialMetrics object exists
              ...prevStats.financialMetrics,
              ...(response.data.financialMetrics || {})
         },
         documentsByType: response.data.documentsByType || {} // Ensure documentsByType object exists
      }));
    } catch (err) {
      console.error('Error fetching stats:', err);
      // Optionally set an error state for stats loading failure
      // setError('Failed to load dashboard statistics.'); 
    }
  };

  const handleUploadSuccess = () => {
    setShowUploader(false);
    // Refresh data after successful upload
    fetchDocuments();
    fetchStats();
  };

  const handleDeleteDocument = async (documentId) => {
    // Add confirmation dialog
    if (window.confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      try {
        // Use the correct API endpoint from pdf_scanning/service.py
        await axios.delete(`/api/documents/${documentId}`); 
        // Refresh data after deletion
        fetchDocuments();
        fetchStats();
      } catch (err) {
        console.error('Error deleting document:', err);
        setError('Failed to delete document. Please try again later.');
      }
    }
  };

  // --- Chart Rendering ---

  const renderDocumentTypeChart = () => {
    // Check if stats and documentsByType are available and have data
    if (!stats || !stats.documentsByType || Object.keys(stats.documentsByType).length === 0) {
      return <Alert variant="info" className="text-center small">No document type data available</Alert>;
    }

    const chartData = {
      labels: Object.keys(stats.documentsByType),
      datasets: [
        {
          label: 'Documents by Type',
          data: Object.values(stats.documentsByType),
          backgroundColor: [ // Add more colors if needed
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
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
               title: {
                    display: false, // Title is in Card.Header
               }
          }
     };

    return <Pie data={chartData} options={options} />;
  };

  const renderProcessingStatusChart = () => {
     // Calculate pending count, ensuring it's not negative
     const pendingCount = Math.max(0, stats.totalDocuments - (stats.processedDocuments || 0) - (stats.failedDocuments || 0));
     const chartData = {
       labels: ['Processed', 'Failed', 'Pending'],
       datasets: [
         {
           label: 'Document Processing Status',
           data: [
             stats.processedDocuments || 0, 
             stats.failedDocuments || 0, 
             pendingCount
           ],
           backgroundColor: [
             'rgba(75, 192, 192, 0.7)', // Processed - Green
             'rgba(255, 99, 132, 0.7)', // Failed - Red
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
          responsive: true,
          indexAxis: 'y', // Make it a horizontal bar chart for better label readability if needed
          scales: {
               x: { // Note: 'x' axis for horizontal bar chart values
                    beginAtZero: true,
                    title: {
                         display: true,
                         text: 'Number of Documents'
                    },
                    ticks: {
                         stepSize: 1 // Ensure integer ticks if counts are low
                    }
               }
          },
          plugins: {
               legend: {
                    display: false // Legend might be redundant for simple status
               },
               title: {
                    display: false, // Title is in Card.Header
               }
          }
     };
 
     // Use Bar chart instead of horizontal if preferred
     return <Bar data={chartData} options={options} />; 
   };

  // --- Table Rendering ---

  const renderRecentDocumentsTable = () => {
    if (loading) {
      return <div className="text-center p-3"><Spinner animation="border" size="sm" /> Loading documents...</div>;
    }

    if (error) {
      // Show error specific to document loading
      return <Alert variant="danger">{error}</Alert>;
    }

    if (!documents || documents.length === 0) {
      return <Alert variant="light" className="text-center">No documents found. Upload your first document using the button above.</Alert>;
    }

    // Sort documents by upload date (descending) - ensure date parsing is robust
    const sortedDocuments = [...documents].sort((a, b) => {
         const dateA = a.uploaded_at ? new Date(a.uploaded_at) : new Date(0);
         const dateB = b.uploaded_at ? new Date(b.uploaded_at) : new Date(0);
         return dateB - dateA; // Descending order
    });

    // Take only the 5 most recent
    const recentDocuments = sortedDocuments.slice(0, 5);

    return (
      <Table striped hover responsive size="sm">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Upload Date</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {recentDocuments.map(doc => (
            // Use doc.id which should be the unique identifier from the backend
            <tr key={doc.id}> 
              <td>
                {/* Link uses doc.id */}
                <Link to={`/documents/${doc.id}`} title={doc.file_name}> 
                  {/* Truncate long filenames if necessary */}
                  {doc.file_name && doc.file_name.length > 40 ? `${doc.file_name.substring(0, 37)}...` : doc.file_name}
                </Link>
              </td>
              <td>{doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleString() : 'N/A'}</td>
              <td>
                 {/* Use metadata status */}
                <span className={`status-badge status-${doc.metadata?.processing_status?.toLowerCase() || 'unknown'}`}>
                  {doc.metadata?.processing_status || 'Unknown'}
                </span>
              </td>
              <td>
                <div className="action-buttons">
                  {/* Link uses doc.id */}
                  <Link to={`/documents/${doc.id}`} className="btn btn-sm btn-outline-primary me-1"> 
                    View
                  </Link>
                  <Button 
                    variant="outline-danger" 
                    size="sm" 
                    onClick={() => handleDeleteDocument(doc.id)} // Use doc.id
                  >
                    Delete
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    );
  };

  // --- Main Render ---

  return (
    <Container fluid className="dashboard-container mt-3">
      <Row className="mb-4 align-items-center">
        <Col>
          <h1 className="h3">Financial Documents Dashboard</h1>
        </Col>
        <Col xs="auto">
          <Button 
            variant="primary" 
            onClick={() => setShowUploader(!showUploader)}
            size="sm"
          >
            {showUploader ? 'Hide Uploader' : 'Upload New Document'}
          </Button>
        </Col>
      </Row>

      {/* Uploader Section */}
      {showUploader && (
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Body>
                {/* Make sure DocumentUploader component is created and imported */}
                <DocumentUploader onSuccess={handleUploadSuccess} /> 
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Stats Cards */}
      <Row className="mb-4">
        {/* Use map for cleaner stats cards if stats structure is consistent */}
        <Col md={3} sm={6} className="mb-3">
          <Card className="dashboard-stat-card h-100">
            <Card.Body>
              <Card.Title className="text-muted small">Total Documents</Card.Title>
              <div className="stat-value display-6">{stats.totalDocuments || 0}</div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6} className="mb-3">
          <Card className="dashboard-stat-card h-100">
            <Card.Body>
              <Card.Title className="text-muted small">Processed</Card.Title>
              <div className="stat-value display-6">{stats.processedDocuments || 0}</div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6} className="mb-3">
          <Card className="dashboard-stat-card h-100">
            <Card.Body>
              <Card.Title className="text-muted small">ISINs Found</Card.Title>
              <div className="stat-value display-6">{stats.financialMetrics?.isinCount || 0}</div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6} className="mb-3">
          <Card className="dashboard-stat-card h-100">
            <Card.Body>
              <Card.Title className="text-muted small">Tables Extracted</Card.Title>
              <div className="stat-value display-6">{stats.financialMetrics?.tableCount || 0}</div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row className="mb-4">
        <Col lg={6} className="mb-3">
          <Card className="h-100">
            <Card.Header>Processing Status</Card.Header>
            <Card.Body>
              {renderProcessingStatusChart()}
            </Card.Body>
          </Card>
        </Col>
        <Col lg={6} className="mb-3">
          <Card className="h-100">
            <Card.Header>Document Types</Card.Header>
            <Card.Body>
              {renderDocumentTypeChart()}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Recent Documents Table */}
      <Row>
        <Col>
          <Card>
            <Card.Header>Recent Documents</Card.Header>
            <Card.Body className="p-0"> {/* Remove padding for full-width table */}
              {renderRecentDocumentsTable()}
            </Card.Body>
            {documents.length > 5 && (
              <Card.Footer className="text-center">
                <Link to="/documents" className="btn btn-outline-primary btn-sm">
                  View All Documents
                </Link>
              </Card.Footer>
            )}
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;