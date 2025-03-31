import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Button, IconButton,
  Chip, CircularProgress, Alert, Pagination
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Delete as DeleteIcon // Keep for potential future use
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { documentApi } from '../api/api'; // Use standardized API client

const DocumentsList = () => {
  const [loading, setLoading] = useState(true);
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const limit = 10; // Number of documents per page

  // Fetch documents when page changes
  useEffect(() => {
    fetchDocuments();
  }, [page]);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);

    try {
      // Use the correct API endpoint and handle pagination
      const response = await documentApi.getDocuments({ page, limit });

      if (response.status === 'success' && response.data) {
        // Assuming the API returns { documents: [], pagination: { total: ..., pages: ... } }
        setDocuments(response.data.documents || []);
        setTotalPages(response.data.pagination?.pages || 1);
      } else {
        setError(response.message || 'Failed to fetch documents');
        setDocuments([]); // Clear documents on error
        setTotalPages(1);
      }
    } catch (err) {
      console.error("Error fetching documents:", err);
      setError(err.message || 'An error occurred while fetching documents');
      setDocuments([]); // Clear documents on error
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  };

  // Format date string
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      // Use UTC date parsing
      return new Date(dateString).toLocaleDateString(undefined, { timeZone: 'UTC' }) + ' ' +
             new Date(dateString).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' });
    } catch (e) {
      return 'Invalid Date';
    }
  };

  // Get display label for language code
  const getLanguageLabel = (langCode) => {
    const languages = {
      'en': 'English',
      'he': 'Hebrew',
      'unknown': 'Unknown'
    };
    return languages[langCode] || langCode;
  };

  // Get MUI Chip component based on document status
  const getStatusChip = (status) => {
    switch(status?.toLowerCase()) { // Handle potential null/undefined status
      case 'completed':
        return <Chip label="Completed" color="success" size="small" variant="outlined" />;
      case 'processing':
        return <Chip label="Processing" color="warning" size="small" variant="outlined" />;
      case 'failed':
        return <Chip label="Failed" color="error" size="small" variant="outlined" />;
      default:
        return <Chip label={status || 'Unknown'} size="small" variant="outlined" />;
    }
  };

  // Handle pagination change
  const handlePageChange = (event, value) => {
    setPage(value);
  };

  // Display loading indicator
  if (loading && documents.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  // Display error message
  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error} - Please ensure the backend API is running and accessible.
      </Alert>
    );
  }

  // Display message when no documents are found
  if (documents.length === 0) {
    return (
      <Paper elevation={0} sx={{ p: 4, textAlign: 'center', backgroundColor: 'grey.50' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No documents found
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Upload your first document to get started.
        </Typography>
        <Button
          variant="contained"
          color="primary"
          component={RouterLink}
          to="/upload"
        >
          Upload Document
        </Button>
      </Paper>
    );
  }

  // Display the documents table
  return (
    <Box>
      <TableContainer component={Paper} elevation={1}>
        <Table sx={{ minWidth: 650 }} aria-label="documents table">
          <TableHead>
            <TableRow sx={{ backgroundColor: 'action.hover' }}>
              <TableCell sx={{ fontWeight: 'bold' }}>Filename</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Date Uploaded</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Pages</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Language</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
              <TableCell align="center" sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {documents.map((doc) => (
              <TableRow
                key={doc.id} // Use 'id' which should be the string version of _id
                hover
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {/* Access metadata fields safely */}
                  {doc.filename || 'Unnamed Document'}
                </TableCell>
                <TableCell>{formatDate(doc.upload_date)}</TableCell>
                <TableCell>{doc.page_count ?? 'N/A'}</TableCell>
                <TableCell>{getLanguageLabel(doc.language)}</TableCell>
                <TableCell>{getStatusChip(doc.status)}</TableCell>
                <TableCell align="center">
                  <IconButton
                    component={RouterLink}
                    to={`/document/${doc.id}`} // Link to document view page
                    color="primary"
                    size="small"
                    aria-label={`view document ${doc.filename}`}
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  {/* Add Delete button later if needed */}
                  {/* <IconButton color="error" size="small" aria-label={`delete document ${doc.filename}`}>
                    <DeleteIcon fontSize="small" />
                  </IconButton> */}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={3}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={handlePageChange}
            color="primary"
            showFirstButton
            showLastButton
          />
        </Box>
      )}
    </Box>
  );
};

export default DocumentsList;