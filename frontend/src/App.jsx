import React, { useState } from 'react';
import { 
  BrowserRouter as Router, 
  Routes, 
  Route, 
  Navigate
} from 'react-router-dom';
import { 
  Box, 
  CssBaseline, 
  ThemeProvider, 
  createTheme,
  Container,
  useMediaQuery
} from '@mui/material';
import { 
  blue, 
  blueGrey
} from '@mui/material/colors';

// Layout components
import AppNavigation from './shared/components/AppNavigation';
import Breadcrumbs from './shared/components/Breadcrumbs';

// Feature components
import DocumentUploader from './features/pdf_scanning/components/DocumentUploader';
import DocumentList from './features/pdf_scanning/components/DocumentList';
import ChatInterface from './features/chatbot/components/ChatInterface';
import TableGenerator from './features/tables/components/TableGenerator';
import DashboardPage from './features/dashboard/pages/DashboardPage';

// Context providers
import DocumentContextProvider from './shared/contexts/DocumentContext';

/**
 * Main App component that serves as the entry point for the application
 * 
 * Features:
 * - Routing configuration
 * - Theming
 * - Context providers
 * - Language detection and handling
 */
function App() {
  // Theme preference detection
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  
  // User preferences state
  const [language, setLanguage] = useState(
    document.documentElement.lang === 'he' ? 'he' : 'en'
  );
  const [themeMode, setThemeMode] = useState(prefersDarkMode ? 'dark' : 'light');
  
  // Theme configuration
  const theme = React.useMemo(() => {
    const isDark = themeMode === 'dark';
    
    return createTheme({
      palette: {
        mode: themeMode,
        primary: blue,
        secondary: {
          main: '#f50057',
        },
        background: {
          default: isDark ? '#121212' : '#f5f5f5',
          paper: isDark ? '#1e1e1e' : '#ffffff',
        },
      },
      direction: language === 'he' ? 'rtl' : 'ltr',
      typography: {
        fontFamily: language === 'he' 
          ? '"Assistant", "Heebo", "Roboto", "Helvetica", "Arial", sans-serif'
          : '"Roboto", "Helvetica", "Arial", sans-serif',
      },
      components: {
        MuiButton: {
          styleOverrides: {
            root: {
              textTransform: 'none',
            },
          },
        },
      },
    });
  }, [themeMode, language]);
  
  // Set theme direction based on language
  React.useEffect(() => {
    document.dir = language === 'he' ? 'rtl' : 'ltr';
  }, [language]);
  
  // Toggle theme function
  const toggleTheme = () => {
    setThemeMode(prev => prev === 'light' ? 'dark' : 'light');
  };
  
  // Switch language function
  const toggleLanguage = () => {
    setLanguage(prev => prev === 'en' ? 'he' : 'en');
  };
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <DocumentContextProvider>
        <Router>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              minHeight: '100vh',
            }}
          >
            {/* App Navigation */}
            <AppNavigation 
              language={language} 
              themeMode={themeMode}
              onToggleTheme={toggleTheme}
              onToggleLanguage={toggleLanguage}
            />
            
            {/* Main Content */}
            <Box
              component="main"
              sx={{
                flexGrow: 1,
                py: 3,
                px: { xs: 2, md: 3 },
              }}
            >
              {/* Breadcrumbs */}
              <Breadcrumbs language={language} />
              
              <Container maxWidth="xl" sx={{ mt: 2 }}>
                <Routes>
                  {/* Dashboard */}
                  <Route 
                    path="/" 
                    element={<DashboardPage language={language} />} 
                  />
                  
                  {/* Documents */}
                  <Route 
                    path="/documents" 
                    element={<DocumentList language={language} />} 
                  />
                  <Route 
                    path="/documents/upload" 
                    element={<DocumentUploader language={language} />} 
                  />
                  
                  {/* Chat */}
                  <Route 
                    path="/chat" 
                    element={<ChatInterface language={language} />} 
                  />
                  
                  {/* Tables */}
                  <Route 
                    path="/tables/new" 
                    element={<TableGenerator language={language} />} 
                  />
                  
                  {/* Redirect unknown routes to dashboard */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Container>
            </Box>
            
            {/* Footer (could be added later) */}
          </Box>
        </Router>
      </DocumentContextProvider>
    </ThemeProvider>
  );
}

export default App;
