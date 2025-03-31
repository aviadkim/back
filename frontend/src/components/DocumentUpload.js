import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { documentApi } from '../api/api';
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
  LinearProgress
} from '@mui/material';
import { Upload as UploadIcon, Description as DescriptionIcon } from '@mui/icons-material';

const DocumentUpload = ({ onSuccess, supportedLanguages = ['auto', 'he', 'en'] }) => {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState('auto');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Handle file drop
  const onDrop = useCallback(acceptedFiles => {
    // Reset states
    setError(null);
    setSuccess(null);

    // Validate file
    const newFile = acceptedFiles[0];
    if (!newFile) return;

    // Check file type
    const fileExt = newFile.name.split('.').pop().toLowerCase();
    const supportedTypes = ['pdf', 'xlsx', 'xls', 'csv'];

    if (!supportedTypes.includes(fileExt)) {
      setError(`Unsupported file type. Please upload: ${supportedTypes.join(', ')}`);
      return;
    }

    // Check file size (max 50MB)
    if (newFile.size > 50 * 1024 * 1024) {
      setError('File too large. Maximum size is 50MB.');
      return;
    }

    setFile(newFile);
  }, []);

  // Configure dropzone
  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  // Handle language change
  const handleLanguageChange = (event) => {
    setLanguage(event.target.value);
  };

  // Upload document
  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setUploading(true);
    setProgress(0);
    setError(null);
    setSuccess(null);

    try {
      const result = await documentApi.uploadDocument(file, {
        language,
        onProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
        }
      });

      setSuccess(`Document processed successfully! ${result.data.page_count} pages processed.`);

      // Call success callback if provided
      if (onSuccess && typeof onSuccess === 'function') {
        onSuccess(result.data);
      }
    } catch (err) {
      setError(err.message || 'Failed to upload document. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  // Reset form
  const handleReset = () => {
    setFile(null);
    setError(null);
    setSuccess(null);
    setProgress(0);
  };

  // Get language label
  const getLanguageLabel = (code) => {
    const labels = {
      'auto': 'Auto-detect',
      'he': 'Hebrew (עברית)',
      'en': 'English'
    };
    return labels[code] || code;
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h5" component="h2" gutterBottom>
        Upload Financial Document
      </Typography>

      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Success message */}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* File dropzone */}
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: isDragReject ? 'error.main' : isDragActive ? 'primary.main' : 'grey.400',
          borderRadius: 1,
          p: 3,
          mb: 2,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? 'rgba(25, 118, 210, 0.04)' : 'transparent',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'rgba(25, 118, 210, 0.04)'
          }
        }}
      >
        <input {...getInputProps()} />

        {file ? (
          <Box display="flex" alignItems="center" justifyContent="center" flexDirection="column">
            <DescriptionIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography>{file.name}</Typography>
            <Typography variant="body2" color="textSecondary">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </Typography>
          </Box>
        ) : (
          <Box display="flex" alignItems="center" justifyContent="center" flexDirection="column">
            <UploadIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
            <Typography>Drag and drop a file here, or click to select file</Typography>
            <Typography variant="body2" color="textSecondary">
              Supported formats: PDF, Excel, CSV
            </Typography>
          </Box>
        )}
      </Box>

      {/* Language selection */}
      <FormControl component="fieldset" sx={{ mb: 2 }}>
        <FormLabel component="legend">Document Language</FormLabel>
        <RadioGroup
          row
          name="language"
          value={language}
          onChange={handleLanguageChange}
        >
          {supportedLanguages.map(lang => (
            <FormControlLabel
              key={lang}
              value={lang}
              control={<Radio />}
              label={getLanguageLabel(lang)}
            />
          ))}
        </RadioGroup>
      </FormControl>

      {/* Upload progress */}
      {uploading && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Processing document: {progress}%
          </Typography>
          <LinearProgress variant="determinate" value={progress} />
        </Box>
      )}

      {/* Action buttons */}
      <Box display="flex" justifyContent="space-between">
        <Button
          variant="outlined"
          onClick={handleReset}
          disabled={uploading || (!file && !error && !success)}
        >
          Reset
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={!file || uploading}
          startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <UploadIcon />}
        >
          {uploading ? 'Processing...' : 'Upload & Process'}
        </Button>
      </Box>
    </Paper>
  );
};

export default DocumentUpload;