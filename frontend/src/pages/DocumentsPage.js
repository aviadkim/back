import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material'; // Added Paper
import { UploadFile as UploadIcon } from '@mui/icons-material'; // Renamed for clarity
import { Link as RouterLink } from 'react-router-dom';
import Layout from '../components/Layout'; // Use main layout
import DocumentsList from '../components/documents/DocumentList'; // Use the list component

const DocumentsPage = () => {
  return (
    <Layout title="My Documents"> {/* Set the title for the layout */}
      {/* Page Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" gutterBottom>
            My Documents
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Browse, view, and manage your uploaded financial documents.
          </Typography>
        </Box>

        {/* Upload Button */}
        <Button
          variant="contained"
          color="primary"
          startIcon={<UploadIcon />}
          component={RouterLink}
          to="/upload"
          sx={{ whiteSpace: 'nowrap' }} // Prevent button text wrapping
        >
          Upload New
        </Button>
      </Box>

      {/* Document List Component */}
      {/* Wrap DocumentsList in Paper for visual separation if desired */}
      <Paper elevation={0} sx={{ p: { xs: 1, sm: 2 }, backgroundColor: 'transparent' }}>
         <DocumentsList />
      </Paper>
    </Layout>
  );
};

export default DocumentsPage;