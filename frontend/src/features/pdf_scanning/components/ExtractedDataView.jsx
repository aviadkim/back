import React, { useState } from 'react';
import { 
  Box, 
  Tab, 
  Tabs, 
  Typography, 
  Paper, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DataObjectIcon from '@mui/icons-material/DataObject';
import TableChartIcon from '@mui/icons-material/TableChart';
import TextSnippetIcon from '@mui/icons-material/TextSnippet';
import DescriptionIcon from '@mui/icons-material/Description';

/**
 * Displays the extracted data from a processed financial document
 * 
 * This component presents document data in multiple tabs:
 * - Overview: Basic document information
 * - Text: Extracted text content
 * - Tables: Extracted tables from the document
 * - Raw Data: JSON representation of all extracted data
 */
function ExtractedDataView({ data }) {
  const [tabValue, setTabValue] = useState(0);

  // Handle tab changes
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Tab navigation */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          aria-label="Document data tabs"
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<DescriptionIcon />} label="Overview" />
          <Tab icon={<TextSnippetIcon />} label="Text" />
          <Tab icon={<TableChartIcon />} label="Tables" />
          <Tab icon={<DataObjectIcon />} label="Raw Data" />
        </Tabs>
      </Box>

      {/* Overview Tab */}
      <TabPanel value={tabValue} index={0}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Document Information
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableBody>
                <TableRow>
                  <TableCell component="th" scope="row" width="30%">Document ID</TableCell>
                  <TableCell>{data.document_id || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell component="th" scope="row">Original Filename</TableCell>
                  <TableCell>{data.original_filename || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell component="th" scope="row">Processing Date</TableCell>
                  <TableCell>{data.processing_date ? new Date(data.processing_date).toLocaleString() : 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell component="th" scope="row">Language</TableCell>
                  <TableCell>{data.language || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell component="th" scope="row">Page Count</TableCell>
                  <TableCell>{data.page_count || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell component="th" scope="row">Tables Found</TableCell>
                  <TableCell>{data.tables ? data.tables.length : 0}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
        
        {/* Document metadata section */}
        {data.metadata && Object.keys(data.metadata).length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Document Metadata
            </Typography>
            
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableBody>
                  {Object.entries(data.metadata).map(([key, value]) => (
                    <TableRow key={key}>
                      <TableCell component="th" scope="row" width="30%">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </TableCell>
                      <TableCell>{typeof value === 'object' ? JSON.stringify(value) : value}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
        
        {/* Financial summary section */}
        {data.financial_summary && Object.keys(data.financial_summary).length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Financial Summary
            </Typography>
            
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableBody>
                  {Object.entries(data.financial_summary).map(([key, value]) => (
                    <TableRow key={key}>
                      <TableCell component="th" scope="row" width="30%">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </TableCell>
                      <TableCell>
                        {typeof value === 'number' 
                          ? value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) 
                          : (typeof value === 'object' ? JSON.stringify(value) : value)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </TabPanel>

      {/* Text Content Tab */}
      <TabPanel value={tabValue} index={1}>
        <Typography variant="h6" gutterBottom>
          Extracted Text
        </Typography>
        
        <Paper 
          variant="outlined" 
          sx={{ 
            p: 2, 
            maxHeight: '500px', 
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            direction: data.language === 'he' ? 'rtl' : 'ltr',
            fontSize: '0.9rem'
          }}
        >
          {data.text_content || 'No text content extracted.'}
        </Paper>
      </TabPanel>

      {/* Tables Tab */}
      <TabPanel value={tabValue} index={2}>
        <Typography variant="h6" gutterBottom>
          Extracted Tables
        </Typography>
        
        {(!data.tables || data.tables.length === 0) ? (
          <Typography variant="body1" color="text.secondary">
            No tables found in document.
          </Typography>
        ) : (
          data.tables.map((table, index) => (
            <Accordion key={index} sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>
                  Table {index + 1}
                  {table.table_title && ` - ${table.table_title}`}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    {/* Render headers if available */}
                    {table.headers && table.headers.length > 0 && (
                      <TableHead>
                        <TableRow>
                          {table.headers.map((header, idx) => (
                            <TableCell key={idx}>{header}</TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                    )}
                    
                    <TableBody>
                      {/* Render rows if available in expected format */}
                      {table.rows && table.rows.map((row, rowIdx) => (
                        <TableRow key={rowIdx}>
                          {Array.isArray(row) ? (
                            // If row is an array of values
                            row.map((cell, cellIdx) => (
                              <TableCell key={cellIdx}>{cell}</TableCell>
                            ))
                          ) : (
                            // If row is a string (fallback)
                            <TableCell>{row}</TableCell>
                          )}
                        </TableRow>
                      ))}
                      
                      {/* Fallback if table content is provided as a string */}
                      {!table.rows && table.content && (
                        <TableRow>
                          <TableCell>{table.content}</TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
                
                {/* Table metadata */}
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Table Information
                  </Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    {table.page_number && (
                      <Chip label={`Page ${table.page_number}`} size="small" />
                    )}
                    {table.confidence && (
                      <Chip 
                        label={`Confidence: ${Math.round(table.confidence * 100)}%`} 
                        size="small"
                        color={table.confidence > 0.7 ? "success" : table.confidence > 0.4 ? "warning" : "error"}
                      />
                    )}
                    {table.row_count && (
                      <Chip label={`${table.row_count} rows`} size="small" />
                    )}
                    {table.column_count && (
                      <Chip label={`${table.column_count} columns`} size="small" />
                    )}
                  </Box>
                </Box>
              </AccordionDetails>
            </Accordion>
          ))
        )}
      </TabPanel>

      {/* Raw Data Tab */}
      <TabPanel value={tabValue} index={3}>
        <Typography variant="h6" gutterBottom>
          Raw Extracted Data (JSON)
        </Typography>
        
        <Paper 
          variant="outlined" 
          sx={{ 
            p: 2, 
            maxHeight: '500px', 
            overflow: 'auto' 
          }}
        >
          <pre style={{ margin: 0 }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        </Paper>
      </TabPanel>
    </Box>
  );
}

// Tab Panel component for the tabs
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
      {value === index && (
        <Box sx={{ p: 1 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export default ExtractedDataView;
