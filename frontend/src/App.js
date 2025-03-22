import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Paper, 
  Button, 
  Grid, 
  Divider,
  AppBar,
  Toolbar,
  CssBaseline,
  ThemeProvider,
  createTheme,
  IconButton,
  Snackbar,
  Alert,
  CircularProgress,
  useMediaQuery,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import { 
  CloudUpload as CloudUploadIcon,
  MenuBook as MenuBookIcon,
  TableChart as TableChartIcon,
  Menu as MenuIcon,
  Assessment as AssessmentIcon,
  Home as HomeIcon,
  Info as InfoIcon,
  UploadFile as UploadIcon
} from '@mui/icons-material';
import { rtlCache } from './rtlConfig';
import PdfViewer from './components/PdfViewer';
import DocumentTable from './components/DocumentTable';
import api from './services/api';

// יצירת ערכת נושא מותאמת עם תמיכה ב-RTL
const theme = createTheme({
  direction: 'rtl',
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5'
    }
  },
  typography: {
    fontFamily: "'Heebo', 'Roboto', 'Arial', sans-serif",
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          direction: 'rtl',
        },
      },
    },
  },
});

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeView, setActiveView] = useState('viewer');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // טיפול בהעלאת קובץ
  const handleFileChange = (event) => {
    const uploadedFile = event.target.files[0];
    
    if (uploadedFile && uploadedFile.type === 'application/pdf') {
      setSelectedFile(uploadedFile);
      setAnalysisResults(null);
      setError(null);
      
      // הצגת הודעה למשתמש
      setSnackbar({
        open: true,
        message: `הקובץ "${uploadedFile.name}" נטען בהצלחה`,
        severity: 'success'
      });
    } else {
      setError('נא להעלות קובץ PDF בלבד');
    }
  };
  
  // ניתוח מסמך שלם
  const analyzeDocument = async () => {
    if (!selectedFile) {
      setSnackbar({
        open: true,
        message: 'אנא בחר קובץ PDF לניתוח',
        severity: 'warning'
      });
      return;
    }
    
    setIsAnalyzing(true);
    
    try {
      const response = await api.analyzePdf(selectedFile);
      setAnalysisResults(response.data);
      
      setSnackbar({
        open: true,
        message: 'המסמך נותח בהצלחה',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error analyzing document:', error);
      
      setSnackbar({
        open: true,
        message: `שגיאה בניתוח המסמך: ${error.response?.data?.detail || error.message}`,
        severity: 'error'
      });
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  // סגירת הודעת snackbar
  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({
      ...prev,
      open: false
    }));
  };
  
  // פתיחה/סגירה של תפריט במובייל
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };
  
  // תוכן המגירה הצדדית
  const drawer = (
    <Box sx={{ width: 240 }}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          padding: 2,
          bgcolor: 'primary.main',
          color: 'white',
        }}
      >
        <MenuBookIcon sx={{ mr: 1 }} />
        <Typography variant="h6" noWrap>
          מערכת ניתוח מסמכים
        </Typography>
      </Box>
      <Divider />
      <List>
        <ListItem 
          button 
          selected={activeView === 'viewer'} 
          onClick={() => setActiveView('viewer')}
        >
          <ListItemIcon>
            <HomeIcon />
          </ListItemIcon>
          <ListItemText primary="צפייה במסמך" />
        </ListItem>
        
        <ListItem 
          button 
          selected={activeView === 'tables'} 
          onClick={() => setActiveView('tables')}
          disabled={!analysisResults}
        >
          <ListItemIcon>
            <TableChartIcon />
          </ListItemIcon>
          <ListItemText primary="טבלאות מזוהות" />
        </ListItem>
        
        <ListItem 
          button 
          selected={activeView === 'analysis'} 
          onClick={() => setActiveView('analysis')}
          disabled={!analysisResults}
        >
          <ListItemIcon>
            <AssessmentIcon />
          </ListItemIcon>
          <ListItemText primary="נתונים פיננסיים" />
        </ListItem>
        
        <ListItem 
          button 
          selected={activeView === 'about'} 
          onClick={() => setActiveView('about')}
        >
          <ListItemIcon>
            <InfoIcon />
          </ListItemIcon>
          <ListItemText primary="אודות" />
        </ListItem>
      </List>
      <Divider />
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary">
          גרסה 1.2.0
        </Typography>
        <Typography variant="caption" color="text.secondary">
          מופעל על ידי PyMuPDF
        </Typography>
      </Box>
    </Box>
  );
  
  // תצוגת 'אודות'
  const renderAboutView = () => (
    <Paper sx={{ p: 3, mt: 3 }}>
      <Typography variant="h5" gutterBottom>
        אודות המערכת
      </Typography>
      <Divider sx={{ mb: 2 }} />
      
      <Typography variant="body1" paragraph>
        מערכת ניתוח מסמכים פיננסיים מאפשרת הפקת מידע מובנה ממסמכים בנקאיים ופיננסיים
        באמצעות טכנולוגיות מתקדמות לעיבוד טקסט וזיהוי טבלאות.
      </Typography>
      
      <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
        יכולות עיקריות:
      </Typography>
      
      <Box component="ul" sx={{ pl: 2 }}>
        <Box component="li">
          <Typography>חילוץ טקסט מדויק ממסמכי PDF באיכות משתנה</Typography>
        </Box>
        <Box component="li">
          <Typography>זיהוי טבלאות באופן אוטומטי והמרתן למבנה נתונים</Typography>
        </Box>
        <Box component="li">
          <Typography>חילוץ מידע פיננסי כגון קודי ISIN, תאריכים וסכומים</Typography>
        </Box>
        <Box component="li">
          <Typography>ניתוח מבנה המסמך ופירוק לרכיבים מובנים</Typography>
        </Box>
      </Box>
      
      <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
        טכנולוגיות:
      </Typography>
      
      <Box component="ul" sx={{ pl: 2 }}>
        <Box component="li">
          <Typography>Python עם PyMuPDF לעיבוד PDF</Typography>
        </Box>
        <Box component="li">
          <Typography>FastAPI לשירותי Backend</Typography>
        </Box>
        <Box component="li">
          <Typography>React עם Material UI לממשק משתמש</Typography>
        </Box>
        <Box component="li">
          <Typography>אלגוריתמים מתקדמים לזיהוי דפוסים וטבלאות</Typography>
        </Box>
      </Box>
    </Paper>
  );
  
  // תצוגת טבלאות
  const renderTablesView = () => {
    if (!analysisResults) {
      return (
        <Paper sx={{ p: 3, mt: 3, textAlign: 'center' }}>
          <Typography color="text.secondary">
            אנא נתח מסמך תחילה כדי לצפות בטבלאות
          </Typography>
        </Paper>
      );
    }
    
    // בחירת הטבלה הראשונה מהעמוד הראשון שנותח, אם קיימת
    const firstPageKey = Object.keys(analysisResults.pages)[0];
    const firstTable = analysisResults.pages[firstPageKey]?.tables?.[0];
    
    return (
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h5" gutterBottom>
          טבלאות שזוהו
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Box mt={2}>
          {firstTable ? (
            <DocumentTable 
              table={firstTable} 
              filename={analysisResults.filename}
            />
          ) : (
            <Typography color="text.secondary" align="center">
              לא זוהו טבלאות במסמך
            </Typography>
          )}
        </Box>
      </Paper>
    );
  };
  
  // תצוגת נתונים פיננסיים
  const renderAnalysisView = () => {
    if (!analysisResults) {
      return (
        <Paper sx={{ p: 3, mt: 3, textAlign: 'center' }}>
          <Typography color="text.secondary">
            אנא נתח מסמך תחילה כדי לצפות בנתונים
          </Typography>
        </Paper>
      );
    }
    
    // איסוף נתונים פיננסיים מכל העמודים
    const financialData = {
      isins: new Set(),
      dates: new Set(),
      amounts: new Set(),
      possible_table_rows: new Set()
    };
    
    // איסוף נתונים מכל העמודים
    Object.values(analysisResults.pages).forEach(page => {
      if (page.financial_data) {
        if (page.financial_data.isins) {
          page.financial_data.isins.forEach(item => financialData.isins.add(item));
        }
        if (page.financial_data.dates) {
          page.financial_data.dates.forEach(item => financialData.dates.add(item));
        }
        if (page.financial_data.amounts) {
          page.financial_data.amounts.forEach(item => financialData.amounts.add(item));
        }
        if (page.financial_data.possible_table_rows) {
          page.financial_data.possible_table_rows.forEach(item => financialData.possible_table_rows.add(item));
        }
      }
    });
    
    return (
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h5" gutterBottom>
          ניתוח נתונים פיננסיים
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                קודי ISIN
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                סה"כ: {financialData.isins.size}
              </Typography>
              <Box sx={{ maxHeight: '200px', overflow: 'auto' }}>
                <Box component="ul" sx={{ pl: 2, mt: 1 }}>
                  {Array.from(financialData.isins).map((isin, index) => (
                    <Box component="li" key={index} sx={{ mb: 0.5 }}>
                      <Typography variant="body2">{isin}</Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                תאריכים
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                סה"כ: {financialData.dates.size}
              </Typography>
              <Box sx={{ maxHeight: '200px', overflow: 'auto' }}>
                <Box component="ul" sx={{ pl: 2, mt: 1 }}>
                  {Array.from(financialData.dates).slice(0, 20).map((date, index) => (
                    <Box component="li" key={index} sx={{ mb: 0.5 }}>
                      <Typography variant="body2">{date}</Typography>
                    </Box>
                  ))}
                  {financialData.dates.size > 20 && (
                    <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                      ...ועוד {financialData.dates.size - 20} תאריכים נוספים
                    </Typography>
                  )}
                </Box>
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                סכומים
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                סה"כ: {financialData.amounts.size}
              </Typography>
              <Box sx={{ maxHeight: '200px', overflow: 'auto' }}>
                <Box component="ul" sx={{ pl: 2, mt: 1 }}>
                  {Array.from(financialData.amounts).slice(0, 20).map((amount, index) => (
                    <Box component="li" key={index} sx={{ mb: 0.5 }}>
                      <Typography variant="body2">{amount}</Typography>
                    </Box>
                  ))}
                  {financialData.amounts.size > 20 && (
                    <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                      ...ועוד {financialData.amounts.size - 20} סכומים נוספים
                    </Typography>
                  )}
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Paper>
    );
  };
  
  useEffect(() => {
    const fetchInitialData = async () => {
      if (!file) return;
      
      setLoading(true);
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await api.analyzePdf(formData);
        setAnalysisResults(response.data);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, [file]); // Only re-run when file changes

  useEffect(() => {
    if (!selectedFile || isAnalyzing) return;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000); // 3min timeout

    const analyzeFile = async () => {
      setIsAnalyzing(true);
      try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await api.analyzePdf(selectedFile);
        setAnalysisResults(response.data);
        setSnackbar({
          open: true,
          message: 'המסמך נותח בהצלחה',
          severity: 'success'
        });
      } catch (err) {
        console.error('Error analyzing document:', err);
        setSnackbar({
          open: true,
          message: `שגיאה בניתוח המסמך: ${err.response?.data?.detail || err.message}`,
          severity: 'error'
        });
        setAnalysisResults(null);
      } finally {
        setIsAnalyzing(false);
      }
    };

    analyzeFile();
    
    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [selectedFile, isAnalyzing]); // Proper dependencies
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        {/* סרגל כלים */}
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { md: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              מערכת ניתוח מסמכים פיננסיים
            </Typography>
            
            <Box>
              <input
                accept="application/pdf"
                style={{ display: 'none' }}
                id="contained-button-file"
                type="file"
                onChange={handleFileChange}
              />
              <label htmlFor="contained-button-file">
                <Button
                  variant="contained"
                  component="span"
                  color="secondary"
                  startIcon={<CloudUploadIcon />}
                  size={isMobile ? "small" : "medium"}
                >
                  העלה PDF
                </Button>
              </label>
              
              <Button
                variant="contained"
                color="primary"
                onClick={analyzeDocument}
                disabled={!selectedFile || isAnalyzing}
                startIcon={isAnalyzing ? <CircularProgress size={20} color="inherit" /> : <AssessmentIcon />}
                sx={{ ml: 1 }}
                size={isMobile ? "small" : "medium"}
              >
                {isAnalyzing ? 'מנתח...' : 'נתח מסמך'}
              </Button>
            </Box>
          </Toolbar>
        </AppBar>
        
        {/* מגירה צדדית */}
        <Box
          component="nav"
          sx={{ width: { md: 240 }, flexShrink: { md: 0 } }}
        >
          {/* מגירה למובייל */}
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true, // שיפור ביצועים במובייל
            }}
            sx={{
              display: { xs: 'block', md: 'none' },
              '& .MuiDrawer-paper': { width: 240 },
            }}
          >
            {drawer}
          </Drawer>
          
          {/* מגירה קבועה למסכים גדולים */}
          <Drawer
            variant="permanent"
            sx={{
              display: { xs: 'none', md: 'block' },
              '& .MuiDrawer-paper': { width: 240, boxSizing: 'border-box', position: 'relative' },
            }}
            open
          >
            {drawer}
          </Drawer>
        </Box>
        
        {/* תוכן ראשי */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: { md: `calc(100% - 240px)` },
            marginTop: '64px',
          }}
        >
          {/* תצוגת הקובץ והניתוח */}
          {activeView === 'viewer' && (
            <Box mt={2}>
              {selectedFile ? (
                <PdfViewer 
                  pdfFile={selectedFile}
                  analysisResults={analysisResults}
                />
              ) : (
                <Paper sx={{ p: 5, textAlign: 'center' }}>
                  <CloudUploadIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h5" color="text.secondary" gutterBottom>
                    אין קובץ שנבחר
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    העלה קובץ PDF כדי להתחיל בניתוח
                  </Typography>
                  <input
                    accept="application/pdf"
                    style={{ display: 'none' }}
                    id="button-file-main"
                    type="file"
                    onChange={handleFileChange}
                  />
                  <label htmlFor="button-file-main">
                    <Button 
                      variant="contained" 
                      component="span"
                      startIcon={<CloudUploadIcon />}
                    >
                      בחר קובץ PDF
                    </Button>
                  </label>
                </Paper>
              )}
            </Box>
          )}
          
          {/* תצוגת טבלאות */}
          {activeView === 'tables' && renderTablesView()}
          
          {/* תצוגת נתונים פיננסיים */}
          {activeView === 'analysis' && renderAnalysisView()}
          
          {/* תצוגת אודות */}
          {activeView === 'about' && renderAboutView()}
        </Box>
      </Box>
      
      {/* הודעות */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;