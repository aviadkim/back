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
   * Triggers file input click
   */
  const handleBrowseClick = () => {
    fileInputRef.current.click();
  };
  
  /**
   * Handles file selection via input
   */
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setUploadError(null);
      setUploadResult(null);
    }
  };
  
  /**
   * Handles file drop
   */
  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];
      setSelectedFile(file);
      setUploadError(null);
      setUploadResult(null);
    }
  };
  
  /**
   * Handles drag over event
   */
  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };
  
  /**
   * Handles drag leave event
   */
  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragging(false);
  };
  
  /**
   * Uploads the selected file
   */
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError(language === 'he' ? 'אנא בחר קובץ' : 'Please select a file');
      return;
    }
    
    setIsUploading(true);
    setUploadProgress(0);
    setUploadError(null);
    setUploadResult(null);
    
    // Create a FormData object to send the file
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('language', fileLanguage);
    
    try {
      // Simulated upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return 95;
          }
          return prev + 5;
        });
      }, 300);
      
      // Upload the file
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Processing failed');
      }
      
      // Handle successful upload
      setUploadResult({
        success: true,
        documentId: result.document_id,
        message: result.message || (language === 'he' ? 'המסמך הועלה ועובד בהצלחה' : 'Document uploaded and processed successfully')
      });
      
      // Add to recent uploads
      const upload = {
        id: result.document_id,
        filename: selectedFile.name,
        timestamp: new Date().toISOString(),
        success: true
      };
      
      setRecentUploads((prev) => [upload, ...prev].slice(0, 5));
      
      // Reset selected file
      setSelectedFile(null);
      
      // Callback
      if (onUploadSuccess) {
        onUploadSuccess(result.document_id, result);
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(error.message || 'An error occurred during upload');
      
      // Add to recent uploads
      const upload = {
        id: null,
        filename: selectedFile.name,
        timestamp: new Date().toISOString(),
        success: false,
        error: error.message
      };
      
      setRecentUploads((prev) => [upload, ...prev].slice(0, 5));
    } finally {
      setIsUploading(false);
    }
  };
  
  /**
   * Resets the form
   */
  const handleReset = () => {
    setSelectedFile(null);
    setUploadError(null);
    setUploadResult(null);
    setUploadProgress(0);
  };
  
  // Format file size for display
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: '800px', mx: 'auto' }}>
      <Typography variant="h5" component="h2" gutterBottom>
        {language === 'he' ? 'העלאת מסמך פיננסי' : 'Upload Financial Document'}
      </Typography>
      
      {/* Drag and drop area */}
      <Box
        sx={{
          border: '2px dashed',
          borderColor: isDragging ? 'primary.main' : 'grey.400',
          borderRadius: 2,
          p: 3,
          mb: 3,
          backgroundColor: isDragging ? 'rgba(63, 81, 181, 0.08)' : 'transparent',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'rgba(63, 81, 181, 0.04)'
          }
        }}
        onClick={handleBrowseClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          type="file"
          accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        
        <UploadFileIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        
        <Typography variant="h6" gutterBottom>
          {language === 'he' ? 'גרור ושחרר קובץ כאן' : 'Drag & Drop File Here'}
        </Typography>
        
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {language === 'he' 
            ? 'או לחץ לבחירת קובץ'
            : 'Or click to browse files'}
        </Typography>
        
        <Typography variant="body2" color="text.secondary">
          {language === 'he'
            ? 'סוגי קבצים נתמכים: PDF, DOCX, XLSX, PNG, JPG'
            : 'Supported file types: PDF, DOCX, XLSX, PNG, JPG'}
        </Typography>
      </Box>
      
      {/* Selected file info */}
      {selectedFile && (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <DescriptionIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
              
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="subtitle1" component="div">
                  {selectedFile.name}
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  {formatFileSize(selectedFile.size)}
                </Typography>
              </Box>
              
              <Button
                variant="outlined"
                color="secondary"
                size="small"
                onClick={handleReset}
                disabled={isUploading}
              >
                {language === 'he' ? 'ביטול' : 'Cancel'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}
      
      {/* Upload options */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6}>
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
                {language === 'he' ? 'זיהוי אוטומטי' : 'Auto-detect'}
              </MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            startIcon={isUploading ? <CircularProgress size={20} color="inherit" /> : <UploadFileIcon />}
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
          >
            {language === 'he' ? 'העלה מסמך' : 'Upload Document'}
          </Button>
        </Grid>
      </Grid>
      
      {/* Upload progress */}
      {isUploading && (
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
              {language === 'he' ? 'מעלה את המסמך' : 'Uploading document'}
            </Typography>
            <Typography variant="body2" color="primary">
              {uploadProgress}%
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={uploadProgress} 
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>
      )}
      
      {/* Upload error */}
      {uploadError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {uploadError}
        </Alert>
      )}
      
      {/* Upload success */}
      {uploadResult && uploadResult.success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <CheckCircleIcon sx={{ mr: 1 }} />
            <Box>
              <Typography variant="body1">
                {uploadResult.message}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {language === 'he' ? 'מזהה מסמך: ' : 'Document ID: '} 
                {uploadResult.documentId}
              </Typography>
            </Box>
          </Box>
        </Alert>
      )}
      
      {/* Recent uploads */}
      {recentUploads.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Divider sx={{ mb: 2 }} />
          
          <Typography variant="h6" gutterBottom>
            {language === 'he' ? 'העלאות אחרונות' : 'Recent Uploads'}
          </Typography>
          
          {recentUploads.map((upload) => (
            <Card 
              key={upload.timestamp} 
              variant="outlined"
              sx={{ 
                mb: 1,
                borderLeft: 5,
                borderLeftColor: upload.success ? 'success.main' : 'error.main'
              }}
            >
              <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {upload.success ? (
                    <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                  ) : (
                    <ErrorIcon color="error" sx={{ mr: 1 }} />
                  )}
                  
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2">
                      {upload.filename}
                    </Typography>
                    
                    <Typography variant="caption" color="text.secondary">
                      {new Date(upload.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                  
                  {upload.success && (
                    <Button 
                      size="small"
                      onClick={() => onUploadSuccess && onUploadSuccess(upload.id)}
                    >
                      {language === 'he' ? 'הצג' : 'View'}
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Paper>
  );
}

export default DocumentUploader;
