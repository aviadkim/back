import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
  Card,
  CardContent,
  Button,
  Collapse
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';

/**
 * DocumentContext component displays information about the documents being used in the chat
 * 
 * This component:
 * - Fetches metadata for documents referenced in the chat
 * - Displays key information like document type, date, and financial data
 * - Provides context for the AI chat assistant
 */
function DocumentContext({ documentIds = [], language = 'he' }) {
  // Document data state
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // UI state for expandable document details
  const [expandedDocId, setExpandedDocId] = useState(null);
  
  // Load document data when document IDs change
  useEffect(() => {
    if (documentIds && documentIds.length > 0) {
      loadDocuments();
    } else {
      setDocuments([]);
    }
  }, [documentIds]);
  
  /**
   * Loads document metadata for the given document IDs
   */
  const loadDocuments = async () => {
    if (!documentIds || documentIds.length === 0) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Load each document's metadata
      const documentsData = await Promise.all(
        documentIds.map(async (docId) => {
          try {
            const response = await fetch(`/api/pdf/${docId}`);
            
            if (!response.ok) {
              throw new Error(`Failed to load document ${docId}`);
            }
            
            const result = await response.json();
            return result.document;
          } catch (error) {
            console.error(`Error loading document ${docId}:`, error);
            return { 
              id: docId,
              error: true,
              errorMessage: error.message
            };
          }
        })
      );
      
      setDocuments(documentsData.filter(Boolean));
    } catch (error) {
      console.error('Error loading documents:', error);
      setError(error.message || 'Failed to load document information');
    } finally {
      setIsLoading(false);
    }
  };
  
  /**
   * Toggles expanded state for a document
   */
  const toggleDocumentExpanded = (docId) => {
    if (expandedDocId === docId) {
      setExpandedDocId(null);
    } else {
      setExpandedDocId(docId);
    }
  };
  
  /**
   * Extracts and formats a date from document metadata
   */
  const extractDate = (document) => {
    if (!document || !document.metadata) return null;
    
    // Try to find date fields in metadata
    const dateFields = [
      'date', 'report_date', 'statement_date', 'valuation_date', 
      'created_at', 'updated_at', 'processing_date'
    ];
    
    for (const field of dateFields) {
      if (document.metadata[field]) {
        try {
          return new Date(document.metadata[field]).toLocaleDateString();
        } catch (e) {
          return document.metadata[field];
        }
      }
    }
    
    return null;
  };
  
  /**
   * Returns document type based on metadata
   */
  const getDocumentType = (document) => {
    if (!document || !document.metadata) return language === 'he' ? 'מסמך פיננסי' : 'Financial Document';
    
    if (document.metadata.document_type) {
      return document.metadata.document_type;
    }
    
    // Try to infer document type from file name or content
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
   * Renders document summary information for a document
   */
  const renderDocumentSummary = (document) => {
    if (!document) return null;
    
    const documentDate = extractDate(document);
    const documentType = getDocumentType(document);
    
    return (
      <Box>
        <Typography variant="subtitle1" component="div" gutterBottom>
          {document.metadata?.title || document.file_name || document.id}
        </Typography>
        
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
          <Chip
            size="small"
            label={documentType}
            icon={<DescriptionIcon />}
          />
          
          {documentDate && (
            <Chip
              size="small"
              label={documentDate}
              icon={<CalendarTodayIcon />}
            />
          )}
          
          {document.metadata?.institution && (
            <Chip
              size="small"
              label={document.metadata.institution}
              icon={<AccountBalanceIcon />}
            />
          )}
        </Box>
      </Box>
    );
  };
  
  /**
   * Renders detailed information for a document
   */
  const renderDocumentDetails = (document) => {
    if (!document || !document.metadata) return null;
    
    // Extract financial summary if available
    const financialSummary = document.financial_summary || {};
    
    return (
      <Collapse in={expandedDocId === document.id}>
        <Box sx={{ mt: 2 }}>
          {Object.keys(financialSummary).length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                {language === 'he' ? 'תקציר פיננסי' : 'Financial Summary'}
              </Typography>
              
              <List dense disablePadding>
                {Object.entries(financialSummary).map(([key, value]) => {
                  // Format key for display
                  const displayKey = key
                    .replace(/_/g, ' ')
                    .replace(/\b\w/g, (l) => l.toUpperCase());
                  
                  // Format value
                  let displayValue = value;
                  if (typeof value === 'number') {
                    // Format as currency if it looks like a money value
                    if (key.includes('amount') || key.includes('value') || key.includes('balance')) {
                      displayValue = new Intl.NumberFormat(language === 'he' ? 'he-IL' : 'en-US', {
                        style: 'currency',
                        currency: document.metadata.currency || 'ILS'
                      }).format(value);
                    } else if (key.includes('percentage')) {
                      // Format as percentage
                      displayValue = `${value.toFixed(2)}%`;
                    }
                  }
                  
                  return (
                    <ListItem key={key} disablePadding sx={{ py: 0.5 }}>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" color="text.secondary">
                              {language === 'he' ? key : displayKey}
                            </Typography>
                            <Typography variant="body2" fontWeight="medium">
                              {displayValue}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  );
                })}
              </List>
            </Box>
          )}
          
          {document.metadata && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                {language === 'he' ? 'פרטי מסמך' : 'Document Details'}
              </Typography>
              
              <List dense disablePadding>
                {Object.entries(document.metadata)
                  .filter(([key]) => !key.includes('_id') && key !== 'title')
                  .map(([key, value]) => {
                    // Format key for display
                    const displayKey = key
                      .replace(/_/g, ' ')
                      .replace(/\b\w/g, (l) => l.toUpperCase());
                    
                    // Skip complex nested objects
                    if (typeof value === 'object' && value !== null) {
                      return null;
                    }
                    
                    return (
                      <ListItem key={key} disablePadding sx={{ py: 0.5 }}>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                              <Typography variant="body2" color="text.secondary">
                                {language === 'he' ? key : displayKey}
                              </Typography>
                              <Typography variant="body2">
                                {value}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                    );
                  })
                  .filter(Boolean)}
              </List>
            </Box>
          )}
        </Box>
      </Collapse>
    );
  };
  
  // If no documents are selected
  if (documentIds.length === 0) {
    return (
      <Alert severity="info">
        {language === 'he'
          ? 'לא נבחרו מסמכים. השיחה תהיה כללית ללא הקשר מסמכים.'
          : 'No documents selected. The conversation will be general without document context.'}
      </Alert>
    );
  }
  
  // Loading state
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
        <CircularProgress size={24} />
        <Typography variant="body2" sx={{ ml: 1 }}>
          {language === 'he' ? 'טוען פרטי מסמכים...' : 'Loading documents...'}
        </Typography>
      </Box>
    );
  }
  
  // Error state
  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }
  
  // Empty state (no documents loaded)
  if (documents.length === 0) {
    return (
      <Alert severity="warning">
        {language === 'he'
          ? 'לא ניתן לטעון את פרטי המסמכים'
          : 'Unable to load document details'}
      </Alert>
    );
  }
  
  // Documents loaded successfully
  return (
    <Box>
      {documents.map((document, index) => (
        <Card
          key={document.id}
          variant="outlined"
          sx={{
            mb: 2,
            cursor: 'pointer'
          }}
          onClick={() => toggleDocumentExpanded(document.id)}
        >
          <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
            {/* Document with error */}
            {document.error ? (
              <Alert severity="error" sx={{ py: 0 }}>
                {language === 'he'
                  ? `שגיאה בטעינת מסמך: ${document.id}`
                  : `Error loading document: ${document.id}`}
              </Alert>
            ) : (
              <>
                {/* Document summary */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ flexGrow: 1 }}>
                    {renderDocumentSummary(document)}
                  </Box>
                  
                  <ExpandMoreIcon
                    sx={{
                      transform: expandedDocId === document.id ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 0.3s'
                    }}
                  />
                </Box>
                
                {/* Document details (expandable) */}
                {renderDocumentDetails(document)}
              </>
            )}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}

export default DocumentContext;
