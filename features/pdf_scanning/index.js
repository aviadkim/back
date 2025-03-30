/**
 * PDF Scanning Feature Module
 * 
 * This module provides functionality for scanning and analyzing PDF documents.
 * It implements a complete vertical slice for the PDF scanning feature.
 */

const path = require('path');
const fs = require('fs');
const express = require('express');
const multer = require('multer');
const router = express.Router();

// Import service layer
const pdfService = require('./service');

// Configure file upload with multer
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'), false);
    }
  }
});

// Define routes
router.post('/api/pdf/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Process the uploaded PDF
    const result = await pdfService.processPdf(req.file.path, {
      language: req.body.language || 'he',
      extractTables: req.body.extractTables === 'true',
      extractText: req.body.extractText !== 'false'
    });

    return res.json({
      status: 'success',
      document_id: result.documentId,
      filename: req.file.originalname,
      details: result
    });
  } catch (error) {
    console.error('Error processing PDF:', error);
    return res.status(500).json({ 
      error: 'Failed to process PDF',
      message: error.message
    });
  }
});

router.get('/api/pdf/:documentId', async (req, res) => {
  try {
    const documentId = req.params.documentId;
    const documentData = await pdfService.getDocumentData(documentId);
    
    if (!documentData) {
      return res.status(404).json({ error: 'Document not found' });
    }
    
    return res.json(documentData);
  } catch (error) {
    console.error('Error retrieving document:', error);
    return res.status(500).json({ error: 'Failed to retrieve document' });
  }
});

// Export the router
module.exports = router;
