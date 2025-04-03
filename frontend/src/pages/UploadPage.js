import React from 'react';
import { Box, Typography, Paper, Grid } from '@mui/material';
import Layout from '../components/Layout'; // Use main layout
import DocumentUpload from '../components/DocumentUpload'; // Use the upload component

const UploadPage = () => {
  // Callback function for successful upload (optional)
  const handleUploadSuccess = (data) => {
    console.log('Document uploaded successfully from UploadPage:', data);
    // Optionally navigate or show a persistent success message
    // navigate(`/document/${data.document_id}`); // Example navigation
  };

  return (
    <Layout title="Upload Document"> {/* Set the title for the layout */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Upload New Document
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Select a financial document (PDF, Excel, CSV) to begin analysis.
        </Typography>
      </Box>

      <Grid container spacing={3} justifyContent="center"> {/* Center content */}
        {/* Document Upload Component */}
        <Grid item xs={12} md={8} lg={7}> {/* Adjust width as needed */}
          <DocumentUpload onSuccess={handleUploadSuccess} />
        </Grid>

        {/* Helper Information Panel */}
        <Grid item xs={12} md={4} lg={5}> {/* Adjust width */}
          <Paper elevation={0} sx={{ p: 3, backgroundColor: 'grey.50', height: '100%' }}> {/* Lighter background */}
            <Typography variant="h6" gutterBottom>
              Supported Formats
            </Typography>
            <Typography variant="body2" paragraph>
              We currently support the following document types:
            </Typography>
            <ul style={{ paddingLeft: '20px', marginBottom: '24px' }}>
              <li><Typography variant="body2">PDF Documents (Searchable preferred)</Typography></li>
              <li><Typography variant="body2">Excel Spreadsheets (.xlsx, .xls)</Typography></li>
              <li><Typography variant="body2">CSV Files (.csv)</Typography></li>
            </ul>

            <Typography variant="h6" gutterBottom>
              Language Support
            </Typography>
            <Typography variant="body2" paragraph>
              The system attempts auto-detection. You can also specify:
            </Typography>
            <ul style={{ paddingLeft: '20px', marginBottom: '24px' }}>
              <li><Typography variant="body2">English</Typography></li>
              <li><Typography variant="body2">Hebrew (עברית)</Typography></li>
            </ul>

            <Typography variant="h6" gutterBottom>
              Tips for Best Results
            </Typography>
            <ul style={{ paddingLeft: '20px' }}>
              <li><Typography variant="body2">Ensure clear text and good resolution.</Typography></li>
              <li><Typography variant="body2">Maximum file size is 50MB.</Typography></li>
              <li><Typography variant="body2">Processing time may vary based on document size and complexity.</Typography></li>
            </ul>
          </Paper>
        </Grid>
      </Grid>
    </Layout>
  );
};

export default UploadPage;