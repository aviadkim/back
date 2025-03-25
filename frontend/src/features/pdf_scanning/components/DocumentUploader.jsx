import React, { useState } from 'react';
import { Box, Button, CircularProgress, Paper, Typography, LinearProgress, Alert } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import ExtractedDataView from './ExtractedDataView';

/**
 * DocumentUploader component handles the file upload process for financial PDFs
 * 
 * This component provides a complete upload workflow:
 * 1. File selection/drag & drop
 * 2. Upload with progress indicator
 * 3. Processing status
 * 4. Success confirmation with extracted data preview
 */
function DocumentUploader() {
  // Track the current upload state
  const [uploadStep, setUploadStep] = useState('upload'); // upload, uploading, processing, complete, error
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documentId, setDocumentId] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  /**
   * Handles when a file is selected either via input or drag & drop
   */
  const handleFileSelect = (file) => {
    // Reset any previous state
    setUploadStep('upload');
    setUploadProgress(0);
    setError(null);
    
    // Validate the file is a PDF
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    } else {
      setError('Please select a valid PDF file');
    }
  };

  /**
   * Handles the file upload process
   */
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setUploadStep('uploading');
    setError(null);
    
    // Create form data for the file upload
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('language', 'he'); // Default to Hebrew, can be made configurable
    
    try {
      // Upload the file to the PDF scanning endpoint
      const uploadResponse = await fetch('/api/pdf/upload', {
        method: 'POST',
        body: formData,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.lengthComputable) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(progress);
          }
        },
      });
      
      // Check if upload was successful
      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(errorData.error || 'Error uploading file');
      }
      
      // Upload completed, now processing on server
      setUploadStep('processing');
      
      // Get the response with document ID
      const uploadResult = await uploadResponse.json();
      setDocumentId(uploadResult.document_id);
      
      // Wait a moment for processing to complete
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Fetch the extracted data for the uploaded document
      const documentResponse = await fetch(`/api/pdf/${uploadResult.document_id}`);
      
      if (!documentResponse.ok) {
        const errorData = await documentResponse.json();
        throw new Error(errorData.error || 'Error retrieving document data');
      }
      
      const documentData = await documentResponse.json();
      setExtractedData(documentData.document);
      setUploadStep('complete');
      
      // Return the document ID for parent components
      return uploadResult.document_id;
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || 'An error occurred during upload');
      setUploadStep('error');
      return null;
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: '800px', mx: 'auto', mb: 4 }}>
      {/* Upload Step */}
      {uploadStep === 'upload' && (
        <Box textAlign="center" p={3}>
          <Typography variant="h5" component="h2" gutterBottom>
            Upload Financial Document
          </Typography>
          
          <Box 
            sx={{ 
              border: '2px dashed #ccc', 
              borderRadius: 2, 
              p: 3, 
              my: 2,
              bgcolor: 'rgba(0, 0, 0, 0.02)',
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'rgba(0, 0, 0, 0.05)',
              }
            }}
            onClick={() => document.getElementById('file-input').click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              const file = e.dataTransfer.files[0];
              handleFileSelect(file);
            }}
          >
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={(e) => handleFileSelect(e.target.files[0])}
            />
            <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="body1">
              {selectedFile ? `Selected: ${selectedFile.name}` : 'Drag and drop a PDF file here, or click to browse'}
            </Typography>
          </Box>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Button 
            variant="contained" 
            color="primary" 
            size="large"
            onClick={handleUpload}
            disabled={!selectedFile}
          >
            Upload and Process Document
          </Button>
        </Box>
      )}
      
      {/* Uploading Step */}
      {uploadStep === 'uploading' && (
        <Box textAlign="center" p={3}>
          <Typography variant="h5" component="h2" gutterBottom>
            Uploading Document
          </Typography>
          
          <Box sx={{ my: 3 }}>
            <LinearProgress 
              variant="determinate" 
              value={uploadProgress} 
              sx={{ height: 10, borderRadius: 5 }}
            />
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
              {uploadProgress}% Complete
            </Typography>
          </Box>
          
          <Typography variant="body1">
            Uploading {selectedFile?.name}...
          </Typography>
        </Box>
      )}
      
      {/* Processing Step */}
      {uploadStep === 'processing' && (
        <Box textAlign="center" p={3}>
          <Typography variant="h5" component="h2" gutterBottom>
            Processing Document
          </Typography>
          
          <CircularProgress sx={{ my: 3 }} />
          
          <Typography variant="body1">
            Extracting text, tables, and financial data...
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This may take a few moments depending on document size and complexity.
          </Typography>
        </Box>
      )}
      
      {/* Complete Step */}
      {uploadStep === 'complete' && extractedData && (
        <Box p={3}>
          <Box display="flex" alignItems="center" mb={3}>
            <CheckCircleIcon color="success" sx={{ fontSize: 30, mr: 1 }} />
            <Typography variant="h5" component="h2">
              Document Processed Successfully
            </Typography>
          </Box>
          
          <ExtractedDataView data={extractedData} />
          
          <Box mt={2} display="flex" justifyContent="center" gap={2}>
            <Button 
              variant="outlined" 
              onClick={() => {
                setUploadStep('upload');
                setSelectedFile(null);
              }}
            >
              Upload Another Document
            </Button>
            
            <Button 
              variant="contained" 
              color="primary"
              onClick={() => {
                // Navigate to document detail view, can be handled by parent component
                window.location.href = `/documents/${documentId}`;
              }}
            >
              View Full Document Details
            </Button>
          </Box>
        </Box>
      )}
      
      {/* Error Step */}
      {uploadStep === 'error' && (
        <Box textAlign="center" p={3}>
          <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
            <ErrorIcon color="error" sx={{ fontSize: 30, mr: 1 }} />
            <Typography variant="h5" component="h2">
              Upload Failed
            </Typography>
          </Box>
          
          <Alert severity="error" sx={{ mb: 3 }}>
            {error || 'An error occurred while processing your document.'}
          </Alert>
          
          <Button 
            variant="contained" 
            onClick={() => {
              setUploadStep('upload');
              setError(null);
            }}
          >
            Try Again
          </Button>
        </Box>
      )}
    </Paper>
  );
}

export default DocumentUploader;
