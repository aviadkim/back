import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  CircularProgress,
  Alert,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TablePagination,
  InputBase,
  Divider
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import DeleteIcon from '@mui/icons-material/Delete';
import FilterListIcon from '@mui/icons-material/FilterList';
import SearchIcon from '@mui/icons-material/Search';
import ChatIcon from '@mui/icons-material/Chat';
import TableChartIcon from '@mui/icons-material/TableChart';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import CheckIcon from '@mui/icons-material/Check';
import ClearIcon from '@mui/icons-material/Clear';

// Import document context
import { DocumentContext } from '../../../shared/contexts/DocumentContext';

/**
 * DocumentList component displays all available documents with filtering and search
 * 
 * Features:
 * - List of all documents with key metadata
 * - Search and filter capabilities
 * - Document selection for active use
 * - Actions for each document (view, chat, generate tables)
 * - Pagination for large document sets
 */
function DocumentList({ language = 'he' }) {
  const navigate = useNavigate();
  const { activeDocuments, addActiveDocument, removeActiveDocument, isDocumentActive } = useContext(DocumentContext);
  
  // Documents state
  const [documents, setDocuments] = useState([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
  const [documentsError, setDocumentsError] = useState(null);
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredDocuments, setFilteredDocuments] = useState([]);
  
  // Action menu state
  const [actionMenuAnchorEl, setActionMenuAnchorEl] = useState(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  
  // Delete confirmation dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  
  // Load documents on component mount
  useEffect(() => {
    loadDocuments();
  }, []);
  
  // Filter documents when search query or documents change
  useEffect(() => {
    filterDocuments();
  }, [searchQuery, documents]);
  
  /**
   * Loads all documents from the API
   */
  const loadDocuments = async () => {
    setIsLoadingDocuments(true);
    setDocumentsError(null);
    
    try {
      const response = await fetch('/api/pdf');
      
      if (!response.ok) {
        throw new Error('Failed to load documents');
      }
      
      const result = await response.json();
      
      if (result.success && result.documents) {
        setDocuments(result.documents);
      } else {
        throw new Error(result.error || 'No documents found');
      }
    } catch (error) {
      console.error('Error loading documents:', error);
      setDocumentsError(error.message || 'Failed to load documents');
      
      // Use empty array if we couldn't load documents
      setDocuments([]);
    } finally {
      setIsLoadingDocuments(false);
    }
  };
  
  /**
   * Filters documents based on search query
   */
  const filterDocuments = () => {
    if (!searchQuery.trim()) {
      setFilteredDocuments(documents);
      return;
    }
    
    const query = searchQuery.toLowerCase();
    const filtered = documents.filter(doc => {
      // Search in title, file name, and metadata
      const titleMatch = (doc.title || '').toLowerCase().includes(query);
      const fileNameMatch = (doc.file_name || '').toLowerCase().includes(query);
      
      // Search in metadata
      let metadataMatch = false;
      if (doc.metadata) {
        metadataMatch = Object.values(doc.metadata).some(value => 
          String(value).toLowerCase().includes(query)
        );
      }
      
      return titleMatch || fileNameMatch || metadataMatch;
    });
    
    setFilteredDocuments(filtered);
  };
  
  /**
   * Handles page change in pagination
   */
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  /**
   * Handles rows per page change in pagination
   */
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  /**
   * Opens the action menu for a document
   */
  const handleOpenActionMenu = (event, documentId) => {
    event.stopPropagation(); // Prevent row click
    setActionMenuAnchorEl(event.currentTarget);
    setSelectedDocumentId(documentId);
  };
  
  /**
   * Closes the action menu
   */
  const handleCloseActionMenu = () => {
    setActionMenuAnchorEl(null);
    setSelectedDocumentId(null);
  };
  
  /**
   * Opens delete confirmation dialog
   */
  const handleOpenDeleteDialog = (document) => {
    setDocumentToDelete(document);
    setDeleteDialogOpen(true);
    handleCloseActionMenu();
  };
  
  /**
   * Closes delete confirmation dialog
   */
  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setDocumentToDelete(null);
  };
  
  /**
   * Deletes a document
   */
  const handleDeleteDocument = async () => {
    if (!documentToDelete) return;
    
    setIsDeleting(true);
    
    try {
      const response = await fetch(`/api/pdf/${documentToDelete.id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete document');
      }
      
      // Remove from active documents if active
      if (isDocumentActive(documentToDelete.id)) {
        removeActiveDocument(documentToDelete.id);
      }
      
      // Remove from documents list
      setDocuments(prev => prev.filter(doc => doc.id !== documentToDelete.id));
      
      // Close dialog
      handleCloseDeleteDialog();
    } catch (error) {
      console.error('Error deleting document:', error);
      alert(error.message || 'Failed to delete document');
    } finally {
      setIsDeleting(false);
    }
  };
  
  /**
   * Toggles a document's active status
   */
  const toggleDocumentActive = (document) => {
    if (isDocumentActive(document.id)) {
      removeActiveDocument(document.id);
    } else {
      addActiveDocument({
        id: document.id,
        title: document.title || document.file_name || document.id
      });
    }
    
    handleCloseActionMenu();
  };
  
  /**
   * Navigates to chat with specific document
   */
  const handleChatWithDocument = (documentId) => {
    navigate(`/chat?document=${documentId}`);
    handleCloseActionMenu();
  };
  
  /**
   * Navigates to table generation with specific document
   */
  const handleGenerateTable = (documentId) => {
    navigate(`/tables/new?document=${documentId}`);
    handleCloseActionMenu();
  };
  
  /**
   * Extracts document type from metadata
   */
  const getDocumentType = (document) => {
    if (!document || !document.metadata) {
      return language === 'he' ? 'מסמך פיננסי' : 'Financial Document';
    }
    
    if (document.metadata.document_type) {
      return document.metadata.document_type;
    }
    
    // Try to infer document type from file name
    const fileName = document.file_name || '';
    
    if (fileName.includes('statement')) {
      return language === 'he' ? 'דף חשבון' : 'Account Statement';
    }
    
    if (fileName.includes('report')) {
      return language === 'he' ? 'דוח' : 'Report';
    }
    
    if (fileName.includes('portfolio') || fileName.includes('valuation')) {
      return language === 'he' ? 'דוח תיק השקעות' : 'Portfolio Valuation';
    }
    
    return language === 'he' ? 'מסמך פיננסי' : 'Financial Document';
  };
  
  /**
   * Formats a date for display
   */
  const formatDate = (dateString) => {
    if (!dateString) return '';
    
    try {
      return new Date(dateString).toLocaleDateString();
    } catch (e) {
      return dateString;
    }
  };
  
  /**
   * Formats file size for display
   */
  const formatFileSize = (bytes) => {
    if (!bytes || isNaN(parseInt(bytes))) return '';
    
    bytes = parseInt(bytes);
    if (bytes === 0) return '0 B';
    
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };
  
  // Calculate pagination
  const emptyRows = rowsPerPage - Math.min(rowsPerPage, filteredDocuments.length - page * rowsPerPage);
  
  // Get selected document (for action menu)
  const selectedDocument = documents.find(doc => doc.id === selectedDocumentId);
  
  return (
    <Paper sx={{ p: 3 }}>
      {/* Header with title and actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h1">
          {language === 'he' ? 'המסמכים שלי' : 'My Documents'}
        </Typography>
        
        <Button
          variant="contained"
          color="primary"
          startIcon={<UploadFileIcon />}
          onClick={() => navigate('/documents/upload')}
        >
          {language === 'he' ? 'העלאת מסמך' : 'Upload Document'}
        </Button>
      </Box>
      
      {/* Search and filter bar */}
      <Paper 
        sx={{ 
          p: '2px 4px', 
          display: 'flex', 
          alignItems: 'center', 
          width: '100%',
          mb: 3 
        }}
      >
        <IconButton sx={{ p: '10px' }} aria-label="menu">
          <FilterListIcon />
        </IconButton>
        
        <InputBase
          sx={{ ml: 1, flex: 1 }}
          placeholder={language === 'he' ? 'חיפוש מסמכים...' : 'Search documents...'}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        
        <IconButton type="button" sx={{ p: '10px' }} aria-label="search">
          <SearchIcon />
        </IconButton>
      </Paper>
      
      {/* Error alert */}
      {documentsError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {documentsError}
        </Alert>
      )}
      
      {/* Loading indicator */}
      {isLoadingDocuments ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : filteredDocuments.length === 0 ? (
        <Box sx={{ py: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchQuery.trim() 
              ? (language === 'he' ? 'לא נמצאו תוצאות' : 'No results found')
              : (language === 'he' ? 'אין מסמכים' : 'No documents')}
          </Typography>
          
          {!searchQuery.trim() && (
            <Button
              variant="outlined"
              color="primary"
              startIcon={<UploadFileIcon />}
              onClick={() => navigate('/documents/upload')}
              sx={{ mt: 2 }}
            >
              {language === 'he' ? 'העלאת המסמך הראשון שלך' : 'Upload Your First Document'}
            </Button>
          )}
        </Box>
      ) : (
        <>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    {language === 'he' ? 'שם מסמך' : 'Document Name'}
                  </TableCell>
                  <TableCell>
                    {language === 'he' ? 'סוג' : 'Type'}
                  </TableCell>
                  <TableCell>
                    {language === 'he' ? 'תאריך' : 'Date'}
                  </TableCell>
                  <TableCell>
                    {language === 'he' ? 'גודל' : 'Size'}
                  </TableCell>
                  <TableCell align="center">
                    {language === 'he' ? 'פעיל' : 'Active'}
                  </TableCell>
                  <TableCell align="right">
                    {language === 'he' ? 'פעולות' : 'Actions'}
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredDocuments
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((document) => (
                    <TableRow 
                      key={document.id}
                      hover
                      sx={{ 
                        cursor: 'pointer',
                        '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.04)' }
                      }}
                      onClick={() => navigate(`/documents/${document.id}`)}
                    >
                      <TableCell component="th" scope="row">
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <DescriptionIcon sx={{ mr: 1, color: 'primary.main' }} />
                          <Typography variant="body1">
                            {document.title || document.file_name || document.id}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={getDocumentType(document)} 
                          size="small"
                          variant="outlined" 
                        />
                      </TableCell>
                      <TableCell>
                        {formatDate(document.created_at || document.metadata?.date)}
                      </TableCell>
                      <TableCell>
                        {formatFileSize(document.size || document.metadata?.size)}
                      </TableCell>
                      <TableCell align="center">
                        {isDocumentActive(document.id) ? (
                          <CheckIcon color="success" />
                        ) : (
                          <ClearIcon color="disabled" />
                        )}
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                          <IconButton
                            size="small"
                            onClick={(e) => handleOpenActionMenu(e, document.id)}
                            sx={{ ml: 1 }}
                          >
                            <MoreVertIcon />
                          </IconButton>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                
                {emptyRows > 0 && (
                  <TableRow style={{ height: 53 * emptyRows }}>
                    <TableCell colSpan={6} />
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={filteredDocuments.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            labelRowsPerPage={language === 'he' ? 'שורות בעמוד:' : 'Rows per page:'}
            labelDisplayedRows={({ from, to, count }) => 
              language === 'he'
                ? `${from}-${to} מתוך ${count}`
                : `${from}-${to} of ${count}`
            }
          />
        </>
      )}
      
      {/* Document action menu */}
      <Menu
        anchorEl={actionMenuAnchorEl}
        open={Boolean(actionMenuAnchorEl)}
        onClose={handleCloseActionMenu}
      >
        <MenuItem 
          onClick={() => selectedDocument && toggleDocumentActive(selectedDocument)}
        >
          {selectedDocument && isDocumentActive(selectedDocument.id) 
            ? (language === 'he' ? 'הסר מפעילים' : 'Remove from active')
            : (language === 'he' ? 'הוסף לפעילים' : 'Add to active')}
        </MenuItem>
        <MenuItem 
          onClick={() => selectedDocumentId && handleChatWithDocument(selectedDocumentId)}
        >
          <ChatIcon fontSize="small" sx={{ mr: 1 }} />
          {language === 'he' ? 'צ\'אט עם מסמך' : 'Chat with document'}
        </MenuItem>
        <MenuItem 
          onClick={() => selectedDocumentId && handleGenerateTable(selectedDocumentId)}
        >
          <TableChartIcon fontSize="small" sx={{ mr: 1 }} />
          {language === 'he' ? 'צור טבלה' : 'Generate table'}
        </MenuItem>
        <Divider />
        <MenuItem 
          onClick={() => selectedDocument && handleOpenDeleteDialog(selectedDocument)}
          sx={{ color: 'error.main' }}
        >
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          {language === 'he' ? 'מחק מסמך' : 'Delete document'}
        </MenuItem>
      </Menu>
      
      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
      >
        <DialogTitle>
          {language === 'he' ? 'מחיקת מסמך' : 'Delete Document'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {language === 'he'
              ? `האם אתה בטוח שברצונך למחוק את המסמך "${documentToDelete?.title || documentToDelete?.file_name || documentToDelete?.id}"? לא ניתן לבטל פעולה זו.`
              : `Are you sure you want to delete the document "${documentToDelete?.title || documentToDelete?.file_name || documentToDelete?.id}"? This action cannot be undone.`}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} disabled={isDeleting}>
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
    </Paper>
  );
}

export default DocumentList;
