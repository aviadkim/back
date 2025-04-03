import React, { useState } from 'react';
import { Form, Button, ProgressBar, Alert, Card, Spinner } from 'react-bootstrap'; // Add Spinner import
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUpload, faFilePdf, faTrash, faCheck } from '@fortawesome/free-solid-svg-icons'; // Use faFilePdf
import axios from 'axios';
import './DocumentUploader.css';

const DocumentUploader = ({ onSuccess }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [language, setLanguage] = useState('auto'); // Default language

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    
    // Filter for PDF files only
    const pdfFiles = selectedFiles.filter(file => 
      file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
    );
    
    // Reset success message
    setUploadSuccess(false);

    if (pdfFiles.length !== selectedFiles.length) {
      setUploadError('Only PDF files are supported. Non-PDF files were excluded.');
    } else {
      setUploadError(null); // Clear error if only PDFs were selected
    }
    
    // Add only new, unique PDF files (prevent duplicates)
    setFiles(prevFiles => {
         const newFiles = pdfFiles.filter(newFile => !prevFiles.some(existingFile => existingFile.name === newFile.name && existingFile.size === newFile.size));
         return [...prevFiles, ...newFiles];
    });

    // Clear the input value to allow selecting the same file again after removal
    e.target.value = null; 
  };

  const handleRemoveFile = (indexToRemove) => {
    setFiles(prevFiles => prevFiles.filter((_, index) => index !== indexToRemove));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setUploadError('Please select at least one PDF file to upload.');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setUploadError(null);
    setUploadSuccess(false);

    const totalFiles = files.length;
    let filesUploadedSuccessfully = 0;
    let firstError = null;

    try {
      // Upload files one by one to track progress accurately
      for (let i = 0; i < totalFiles; i++) {
        const currentFile = files[i];
        const formData = new FormData();
        formData.append('file', currentFile);
        // Include language if needed by the backend endpoint
        // formData.append('language', language); 

        try {
             // Use the correct endpoint from vertical_slice_app.py
             await axios.post('/api/upload', formData, { 
               headers: {
                 'Content-Type': 'multipart/form-data'
               },
               onUploadProgress: (progressEvent) => {
                 // Calculate individual file progress
                 const individualProgress = progressEvent.total ? (progressEvent.loaded / progressEvent.total) * 100 : 0;
                 
                 // Calculate overall progress based on files completed and current file progress
                 const overallProgress = (((i + (progressEvent.loaded / progressEvent.total)) / totalFiles) * 100);
                 setUploadProgress(Math.round(overallProgress));
               }
             });
             filesUploadedSuccessfully++;
        } catch (fileError) {
             console.error(`Error uploading ${currentFile.name}:`, fileError);
             if (!firstError) { // Store the first error encountered
                  firstError = fileError.response?.data?.message || fileError.message || `Failed to upload ${currentFile.name}.`;
             }
             // Optionally break the loop on first error or continue uploading others
             // break; 
        }
      }

      if (filesUploadedSuccessfully === totalFiles) {
           // All files uploaded successfully
           setUploadSuccess(true);
           setFiles([]); // Clear file list on full success
           setUploadProgress(100);
           if (onSuccess) {
             onSuccess(); // Notify parent component
           }
      } else {
           // Handle partial success / errors
           setUploadError(firstError || `Uploaded ${filesUploadedSuccessfully}/${totalFiles} files successfully. Some uploads failed.`);
           // Optionally keep failed files in the list for retry? For now, clear list.
           // setFiles([]); 
      }

    } catch (error) {
      // Catch unexpected errors during the loop setup (less likely)
      console.error('General upload error:', error);
      setUploadError('An unexpected error occurred during upload.');
    } finally {
      setUploading(false);
      // Don't reset progress to 0 immediately, let user see 100% or error state
      // setUploadProgress(0); 
    }
  };

  const renderFileList = () => {
    if (files.length === 0) {
      return <p className="text-center text-muted mt-3">No files selected.</p>;
    }

    return (
      <Card className="mt-3 mb-3 file-list-card">
        <Card.Header className="py-2 small">Selected Files ({files.length})</Card.Header>
        <Card.Body className="p-2">
          <ul className="list-unstyled file-list mb-0">
            {files.map((file, index) => (
              <li key={index} className="file-item d-flex justify-content-between align-items-center p-2 border-bottom">
                <div className="file-info d-flex align-items-center overflow-hidden">
                  <FontAwesomeIcon icon={faFilePdf} className="file-icon me-2 text-danger" />
                  <span className="file-name text-truncate" title={file.name}>{file.name}</span>
                  <span className="file-size text-muted ms-2 small flex-shrink-0">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                </div>
                <Button 
                  variant="outline-danger" 
                  size="sm" 
                  className="ms-2 flex-shrink-0"
                  onClick={() => handleRemoveFile(index)}
                  disabled={uploading}
                  title="Remove file"
                >
                  <FontAwesomeIcon icon={faTrash} />
                </Button>
              </li>
            ))}
          </ul>
        </Card.Body>
      </Card>
    );
  };

  return (
    <div className="document-uploader">
      <div className="upload-area p-4 border rounded bg-light">
        <div className="text-center mb-4">
          <h4 className="mb-1">Upload Financial Documents</h4>
          <p className="text-muted small mb-0">Upload your PDF documents for analysis</p>
        </div>

        {/* Success/Error Alerts */}
        {uploadSuccess && (
          <Alert variant="success" onClose={() => setUploadSuccess(false)} dismissible className="d-flex align-items-center">
            <FontAwesomeIcon icon={faCheck} className="me-2" /> Documents uploaded successfully!
          </Alert>
        )}
        {uploadError && (
          <Alert variant="danger" onClose={() => setUploadError(null)} dismissible>
            {uploadError}
          </Alert>
        )}

        <Form>
          {/* Language Selection (Optional based on backend needs) */}
          {/* 
          <Form.Group className="mb-3">
            <Form.Label className="small mb-1">Document Language</Form.Label>
            <Form.Select 
              size="sm"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              disabled={uploading}
            >
              <option value="auto">Auto-detect</option>
              <option value="heb">Hebrew</option>
              <option value="eng">English</option>
              <option value="mixed">Mixed (Hebrew & English)</option>
            </Form.Select>
            <Form.Text className="text-muted small">
              Helps improve text recognition accuracy.
            </Form.Text>
          </Form.Group> 
          */}

          {/* Drop Zone */}
          <div 
             className="upload-drop-zone border-dashed p-4 text-center mb-3" 
             onClick={() => !uploading && document.getElementById('fileInput').click()} // Prevent click during upload
             role="button" 
             tabIndex="0"
             onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && !uploading && document.getElementById('fileInput').click()} // Accessibility
          >
            <input
              type="file"
              id="fileInput"
              multiple
              accept=".pdf,application/pdf" // More specific accept types
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              disabled={uploading}
            />
            <div className="upload-icon mb-2">
              <FontAwesomeIcon icon={faUpload} size="2x" className="text-secondary" />
            </div>
            <p className="mb-1">Drag & drop PDF files here or click to browse</p>
            <p className="small text-muted mb-0">(Only PDF files are supported)</p>
          </div>

          {/* File List */}
          {renderFileList()}

          {/* Progress Bar */}
          {uploading && (
            <div className="mt-3 mb-3">
              <ProgressBar 
                now={uploadProgress} 
                label={`${uploadProgress}%`} 
                animated={uploadProgress < 100} 
                variant="info" // Use a different variant for progress
              />
              <p className="text-center small mt-1 text-muted">Uploading {files.length} file(s)...</p>
            </div>
          )}

          {/* Upload Button */}
          <div className="d-grid gap-2 mt-3">
            <Button 
              variant="primary" 
              size="lg" 
              onClick={handleUpload}
              disabled={uploading || files.length === 0}
            >
              {uploading ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
                  Uploading...
                </>
              ) : `Upload ${files.length} Document${files.length !== 1 ? 's' : ''}`}
            </Button>
          </div>
        </Form>
      </div>
    </div>
  );
};

export default DocumentUploader;
