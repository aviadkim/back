import React, { useState, useEffect, useContext } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  IconButton,
  Link,
  Paper,
  Stack,
  Typography,
  Alert,
  useTheme,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
  ListAlt as ListAltIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import DocumentContext from '../../../shared/contexts/DocumentContext';

// Translations for the component
const translations = {
  en: {
    title: 'Document Library',
    uploadNewDocument: 'Upload New Document',
    noDocuments: 'No documents found. Upload a new document to get started.',
    searchPlaceholder: 'Search documents...',
    documentType: 'Document Type',
    uploadDate: 'Upload Date',
    status: 'Status',
    actions: 'Actions',
    view: 'View',
    delete: 'Delete',
    download: 'Download',
    processing: 'Processing',
    completed: 'Completed',
    failed: 'Failed',
    documentDeleted: 'Document deleted successfully',
    errorLoading: 'Error loading documents',
    confirmDelete: 'Are you sure you want to delete this document?',
  },
  he: {
    title: 'ספריית מסמכים',
    uploadNewDocument: 'העלאת מסמך חדש',
    noDocuments: 'לא נמצאו מסמכים. העלה מסמך חדש כדי להתחיל.',
    searchPlaceholder: 'חיפוש מסמכים...',
    documentType: 'סוג מסמך',
    uploadDate: 'תאריך העלאה',
    status: 'סטטוס',
    actions: 'פעולות',
    view: 'צפייה',
    delete: 'מחיקה',
    download: 'הורדה',
    processing: 'מעבד',
    completed: 'הושלם',
    failed: 'נכשל',
    documentDeleted: 'המסמך נמחק בהצלחה',
    errorLoading: 'שגיאה בטעינת המסמכים',
    confirmDelete: 'האם אתה בטוח שברצונך למחוק את המסמך הזה?',
  },
};

/**
 * DocumentList component displays all uploaded documents and provides actions like view, download, and delete
 * 
 * @param {Object} props - Component properties
 * @param {string} props.language - Current language (en/he)
 * @returns {JSX.Element} The rendered component
 */
const DocumentList = ({ language = 'en' }) => {
  const theme = useTheme();
  const { documents, loadDocuments, deleteDocument } = useContext(DocumentContext);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteSuccess, setDeleteSuccess] = useState(false);
  const navigate = useNavigate();
  const t = translations[language];

  // Load documents when component mounts
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setLoading(true);
        await loadDocuments();
        setError(null);
      } catch (err) {
        setError(t.errorLoading);
        console.error('Error loading documents:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [loadDocuments, t.errorLoading]);

  // Handle document deletion
  const handleDeleteDocument = async (id) => {
    if (window.confirm(t.confirmDelete)) {
      try {
        await deleteDocument(id);
        setDeleteSuccess(true);
        setTimeout(() => setDeleteSuccess(false), 3000);
      } catch (err) {
        console.error('Error deleting document:', err);
      }
    }
  };

  // Filter documents based on search term
  const filteredDocuments = documents.filter(doc => 
    doc.title?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    doc.documentType?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get status chip color based on status
  const getStatusChipColor = (status) => {
    switch (status) {
      case 'processing':
        return 'warning';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return format(date, 'PPP');
    } catch (err) {
      return dateString;
    }
  };

  return (
    <Box>
      {/* Page header */}
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          mb: 3
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom>
          {t.title}
        </Typography>
        
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          component={RouterLink}
          to="/documents/upload"
        >
          {t.uploadNewDocument}
        </Button>
      </Box>

      {/* Notifications */}
      {deleteSuccess && (
        <Alert 
          severity="success" 
          sx={{ mb: 2 }}
          onClose={() => setDeleteSuccess(false)}
        >
          {t.documentDeleted}
        </Alert>
      )}
      
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}

      {/* Search bar */}
      <Paper 
        sx={{ 
          p: 2, 
          mb: 3, 
          display: 'flex',
          alignItems: 'center'
        }}
      >
        <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
        <input
          type="text"
          placeholder={t.searchPlaceholder}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            border: 'none',
            outline: 'none',
            width: '100%',
            background: 'transparent',
            fontSize: '1rem',
            fontFamily: theme.typography.fontFamily,
          }}
        />
      </Paper>

      {/* Loading state */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Empty state */}
      {!loading && filteredDocuments.length === 0 && (
        <Paper 
          sx={{ 
            p: 4, 
            textAlign: 'center',
            backgroundColor: theme.palette.background.default
          }}
        >
          <ListAltIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {searchTerm ? 'No documents match your search' : t.noDocuments}
          </Typography>
          {!searchTerm && (
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              component={RouterLink}
              to="/documents/upload"
              sx={{ mt: 2 }}
            >
              {t.uploadNewDocument}
            </Button>
          )}
        </Paper>
      )}

      {/* Document grid */}
      {!loading && filteredDocuments.length > 0 && (
        <Grid container spacing={3}>
          {filteredDocuments.map((document) => (
            <Grid item xs={12} sm={6} md={4} key={document.id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'all 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: theme.shadows[4],
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography 
                    variant="h6" 
                    component="h2" 
                    gutterBottom
                    sx={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                    }}
                  >
                    {document.title || 'Untitled Document'}
                  </Typography>
                  
                  <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                    <Chip 
                      label={document.documentType || 'Unknown Type'} 
                      size="small" 
                      color="primary"
                      variant="outlined"
                    />
                    <Chip 
                      label={t[document.status] || document.status} 
                      size="small" 
                      color={getStatusChipColor(document.status)}
                    />
                  </Stack>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {t.uploadDate}: {formatDate(document.uploadDate || document.createdAt)}
                  </Typography>
                </CardContent>
                
                <Divider />
                
                <CardActions>
                  <IconButton 
                    aria-label={t.view}
                    onClick={() => navigate(`/documents/${document.id}`)}
                    title={t.view}
                  >
                    <VisibilityIcon />
                  </IconButton>
                  
                  <IconButton 
                    aria-label={t.download}
                    onClick={() => window.open(`/api/documents/${document.id}/download`, '_blank')}
                    title={t.download}
                  >
                    <DownloadIcon />
                  </IconButton>
                  
                  <Box sx={{ flexGrow: 1 }} />
                  
                  <IconButton 
                    aria-label={t.delete}
                    onClick={() => handleDeleteDocument(document.id)}
                    color="error"
                    title={t.delete}
                  >
                    <DeleteIcon />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default DocumentList;
