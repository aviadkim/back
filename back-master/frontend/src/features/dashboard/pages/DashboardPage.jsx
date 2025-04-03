import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import ChatIcon from '@mui/icons-material/Chat';
import TableChartIcon from '@mui/icons-material/TableChart';
import BarChartIcon from '@mui/icons-material/BarChart';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import PieChartIcon from '@mui/icons-material/PieChart';

// Import document context
import { DocumentContext } from '../../../shared/contexts/DocumentContext';

/**
 * DashboardPage component serves as the landing page for the application
 * 
 * Features:
 * - Overview of recent activities
 * - Access to recent documents
 * - Quick links to main features
 * - System status and alerts
 */
function DashboardPage({ language = 'he' }) {
  const navigate = useNavigate();
  const { activeDocuments } = useContext(DocumentContext);
  
  // Recent documents state
  const [recentDocuments, setRecentDocuments] = useState([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
  const [documentsError, setDocumentsError] = useState(null);
  
  // Load recent documents
  useEffect(() => {
    loadRecentDocuments();
  }, []);
  
  /**
   * Loads recent documents from the API
   */
  const loadRecentDocuments = async () => {
    setIsLoadingDocuments(true);
    setDocumentsError(null);
    
    try {
      const response = await fetch('/api/pdf/recent');
      
      if (!response.ok) {
        throw new Error('Failed to load recent documents');
      }
      
      const result = await response.json();
      
      if (result.success && result.documents) {
        setRecentDocuments(result.documents);
      } else {
        throw new Error(result.error || 'No documents found');
      }
    } catch (error) {
      console.error('Error loading recent documents:', error);
      setDocumentsError(error.message || 'Failed to load recent documents');
      
      // Use empty array if we couldn't load documents
      setRecentDocuments([]);
    } finally {
      setIsLoadingDocuments(false);
    }
  };
  
  // Feature cards data
  const features = [
    {
      title: language === 'he' ? 'העלאת מסמך' : 'Upload Document',
      description: language === 'he' 
        ? 'העלה מסמכים פיננסיים לניתוח מהיר ומדויק' 
        : 'Upload financial documents for quick and accurate analysis',
      icon: <UploadFileIcon fontSize="large" color="primary" />,
      path: '/documents/upload'
    },
    {
      title: language === 'he' ? 'צ\'אט עם המסמכים' : 'Chat with Documents',
      description: language === 'he' 
        ? 'שאל שאלות על המסמכים הפיננסיים שלך בשפה טבעית' 
        : 'Ask questions about your financial documents in natural language',
      icon: <ChatIcon fontSize="large" color="primary" />,
      path: '/chat'
    },
    {
      title: language === 'he' ? 'יצירת טבלאות' : 'Generate Tables',
      description: language === 'he' 
        ? 'צור טבלאות מותאמות אישית מהנתונים הפיננסיים שלך' 
        : 'Create custom tables from your financial data',
      icon: <TableChartIcon fontSize="large" color="primary" />,
      path: '/tables/new'
    }
  ];
  
  // Mock statistics data for demonstration
  const stats = [
    {
      title: language === 'he' ? 'מסמכים שנותחו' : 'Documents Analyzed',
      value: recentDocuments.length,
      icon: <DescriptionIcon fontSize="large" color="info" />
    },
    {
      title: language === 'he' ? 'בנקים מחוברים' : 'Connected Banks',
      value: 3,
      icon: <AccountBalanceIcon fontSize="large" color="info" />
    },
    {
      title: language === 'he' ? 'פעולות אחרונות' : 'Recent Actions',
      value: 12,
      icon: <BarChartIcon fontSize="large" color="info" />
    }
  ];
  
  return (
    <Box>
      {/* Welcome header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {language === 'he' 
            ? 'ברוכים הבאים למנתח המסמכים הפיננסיים' 
            : 'Welcome to Financial Document Analyzer'}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {language === 'he'
            ? 'נתח, הבן וקבל תובנות מהמסמכים הפיננסיים שלך בקלות'
            : 'Analyze, understand, and gain insights from your financial documents with ease'}
        </Typography>
      </Box>
      
      {/* Feature cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                transition: 'transform 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" component="h2" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  onClick={() => navigate(feature.path)}
                >
                  {language === 'he' ? 'התחל' : 'Get Started'}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {/* Recent documents and statistics */}
      <Grid container spacing={3}>
        {/* Recent documents */}
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              {language === 'he' ? 'מסמכים אחרונים' : 'Recent Documents'}
            </Typography>
            
            {isLoadingDocuments ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : documentsError ? (
              <Alert severity="error" sx={{ mt: 2 }}>
                {documentsError}
              </Alert>
            ) : recentDocuments.length === 0 ? (
              <Box sx={{ py: 2 }}>
                <Alert severity="info">
                  {language === 'he'
                    ? 'אין מסמכים אחרונים. העלה את המסמך הראשון שלך!'
                    : 'No recent documents. Upload your first document!'}
                </Alert>
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<UploadFileIcon />}
                    onClick={() => navigate('/documents/upload')}
                  >
                    {language === 'he' ? 'העלאת מסמך' : 'Upload Document'}
                  </Button>
                </Box>
              </Box>
            ) : (
              <List>
                {recentDocuments.map((document, index) => (
                  <React.Fragment key={document.id}>
                    {index > 0 && <Divider component="li" />}
                    <ListItem
                      button
                      onClick={() => navigate(`/documents/${document.id}`)}
                    >
                      <ListItemIcon>
                        <DescriptionIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={document.title || document.file_name || document.id}
                        secondary={
                          document.created_at
                            ? new Date(document.created_at).toLocaleDateString()
                            : null
                        }
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
        
        {/* Statistics */}
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              {language === 'he' ? 'סטטיסטיקה' : 'Statistics'}
            </Typography>
            
            <Grid container spacing={2} sx={{ mt: 1 }}>
              {stats.map((stat, index) => (
                <Grid item xs={12} key={index}>
                  <Box sx={{ display: 'flex', alignItems: 'center', p: 1 }}>
                    <Box sx={{ mr: 2 }}>
                      {stat.icon}
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {stat.title}
                      </Typography>
                      <Typography variant="h5">
                        {stat.value}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
            
            {/* Active documents section */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                {language === 'he' ? 'מסמכים פעילים' : 'Active Documents'}
              </Typography>
              
              {activeDocuments.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  {language === 'he' 
                    ? 'אין מסמכים פעילים כרגע'
                    : 'No active documents at the moment'}
                </Typography>
              ) : (
                <List dense>
                  {activeDocuments.slice(0, 3).map((doc) => (
                    <ListItem key={doc.id} dense>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <DescriptionIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={doc.title || doc.id}
                        primaryTypographyProps={{
                          variant: 'body2',
                          noWrap: true
                        }}
                      />
                    </ListItem>
                  ))}
                  
                  {activeDocuments.length > 3 && (
                    <Typography variant="caption" color="text.secondary">
                      {language === 'he'
                        ? `ועוד ${activeDocuments.length - 3} מסמכים...`
                        : `And ${activeDocuments.length - 3} more documents...`}
                    </Typography>
                  )}
                </List>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DashboardPage;
