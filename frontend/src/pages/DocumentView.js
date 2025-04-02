import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Paper, Typography, Box, Tabs, Tab, CircularProgress } from '@mui/material';
import DocumentViewer from '../components/DocumentViewer';
import DocumentQA from '../components/DocumentQA';
import DocumentExtraction from '../components/DocumentExtraction';

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index} id={`tabpanel-${index}`}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function DocumentView() {
  const { id } = useParams();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    async function fetchDocument() {
      try {
        const response = await fetch(`/api/documents/${id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch document');
        }
        const data = await response.json();
        setDocument(data);
      } catch (err) {
        console.error('Error fetching document:', err);
        setError(err.message || 'Failed to load document');
      } finally {
        setLoading(false);
      }
    }

    fetchDocument();
  }, [id]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 5 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Typography color="error" variant="h6">{error}</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>{document?.filename}</Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Document ID: {id}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Status: {document?.status}
        </Typography>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="View Document" />
            <Tab label="Ask Questions" />
            <Tab label="Extractions" />
          </Tabs>
        </Box>
        
        <TabPanel value={tabValue} index={0}>
          <DocumentViewer documentId={id} />
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <DocumentQA documentId={id} />
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          <DocumentExtraction documentId={id} />
        </TabPanel>
      </Paper>
    </Container>
  );
}

export default DocumentView;
