import React, { useState, useEffect } from 'react';
import { Box, Typography, CircularProgress, Button, Grid, Paper, Divider, Chip, Tab, Tabs } from '@mui/material';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import DownloadIcon from '@mui/icons-material/Download';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import TableChartIcon from '@mui/icons-material/TableChart';
import InfoIcon from '@mui/icons-material/Info';
import api from '../services/api';

// הגדרת Worker ל-PDF.js
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const PdfViewer = ({ pdfFile, documentId }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.2);
  const [pdfBlob, setPdfBlob] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedTable, setSelectedTable] = useState(null);
  
  // טעינת קובץ ה-PDF
  useEffect(() => {
    const loadPdf = async () => {
      try {
        if (pdfFile instanceof Blob) {
          // אם זה כבר Blob, השתמש בו ישירות
          setPdfBlob(pdfFile);
          setIsLoading(false);
        } else if (documentId) {
          // אם יש מזהה מסמך, טען מהשרת
          const response = await api.get(`/documents/${documentId}/download`, {
            responseType: 'blob'
          });
          setPdfBlob(response.data);
          setIsLoading(false);
        } else if (pdfFile) {
          // אם זה URL או נתיב, טען את הקובץ
          const response = await fetch(pdfFile);
          const blob = await response.blob();
          setPdfBlob(blob);
          setIsLoading(false);
        }
      } catch (error) {
        console.error('Error loading PDF:', error);
        setIsLoading(false);
      }
    };
    
    loadPdf();
  }, [pdfFile, documentId]);
  
  // עדכון מספר העמודים
  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
  };
  
  // דפדוף
  const goToPrevPage = () => {
    setPageNumber(prevPageNumber => Math.max(prevPageNumber - 1, 1));
  };
  
  const goToNextPage = () => {
    setPageNumber(prevPageNumber => Math.min(prevPageNumber + 1, numPages));
  };
  
  // שינוי זום
  const zoomIn = () => {
    setScale(prevScale => Math.min(prevScale + 0.2, 3));
  };
  
  const zoomOut = () => {
    setScale(prevScale => Math.max(prevScale - 0.2, 0.6));
  };
  
  // ניתוח העמוד הנוכחי
  const analyzePage = async () => {
    if (!pdfBlob) return;
    
    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', pdfBlob, 'document.pdf');
      formData.append('pages', pageNumber);
      
      const response = await api.post('/pdf/analyze', formData);
      setAnalysisResults(response.data);
      setActiveTab(1); // עבור ללשונית הניתוח
      
      // אם יש טבלאות בתוצאות, בחר את הראשונה
      const pageKey = String(pageNumber);
      if (response.data.pages[pageKey]?.tables?.length > 0) {
        setSelectedTable(response.data.pages[pageKey].tables[0]);
      }
    } catch (error) {
      console.error('Error analyzing PDF:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  // החלפת לשונית
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // תוכן ניתוח העמוד
  const renderAnalysisContent = () => {
    if (!analysisResults) return null;
    
    const pageKey = String(pageNumber);
    const pageData = analysisResults.pages[pageKey];
    
    if (!pageData) {
      return (
        <Typography color="text.secondary" align="center" py={3}>
          אין נתונים מנותחים עבור עמוד זה
        </Typography>
      );
    }
    
    return (
      <Box>
        {/* מידע פיננסי */}
        <Typography variant="h6" gutterBottom>
          מידע פיננסי
        </Typography>
        
        <Grid container spacing={2} mb={3}>
          {/* קודי ISIN */}
          <Grid item xs={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Typography variant="subtitle1" gutterBottom>
                קודי ISIN ({pageData.financial_data?.isins?.length || 0})
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {pageData.financial_data?.isins?.length > 0 ? (
                  pageData.financial_data.isins.map((isin, index) => (
                    <Chip key={index} label={isin} size="small" />
                  ))
                ) : (
                  <Typography color="text.secondary">לא נמצאו קודי ISIN</Typography>
                )}
              </Box>
            </Paper>
          </Grid>
          
          {/* תאריכים */}
          <Grid item xs={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Typography variant="subtitle1" gutterBottom>
                תאריכים ({pageData.financial_data?.dates?.length || 0})
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {pageData.financial_data?.dates?.length > 0 ? (
                  pageData.financial_data.dates.slice(0, 10).map((date, index) => (
                    <Chip key={index} label={date} size="small" />
                  ))
                ) : (
                  <Typography color="text.secondary">לא נמצאו תאריכים</Typography>
                )}
                {(pageData.financial_data?.dates?.length || 0) > 10 && (
                  <Typography variant="caption">
                    ...ועוד {pageData.financial_data.dates.length - 10}
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>
          
          {/* סכומים */}
          <Grid item xs={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Typography variant="subtitle1" gutterBottom>
                סכומים ({pageData.financial_data?.amounts?.length || 0})
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {pageData.financial_data?.amounts?.length > 0 ? (
                  pageData.financial_data.amounts.slice(0, 10).map((amount, index) => (
                    <Chip key={index} label={amount} size="small" />
                  ))
                ) : (
                  <Typography color="text.secondary">לא נמצאו סכומים</Typography>
                )}
                {(pageData.financial_data?.amounts?.length || 0) > 10 && (
                  <Typography variant="caption">
                    ...ועוד {pageData.financial_data.amounts.length - 10}
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
        
        {/* טבלאות */}
        <Typography variant="h6" gutterBottom>
          טבלאות שזוהו ({pageData.tables_count || 0})
        </Typography>
        
        <Box mb={3}>
          {pageData.tables?.length > 0 ? (
            <Box>
              {/* בחירת טבלה אם יש יותר מאחת */}
              {pageData.tables.length > 1 && (
                <Box display="flex" gap={1} mb={2}>
                  {pageData.tables.map((table, index) => (
                    <Button
                      key={index}
                      variant={selectedTable === table ? "contained" : "outlined"}
                      size="small"
                      onClick={() => setSelectedTable(table)}
                    >
                      טבלה {index + 1}
                    </Button>
                  ))}
                </Box>
              )}
              
              {/* הצגת הטבלה הנבחרת */}
              {selectedTable && (
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="subtitle1">
                      רמת ביטחון: {(selectedTable.confidence * 100).toFixed(0)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      סוג: {selectedTable.structure_type || "בסיסי"}
                    </Typography>
                  </Box>
                  
                  {selectedTable.headers && selectedTable.rows && (
                    <Box mt={2}>
                      <Typography variant="subtitle2" mb={1}>תוכן הטבלה:</Typography>
                      <Box sx={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                          <thead>
                            <tr>
                              {selectedTable.headers.map((header, i) => (
                                <th key={i} style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5' }}>
                                  {header}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {selectedTable.rows.map((row, rowIndex) => (
                              <tr key={rowIndex}>
                                {row.map((cell, cellIndex) => (
                                  <td key={cellIndex} style={{ border: '1px solid #ddd', padding: '8px' }}>
                                    {cell}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </Box>
                    </Box>
                  )}
                  
                  {!selectedTable.headers && (
                    <Typography color="text.secondary">
                      זוהתה טבלה אך לא ניתן לחלץ את המבנה המדויק שלה
                    </Typography>
                  )}
                </Paper>
              )}
            </Box>
          ) : (
            <Typography color="text.secondary">לא זוהו טבלאות בעמוד זה</Typography>
          )}
        </Box>
        
        {/* שורות טבלה אפשריות */}
        <Typography variant="h6" gutterBottom>
          שורות טבלה אפשריות ({pageData.financial_data?.possible_table_rows?.length || 0})
        </Typography>
        
        <Paper variant="outlined" sx={{ p: 2, mb: 3, maxHeight: 200, overflow: 'auto' }}>
          {pageData.financial_data?.possible_table_rows?.length > 0 ? (
            <Box component="ul" sx={{ pl: 2, my: 0 }}>
              {pageData.financial_data.possible_table_rows.map((row, index) => (
                <Box component="li" key={index} mb={0.5}>
                  {row}
                </Box>
              ))}
            </Box>
          ) : (
            <Typography color="text.secondary">לא זוהו שורות טבלה אפשריות</Typography>
          )}
        </Paper>
      </Box>
    );
  };
  
  // תצוגת טקסט המסמך
  const renderTextContent = () => {
    if (!analysisResults) return null;
    
    const pageKey = String(pageNumber);
    const pageData = analysisResults.pages[pageKey];
    
    if (!pageData) {
      return (
        <Typography color="text.secondary" align="center" py={3}>
          אין טקסט מחולץ עבור עמוד זה
        </Typography>
      );
    }
    
    return (
      <Paper variant="outlined" sx={{ p: 2, maxHeight: 500, overflow: 'auto' }}>
        <pre style={{ 
          fontFamily: 'inherit', 
          whiteSpace: 'pre-wrap',
          direction: 'rtl', 
          textAlign: 'right',
          margin: 0
        }}>
          {pageData.text}
        </pre>
      </Paper>
    );
  };
  
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box>
      {/* פקדי ניווט ושליטה */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container alignItems="center" spacing={2}>
          <Grid item xs={12} md={6}>
            <Box display="flex" alignItems="center">
              <Button 
                onClick={goToPrevPage} 
                disabled={pageNumber <= 1}
                startIcon={<NavigateBeforeIcon />}
                size="small"
                sx={{ ml: 1 }}
              >
                הקודם
              </Button>
              
              <Typography variant="body2" mx={2} sx={{ minWidth: 80, textAlign: 'center' }}>
                עמוד {pageNumber} מתוך {numPages || '?'}
              </Typography>
              
              <Button 
                onClick={goToNextPage} 
                disabled={pageNumber >= numPages}
                endIcon={<NavigateNextIcon />}
                size="small"
                sx={{ mr: 1 }}
              >
                הבא
              </Button>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box display="flex" alignItems="center" justifyContent="flex-end">
              <Button onClick={zoomOut} startIcon={<ZoomOutIcon />} size="small">
                הקטן
              </Button>
              
              <Typography variant="body2" mx={1}>
                {Math.round(scale * 100)}%
              </Typography>
              
              <Button onClick={zoomIn} endIcon={<ZoomInIcon />} size="small">
                הגדל
              </Button>
              
              <Divider orientation="vertical" flexItem sx={{ mx: 2 }} />
              
              <Button 
                color="primary" 
                variant="contained" 
                startIcon={<AnalyticsIcon />}
                onClick={analyzePage}
                disabled={isAnalyzing}
                size="small"
              >
                {isAnalyzing ? 'מנתח...' : 'נתח עמוד'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      <Grid container spacing={3}>
        {/* תצוגת המסמך */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
            {pdfBlob ? (
              <Document
                file={pdfBlob}
                onLoadSuccess={onDocumentLoadSuccess}
                loading={<CircularProgress />}
                error={
                  <Typography color="error">
                    שגיאה בטעינת המסמך. ייתכן שהפורמט אינו נתמך.
                  </Typography>
                }
              >
                <Page 
                  pageNumber={pageNumber}
                  scale={scale}
                  renderTextLayer={true}
                  renderAnnotationLayer={true}
                  loading={<CircularProgress />}
                />
              </Document>
            ) : (
              <Typography color="text.secondary">
                לא נבחר קובץ PDF
              </Typography>
            )}
          </Paper>
        </Grid>
        
        {/* תוצאות ניתוח */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            {analysisResults ? (
              <Box>
                <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
                  <Tab icon={<InfoIcon />} label="מידע" />
                  <Tab icon={<AnalyticsIcon />} label="ניתוח" />
                  <Tab icon={<TableChartIcon />} label="טקסט" />
                </Tabs>
                
                <Box role="tabpanel" hidden={activeTab !== 0}>
                  {activeTab === 0 && (
                    <Box sx={{ p: 1 }}>
                      <Typography variant="h6" gutterBottom>פרטי מסמך</Typography>
                      
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        מטא-דאטה
                      </Typography>
                      
                      <Box component="dl" sx={{ 
                        display: 'grid', 
                        gridTemplateColumns: '1fr 2fr',
                        gap: '8px 16px'
                      }}>
                        {analysisResults.metadata && Object.entries(analysisResults.metadata)
                          .filter(([_, value]) => value)
                          .map(([key, value]) => (
                            <React.Fragment key={key}>
                              <Box component="dt" sx={{ fontWeight: 'bold' }}>{key}:</Box>
                              <Box component="dd" sx={{ margin: 0 }}>{value}</Box>
                            </React.Fragment>
                          ))
                        }
                      </Box>
                      
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ mt: 2 }}>
                        סיכום ניתוח
                      </Typography>
                      
                      <Box component="dl" sx={{ 
                        display: 'grid', 
                        gridTemplateColumns: '1fr 2fr',
                        gap: '8px 16px'
                      }}>
                        <Box component="dt" sx={{ fontWeight: 'bold' }}>סה"כ עמודים:</Box>
                        <Box component="dd" sx={{ margin: 0 }}>{analysisResults.total_pages_analyzed}</Box>
                        
                        <Box component="dt" sx={{ fontWeight: 'bold' }}>מספר עמוד נוכחי:</Box>
                        <Box component="dd" sx={{ margin: 0 }}>{pageNumber}</Box>
                        
                        <Box component="dt" sx={{ fontWeight: 'bold' }}>שם קובץ:</Box>
                        <Box component="dd" sx={{ margin: 0 }}>{analysisResults.filename}</Box>
                      </Box>
                    </Box>
                  )}
                </Box>
                
                <Box role="tabpanel" hidden={activeTab !== 1}>
                  {activeTab === 1 && renderAnalysisContent()}
                </Box>
                
                <Box role="tabpanel" hidden={activeTab !== 2}>
                  {activeTab === 2 && renderTextContent()}
                </Box>
              </Box>
            ) : (
              <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" p={4}>
                <AnalyticsIcon color="action" sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  טרם נותח העמוד
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center">
                  לחץ על "נתח עמוד" כדי להפעיל את הניתוח האוטומטי על העמוד הנוכחי
                </Typography>
                <Button 
                  variant="contained" 
                  color="primary"
                  startIcon={<AnalyticsIcon />}
                  onClick={analyzePage}
                  disabled={isAnalyzing}
                  sx={{ mt: 2 }}
                >
                  {isAnalyzing ? 'מנתח...' : 'נתח עמוד'}
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PdfViewer; 