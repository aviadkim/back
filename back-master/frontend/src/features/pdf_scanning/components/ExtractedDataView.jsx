import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Divider,
  Typography,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Chip,
  useTheme,
} from '@mui/material';

// Translations for the component
const translations = {
  en: {
    extractedData: 'Extracted Data',
    financialSummary: 'Financial Summary',
    entities: 'Extracted Entities',
    tables: 'Extracted Tables',
    noData: 'No data has been extracted from this document.',
    noEntities: 'No entities were found in this document.',
    noTables: 'No tables were found in this document.',
    date: 'Date',
    institution: 'Institution',
    accountNumber: 'Account Number',
    accountHolder: 'Account Holder',
    totalIncome: 'Total Income',
    totalExpenses: 'Total Expenses',
    balance: 'Balance',
    currency: 'Currency',
    table: 'Table',
    entityType: 'Type',
    entityValue: 'Value',
    entityConfidence: 'Confidence',
  },
  he: {
    extractedData: 'נתונים שחולצו',
    financialSummary: 'סיכום פיננסי',
    entities: 'ישויות שחולצו',
    tables: 'טבלאות שחולצו',
    noData: 'לא חולצו נתונים ממסמך זה.',
    noEntities: 'לא נמצאו ישויות במסמך זה.',
    noTables: 'לא נמצאו טבלאות במסמך זה.',
    date: 'תאריך',
    institution: 'מוסד',
    accountNumber: 'מספר חשבון',
    accountHolder: 'בעל החשבון',
    totalIncome: 'סך הכנסות',
    totalExpenses: 'סך הוצאות',
    balance: 'יתרה',
    currency: 'מטבע',
    table: 'טבלה',
    entityType: 'סוג',
    entityValue: 'ערך',
    entityConfidence: 'ביטחון',
  },
};

/**
 * Format a numeric value as currency
 * 
 * @param {number} value - The numeric value
 * @param {string} currency - The currency code
 * @returns {string} The formatted currency value
 */
const formatCurrency = (value, currency = 'ILS') => {
  if (value === null || value === undefined) return '-';
  
  return new Intl.NumberFormat('he-IL', {
    style: 'currency',
    currency: currency,
  }).format(value);
};

/**
 * Format a date value
 * 
 * @param {string} dateStr - The date string
 * @returns {string} The formatted date
 */
const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('he-IL');
  } catch (err) {
    return dateStr;
  }
};

/**
 * ExtractedDataView component displays data extracted from a document
 * 
 * @param {Object} props - Component properties
 * @param {Object} props.document - The document object
 * @param {string} props.language - Current language (en/he)
 * @returns {JSX.Element} The rendered component
 */
const ExtractedDataView = ({ document, language = 'en' }) => {
  const theme = useTheme();
  const t = translations[language];
  
  // Check if the document has any extracted data
  const hasAnalysis = document?.analysis || document?.extracted_data;
  const extractedData = document?.analysis || document?.extracted_data || {};
  
  // Extract financial data
  const financialData = extractedData.financial_data || {};
  
  // Extract entities
  const entities = extractedData.entities || [];
  
  // Extract tables
  const tables = extractedData.tables || [];
  
  // If no data is available
  if (!hasAnalysis) {
    return (
      <Alert severity="info">
        {t.noData}
      </Alert>
    );
  }
  
  return (
    <Box>
      {/* Financial Summary */}
      <Typography variant="h6" gutterBottom>
        {t.financialSummary}
      </Typography>
      
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={3}>
            {/* Date and institution */}
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" color="text.secondary">
                {t.date}
              </Typography>
              <Typography variant="body1">
                {formatDate(financialData.date)}
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" color="text.secondary">
                {t.institution}
              </Typography>
              <Typography variant="body1">
                {financialData.institution || '-'}
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" color="text.secondary">
                {t.accountNumber}
              </Typography>
              <Typography variant="body1">
                {financialData.account_number || '-'}
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" color="text.secondary">
                {t.accountHolder}
              </Typography>
              <Typography variant="body1">
                {financialData.account_holder || '-'}
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
            </Grid>
            
            {/* Financial figures */}
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" color="text.secondary">
                {t.totalIncome}
              </Typography>
              <Typography 
                variant="body1" 
                color={financialData.total_income > 0 ? 'success.main' : 'text.primary'}
                fontWeight="medium"
              >
                {formatCurrency(financialData.total_income, financialData.currency)}
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" color="text.secondary">
                {t.totalExpenses}
              </Typography>
              <Typography 
                variant="body1" 
                color={financialData.total_expenses > 0 ? 'error.main' : 'text.primary'}
                fontWeight="medium"
              >
                {formatCurrency(financialData.total_expenses, financialData.currency)}
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" color="text.secondary">
                {t.balance}
              </Typography>
              <Typography 
                variant="body1" 
                color={
                  financialData.balance > 0 
                    ? 'success.main' 
                    : financialData.balance < 0 
                      ? 'error.main' 
                      : 'text.primary'
                }
                fontWeight="medium"
              >
                {formatCurrency(financialData.balance, financialData.currency)}
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" color="text.secondary">
                {t.currency}
              </Typography>
              <Typography variant="body1">
                {financialData.currency || 'ILS'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      {/* Extracted Entities */}
      <Typography variant="h6" gutterBottom>
        {t.entities}
      </Typography>
      
      {entities.length > 0 ? (
        <TableContainer component={Paper} sx={{ mb: 4 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t.entityType}</TableCell>
                <TableCell>{t.entityValue}</TableCell>
                <TableCell align="right">{t.entityConfidence}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {entities.map((entity, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Chip 
                      label={entity.type} 
                      size="small"
                      color={
                        entity.type.includes('MONEY') || entity.type.includes('CURRENCY')
                          ? 'success'
                          : entity.type.includes('DATE')
                            ? 'primary'
                            : entity.type.includes('PERSON')
                              ? 'secondary'
                              : 'default'
                      }
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{entity.text}</TableCell>
                  <TableCell align="right">
                    {entity.confidence
                      ? `${(entity.confidence * 100).toFixed(0)}%`
                      : '-'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Alert severity="info" sx={{ mb: 4 }}>
          {t.noEntities}
        </Alert>
      )}
      
      {/* Extracted Tables */}
      <Typography variant="h6" gutterBottom>
        {t.tables}
      </Typography>
      
      {tables.length > 0 ? (
        tables.map((table, tableIndex) => (
          <Box key={tableIndex} sx={{ mb: 4 }}>
            <Typography variant="subtitle1" gutterBottom>
              {`${t.table} ${tableIndex + 1}`}
            </Typography>
            
            <TableContainer component={Paper}>
              <Table size="small">
                {table.headers && (
                  <TableHead>
                    <TableRow>
                      {table.headers.map((header, idx) => (
                        <TableCell key={idx}>
                          {header}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                )}
                
                <TableBody>
                  {table.rows && table.rows.map((row, rowIdx) => (
                    <TableRow key={rowIdx}>
                      {row.map((cell, cellIdx) => (
                        <TableCell key={cellIdx}>
                          {cell}
                        </TableCell>
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
          {t.noTables}
        </Alert>
      )}
    </Box>
  );
};

export default ExtractedDataView;
