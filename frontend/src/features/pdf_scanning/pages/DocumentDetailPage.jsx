import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Button,
  Tabs,
  Tab,
  Grid,
  CircularProgress,
  Alert,
  Divider,
  Chip,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import TableChartIcon from '@mui/icons-material/TableChart';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

import { DocumentContext } from '../../../shared/contexts/DocumentContext';
import ExtractedDataView from '../components/ExtractedDataView';

/**
 * DocumentDetailPage displays detailed information about a single document
 * 
 * Features:
 * - Overview of document metadata
 * - View of document content
 * - Financial data extracted from the document
 * - Tables detected in the document
 * - Actions: chat with document, create tables, delete
 */
function DocumentDetailPage({ language = 'he' }) {
  const { documentId } = useParams();
  const navigate = useNavigate();
  const { addActiveDocument, removeActiveDocument, isDocumentActive } = useContext(DocumentContext);
  
  // Document state
  const [document, setDocument] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Tab state
  const [activeTab, setActiveTab] = useState(0);
  
  // Delete dialog state
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  
  // Load document data
  useEffect(() => {
    if (documentId) {
      loadDocument();
    }
  }, [documentId]);
  
  // Load document details
  const loadDocument = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/pdf/${documentId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load document');
      }
      
      const result = await response.json();
      
      if (result.success && result.document) {
        setDocument(result.document);
      } else {
        throw new Error(result.error || 'Document not found');
      }
    } catch (error) {
      console.error('Error loading document:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Toggle document active status
  const toggleDocumentActive = () => {
    if (!document) return;
    
    if (isDocumentActive(document.id)) {
      removeActiveDocument(document.id);
    } else {
      addActiveDocument({
        id: document.id,
        title: document.title || document.file_name || document.id
      });
    }
  };
  
  // Handle navigation to chat with this document
  const handleChatWithDocument = () => {
    navigate(`/chat?document=${documentId}`);
  };
  
  // Handle navigation to create table from this document
  const handleCreateTable = () => {
    navigate(`/tables/new?document=${documentId}`);
  };
  
  // Handle document deletion
  const handleDeleteDocument = async () => {
    if (!document) return;
    
    setIsDeleting(true);
    
    try {
      const response = await fetch(`/api/pdf/${document.id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete document');
      }
      
      // If active, remove from active documents
      if (isDocumentActive(document.id)) {
        removeActiveDocument(document.id);
      }
      
      // Navigate back to documents list
      navigate('/documents');
    } catch (error) {
      console.error('Error deleting document:', error);
      alert(error.message || 'Failed to delete document');
    } finally {
      setIsDeleting(false);
      setShowDeleteDialog(false);
    }
  };
  
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Box sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/documents')}
        >
          {language === 'he' ? 'חזרה לרשימת המסמכים' : 'Back to Documents'}
        </Button>
      </Box>
    );
  }
  
  if (!document) {
    return (
      <Box sx={{ py: 4 }}>
        <Alert severity="info">
          {language === 'he' ? 'אין מידע זמין על מסמך זה' : 'No information available for this document'}
        </Alert>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/documents')}
          sx={{ mt: 2 }}
        >
          {language === 'he' ? 'חזרה לרשימת המסמכים' : 'Back to Documents'}
        </Button>
      </Box>
    );
  }
  
  return (
    <Box>
      {/* Header with title and actions */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h5" component="h1" gutterBottom>
              {document.title || document.file_name || document.id}
            </Typography>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
              {document.metadata?.document_type && (
                <Chip
                  label={document.metadata.document_type}
                  color="primary"
                  variant="outlined"
                  size="small"
                />
              )}
              
              {document.metadata?.date && (
                <Chip
                  label={new Date(document.metadata.date).toLocaleDateString()}
                  size="small"
                />
              )}
              
              {document.metadata?.institution && (
                <Chip
                  label={document.metadata.institution}
                  size="small"
                />
              )}
              
              <Chip
                label={isDocumentActive(document.id) 
                  ? (language === 'he' ? 'פעיל' : 'Active')
                  : (language === 'he' ? 'לא פעיל' : 'Inactive')}
                color={isDocumentActive(document.id) ? 'success' : 'default'}
                size="small"
                onClick={toggleDocumentActive}
              />
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<ChatIcon />}
              onClick={handleChatWithDocument}
            >
              {language === 'he' ? 'צ\'אט' : 'Chat'}
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<TableChartIcon />}
              onClick={handleCreateTable}
            >
              {language === 'he' ? 'צור טבלה' : 'Create Table'}
            </Button>
            
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setShowDeleteDialog(true)}
            >
              {language === 'he' ? 'מחק' : 'Delete'}
            </Button>
          </Box>
        </Box>
      </Paper>
      
      {/* Document content tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          variant="fullWidth"
        >
          <Tab label={language === 'he' ? 'סקירה' : 'Overview'} />
          <Tab label={language === 'he' ? 'תוכן' : 'Content'} />
          <Tab label={language === 'he' ? 'נתונים פיננסיים' : 'Financial Data'} />
          <Tab label={language === 'he' ? 'טבלאות' : 'Tables'} />
        </Tabs>
        
        <Box sx={{ p: 3 }}>
          {/* Overview tab */}
          {activeTab === 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {language === 'he' ? 'מידע על המסמך' : 'Document Information'}
                    </Typography>
                    
                    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        {language === 'he' ? 'שם קובץ:' : 'Filename:'}
                      </Typography>
                      <Typography variant="body2">
                        {document.file_name || '-'}
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary">
                        {language === 'he' ? 'סוג מסמך:' : 'Document Type:'}
                      </Typography>
                      <Typography variant="body2">
                        {document.metadata?.document_type || '-'}
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary">
                        {language === 'he' ? 'תאריך:' : 'Date:'}
                      </Typography>
                      <Typography variant="body2">
                        {document.metadata?.date ? new Date(document.metadata.date).toLocaleDateString() : '-'}
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary">
                        {language === 'he' ? 'גודל:' : 'Size:'}
                      </Typography>
                      <Typography variant="body2">
                        {document.size ? `${Math.round(document.size / 1024)} KB` : '-'}
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary">
                        {language === 'he' ? 'תאריך העלאה:' : 'Upload Date:'}
                      </Typography>
                      <Typography variant="body2">
                        {document.created_at ? new Date(document.created_at).toLocaleString() : '-'}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {language === 'he' ? 'תקציר פיננסי' : 'Financial Summary'}
                    </Typography>
                    
                    {document.financial_summary ? (
                      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 2 }}>
                        {Object.entries(document.financial_summary).map(([key, value]) => (
                          <React.Fragment key={key}>
                            <Typography variant="body2" color="text.secondary">
                              {key.replace(/_/g, ' ')}:
                            </Typography>
                            <Typography variant="body2">
                              {typeof value === 'number' ? value.toLocaleString() : value}
                            </Typography>
                          </React.Fragment>
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        {language === 'he' ? 'אין מידע פיננסי זמין' : 'No financial information available'}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
          
          {/* Content tab */}
          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {language === 'he' ? 'תוכן המסמך' : 'Document Content'}
              </Typography>
              
              {document.content ? (
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    maxHeight: '500px', 
                    overflow: 'auto',
                    whiteSpace: 'pre-wrap'
                  }}
                >
                  <Typography variant="body2">
                    {document.content}
                  </Typography>
                </Paper>
              ) : (
                <Alert severity="info">
                  {language === 'he' ? 'אין תוכן זמין למסמך זה' : 'No content available for this document'}
                </Alert>
              )}
            </Box>
          )}
          
          {/* Financial Data tab */}
          {activeTab === 2 && (
            <ExtractedDataView document={document} language={language} />
          )}
          
          {/* Tables tab */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {language === 'he' ? 'טבלאות שזוהו במסמך' : 'Tables Detected in Document'}
              </Typography>
              
              {document.tables && document.tables.length > 0 ? (
                document.tables.map((table, index) => (
                  <Box key={index} sx={{ mb: 4 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      {language === 'he' ? `טבלה ${index + 1}` : `Table ${index + 1}`}
                    </Typography>
                    
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        {table.headers && (
                          <TableHead>
                            <TableRow>
                              {table.headers.map((header, idx) => (
                                <TableCell key={idx}>{header}</TableCell>
                              ))}
                            </TableRow>
                          </TableHead>
                        )}
                        <TableBody>
                          {table.data && table.data.map((row, rowIdx) => (
                            <TableRow key={rowIdx}>
                              {row.map((cell, cellIdx) => (
                                <TableCell key={cellIdx}>{cell}</TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                ))
              ) : (
                <Alert severity="info">
                  {language === 'he' ? 'לא זוהו טבלאות במסמך זה' : 'No tables detected in this document'}
                </Alert>
              )}
            </Box>
          )}
        </Box>
      </Paper>
      
      {/* Delete confirmation dialog */}
      <Dialog
        open={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
      >
        <DialogTitle>
          {language === 'he' ? 'מחיקת מסמך' : 'Delete Document'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {language === 'he'
              ? `האם אתה בטוח שברצונך למחוק את המסמך "${document.title || document.file_name || document.id}"? לא ניתן לבטל פעולה זו.`
              : `Are you sure you want to delete the document "${document.title || document.file_name || document.id}"? This action cannot be undone.`}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDeleteDialog(false)} disabled={isDeleting}>
            {language === 'he' ? 'ביטול' : 'Cancel'}
          </Button>
          <Button 
            onClick={handleDeleteDocument} 
            color="error" 
            disabled={isDeleting}
            startIcon={isDeleting ? <CircularProgress size={20} /> : <DeleteIcon />}
          >
            {language === 'he' ? 'מחק' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default DocumentDetailPage;
