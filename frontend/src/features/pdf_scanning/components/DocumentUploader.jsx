import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Divider,
  Grid,
  LinearProgress
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

/**
 * DocumentUploader component for uploading financial documents
 * 
 * Features:
 * - File selection via button or drag-and-drop
 * - Language selection for document processing
 * - Upload progress indicator
 * - Success/error feedback
 * - Upload history display
 */
function DocumentUploader({ onUploadSuccess, language = 'he' }) {
  // File selection state
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileLanguage, setFileLanguage] = useState(language);
  const fileInputRef = useRef(null);
  
  // Upload state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  
  // Upload history
  const [recentUploads, setRecentUploads] = useState([]);
  
  // Drag and drop state
  const [isDragging, setIsDragging] = useState(false);
  
  /**
   * Handles file selection from the file input
   */
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setUploadError(null);
      setUploadResult(null);
    }
  };
  
  /**
   * Triggers the hidden file input
   */
  const handleBrowseClick = () => {
    fileInputRef.current.click();
  };
  
  /**
   * Handles drag events for the dropzone
   */
  const handleDragEvents = (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    // Update dragging state based on event type
    if (event.type === 'dragenter' || event.type === 'dragover') {
      setIsDragging(true);
    } else if (event.type === 'dragleave' || event.type === 'drop') {
      setIsDragging(false);
    }
    
    // Handle file drop
    if (event.type === 'drop') {
      const file = event.dataTransfer.files[0];
      if (file) {
        setSelectedFile(file);
        setUploadError(null);
        setUploadResult(null);
      }
    }
  };
  
  /**
   * Resets the uploader state
   */
  const resetUploader = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    setUploadError(null);
    setUploadResult(null);
    // Keep the language setting and recent uploads
  };
  
  /**
   * Handles the file upload process
   */
  const handleUpload = async () => {
    if (!selectedFile) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    setUploadError(null);
    setUploadResult(null);
    
    // Create FormData for the upload
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('language', fileLanguage);
    
    try {
      // Create custom XMLHttpRequest to track progress
      const xhr = new XMLHttpRequest();
      
      // Set up progress tracking
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(progress);
        }
      });
      
      // Create a promise for the XHR request
      const uploadPromise = new Promise((resolve, reject) => {
        xhr.open('POST', '/api/upload', true);
        
        xhr.onload = function() {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const response = JSON.parse(xhr.responseText);
              resolve(response);
            } catch (error) {
              reject(new Error('Invalid response format'));
            }
          } else {
            try {
              const errorData = JSON.parse(xhr.responseText);
              reject(new Error(errorData.error || 'Upload failed'));
            } catch (error) {
              reject(new Error(`Upload failed with status ${xhr.status}`));
            }
          }
        };
        
        xhr.onerror = function() {
          reject(new Error('Network error during upload'));
        };
        
        xhr.send(formData);
      });
      
      // Wait for the upload to complete
      const response = await uploadPromise;
      
      if (!response.success) {
        throw new Error(response.error || 'Upload failed');
      }
      
      // Processing animation (simulate processing time)
      setUploadProgress(100);
      
      // Success state
      setUploadResult({
        success: true,
        documentId: response.document_id,
        processingResults: response.processing_results || {}
      });
      
      // Add to recent uploads
      const newUpload = {
        id: response.document_id,
        filename: selectedFile.name,
        uploadTime: new Date().toISOString(),
        language: fileLanguage,
        size: selectedFile.size,
        success: true
      };
      
      setRecentUploads(prevUploads => [newUpload, ...prevUploads].slice(0, 5));
      
      // Callback for parent component
      if (typeof onUploadSuccess === 'function') {
        onUploadSuccess(response.document_id, response);
      }
    } catch (error) {
      console.error('Error uploading document:', error);
      setUploadError(error.message || 'An error occurred during upload');
      
      // Add failed upload to history
      const failedUpload = {
        id: `failed-${Date.now()}`,
        filename: selectedFile.name,
        uploadTime: new Date().toISOString(),
        language: fileLanguage,
        size: selectedFile.size,
        success: false,
        error: error.message
      };
      
      setRecentUploads(prevUploads => [failedUpload, ...prevUploads].slice(0, 5));
    } finally {
      setIsUploading(false);
    }
  };
  
  /**
   * Formats file size for display
   */
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    return `${parseFloat((bytes / Math.pow(1024, i)).toFixed(2))} ${sizes[i]}`;
  };
  
  /**
   * Renders the file selection area
   */
  const renderFileSelection = () => (
    <Box 
      sx={{ 
        border: '2px dashed',
        borderColor: isDragging ? 'primary.main' : 'divider',
        borderRadius: 2,
        p: 3,
        textAlign: 'center',
        backgroundColor: isDragging ? 'action.hover' : 'background.paper',
        transition: 'all 0.3s ease'
      }}
      onDragEnter={handleDragEvents}
      onDragOver={handleDragEvents}
      onDragLeave={handleDragEvents}
      onDrop={handleDragEvents}
    >
      <input
        type="file"
        accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.txt"
        style={{ display: 'none' }}
        ref={fileInputRef}
        onChange={handleFileSelect}
      />
      
      <UploadFileIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
      
      <Typography variant="h6" gutterBottom>
        {language === 'he' 
          ? 'גרור ושחרר קובץ כאן או'
          : 'Drag & drop a file here or'}
      </Typography>
      
      <Button 
        variant="contained" 
        onClick={handleBrowseClick}
        sx={{ mt: 1 }}
      >
        {language === 'he' ? 'בחר קובץ' : 'Browse Files'}
      </Button>
      
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        {language === 'he'
          ? 'סוגי קבצים נתמכים: PDF, Word, Excel, CSV, Text'
          : 'Supported file types: PDF, Word, Excel, CSV, Text'}
      </Typography>
    </Box>
  );
  
  /**
   * Renders the selected file info
   */
  const renderSelectedFileInfo = () => {
    if (!selectedFile) return null;
    
    return (
      <Card variant="outlined" sx={{ mt: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <DescriptionIcon color="primary" sx={{ fontSize: 40 }} />
            </Grid>
            
            <Grid item xs>
              <Typography variant="subtitle1" component="div" noWrap>
                {selectedFile.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatFileSize(selectedFile.size)}
              </Typography>
            </Grid>
            
            <Grid item>
              <Button 
                color="error" 
                size="small" 
                onClick={resetUploader}
                disabled={isUploading}
              >
                {language === 'he' ? 'הסר' : 'Remove'}
              </Button>
            </Grid>
          </Grid>
          
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth size="small">
              <InputLabel>
                {language === 'he' ? 'שפת המסמך' : 'Document Language'}
              </InputLabel>
              <Select
                value={fileLanguage}
                label={language === 'he' ? 'שפת המסמך' : 'Document Language'}
                onChange={(e) => setFileLanguage(e.target.value)}
                disabled={isUploading}
              >
                <MenuItem value="he">עברית (Hebrew)</MenuItem>
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="auto">
                  {language === 'he' ? 'זיהוי אוטומטי' : 'Auto Detect'}
                </MenuItem>
              </Select>
            </FormControl>
          </Box>
          
          <Box sx={{ mt: 2 }}>
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleUpload}
              disabled={isUploading}
              startIcon={isUploading ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {isUploading
                ? (language === 'he' ? 'מעלה...' : 'Uploading...')
                : (language === 'he' ? 'העלה מסמך' : 'Upload Document')}
            </Button>
          </Box>
          
          {isUploading && (
            <Box sx={{ width: '100%', mt: 2 }}>
              <LinearProgress variant="determinate" value={uploadProgress} />
              <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                {uploadProgress}%
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };
  
  /**
   * Renders the upload result
   */
  const renderUploadResult = () => {
    if (uploadError) {
      return (
        <Alert severity="error" sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            {language === 'he' ? 'שגיאה בהעלאת המסמך' : 'Error Uploading Document'}
          </Typography>
          <Typography variant="body2">
            {uploadError}
          </Typography>
        </Alert>
      );
    }
    
    if (uploadResult && uploadResult.success) {
      return (
        <Alert severity="success" sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            {language === 'he' ? 'המסמך הועלה בהצלחה' : 'Document Uploaded Successfully'}
          </Typography>
          <Typography variant="body2">
            {language === 'he'
              ? `מזהה מסמך: ${uploadResult.documentId}`
              : `Document ID: ${uploadResult.documentId}`}
          </Typography>
          
          <Box sx={{ mt: 2 }}>
            <Button 
              variant="outlined" 
              size="small"
              onClick={resetUploader}
            >
              {language === 'he' ? 'העלה מסמך נוסף' : 'Upload Another Document'}
            </Button>
          </Box>
        </Alert>
      );
    }
    
    return null;
  };
  
  /**
   * Renders the recent uploads section
   */
  const renderRecentUploads = () => {
    if (recentUploads.length === 0) return null;
    
    return (
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          {language === 'he' ? 'העלאות אחרונות' : 'Recent Uploads'}
        </Typography>
        
        <Paper variant="outlined">
          {recentUploads.map((upload, index) => (
            <React.Fragment key={upload.id}>
              {index > 0 && <Divider />}
              <Box sx={{ p: 2 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item>
                    {upload.success ? (
                      <CheckCircleIcon color="success" />
                    ) : (
                      <ErrorIcon color="error" />
                    )}
                  </Grid>
                  
                  <Grid item xs>
                    <Typography variant="subtitle2" component="div" noWrap>
                      {upload.filename}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {formatFileSize(upload.size)} • {new Date(upload.uploadTime).toLocaleString()}
                    </Typography>
                    
                    {!upload.success && upload.error && (
                      <Typography variant="body2" color="error" sx={{ mt: 0.5 }}>
                        {upload.error}
                      </Typography>
                    )}
                  </Grid>
                  
                  {upload.success && (
                    <Grid item>
                      <Button 
                        variant="outlined" 
                        size="small"
                        onClick={() => {
                          if (typeof onUploadSuccess === 'function') {
                            onUploadSuccess(upload.id, { document_id: upload.id });
                          }
                        }}
                      >
                        {language === 'he' ? 'בחר' : 'Select'}
                      </Button>
                    </Grid>
                  )}
                </Grid>
              </Box>
            </React.Fragment>
          ))}
        </Paper>
      </Box>
    );
  };
  
  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom>
        {language === 'he' ? 'העלאת מסמך פיננסי' : 'Upload Financial Document'}
      </Typography>
      
      <Typography variant="body1" paragraph>
        {language === 'he'
          ? 'העלה מסמכים פיננסיים לניתוח ועיבוד אוטומטי. המערכת תחלץ נתונים, טבלאות ומידע רלוונטי.'
          : 'Upload financial documents for automatic analysis and processing. The system will extract data, tables, and relevant information.'}
      </Typography>
      
      {renderFileSelection()}
      {renderSelectedFileInfo()}
      {renderUploadResult()}
      {renderRecentUploads()}
    </Box>
  );
}

export default DocumentUploader;
