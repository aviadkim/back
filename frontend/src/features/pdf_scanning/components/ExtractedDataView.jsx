import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Divider,
  Chip,
  Grid,
  Paper,
  Alert,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';

/**
 * ExtractedDataView component displays financial data extracted from documents
 * 
 * The component organizes and formats different types of financial data:
 * - Financial metrics (e.g., totals, averages, ratios)
 * - Account information
 * - Transaction details
 * - Investment holdings
 * - Performance metrics
 */
function ExtractedDataView({ document, language = 'he' }) {
  if (!document || !document.extracted_data) {
    return (
      <Alert severity="info">
        {language === 'he' 
          ? 'אין נתונים פיננסיים מחולצים למסמך זה' 
          : 'No extracted financial data available for this document'}
      </Alert>
    );
  }
  
  const { extracted_data } = document;
  
  // Helper function to format currency values
  const formatCurrency = (value, currencyCode = 'ILS') => {
    if (value === undefined || value === null) return '-';
    
    return new Intl.NumberFormat(language === 'he' ? 'he-IL' : 'en-US', {
      style: 'currency',
      currency: currencyCode
    }).format(value);
  };
  
  // Helper function to format percentage values
  const formatPercentage = (value) => {
    if (value === undefined || value === null) return '-';
    
    return `${value.toFixed(2)}%`;
  };
  
  // Helper function to format dates
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    
    try {
      return new Date(dateString).toLocaleDateString();
    } catch (e) {
      return dateString;
    }
  };
  
  return (
    <Box>
      {/* Financial Metrics Section */}
      {extracted_data.financial_metrics && (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {language === 'he' ? 'מדדים פיננסיים' : 'Financial Metrics'}
            </Typography>
            
            <Grid container spacing={2}>
              {Object.entries(extracted_data.financial_metrics).map(([key, value]) => (
                <Grid item xs={12} sm={6} md={4} key={key}>
                  <Box sx={{ p: 2, borderRadius: 1, bgcolor: 'background.paper' }}>
                    <Typography variant="caption" color="text.secondary">
                      {key.replace(/_/g, ' ')}
                    </Typography>
                    <Typography variant="h6">
                      {typeof value === 'number' && key.includes('percent') 
                        ? formatPercentage(value)
                        : typeof value === 'number' && (key.includes('amount') || key.includes('value') || key.includes('balance'))
                          ? formatCurrency(value, document.metadata?.currency)
                          : typeof value === 'string' && key.includes('date')
                            ? formatDate(value)
                            : value}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}
      
      {/* Account Information Section */}
      {extracted_data.accounts && extracted_data.accounts.length > 0 && (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {language === 'he' ? 'פרטי חשבונות' : 'Account Information'}
            </Typography>
            
            {extracted_data.accounts.map((account, index) => (
              <Paper variant="outlined" sx={{ p: 2, mb: 2 }} key={index}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography variant="subtitle1">
                    {account.account_name || (language === 'he' ? 'חשבון' : 'Account')} {account.account_number ? `#${account.account_number}` : ''}
                  </Typography>
                  
                  <Chip 
                    icon={<AccountBalanceIcon />} 
                    label={account.account_type || (language === 'he' ? 'חשבון' : 'Account')} 
                    size="small"
                  />
                </Box>
                
                <Grid container spacing={2}>
                  {account.balance && (
                    <Grid item xs={12} sm={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">
                          {language === 'he' ? 'יתרה:' : 'Balance:'}
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {formatCurrency(account.balance, account.currency || document.metadata?.currency)}
                        </Typography>
                      </Box>
                    </Grid>
                  )}
                  
                  {account.available_balance && (
                    <Grid item xs={12} sm={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">
                          {language === 'he' ? 'יתרה זמינה:' : 'Available Balance:'}
                        </Typography>
                        <Typography variant="body1">
                          {formatCurrency(account.available_balance, account.currency || document.metadata?.currency)}
                        </Typography>
                      </Box>
                    </Grid>
                  )}
                  
                  {account.last_updated && (
                    <Grid item xs={12} sm={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">
                          {language === 'he' ? 'עדכון אחרון:' : 'Last Updated:'}
                        </Typography>
                        <Typography variant="body1">
                          {formatDate(account.last_updated)}
                        </Typography>
                      </Box>
                    </Grid>
                  )}
                </Grid>
                
                {account.additional_details && Object.keys(account.additional_details).length > 0 && (
                  <>
                    <Divider sx={{ my: 1 }} />
                    <Typography variant="subtitle2" gutterBottom>
                      {language === 'he' ? 'פרטים נוספים' : 'Additional Details'}
                    </Typography>
                    
                    <Grid container spacing={1}>
                      {Object.entries(account.additional_details).map(([key, value]) => (
                        <Grid item xs={12} sm={6} key={key}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" color="text.secondary">
                              {key.replace(/_/g, ' ')}:
                            </Typography>
                            <Typography variant="body2">
                              {value}
                            </Typography>
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  </>
                )}
              </Paper>
            ))}
          </CardContent>
        </Card>
      )}
      
      {/* Investment Holdings Section */}
      {extracted_data.investments && extracted_data.investments.length > 0 && (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {language === 'he' ? 'נכסי השקעה' : 'Investment Holdings'}
            </Typography>
            
            <Paper variant="outlined">
              <Box sx={{ overflowX: 'auto' }}>
                <Box
                  component="table"
                  sx={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    '& th, & td': {
                      px: 2,
                      py: 1.5,
                      borderBottom: '1px solid',
                      borderColor: 'divider',
                    },
                  }}
                >
                  <Box component="thead" sx={{ backgroundColor: 'background.default' }}>
                    <Box component="tr">
                      <Box component="th" sx={{ textAlign: 'left' }}>
                        {language === 'he' ? 'שם נכס' : 'Security Name'}
                      </Box>
                      <Box component="th" sx={{ textAlign: 'right' }}>
                        {language === 'he' ? 'כמות' : 'Quantity'}
                      </Box>
                      <Box component="th" sx={{ textAlign: 'right' }}>
                        {language === 'he' ? 'מחיר יחידה' : 'Unit Price'}
                      </Box>
                      <Box component="th" sx={{ textAlign: 'right' }}>
                        {language === 'he' ? 'שווי שוק' : 'Market Value'}
                      </Box>
                      <Box component="th" sx={{ textAlign: 'right' }}>
                        {language === 'he' ? 'משקל בתיק' : 'Weight'}
                      </Box>
                    </Box>
                  </Box>
                  <Box component="tbody">
                    {extracted_data.investments.map((investment, index) => (
                      <Box component="tr" key={index}>
                        <Box component="td">
                          <Typography variant="body2">
                            {investment.security_name || '-'}
                          </Typography>
                          {investment.symbol && (
                            <Typography variant="caption" color="text.secondary">
                              {investment.symbol}
                            </Typography>
                          )}
                        </Box>
                        <Box component="td" sx={{ textAlign: 'right' }}>
                          <Typography variant="body2">
                            {investment.quantity !== undefined ? investment.quantity.toLocaleString() : '-'}
                          </Typography>
                        </Box>
                        <Box component="td" sx={{ textAlign: 'right' }}>
                          <Typography variant="body2">
                            {investment.unit_price !== undefined
                              ? formatCurrency(investment.unit_price, investment.currency || document.metadata?.currency)
                              : '-'}
                          </Typography>
                        </Box>
                        <Box component="td" sx={{ textAlign: 'right' }}>
                          <Typography variant="body2" fontWeight="medium">
                            {investment.market_value !== undefined
                              ? formatCurrency(investment.market_value, investment.currency || document.metadata?.currency)
                              : '-'}
                          </Typography>
                        </Box>
                        <Box component="td" sx={{ textAlign: 'right' }}>
                          <Typography variant="body2">
                            {investment.weight !== undefined
                              ? formatPercentage(investment.weight)
                              : '-'}
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                  </Box>
                </Box>
              </Box>
            </Paper>
          </CardContent>
        </Card>
      )}
      
      {/* No Data Case */}
      {!extracted_data.financial_metrics && 
       (!extracted_data.accounts || extracted_data.accounts.length === 0) &&
       (!extracted_data.investments || extracted_data.investments.length === 0) && (
        <Alert severity="info">
          {language === 'he'
            ? 'לא נמצאו נתונים פיננסיים מובנים במסמך זה'
            : 'No structured financial data found in this document'}
        </Alert>
      )}
    </Box>
  );
}

export default ExtractedDataView;
