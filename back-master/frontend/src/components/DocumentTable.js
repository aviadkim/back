import React, { useState } from 'react';
import { 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
  TablePagination,
  LinearProgress
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

// קומפוננטה להצגת טבלה המחולצת ממסמך
const DocumentTable = ({ table, isLoading = false, filename }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedCell, setCopiedCell] = useState(null);
  
  // בדיקה האם יש טבלה תקפה
  const hasValidTable = table && 
    table.headers && 
    table.headers.length > 0 && 
    table.rows && 
    table.rows.length > 0;
  
  // סינון שורות לפי חיפוש
  const filteredRows = hasValidTable
    ? table.rows.filter(row => 
        row.some(cell => 
          cell.toString().toLowerCase().includes(searchQuery.toLowerCase())
        )
      )
    : [];
  
  // החלפת עמוד
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  // שינוי מספר שורות לעמוד
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // העתקת תא
  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedCell(text);
    
    // איפוס סטטוס ההעתקה לאחר 2 שניות
    setTimeout(() => {
      setCopiedCell(null);
    }, 2000);
  };
  
  // הורדת הטבלה כקובץ CSV
  const handleDownloadCSV = () => {
    if (!hasValidTable) return;
    
    const headers = table.headers.join(',');
    const rows = table.rows.map(row => row.join(','));
    const csvContent = [headers, ...rows].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename || 'table'}_export.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  // מציג לוחית עם מידע על מהימנות הטבלה
  const renderConfidenceChip = () => {
    if (!table || typeof table.confidence !== 'number') return null;
    
    const confidence = table.confidence * 100;
    let color = 'error';
    
    if (confidence >= 80) {
      color = 'success';
    } else if (confidence >= 60) {
      color = 'primary';
    } else if (confidence >= 40) {
      color = 'warning';
    }
    
    return (
      <Tooltip title="מידת הביטחון בזיהוי מבנה הטבלה">
        <Chip 
          label={`רמת ביטחון: ${confidence.toFixed(0)}%`}
          color={color}
          size="small"
          sx={{ ml: 1 }}
        />
      </Tooltip>
    );
  };
  
  // תוכן בזמן טעינה
  if (isLoading) {
    return (
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box sx={{ width: '100%' }}>
          <Typography variant="body2" color="text.secondary" align="center" mb={1}>
            מחלץ טבלה...
          </Typography>
          <LinearProgress />
        </Box>
      </Paper>
    );
  }
  
  // אם אין טבלה תקפה
  if (!hasValidTable) {
    return (
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Box display="flex" flexDirection="column" alignItems="center">
          <Typography variant="body1" color="text.secondary" align="center">
            לא נמצאה טבלה תקפה במסמך
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" mt={1}>
            נסה לבחור עמוד אחר או לנתח את המסמך שוב
          </Typography>
        </Box>
      </Paper>
    );
  }
  
  return (
    <Paper variant="outlined" sx={{ width: '100%' }}>
      <Box p={2} display="flex" justifyContent="space-between" alignItems="center">
        <Box display="flex" alignItems="center">
          <Typography variant="subtitle1" component="div">
            טבלה {table.table_id || ''}
          </Typography>
          {renderConfidenceChip()}
        </Box>
        
        <Box display="flex" alignItems="center">
          <TextField
            size="small"
            variant="outlined"
            placeholder="חיפוש..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
            sx={{ ml: 2 }}
          />
          
          <Tooltip title="הורדת הטבלה כקובץ CSV">
            <IconButton onClick={handleDownloadCSV} size="small" sx={{ ml: 1 }}>
              <FileDownloadIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      <TableContainer component={Box} sx={{ maxHeight: 440 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              {table.headers.map((header, index) => (
                <TableCell 
                  key={index}
                  align="right"
                  sx={{ 
                    fontWeight: 'bold',
                    backgroundColor: '#f5f5f5',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {header}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredRows
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((row, rowIndex) => (
                <TableRow 
                  key={rowIndex}
                  hover
                  sx={{ '&:nth-of-type(odd)': { backgroundColor: 'rgba(0, 0, 0, 0.02)' } }}
                >
                  {row.map((cell, cellIndex) => (
                    <TableCell 
                      key={cellIndex} 
                      align="right"
                      sx={{ position: 'relative' }}
                    >
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <span>{cell}</span>
                        <Tooltip title="העתק לזיכרון">
                          <IconButton 
                            size="small" 
                            onClick={() => handleCopy(cell)}
                            color={copiedCell === cell ? "success" : "default"}
                            sx={{ 
                              opacity: 0.4, 
                              '&:hover': { opacity: 1 },
                              p: 0.5
                            }}
                          >
                            {copiedCell === cell ? 
                              <CheckCircleIcon fontSize="small" /> : 
                              <ContentCopyIcon fontSize="small" />
                            }
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  ))}
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        rowsPerPageOptions={[5, 10, 25, 50]}
        component="div"
        count={filteredRows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="שורות לעמוד:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} מתוך ${count}`}
      />
    </Paper>
  );
};

export default DocumentTable; 