import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Import pages
import HomePage from './pages/HomePage'; // Assuming this will be created
import DashboardPage from './pages/Dashboard'; // Renamed import
import UploadPage from './pages/UploadPage'; // Assuming this exists or will be created
import DocumentsPage from './pages/DocumentsPage'; // Assuming this exists or will be created
import DocumentViewPage from './pages/DocumentViewPage'; // Assuming this exists or will be created
// Import or create NotFoundPage
// import NotFoundPage from './pages/NotFoundPage';

// Placeholder for NotFoundPage if not created yet
const NotFoundPage = () => (
    <div>
        <h1>404 - Page Not Found</h1>
        <p>The page you are looking for does not exist.</p>
        <RouterLink to="/">Go Home</RouterLink> {/* Use RouterLink if available */}
    </div>
);


// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Blue primary
    },
    secondary: {
      main: '#f50057', // Pink secondary
    },
    background: {
      default: '#f4f6f8', // Light grey background
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '"Segoe UI"',
      'Arial',
      'sans-serif',
    ].join(','),
    h4: {
        fontWeight: 600,
    },
    h5: {
        fontWeight: 600,
    },
    h6: {
        fontWeight: 600,
    }
  },
  components: { // Optional: Global component overrides
    MuiPaper: {
        styleOverrides: {
            root: {
                borderRadius: 8, // Slightly rounded corners for Paper
            }
        }
    },
    MuiCard: {
        styleOverrides: {
            root: {
                borderRadius: 8, // Slightly rounded corners for Card
            }
        }
    }
  }
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Ensures consistent baseline styles */}
      <Router>
        <Routes>
          {/* Define application routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/document/:documentId" element={<DocumentViewPage />} />

          {/* Add other routes like settings, analytics later */}
          {/* <Route path="/settings" element={<SettingsPage />} /> */}
          {/* <Route path="/analytics" element={<AnalyticsPage />} /> */}

          {/* Fallback routes */}
          <Route path="/404" element={<NotFoundPage />} />
          <Route path="*" element={<Navigate to="/404" replace />} /> {/* Redirect any unmatched route to 404 */}
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
