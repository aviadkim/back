import React, { useState, useEffect } from 'react';
import {
  Typography, Grid, Box, Card, CardContent,
  CardActions, Divider, CircularProgress, Button, Alert, // Import Alert
  Paper, List, ListItem, ListItemText, ListItemIcon // Added List components
} from '@mui/material';
import {
  UploadFile as UploadIcon,
  Article as DocumentIcon,
  Analytics as AnalyticsIcon,
  Visibility as VisibilityIcon // Added for recent docs button
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { documentApi } from '../api/api'; // Use standardized API client
import Layout from '../components/Layout'; // Use the main layout

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalDocuments: 0,
    // Add placeholders for other stats if needed
    processingCount: 0,
    errorCount: 0,
  });
  const [recentDocuments, setRecentDocuments] = useState([]);
  const [error, setError] = useState(null); // State for API errors

  useEffect(() => {
    // Load dashboard data (stats and recent documents)
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch recent documents (adjust limit as needed)
        const response = await documentApi.getDocuments({ page: 1, limit: 5 });

        if (response.status === 'success' && response.data) {
           // Assuming API returns { documents: [], pagination: { total: ... } }
           const docs = response.data.documents || [];
           const total = response.data.pagination?.total || docs.length; // Use total from pagination if available

           setRecentDocuments(docs);
           // Update stats based on fetched data (can be enhanced with a dedicated stats endpoint later)
           setStats({
             totalDocuments: total,
             processingCount: 0, // Placeholder - needs backend logic
             errorCount: 0, // Placeholder - needs backend logic
           });
        } else {
           setError(response.message || 'Failed to load recent documents');
           setRecentDocuments([]);
           setStats({ totalDocuments: 0, processingCount: 0, errorCount: 0 });
        }

      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err.message || 'An error occurred while fetching dashboard data.');
        setRecentDocuments([]);
        setStats({ totalDocuments: 0, processingCount: 0, errorCount: 0 });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []); // Fetch data only on component mount

  // Format date utility
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch (e) {
      return 'Invalid Date';
    }
  };

  return (
    <Layout title="Dashboard"> {/* Use Layout component */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Welcome Back!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's a quick overview of your financial document analysis.
        </Typography>
      </Box>

      {/* Quick Action Cards */}
      <Grid container spacing={3} mb={4}>
        {/* Upload Card */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <CardContent>
              <UploadIcon color="primary" sx={{ fontSize: 40, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Upload Document
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Process new financial documents for analysis.
              </Typography>
            </CardContent>
            <CardActions sx={{ justifyContent: 'flex-start', pl: 2, pb: 2 }}>
              <Button size="small" color="primary" component={RouterLink} to="/upload">
                Upload Now
              </Button>
            </CardActions>
          </Card>
        </Grid>

        {/* View Documents Card */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <CardContent>
              <DocumentIcon color="primary" sx={{ fontSize: 40, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                View Documents
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Browse and manage your processed documents.
              </Typography>
            </CardContent>
            <CardActions sx={{ justifyContent: 'flex-start', pl: 2, pb: 2 }}>
              <Button size="small" color="primary" component={RouterLink} to="/documents">
                View All
              </Button>
            </CardActions>
          </Card>
        </Grid>

        {/* Analytics Card (Placeholder) */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <CardContent>
              <AnalyticsIcon color="primary" sx={{ fontSize: 40, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Analytics
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Discover insights and trends (coming soon).
              </Typography>
            </CardContent>
            <CardActions sx={{ justifyContent: 'flex-start', pl: 2, pb: 2 }}>
              <Button size="small" color="primary" component={RouterLink} to="/analytics" disabled>
                View Analytics
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>

      {/* Document Stats */}
      <Paper elevation={1} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Document Statistics
        </Typography>
        <Divider sx={{ mb: 2 }} />

        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : error ? (
           <Alert severity="warning">Could not load statistics: {error}</Alert>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center">
                <Typography variant="h3" color="primary">{stats.totalDocuments}</Typography>
                <Typography variant="body2" color="text.secondary">Total Documents</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center">
                <Typography variant="h3">{stats.processingCount}</Typography>
                <Typography variant="body2" color="text.secondary">Processing</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center">
                <Typography variant="h3" color="error">{stats.errorCount}</Typography>
                <Typography variant="body2" color="text.secondary">With Errors</Typography>
              </Box>
            </Grid>
          </Grid>
        )}
      </Paper>

      {/* Recent Documents List */}
      <Paper elevation={1} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Documents
        </Typography>
        <Divider sx={{ mb: 2 }} />

        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : error ? (
           <Alert severity="warning">Could not load recent documents: {error}</Alert>
        ) : recentDocuments.length > 0 ? (
          <List disablePadding>
            {recentDocuments.map((doc) => (
              <ListItem
                key={doc.id} // Use id from formatted data
                secondaryAction={
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<VisibilityIcon />}
                    component={RouterLink}
                    to={`/document/${doc.id}`}
                  >
                    View
                  </Button>
                }
                divider
              >
                <ListItemIcon>
                  <DocumentIcon color="action" />
                </ListItemIcon>
                <ListItemText
                  primary={doc.filename || 'Unnamed Document'}
                  secondary={`Uploaded: ${formatDate(doc.upload_date)} | Pages: ${doc.page_count ?? 'N/A'}`}
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Box textAlign="center" py={3}>
            <Typography variant="body1" color="text.secondary">
              No recent documents found.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<UploadIcon />}
              sx={{ mt: 2 }}
              component={RouterLink}
              to="/upload"
            >
              Upload Document
            </Button>
          </Box>
        )}
      </Paper>
    </Layout>
  );
};

export default Dashboard;