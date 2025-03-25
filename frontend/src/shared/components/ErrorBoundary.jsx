// This is a placeholder file for ErrorBoundary.jsx
// Please paste the complete code from below in this file

/*
ErrorBoundary Component Guide:

This component catches JavaScript errors anywhere in its child component tree
and displays a fallback UI instead of crashing the entire application.

Features:
1. Catches errors in components during rendering, lifecycle methods, and event handlers
2. Logs error information to the console (and potentially to a monitoring service)
3. Displays a user-friendly error message
4. Provides a way to recover (reset the error state and retry)

How to use:
- Wrap components that might throw errors with this ErrorBoundary
- Use multiple ErrorBoundary components to isolate errors to specific parts of the UI
- Consider wrapping route components to prevent entire app crashes
- Pass custom fallback UI via props if desired
*/
import React, { Component } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  AlertTitle
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import BugReportIcon from '@mui/icons-material/BugReport';

/**
 * ErrorBoundary component catches JavaScript errors in the child component tree
 * and displays a fallback UI instead of crashing the entire application
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null
    };
  }
  
  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    // You can log the error to an error reporting service
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    this.setState({ errorInfo });
    
    // If you have an error monitoring service like Sentry, you would report here
    // Example: reportError(error, errorInfo);
  }
  
  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };
  
  render() {
    const { hasError, error, errorInfo } = this.state;
    const { children, language = 'he', fallbackComponent } = this.props;
    
    if (hasError) {
      // Custom fallback component if provided
      if (fallbackComponent) {
        return fallbackComponent(error, errorInfo, this.handleReset);
      }
      
      // Default error UI
      return (
        <Paper 
          sx={{ 
            p: 3, 
            m: 2, 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center',
            textAlign: 'center'
          }}
        >
          <BugReportIcon color="error" sx={{ fontSize: 60, mb: 2 }} />
          
          <Alert severity="error" sx={{ mb: 3, width: '100%' }}>
            <AlertTitle>
              {language === 'he' ? 'אירעה שגיאה' : 'Something went wrong'}
            </AlertTitle>
            {error?.toString()}
          </Alert>
          
          <Typography variant="body1" sx={{ mb: 3 }}>
            {language === 'he'
              ? 'אירעה שגיאה לא צפויה ברכיב זה. ניתן לנסות לאפס את הרכיב או לנווט לדף אחר.'
              : 'An unexpected error occurred in this component. You can try resetting the component or navigating to another page.'}
          </Typography>
          
          <Button
            variant="contained"
            color="primary"
            startIcon={<RefreshIcon />}
            onClick={this.handleReset}
          >
            {language === 'he' ? 'אפס רכיב' : 'Reset Component'}
          </Button>
          
          {/* Technical details (for development) */}
          {process.env.NODE_ENV === 'development' && errorInfo && (
            <Box sx={{ mt: 4, textAlign: 'left', width: '100%' }}>
              <Typography variant="h6" sx={{ mb: 1 }}>
                {language === 'he' ? 'פרטים טכניים' : 'Technical Details'}
              </Typography>
              <Box
                component="pre"
                sx={{
                  p: 2,
                  backgroundColor: 'grey.100',
                  borderRadius: 1,
                  overflow: 'auto',
                  maxHeight: '200px',
                  fontSize: '0.875rem',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}
              >
                {errorInfo.componentStack}
              </Box>
            </Box>
          )}
        </Paper>
      );
    }
    
    return children;
  }
}

export default ErrorBoundary;
