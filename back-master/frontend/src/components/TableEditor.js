import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Button,
  IconButton,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  Card,
  CardHeader,
  CardContent,
  Grid,
  CircularProgress,
  Tooltip,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Download as DownloadIcon,
  FileCopy as FileCopyIcon,
  ContentCopy as ContentCopyIcon,
} from '@mui/icons-material';

const TableEditor = ({ 
  extractedTables = [], 
  documentId,
  onSaveTemplate,
  savedTemplates = [],
  onApplyTemplate,
}) => {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [editingHeaders, setEditingHeaders] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const [templateName, setTemplateName] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  useEffect(() => {
    if (extractedTables && extractedTables.length > 0) {
      const formattedTables = extractedTables.map((table, index) => ({
        id: `table-${index}`,
        name: `טבלה ${index + 1}`,
        headers: table[0] || [],
        rows: table.slice(1) || [],
        originalHeaders: table[0] || [],
      }));
      setTables(formattedTables);
      if (!selectedTable && formattedTables.length > 0) {
        setSelectedTable(formattedTables[0].id);
      }
    }
  }, [extractedTables]);

  const handleHeaderChange = (index, value) => {
    if (!selectedTable) return;
    
    const updatedTables = tables.map(table => {
      if (table.id === selectedTable) {
        const newHeaders = [...table.headers];
        newHeaders[index] = value;
        return { ...table, headers: newHeaders };
      }
      return table;
    });
    
    setTables(updatedTables);
  };

  const handleCellChange = (rowIndex, colIndex, value) => {
    if (!selectedTable) return;
    
    const updatedTables = tables.map(table => {
      if (table.id === selectedTable) {
        const newRows = [...table.rows];
        if (!newRows[rowIndex]) {
          newRows[rowIndex] = Array(table.headers.length).fill('');
        }
        newRows[rowIndex][colIndex] = value;
        return { ...table, rows: newRows };
      }
      return table;
    });
    
    setTables(updatedTables);
  };

  const addRow = () => {
    if (!selectedTable) return;
    
    const updatedTables = tables.map(table => {
      if (table.id === selectedTable) {
        const emptyRow = Array(table.headers.length).fill('');
        return { ...table, rows: [...table.rows, emptyRow] };
      }
      return table;
    });
    
    setTables(updatedTables);
  };

  const deleteRow = (rowIndex) => {
    if (!selectedTable) return;
    
    const updatedTables = tables.map(table => {
      if (table.id === selectedTable) {
        const newRows = [...table.rows];
        newRows.splice(rowIndex, 1);
        return { ...table, rows: newRows };
      }
      return table;
    });
    
    setTables(updatedTables);
  };

  const addColumn = () => {
    if (!selectedTable) return;
    
    const updatedTables = tables.map(table => {
      if (table.id === selectedTable) {
        const newHeaders = [...table.headers, `עמודה ${table.headers.length + 1}`];
        const newRows = table.rows.map(row => [...row, '']);
        return { 
          ...table, 
          headers: newHeaders, 
          rows: newRows,
          originalHeaders: table.originalHeaders.length < newHeaders.length 
            ? [...table.originalHeaders, ''] 
            : table.originalHeaders
        };
      }
      return table;
    });
    
    setTables(updatedTables);
  };

  const deleteColumn = (colIndex) => {
    if (!selectedTable) return;
    
    const updatedTables = tables.map(table => {
      if (table.id === selectedTable) {
        const newHeaders = [...table.headers];
        newHeaders.splice(colIndex, 1);
        
        const newRows = table.rows.map(row => {
          const newRow = [...row];
          newRow.splice(colIndex, 1);
          return newRow;
        });
        
        const newOriginalHeaders = [...table.originalHeaders];
        if (newOriginalHeaders.length > colIndex) {
          newOriginalHeaders.splice(colIndex, 1);
        }
        
        return { 
          ...table, 
          headers: newHeaders, 
          rows: newRows,
          originalHeaders: newOriginalHeaders
        };
      }
      return table;
    });
    
    setTables(updatedTables);
  };

  const getCurrentTable = () => {
    return tables.find(table => table.id === selectedTable) || null;
  };

  const handleSaveTemplate = () => {
    const currentTable = getCurrentTable();
    if (!currentTable) return;
    
    setLoading(true);
    
    const templateData = {
      name: templateName,
      documentId: documentId,
      headers: currentTable.headers,
      originalHeaders: currentTable.originalHeaders,
    };
    
    onSaveTemplate(templateData)
      .then(() => {
        setSaveDialogOpen(false);
        setTemplateName('');
        
        setSnackbar({
          open: true,
          message: 'התבנית נשמרה בהצלחה',
          severity: 'success'
        });
      })
      .catch(error => {
        console.error('Error saving template:', error);
        
        setSnackbar({
          open: true,
          message: 'אירעה שגיאה בשמירת התבנית',
          severity: 'error'
        });
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleApplyTemplate = () => {
    if (!selectedTemplate) return;
    
    setLoading(true);
    
    onApplyTemplate(selectedTemplate, documentId)
      .then(result => {
        if (result && result.mappedData) {
          // עדכון הטבלה המוצגת עם הנתונים החדשים
          const updatedTables = tables.map(table => {
            if (table.id === selectedTable) {
              return { 
                ...table, 
                headers: result.template.headers,
                rows: result.mappedData,
                originalHeaders: result.template.originalHeaders
              };
            }
            return table;
          });
          
          setTables(updatedTables);
          setTemplateDialogOpen(false);
          
          setSnackbar({
            open: true,
            message: 'התבנית הוחלה בהצלחה',
            severity: 'success'
          });
        }
      })
      .catch(error => {
        console.error('Error applying template:', error);
        
        setSnackbar({
          open: true,
          message: 'אירעה שגיאה בהחלת התבנית',
          severity: 'error'
        });
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const exportToCsv = () => {
    const currentTable = getCurrentTable();
    if (!currentTable) return;
    
    const csvContent = [
      currentTable.headers.join(','),
      ...currentTable.rows.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `${currentTable.name}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const copyToClipboard = () => {
    const currentTable = getCurrentTable();
    if (!currentTable) return;
    
    const textContent = [
      currentTable.headers.join('\t'),
      ...currentTable.rows.map(row => row.join('\t'))
    ].join('\n');
    
    navigator.clipboard.writeText(textContent)
      .then(() => {
        setSnackbar({
          open: true,
          message: 'הטבלה הועתקה ללוח',
          severity: 'success'
        });
      })
      .catch(err => {
        console.error('Error copying to clipboard:', err);
        setSnackbar({
          open: true,
          message: 'אירעה שגיאה בהעתקה ללוח',
          severity: 'error'
        });
      });
  };

  const currentTable = getCurrentTable();

  if (tables.length === 0) {
    return (
      <Card sx={{ height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <CardContent>
          <Typography align="center" color="text.secondary">
            לא נמצאו טבלאות במסמך.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ mb: 2, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <FormControl fullWidth variant="outlined" size="small">
              <InputLabel>בחר טבלה</InputLabel>
              <Select
                value={selectedTable || ''}
                onChange={(e) => setSelectedTable(e.target.value)}
                label="בחר טבלה"
              >
                {tables.map((table) => (
                  <MenuItem key={table.id} value={table.id}>
                    {table.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', gap: 1, justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={() => setEditingHeaders(!editingHeaders)}
                size="small"
              >
                {editingHeaders ? 'סיום עריכת כותרות' : 'ערוך כותרות'}
              </Button>
              <Button
                variant="outlined" 
                startIcon={<SaveIcon />}
                onClick={() => setSaveDialogOpen(true)}
                size="small"
              >
                שמור כתבנית
              </Button>
              <Button
                variant="outlined"
                startIcon={<ContentCopyIcon />}
                onClick={copyToClipboard}
                size="small"
              >
                העתק
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={exportToCsv}
                size="small"
              >
                ייצא
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {currentTable && (
        <Paper sx={{ flexGrow: 1, overflow: 'auto' }}>
          <TableContainer sx={{ maxHeight: '100%' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox" />
                  {currentTable.headers.map((header, index) => (
                    <TableCell key={index} align="center">
                      {editingHeaders ? (
                        <TextField
                          value={header}
                          onChange={(e) => handleHeaderChange(index, e.target.value)}
                          variant="outlined"
                          size="small"
                          fullWidth
                        />
                      ) : (
                        <Box>
                          {header}
                          {currentTable.originalHeaders[index] && currentTable.originalHeaders[index] !== header && (
                            <Tooltip title="שם מקורי">
                              <Chip
                                label={currentTable.originalHeaders[index]}
                                size="small"
                                variant="outlined"
                                sx={{ ml: 1, fontSize: '0.7rem', height: 20 }}
                              />
                            </Tooltip>
                          )}
                        </Box>
                      )}
                    </TableCell>
                  ))}
                  {editingHeaders && (
                    <TableCell align="center">
                      <Button
                        onClick={addColumn}
                        variant="contained"
                        color="primary"
                        size="small"
                        startIcon={<AddIcon />}
                      >
                        הוסף עמודה
                      </Button>
                    </TableCell>
                  )}
                </TableRow>
              </TableHead>
              <TableBody>
                {currentTable.rows.map((row, rowIndex) => (
                  <TableRow key={rowIndex}>
                    <TableCell padding="checkbox">
                      <IconButton
                        size="small"
                        onClick={() => deleteRow(rowIndex)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                    {row.map((cell, colIndex) => (
                      <TableCell key={colIndex} align="center">
                        <TextField
                          value={cell || ''}
                          onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
                          variant="outlined"
                          size="small"
                          fullWidth
                        />
                      </TableCell>
                    ))}
                    {editingHeaders && (
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => deleteColumn(colIndex)}
                          color="error"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={addRow}
            >
              הוסף שורה חדשה
            </Button>
          </Box>
        </Paper>
      )}
      
      {/* דיאלוג שמירת תבנית */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)}>
        <DialogTitle>שמירת תבנית טבלה</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            שמירת התבנית תאפשר לך להשתמש בה בעתיד עבור מסמכים דומים.
          </Typography>
          <TextField
            label="שם התבנית"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            fullWidth
            variant="outlined"
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)} color="inherit">
            ביטול
          </Button>
          <Button 
            onClick={handleSaveTemplate} 
            color="primary" 
            variant="contained"
            disabled={!templateName || loading}
            startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
          >
            שמור
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* דיאלוג החלת תבנית */}
      <Dialog open={templateDialogOpen} onClose={() => setTemplateDialogOpen(false)}>
        <DialogTitle>החלת תבנית טבלה</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            בחר תבנית כדי להחיל אותה על הטבלה הנוכחית.
          </Typography>
          <Autocomplete
            fullWidth
            options={savedTemplates}
            getOptionLabel={(option) => option.name}
            value={selectedTemplate}
            onChange={(_, newValue) => setSelectedTemplate(newValue)}
            renderInput={(params) => <TextField {...params} label="בחר תבנית" />}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTemplateDialogOpen(false)} color="inherit">
            ביטול
          </Button>
          <Button 
            onClick={handleApplyTemplate} 
            color="primary" 
            variant="contained"
            disabled={!selectedTemplate || loading}
            startIcon={loading ? <CircularProgress size={20} /> : <CheckIcon />}
          >
            החל תבנית
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* הודעות */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={5000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert 
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default TableEditor;