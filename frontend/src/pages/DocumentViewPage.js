import {
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import React, { useState, useEffect } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Button,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Grid,
  Card,
  CardContent,
  TextField, // Added for question input
  IconButton // Added for send button
} from '@mui/material';
import {
  Description as DescriptionIcon,
  TableChart as TableChartIcon,
  AttachMoney as MoneyIcon,
  Chat as ChatIcon,
  ArrowBack as ArrowBackIcon,
  Send as SendIcon // Added for send button
} from '@mui/icons-material';
import { documentApi } from '../api/api'; // Use standardized API client
import Layout from '../components/Layout'; // Use main layout

// Tab panel component
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`document-tabpanel-${index}`}
      aria-labelledby={`document-tab-${index}`}
      {...other}
    >
      {/* Render Box only when tab is active */}
      {value === index && (
        <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}> {/* Responsive padding */}
          {children}
        </Box>
      )}
    </div>
  );
}

const DocumentViewPage = () => {
  const { documentId } = useParams(); // Get documentId from URL params
  const [loading, setLoading] = useState(true);
  const [document, setDocument] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [question, setQuestion] = useState(''); // State for question input
  const [answer, setAnswer] = useState(null); // State for answer
  const [asking, setAsking] = useState(false); // State for question loading

  // Load document data when component mounts or documentId changes
  useEffect(() => {
    const fetchData = async () => {
      if (!documentId) {
        setError("No document ID provided.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        setAnswer(null); // Clear previous answer

        const response = await documentApi.getDocument(documentId);

        if (response.status === 'success' && response.data) {
          setDocument(response.data);
        } else {
          setError(response.message || 'Failed to load document');
          setDocument(null);
        }
      } catch (err) {
        console.error("Error fetching document:", err);
        setError(err.message || 'An error occurred while loading the document');
        setDocument(null);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [documentId]); // Re-fetch if documentId changes

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Handle question input change
  const handleQuestionChange = (event) => {
    setQuestion(event.target.value);
  };

  // Handle asking a question
  const handleAskQuestion = async () => {
    if (!question.trim() || !documentId) return;

    setAsking(true);
    setError(null); // Clear previous errors
    setAnswer(null); // Clear previous answer

    try {
      const response = await documentApi.askDocumentQuestion(documentId, question);
      if (response.status === 'success' && response.data) {
        setAnswer(response.data); // Store the answer object
      } else {
        setError(response.message || "Failed to get answer.");
      }
    } catch (err) {
      console.error("Error asking question:", err);
      setError(err.message || "An error occurred while asking the question.");
    } finally {
      setAsking(false);
    }
  };


  // Format date utility
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString(undefined, { timeZone: 'UTC' }) + ' ' +
             new Date(dateString).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' });
    } catch (e) {
      return 'Invalid Date';
    }
  };

  // Get display label for language code
  const getLanguageLabel = (langCode) => {
    const languages = {
      'en': 'English',
      'he': 'Hebrew',
      'unknown': 'Unknown'
    };
    return languages[langCode] || langCode;
  };

  // Loading state
  if (loading) {
    return (
      <Layout title="Loading Document...">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  // Error state or document not found
  if (error || !document) {
    return (
      <Layout title="Document Error">
        <Alert severity="error" sx={{ mt: 2 }}>
          {error || 'Document could not be loaded or was not found.'}
        </Alert>
        <Box mt={2}>
          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            component={RouterLink}
            to="/documents"
          >
            Back to Documents
          </Button>
        </Box>
      </Layout>
    );
  }

  // Extract data safely
  const metadata = document.metadata || {};
  const documentText = document.document_text || {};
  const tables = document.tables || {};
  const financialData = document.financial_data || {};

  // Count tables safely
  const tablesCount = Object.values(tables).reduce((count, pageTables) => {
    // Ensure pageTables is an array before trying to get its length
    return count + (Array.isArray(pageTables) ? pageTables.length : 0);
  }, 0);

  return (
    <Layout title={metadata.original_filename || metadata.filename || 'Document View'}>
      {/* Document Header */}
      <Paper elevation={1} sx={{ p: { xs: 2, sm: 3 }, mb: 3 }}>
        <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box sx={{ overflow: 'hidden', mr: 2 }}>
            <Typography variant="h5" component="h1" noWrap title={metadata.original_filename || metadata.filename}>
              {metadata.original_filename || metadata.filename || 'Unnamed Document'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Uploaded: {formatDate(metadata.upload_date)}
            </Typography>
          </Box>
          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            component={RouterLink}
            to="/documents"
            sx={{ mt: { xs: 2, sm: 0 }, flexShrink: 0 }}
          >
            Back to List
          </Button>
        </Box>

        <Box display="flex" flexWrap="wrap" gap={1} mt={2}>
          <Chip label={`Language: ${getLanguageLabel(metadata.language)}`} size="small" />
          <Chip label={`Pages: ${metadata.page_count || 0}`} size="small" />
          <Chip label={`Tables: ${tablesCount}`} size="small" />
          {metadata.processing_status && (
            <Chip
              label={`Status: ${metadata.processing_status}`}
              size="small"
              color={metadata.processing_status === 'completed' ? 'success' : (metadata.processing_status === 'failed' ? 'error' : 'warning')}
            />
          )}
        </Box>
      </Paper>

      {/* Tab Navigation */}
      <Paper elevation={1}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable" // Allow scrolling on smaller screens
          scrollButtons="auto" // Show scroll buttons automatically
          indicatorColor="primary"
          textColor="primary"
          aria-label="Document view tabs"
        >
          <Tab icon={<DescriptionIcon />} iconPosition="start" label="Overview" />
          <Tab icon={<TableChartIcon />} iconPosition="start" label="Tables" />
          <Tab icon={<MoneyIcon />} iconPosition="start" label="Financial Data" />
          <Tab icon={<ChatIcon />} iconPosition="start" label="Ask Questions" />
        </Tabs>
        <Divider />

        {/* Overview Tab */}
        <TabPanel value={activeTab} index={0}>
          <Typography variant="h6" gutterBottom>Document Summary</Typography>
          <Grid container spacing={3}>
            {/* Document Details Card */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>Details</Typography>
                  <Divider sx={{ mb: 2 }} />
                  <Grid container spacing={1}>
                     <Grid item xs={5}><Typography variant="body2" color="text.secondary">Filename:</Typography></Grid>
                     <Grid item xs={7}><Typography variant="body2" sx={{ wordBreak: 'break-all' }}>{metadata.original_filename || metadata.filename || 'N/A'}</Typography></Grid>
                     <Grid item xs={5}><Typography variant="body2" color="text.secondary">Upload Date:</Typography></Grid>
                     <Grid item xs={7}><Typography variant="body2">{formatDate(metadata.upload_date)}</Typography></Grid>
                     <Grid item xs={5}><Typography variant="body2" color="text.secondary">Pages:</Typography></Grid>
                     <Grid item xs={7}><Typography variant="body2">{metadata.page_count || 0}</Typography></Grid>
                     <Grid item xs={5}><Typography variant="body2" color="text.secondary">Language:</Typography></Grid>
                     <Grid item xs={7}><Typography variant="body2">{getLanguageLabel(metadata.language)}</Typography></Grid>
                     <Grid item xs={5}><Typography variant="body2" color="text.secondary">Status:</Typography></Grid>
                     <Grid item xs={7}><Chip label={metadata.processing_status || 'N/A'} size="small" color={metadata.processing_status === 'completed' ? 'success' : 'warning'} /></Grid>
                     <Grid item xs={5}><Typography variant="body2" color="text.secondary">Tables Found:</Typography></Grid>
                     <Grid item xs={7}><Typography variant="body2">{tablesCount}</Typography></Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
            {/* Document Preview Card (Placeholder) */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>Preview</Typography>
                  <Divider sx={{ mb: 2 }} />
                  <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" sx={{ backgroundColor: 'grey.100', borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary">Document preview unavailable</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          {/* Content Sample Section */}
          <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>Content Sample (First Page)</Typography>
          <Card variant="outlined">
            <CardContent sx={{ maxHeight: 300, overflowY: 'auto' }}>
              {documentText && documentText[0]?.text ? (
                 <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                   {documentText[0].text}
                 </Typography>
              ) : (
                 <Typography variant="body2" color="text.secondary">No text content extracted or available for the first page.</Typography>
              )}
            </CardContent>
          </Card>
        </TabPanel>

        {/* Tables Tab */}
        <TabPanel value={activeTab} index={1}>
          <Typography variant="h6" gutterBottom>Extracted Tables ({tablesCount})</Typography>
          {tablesCount === 0 ? (
            <Alert severity="info">No tables were extracted from this document.</Alert>
          ) : (
            Object.entries(tables).sort(([a],[b]) => Number(a) - Number(b)).map(([pageNum, pageTables]) => ( // Sort by page number
              <Box key={`page-${pageNum}`} mb={4}>
                <Typography variant="subtitle1" gutterBottom sx={{ borderBottom: 1, borderColor: 'divider', pb: 1 }}>
                  Page {Number(pageNum) + 1}
                </Typography>
                {Array.isArray(pageTables) && pageTables.length > 0 ? (
                  pageTables.map((table, tableIndex) => (
                    <Card variant="outlined" sx={{ mb: 2 }} key={`page-${pageNum}-table-${tableIndex}`}>
                      <CardContent>
                        <Typography variant="subtitle2" gutterBottom>
                          Table {tableIndex + 1} {table.title ? `(${table.title})` : ''}
                        </Typography>
                        <TableContainer sx={{ maxHeight: 400 }}> {/* Limit table height */}
                          <Table size="small" stickyHeader>
                            <TableHead>
                              <TableRow>
                                {table.header && table.header.length > 0 ? (
                                  table.header.map((cell, cellIndex) => (
                                    <TableCell key={`header-${cellIndex}`} sx={{ fontWeight: 'bold', backgroundColor: 'grey.100' }}>{cell}</TableCell>
                                  ))
                                ) : (
                                  // Generate generic headers if none exist but rows do
                                  Array.isArray(table.rows) && table.rows[0] && Array.isArray(table.rows[0]) ? (
                                    table.rows[0].map((_, cellIndex) => (
                                      <TableCell key={`gen-header-${cellIndex}`} sx={{ fontWeight: 'bold', backgroundColor: 'grey.100' }}>Col {cellIndex + 1}</TableCell>
                                    ))
                                  ) : <TableCell sx={{ fontWeight: 'bold', backgroundColor: 'grey.100' }}>Data</TableCell>
                                )}
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {Array.isArray(table.rows) && table.rows.length > 0 ? (
                                table.rows.map((row, rowIndex) => (
                                  <TableRow key={`row-${rowIndex}`} hover>
                                    {Array.isArray(row) ? (
                                      row.map((cell, cellIndex) => (
                                        <TableCell key={`cell-${rowIndex}-${cellIndex}`}>{String(cell)}</TableCell> // Ensure cell content is string
                                      ))
                                    ) : (
                                      <TableCell colSpan={table.header?.length || 1}>Invalid row data</TableCell>
                                    )}
                                  </TableRow>
                                ))
                              ) : (
                                <TableRow>
                                  <TableCell colSpan={table.header?.length || 1} align="center">No row data available</TableCell>
                                </TableRow>
                              )}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary">No tables extracted on this page.</Typography>
                )}
              </Box>
            ))
          )}
        </TabPanel>

        {/* Financial Data Tab */}
        <TabPanel value={activeTab} index={2}>
          <Typography variant="h6" gutterBottom>Financial Data Analysis</Typography>
           {!financialData || Object.keys(financialData).length === 0 || (!financialData.metrics && !financialData.tables_analysis) ? (
             <Alert severity="info">No specific financial data points were automatically extracted.</Alert>
           ) : (
             <Grid container spacing={3}>
               {/* Financial Metrics */}
               {financialData.metrics && Object.keys(financialData.metrics).length > 0 && (
                 <Grid item xs={12} md={6}>
                   <Card variant="outlined">
                     <CardContent>
                       <Typography variant="subtitle1" gutterBottom>Key Metrics Found (by Page)</Typography>
                       <Divider sx={{ mb: 2 }} />
                       <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                         {Object.entries(financialData.metrics).sort(([a],[b]) => Number(a) - Number(b)).map(([page, metrics]) => (
                           <Box key={`metrics-page-${page}`} mb={2}>
                             <Typography variant="subtitle2">Page {Number(page) + 1}</Typography>
                             {Object.entries(metrics).map(([key, values]) => (
                               <Box key={key} ml={2}>
                                 <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}:</Typography>
                                 <List dense disablePadding sx={{ pl: 2 }}>
                                   {(Array.isArray(values) ? values : [values]).slice(0, 5).map((value, index) => ( // Limit display
                                     <ListItem key={index} disableGutters sx={{ py: 0 }}>
                                       <ListItemText primaryTypographyProps={{ variant: 'body2' }}>
                                         {typeof value === 'object' && value.code ? `${value.code} (${value.details?.name || 'Details N/A'})` : String(value)}
                                       </ListItemText>
                                     </ListItem>
                                   ))}
                                   {Array.isArray(values) && values.length > 5 && <ListItemText secondary="... more" />}
                                 </List>
                               </Box>
                             ))}
                           </Box>
                         ))}
                       </Box>
                     </CardContent>
                   </Card>
                 </Grid>
               )}
               {/* Table Analysis */}
               {financialData.tables_analysis && Object.keys(financialData.tables_analysis).length > 0 && (
                 <Grid item xs={12} md={6}>
                   <Card variant="outlined">
                     <CardContent>
                       <Typography variant="subtitle1" gutterBottom>Table Analysis (by Page)</Typography>
                       <Divider sx={{ mb: 2 }} />
                       <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                         {Object.entries(financialData.tables_analysis).sort(([a],[b]) => Number(a) - Number(b)).map(([page, tableAnalyses]) => (
                           <Box key={`analysis-page-${page}`} mb={2}>
                             <Typography variant="subtitle2">Page {Number(page) + 1}</Typography>
                             {Array.isArray(tableAnalyses) && tableAnalyses.length > 0 ? (
                               tableAnalyses.map((analysis, index) => (
                                 <Box key={`analysis-${index}`} ml={2} mb={1}>
                                   <Typography variant="body2">
                                     Table {index + 1}: Type - {analysis.analysis?.table_type?.replace(/_/g, ' ') || 'Unknown'}
                                   </Typography>
                                   {/* Optionally display more analysis details */}
                                 </Box>
                               ))
                             ) : (
                               <Typography variant="body2" color="text.secondary">No analysis for tables on this page.</Typography>
                             )}
                           </Box>
                         ))}
                       </Box>
                     </CardContent>
                   </Card>
                 </Grid>
               )}
             </Grid>
           )}
        </TabPanel>

        {/* Ask Questions Tab */}
        <TabPanel value={activeTab} index={3}>
          <Typography variant="h6" gutterBottom>Ask Questions About This Document</Typography>
          <Paper elevation={0} sx={{ p: 2, backgroundColor: 'grey.50', mb: 3 }}>
             <Grid container spacing={2} alignItems="center">
                <Grid item xs>
                   <TextField
                      fullWidth
                      variant="outlined"
                      size="small"
                      label="Ask a question..."
                      value={question}
                      onChange={handleQuestionChange}
                      disabled={asking}
                   />
                </Grid>
                <Grid item>
                   <IconButton color="primary" onClick={handleAskQuestion} disabled={!question.trim() || asking}>
                      {asking ? <CircularProgress size={24} /> : <SendIcon />}
                   </IconButton>
                </Grid>
             </Grid>
          </Paper>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {answer && (
             <Card variant="outlined">
                <CardContent>
                   <Typography variant="subtitle1" gutterBottom>Answer:</Typography>
                   <Typography variant="body1" sx={{ mb: 2 }}>{answer.response}</Typography>
                   {answer.sources && answer.sources.length > 0 && (
                      <>
                         <Typography variant="subtitle2" gutterBottom>Sources:</Typography>
                         <List dense disablePadding>
                            {answer.sources.map((source, index) => (
                               <ListItem key={index} disableGutters sx={{ py: 0 }}>
                                  <ListItemText primaryTypographyProps={{ variant: 'body2' }}>{source}</ListItemText>
                               </ListItem>
                            ))}
                         </List>
                      </>
                   )}
                </CardContent>
             </Card>
          )}
        </TabPanel>
      </Paper>
    </Layout>
  );
};

export default DocumentViewPage;