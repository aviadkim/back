import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Button,
  FormGroup,
  FormControlLabel,
  Checkbox,
  IconButton,
  Collapse,
  Alert,
  Card,
  CardContent,
  Grid,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import TableChartIcon from '@mui/icons-material/TableChart';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import DownloadIcon from '@mui/icons-material/Download';

/**
 * TableGenerator component creates custom tables from financial document data
 * 
 * This component allows users to:
 * - Select fields to include in the table
 * - Define filters to narrow down the data
 * - Sort the data by specific fields
 * - Group data for summary views
 * - Apply templates for common financial tables
 * - Export the generated tables
 */
function TableGenerator({ documentId, language = 'he' }) {
  // Available fields from the document (will be loaded from API)
  const [availableFields, setAvailableFields] = useState([]);
  const [isLoadingFields, setIsLoadingFields] = useState(false);
  
  // Table specification state
  const [selectedFields, setSelectedFields] = useState([]);
  const [filters, setFilters] = useState([]);
  const [sortField, setSortField] = useState('');
  const [sortDirection, setSortDirection] = useState('desc');
  const [groupByField, setGroupByField] = useState('');
  
  // Generated table state
  const [tableData, setTableData] = useState(null);
  const [isGeneratingTable, setIsGeneratingTable] = useState(false);
  const [tableError, setTableError] = useState(null);
  
  // Templates and UI state
  const [showTemplates, setShowTemplates] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  
  // Load available fields when document ID changes
  useEffect(() => {
    if (documentId) {
      loadFieldsFromDocument();
    } else {
      // Clear state when no document is selected
      setAvailableFields([]);
      setSelectedFields([]);
      setFilters([]);
      setSortField('');
      setGroupByField('');
      setTableData(null);
    }
  }, [documentId]);
  
  /**
   * Loads available fields from the document
   */
  const loadFieldsFromDocument = async () => {
    setIsLoadingFields(true);
    setTableError(null);
    
    try {
      // Fetch document metadata to extract fields
      const response = await fetch(`/api/pdf/${documentId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load document data');
      }
      
      const result = await response.json();
      const documentData = result.document;
      
      // Extract fields from the document
      // This could be enhanced to detect types and structures
      let fields = [];
      
      // Add general document fields
      fields.push(
        { name: 'document_id', label: language === 'he' ? 'מזהה מסמך' : 'Document ID', type: 'text' },
        { name: 'processing_date', label: language === 'he' ? 'תאריך עיבוד' : 'Processing Date', type: 'date' }
      );
      
      // Add fields from document metadata
      if (documentData.metadata) {
        Object.entries(documentData.metadata).forEach(([key, value]) => {
          const formattedKey = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
          const fieldType = typeof value === 'number' ? 'number' : 
                           value instanceof Date ? 'date' : 'text';
          
          fields.push({
            name: `metadata.${key}`,
            label: language === 'he' ? key : formattedKey,
            type: fieldType
          });
        });
      }
      
      // Add fields from financial summary
      if (documentData.financial_summary) {
        Object.entries(documentData.financial_summary).forEach(([key, value]) => {
          const formattedKey = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
          const fieldType = typeof value === 'number' ? 'number' : 
                           value instanceof Date ? 'date' : 'text';
          
          fields.push({
            name: `financial_summary.${key}`,
            label: language === 'he' ? key : formattedKey,
            type: fieldType
          });
        });
      }
      
      // Add fields from tables
      if (documentData.tables && documentData.tables.length > 0) {
        documentData.tables.forEach((table, tableIndex) => {
          if (table.headers && table.headers.length > 0) {
            table.headers.forEach((header, headerIndex) => {
              fields.push({
                name: `tables.${tableIndex}.${headerIndex}`,
                label: header,
                type: 'text',
                tableIndex: tableIndex,
                columnIndex: headerIndex
              });
            });
          }
        });
      }
      
      setAvailableFields(fields);
      
      // Auto-select a few fields if none are selected
      if (selectedFields.length === 0 && fields.length > 0) {
        // Select first 3-5 fields as default
        setSelectedFields(fields.slice(0, Math.min(4, fields.length)).map(field => field.name));
      }
    } catch (error) {
      console.error('Error loading fields from document:', error);
      setTableError(error.message || 'Failed to load document fields');
    } finally {
      setIsLoadingFields(false);
    }
  };
  
  /**
   * Generates a table based on the current specification
   */
  const generateTable = async () => {
    // Validate inputs
    if (!documentId) {
      setTableError('No document selected');
      return;
    }
    
    if (selectedFields.length === 0) {
      setTableError('Please select at least one field');
      return;
    }
    
    setIsGeneratingTable(true);
    setTableError(null);
    
    try {
      // Create table specification
      const tableSpec = {
        columns: selectedFields,
        filters: filters.map(filter => ({
          field: filter.field,
          operator: filter.operator,
          value: filter.value
        })),
        sort_by: sortField ? { field: sortField, direction: sortDirection } : {},
        group_by: groupByField || null
      };
      
      // Generate the table
      const response = await fetch('/api/tables/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          document_id: documentId,
          specification: tableSpec
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error generating table');
      }
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to generate table');
      }
      
      setTableData(result.table);
    } catch (error) {
      console.error('Error generating table:', error);
      setTableError(error.message || 'Failed to generate table');
    } finally {
      setIsGeneratingTable(false);
    }
  };
  
  /**
   * Adds a new filter to the filter list
   */
  const addFilter = () => {
    if (availableFields.length === 0) return;
    
    const newFilter = {
      id: Date.now(),
      field: availableFields[0].name,
      operator: '=',
      value: ''
    };
    
    setFilters([...filters, newFilter]);
    setShowFilters(true); // Expand filters section when adding a new filter
  };
  
  /**
   * Removes a filter from the filter list
   */
  const removeFilter = (filterId) => {
    setFilters(filters.filter(filter => filter.id !== filterId));
  };
  
  /**
   * Updates a specific filter
   */
  const updateFilter = (filterId, field, value) => {
    setFilters(filters.map(filter => {
      if (filter.id === filterId) {
        return { ...filter, [field]: value };
      }
      return filter;
    }));
  };
  
  /**
   * Applies a template for a common financial table
   */
  const applyTemplate = (template) => {
    setSelectedFields(template.fields || []);
    setFilters(template.filters || []);
    setSortField(template.sortField || '');
    setSortDirection(template.sortDirection || 'desc');
    setGroupByField(template.groupBy || '');
  };
  
  /**
   * Exports the generated table as a CSV file
   */
  const exportTable = () => {
    if (!tableData || !tableData.headers || !tableData.rows) {
      return;
    }
    
    // Create CSV content
    const headers = tableData.headers.join(',');
    const rows = tableData.rows.map(row => {
      if (Array.isArray(row)) {
        return row.map(cell => `"${cell}"`).join(',');
      }
      return row;
    }).join('\n');
    
    const csvContent = `${headers}\n${rows}`;
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    // Create a download link and trigger it
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `table_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  // Predefined templates for common financial tables
  const templates = [
    {
      name: language === 'he' ? 'הרכב תיק השקעות' : 'Asset Allocation',
      description: language === 'he' ? 'הצגת החלוקה של נכסי ההשקעה לפי סוגים' : 'Shows the breakdown of investment assets by type',
      fields: ['asset_class', 'market_value', 'weight_percentage'],
      sortField: 'weight_percentage',
      sortDirection: 'desc'
    },
    {
      name: language === 'he' ? 'ניתוח ביצועים' : 'Performance Analysis',
      description: language === 'he' ? 'השוואת ביצועי נכסים שונים בתיק' : 'Compares performance of different assets in the portfolio',
      fields: ['security_name', 'performance_ytd', 'performance_1y', 'performance_3y'],
      sortField: 'performance_ytd',
      sortDirection: 'desc'
    },
    {
      name: language === 'he' ? 'חשיפה מטבעית' : 'Currency Exposure',
      description: language === 'he' ? 'ניתוח חשיפת התיק למטבעות שונים' : 'Analysis of portfolio exposure to different currencies',
      fields: ['currency', 'market_value', 'weight_percentage'],
      groupBy: 'currency',
      sortField: 'weight_percentage',
      sortDirection: 'desc'
    }
  ];
  
  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: '1200px', mx: 'auto' }}>
      <Typography variant="h5" component="h2" gutterBottom>
        {language === 'he' ? 'יצירת טבלה מותאמת אישית' : 'Generate Custom Table'}
      </Typography>
      
      {/* Document selector or info */}
      {!documentId ? (
        <Alert severity="info" sx={{ mb: 3 }}>
          {language === 'he' 
            ? 'אנא בחר מסמך תחילה כדי ליצור טבלה'
            : 'Please select a document first to create a table'}
        </Alert>
      ) : (
        <Alert severity="success" sx={{ mb: 3 }}>
          {language === 'he' 
            ? `מסמך נבחר: ${documentId}`
            : `Selected document: ${documentId}`}
        </Alert>
      )}
      
      {/* Error alert */}
      {tableError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {tableError}
        </Alert>
      )}
      
      {isLoadingFields ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Templates section */}
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <Box 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  mb: 1
                }}
                onClick={() => setShowTemplates(!showTemplates)}
                style={{ cursor: 'pointer' }}
              >
                <Typography variant="h6">
                  {language === 'he' ? 'תבניות טבלאות' : 'Table Templates'}
                </Typography>
                <IconButton size="small">
                  <ExpandMoreIcon 
                    sx={{ 
                      transform: showTemplates ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 0.3s'
                    }} 
                  />
                </IconButton>
              </Box>
              
              <Collapse in={showTemplates}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {language === 'he' 
                    ? 'בחר תבנית מוכנה מראש כדי להתחיל במהירות'
                    : 'Choose a predefined template to get started quickly'}
                </Typography>
                
                <Grid container spacing={2}>
                  {templates.map((template, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                      <Card 
                        variant="outlined"
                        sx={{ 
                          cursor: 'pointer',
                          '&:hover': {
                            boxShadow: 2
                          },
                          height: '100%'
                        }}
                        onClick={() => applyTemplate(template)}
                      >
                        <CardContent>
                          <Typography variant="subtitle1" gutterBottom>
                            {template.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {template.description}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Collapse>
            </CardContent>
          </Card>
          
          {/* Field selection */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              {language === 'he' ? 'בחירת שדות' : 'Select Fields'}
            </Typography>
            
            <FormGroup row>
              {availableFields.map((field) => (
                <FormControlLabel
                  key={field.name}
                  control={
                    <Checkbox
                      checked={selectedFields.includes(field.name)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedFields([...selectedFields, field.name]);
                        } else {
                          setSelectedFields(selectedFields.filter(name => name !== field.name));
                        }
                      }}
                    />
                  }
                  label={field.label}
                />
              ))}
            </FormGroup>
            
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2" component="div">
                {language === 'he' ? 'שדות נבחרים:' : 'Selected fields:'}
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {selectedFields.map((fieldName) => {
                  const field = availableFields.find(f => f.name === fieldName);
                  return (
                    <Chip 
                      key={fieldName}
                      label={field ? field.label : fieldName}
                      onDelete={() => setSelectedFields(selectedFields.filter(name => name !== fieldName))}
                      size="small"
                    />
                  );
                })}
              </Box>
            </Box>
          </Box>
          
          {/* Filters section */}
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <Box 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  mb: 1
                }}
                onClick={() => setShowFilters(!showFilters)}
                style={{ cursor: 'pointer' }}
              >
                <Typography variant="h6">
                  {language === 'he' ? 'סינון נתונים' : 'Filter Data'}
                </Typography>
                <IconButton size="small">
                  <ExpandMoreIcon 
                    sx={{ 
                      transform: showFilters ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 0.3s'
                    }} 
                  />
                </IconButton>
              </Box>
              
              <Collapse in={showFilters}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {language === 'he' 
                    ? 'הגדר תנאי סינון כדי להציג רק את הנתונים הרלוונטיים'
                    : 'Define filter conditions to show only relevant data'}
                </Typography>
                
                {filters.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontStyle: 'italic' }}>
                    {language === 'he' 
                      ? 'אין מסננים מוגדרים. כל הנתונים יוצגו.'
                      : 'No filters defined. All data will be shown.'}
                  </Typography>
                ) : (
                  <Box sx={{ mb: 2 }}>
                    {filters.map((filter) => (
                      <Box 
                        key={filter.id} 
                        sx={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: 1, 
                          mb: 1 
                        }}
                      >
                        <FormControl size="small" sx={{ minWidth: 120 }}>
                          <InputLabel>
                            {language === 'he' ? 'שדה' : 'Field'}
                          </InputLabel>
                          <Select
                            value={filter.field}
                            label={language === 'he' ? 'שדה' : 'Field'}
                            onChange={(e) => updateFilter(filter.id, 'field', e.target.value)}
                          >
                            {availableFields.map((field) => (
                              <MenuItem key={field.name} value={field.name}>
                                {field.label}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                        
                        <FormControl size="small" sx={{ minWidth: 100 }}>
                          <InputLabel>
                            {language === 'he' ? 'תנאי' : 'Condition'}
                          </InputLabel>
                          <Select
                            value={filter.operator}
                            label={language === 'he' ? 'תנאי' : 'Condition'}
                            onChange={(e) => updateFilter(filter.id, 'operator', e.target.value)}
                          >
                            <MenuItem value="=">=</MenuItem>
                            <MenuItem value="!=">!=</MenuItem>
                            <MenuItem value=">">&gt;</MenuItem>
                            <MenuItem value=">=">&gt;=</MenuItem>
                            <MenuItem value="<">&lt;</MenuItem>
                            <MenuItem value="<=">&lt;=</MenuItem>
                            <MenuItem value="contains">
                              {language === 'he' ? 'מכיל' : 'Contains'}
                            </MenuItem>
                          </Select>
                        </FormControl>
                        
                        <TextField 
                          size="small"
                          label={language === 'he' ? 'ערך' : 'Value'}
                          value={filter.value}
                          onChange={(e) => updateFilter(filter.id, 'value', e.target.value)}
                          sx={{ flexGrow: 1 }}
                        />
                        
                        <IconButton 
                          size="small" 
                          color="error"
                          onClick={() => removeFilter(filter.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    ))}
                  </Box>
                )}
                
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={addFilter}
                  disabled={availableFields.length === 0}
                  size="small"
                >
                  {language === 'he' ? 'הוסף סינון' : 'Add Filter'}
                </Button>
              </Collapse>
            </CardContent>
          </Card>
          
          {/* Sorting and grouping */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>
                  {language === 'he' ? 'מיון לפי' : 'Sort By'}
                </InputLabel>
                <Select
                  value={sortField}
                  label={language === 'he' ? 'מיון לפי' : 'Sort By'}
                  onChange={(e) => setSortField(e.target.value)}
                >
                  <MenuItem value="">
                    <em>{language === 'he' ? 'ללא מיון' : 'No sorting'}</em>
                  </MenuItem>
                  {selectedFields.map((fieldName) => {
                    const field = availableFields.find(f => f.name === fieldName);
                    return (
                      <MenuItem key={fieldName} value={fieldName}>
                        {field ? field.label : fieldName}
                      </MenuItem>
                    );
                  })}
                </Select>
              </FormControl>
              
              {sortField && (
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <Button
                    size="small"
                    variant={sortDirection === 'asc' ? 'contained' : 'outlined'}
                    startIcon={<ArrowUpwardIcon />}
                    onClick={() => setSortDirection('asc')}
                    sx={{ mr: 1 }}
                  >
                    {language === 'he' ? 'עולה' : 'Ascending'}
                  </Button>
                  <Button
                    size="small"
                    variant={sortDirection === 'desc' ? 'contained' : 'outlined'}
                    startIcon={<ArrowDownwardIcon />}
                    onClick={() => setSortDirection('desc')}
                  >
                    {language === 'he' ? 'יורד' : 'Descending'}
                  </Button>
                </Box>
              )}
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>
                  {language === 'he' ? 'קבץ לפי' : 'Group By'}
                </InputLabel>
                <Select
                  value={groupByField}
                  label={language === 'he' ? 'קבץ לפי' : 'Group By'}
                  onChange={(e) => setGroupByField(e.target.value)}
                >
                  <MenuItem value="">
                    <em>{language === 'he' ? 'ללא קיבוץ' : 'No grouping'}</em>
                  </MenuItem>
                  {selectedFields.map((fieldName) => {
                    const field = availableFields.find(f => f.name === fieldName);
                    return (
                      <MenuItem key={fieldName} value={fieldName}>
                        {field ? field.label : fieldName}
                      </MenuItem>
                    );
                  })}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
          
          {/* Generate button */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={<TableChartIcon />}
              onClick={generateTable}
              disabled={isGeneratingTable || selectedFields.length === 0 || !documentId}
            >
              {isGeneratingTable ? (
                <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
              ) : null}
              {language === 'he' ? 'צור טבלה' : 'Generate Table'}
            </Button>
          </Box>
          
          {/* Generated table display */}
          {tableData && (
            <Box sx={{ mt: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  {language === 'he' ? 'תוצאות' : 'Results'}
                </Typography>
                
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={exportTable}
                  size="small"
                >
                  {language === 'he' ? 'ייצא ל-CSV' : 'Export to CSV'}
                </Button>
              </Box>
              
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      {tableData.headers.map((header, index) => (
                        <TableCell key={index}>
                          <Typography variant="subtitle2">{header}</Typography>
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {tableData.rows.map((row, rowIndex) => (
                      <TableRow key={rowIndex}>
                        {row.map((cell, cellIndex) => (
                          <TableCell key={cellIndex}>{cell}</TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              {tableData.rows.length === 0 && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  {language === 'he' 
                    ? 'לא נמצאו נתונים התואמים את הקריטריונים שהוגדרו'
                    : 'No data found matching the defined criteria'}
                </Alert>
              )}
            </Box>
          )}
        </>
      )}
    </Paper>
  );
}

export default TableGenerator;
