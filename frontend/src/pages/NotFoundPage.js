import React from 'react';
import { Box, Typography, Button, Container, Paper } from '@mui/material'; // Added Paper
import { Home as HomeIcon, ErrorOutline as ErrorIcon } from '@mui/icons-material'; // Added ErrorIcon
import { Link as RouterLink } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <Container maxWidth="sm"> {/* Use sm for smaller content area */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '80vh', // Adjust height as needed
          textAlign: 'center',
          py: 5
        }}
      >
        <Paper elevation={3} sx={{ p: { xs: 3, sm: 5 }, width: '100%' }}>
          <ErrorIcon sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
          <Typography variant="h1" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
            404
          </Typography>
          <Typography variant="h4" component="h2" gutterBottom>
            Page Not Found
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph sx={{ mb: 4 }}>
            Sorry, the page you are looking for doesn't exist or may have been moved.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<HomeIcon />}
            component={RouterLink}
            to="/" // Link to the home page (or dashboard)
            size="large"
          >
            Back to Home
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default NotFoundPage;