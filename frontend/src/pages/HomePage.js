import React from 'react';
import { Box, Button, Typography, Container, Grid, Paper } from '@mui/material';
import { UploadFile as UploadIcon } from '@mui/icons-material'; // Renamed for clarity
import { Link as RouterLink } from 'react-router-dom';

const HomePage = () => {
  return (
    <Box sx={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: 'background.default' // Use theme background
    }}>
      {/* Hero Section */}
      <Box sx={{
        background: 'linear-gradient(135deg, #1976d2 30%, #0d47a1 90%)', // Adjusted gradient
        color: 'white',
        py: { xs: 6, md: 10 }, // Responsive padding
        textAlign: { xs: 'center', md: 'left' }
      }}>
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
                Financial Document Analyzer
              </Typography>
              <Typography variant="h5" paragraph sx={{ opacity: 0.9 }}>
                Extract insights from your financial documents with AI-powered analysis.
              </Typography>
              <Box sx={{ mt: 4 }}>
                <Button
                  variant="contained"
                  color="secondary" // Use secondary color for primary action
                  size="large"
                  component={RouterLink}
                  to="/upload"
                  startIcon={<UploadIcon />}
                  sx={{ mr: 2, mb: { xs: 2, md: 0 } }} // Margin adjustments
                >
                  Upload Document
                </Button>
                <Button
                  variant="outlined"
                  color="inherit" // White outline button
                  size="large"
                  component={RouterLink}
                  to="/dashboard"
                >
                  Go to Dashboard
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6} sx={{ display: { xs: 'none', md: 'block' } }}> {/* Hide image on small screens */}
              <Box component="img"
                // Use a placeholder or ensure the actual image exists in public folder
                src="/images/document-analysis-illustration.svg" // Example path
                alt="Document Analysis Illustration"
                sx={{
                  width: '100%',
                  maxWidth: '450px', // Adjusted size
                  display: 'block',
                  margin: '0 auto',
                }}
              />
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Box sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Typography variant="h4" component="h2" align="center" gutterBottom sx={{ fontWeight: 600 }}>
            Key Features
          </Typography>
          <Typography variant="h6" align="center" color="text.secondary" paragraph sx={{ mb: 5 }}>
            Leverage AI to understand your financial documents faster and more accurately.
          </Typography>

          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Paper elevation={2} sx={{ p: 4, height: '100%', textAlign: 'center' }}>
                <Typography variant="h5" component="h3" gutterBottom>
                  Multi-language Support
                </Typography>
                <Typography color="text.secondary" paragraph>
                  Process documents in English and Hebrew with high accuracy extraction of text and data.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={2} sx={{ p: 4, height: '100%', textAlign: 'center' }}>
                <Typography variant="h5" component="h3" gutterBottom>
                  Table Extraction
                </Typography>
                <Typography color="text.secondary" paragraph>
                  Automatically identify and extract tables from your financial documents for easy analysis.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={2} sx={{ p: 4, height: '100%', textAlign: 'center' }}>
                <Typography variant="h5" component="h3" gutterBottom>
                  Financial Analysis
                </Typography>
                <Typography color="text.secondary" paragraph>
                  Identify key financial metrics, ISIN numbers, and other important financial data points.
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{
        mt: 'auto', // Push footer to bottom
        py: 3,
        bgcolor: 'grey.900',
        color: 'grey.400' // Lighter text for dark background
      }}>
        <Container maxWidth="lg">
          <Typography variant="body2" align="center">
            &copy; {new Date().getFullYear()} Financial Document Analyzer. All rights reserved.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default HomePage;