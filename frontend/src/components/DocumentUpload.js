import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { documentApi } from '../api/api'; // Use the standardized API client
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  CircularProgress,
  Typography,
  Paper,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Alert,
  LinearProgress,
  Card,
  CardContent,
  Grid, // Import Grid for layout
  Fade, // Import Fade for transitions
  useTheme // Import useTheme hook
} from '@mui/material';
import {
  UploadFile as UploadFileIcon, // Renamed for clarity
  Description as DescriptionIcon,
  CloudUpload as CloudUploadIcon, // Use a more descriptive icon
  CheckCircleOutline as CheckCircleIcon, // Success icon
  ErrorOutline as ErrorIcon, // Error icon
  Replay as ResetIcon // Reset icon
} from '@mui/icons-material';

const DocumentUpload = ({ onSuccess }) => {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState('auto'); // Default to auto-detect
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [documentId, setDocumentId] = useState(null);
  const navigate = useNavigate();
  const theme = useTheme(); // Get the theme object

  // Define supported languages for the radio group
  const supportedLanguages = [
    { code: 'auto', label: 'Auto-detect' },
    { code: 'he', label: 'Hebrew (עברית)' },
    { code: 'en', label: 'English' }
  ];

  // Handle file drop with useCallback for performance
  const onDrop = useCallback(acceptedFiles => {
    // Reset states on new file drop
    setError(null);
    setSuccess(null);
    setDocumentId(null);
    setProgress(0);

    const newFile = acceptedFiles[0];
    if (!newFile) return;

    // Basic file type validation (can be enhanced)
    const fileExt = newFile.name.split('.').pop()?.toLowerCase();
    const supportedTypes = ['pdf', 'xlsx', 'xls', 'csv']; // Add more if needed

    if (!fileExt || !supportedTypes.includes(fileExt)) {
      setError(`Unsupported file type: .${fileExt}. Please upload: ${supportedTypes.join(', ')}`);
      setFile(null); // Clear invalid file
      return;
    }

    // Basic file size validation (using config value if available, else default)
    // Note: MAX_FILE_SIZE needs to be accessible here, e.g., via context or props if dynamic
    const maxSizeMB = 50; // Default max size
    if (newFile.size > maxSizeMB * 1024 * 1024) {
      setError(`File too large. Maximum size is ${maxSizeMB}MB.`);
      setFile(null); // Clear invalid file
      return;
    }

    setFile(newFile); // Set the valid file
  }, []); // Empty dependency array means this callback is created once

  // Configure react-dropzone
  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: { // More specific MIME types
      'application/pdf': ['.pdf'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    multiple: false, // Ensure only one file is accepted
  });

  // Handle language selection change
  const handleLanguageChange = (event) => {
    setLanguage(event.target.value);
  };

  // Handle the upload process
  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setUploading(true);
    setProgress(0);
    setError(null);
    setSuccess(null);
    setDocumentId(null);

    try {
      // Call the API using the standardized client
      const result = await documentApi.uploadDocument(file, {
        language, // Pass selected language
        onProgress: (progressEvent) => {
          // Calculate and update progress percentage
          if (progressEvent.total) {
             const percentCompleted = Math.round(
               (progressEvent.loaded * 100) / progressEvent.total
             );
             setProgress(percentCompleted);
          } else {
             // Handle indeterminate progress if total size is unknown
             setProgress(50); // Example: show 50% if size unknown
          }
        }
      });

      // Check the standardized response structure
      if (result.status === 'success' && result.data?.document_id) {
        setSuccess(`Document processed successfully! Pages: ${result.data.page_count || 'N/A'}. Language: ${result.data.language || 'N/A'}.`);
        setDocumentId(result.data.document_id);

        // Call the onSuccess callback prop if provided
        if (onSuccess && typeof onSuccess === 'function') {
          onSuccess(result.data);
        }
      } else {
        // Handle backend processing errors reported in the success response
        setError(result.message || 'An error occurred during document processing.');
      }
    } catch (err) {
      // Handle network errors or errors thrown by the API client interceptor
      console.error("Upload failed:", err);
      setError(err.message || 'Failed to upload document. Please check the network or server status.');
    } finally {
      setUploading(false); // Ensure loading state is turned off
    }
  };

  // Navigate to the document view page
  const handleViewDocument = () => {
    if (documentId) {
      navigate(`/document/${documentId}`); // Use react-router navigation
    }
  };

  // Reset the component state
  const handleReset = () => {
    setFile(null);
    setError(null);
    setSuccess(null);
    setProgress(0);
    setDocumentId(null);
    setLanguage('auto'); // Reset language too
  };

  return (
    <Card elevation={2} sx={{ maxWidth: 700, margin: 'auto' }}> {/* Centered card */}
      <CardContent sx={{ p: { xs: 2, sm: 3, md: 4 } }}> {/* Responsive padding */}
        <Typography variant="h5" component="h2" gutterBottom align="center">
          Upload Financial Document
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph align="center" sx={{ mb: 3 }}>
          Upload PDF, Excel, or CSV files for AI-powered analysis.
        </Typography>

        {/* Dropzone Area */}
        <Box
          {...getRootProps()}
          sx={{
            border: `2px dashed ${isDragReject ? theme.palette.error.main : isDragActive ? theme.palette.primary.main : theme.palette.grey[400]}`,
            borderRadius: 2,
            p: 4,
            mb: 3,
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
            transition: 'border-color 0.2s ease-in-out, background-color 0.2s ease-in-out',
            '&:hover': {
              borderColor: 'primary.main',
            }
          }}
        >
          <input {...getInputProps()} />
          <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
          {file ? (
            <>
              <Typography variant="h6" color="text.primary">{file.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </Typography>
              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                Click or drag another file to replace
              </Typography>
            </>
          ) : (
            <>
              <Typography variant="h6">Drag & drop document here</Typography>
              <Typography variant="body2" color="text.secondary">
                or click to select file
              </Typography>
            </>
          )}
        </Box>

        {/* Language Selection */}
        <FormControl component="fieldset" sx={{ mb: 3, width: '100%' }}>
          <FormLabel component="legend" sx={{ mb: 1 }}>Document Language (Optional)</FormLabel>
          <RadioGroup row name="language" value={language} onChange={handleLanguageChange}>
            {supportedLanguages.map(lang => (
              <FormControlLabel
                key={lang.code}
                value={lang.code}
                control={<Radio size="small" />}
                label={lang.label}
              />
            ))}
          </RadioGroup>
        </FormControl>

        {/* Progress Bar */}
        <Fade in={uploading}>
            <Box sx={{ mb: 3 }}>
                <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }}/>
                <Typography variant="caption" display="block" align="center" sx={{ mt: 1 }}>
                    Processing: {progress}%
                </Typography>
            </Box>
        </Fade>

        {/* Error Alert */}
        <Fade in={!!error}>
            <Alert severity="error" icon={<ErrorIcon />} sx={{ mb: 3 }}>
                {error}
            </Alert>
        </Fade>

        {/* Success Alert */}
        <Fade in={!!success}>
            <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 3 }}>
                {success}
            </Alert>
        </Fade>

        {/* Action Buttons */}
        <Grid container spacing={2} justifyContent="space-between">
          <Grid item>
            <Button
              variant="outlined"
              onClick={handleReset}
              disabled={uploading || (!file && !error && !success)}
              startIcon={<ResetIcon />}
            >
              Reset
            </Button>
          </Grid>
          <Grid item>
            {documentId ? (
              <Button
                variant="contained"
                color="secondary" // Use secondary color for view action
                onClick={handleViewDocument}
                startIcon={<DescriptionIcon />}
              >
                View Document
              </Button>
            ) : (
              <Button
                variant="contained"
                color="primary"
                onClick={handleUpload}
                disabled={!file || uploading}
                startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <UploadFileIcon />}
              >
                {uploading ? 'Processing...' : 'Upload & Process'}
              </Button>
            )}
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default DocumentUpload;