/**
 * Table Extraction Feature Module
 * 
 * This module provides functionality for extracting and managing tables from documents.
 * It implements a complete vertical slice for the table extraction feature.
 */

const express = require('express');
const router = express.Router();

// Import service layer
const tableService = require('./service');

/**
 * Get tables from a document
 */
router.get('/api/tables/document/:documentId', async (req, res) => {
  try {
    const documentId = req.params.documentId;
    const page = req.query.page; // Optional page number filter
    
    const tables = await tableService.getDocumentTables(documentId, page);
    
    return res.json({
      status: 'success',
      document_id: documentId,
      tables: tables
    });
  } catch (error) {
    console.error('Error getting document tables:', error);
    return res.status(500).json({ 
      error: 'Failed to retrieve document tables',
      message: error.message
    });
  }
});

/**
 * Generate a specialized table view
 */
router.post('/api/tables/generate', async (req, res) => {
  try {
    const { documentId, tableIds, format, options } = req.body;
    
    if (!documentId || !tableIds || !Array.isArray(tableIds)) {
      return res.status(400).json({ error: 'Invalid request parameters' });
    }
    
    const generatedTable = await tableService.generateTableView(
      documentId, 
      tableIds, 
      format || 'default',
      options || {}
    );
    
    return res.json({
      status: 'success',
      table: generatedTable
    });
  } catch (error) {
    console.error('Error generating table view:', error);
    return res.status(500).json({ 
      error: 'Failed to generate table view',
      message: error.message
    });
  }
});

/**
 * Export table data in various formats
 */
router.post('/api/tables/export', async (req, res) => {
  try {
    const { documentId, tableId, format } = req.body;
    
    if (!documentId || !tableId) {
      return res.status(400).json({ error: 'Document ID and table ID are required' });
    }
    
    const exportResult = await tableService.exportTable(documentId, tableId, format || 'csv');
    
    // Set appropriate headers based on format
    if (format === 'csv') {
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', `attachment; filename="${tableId}.csv"`);
    } else if (format === 'json') {
      res.setHeader('Content-Type', 'application/json');
    } else if (format === 'xlsx') {
      res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
      res.setHeader('Content-Disposition', `attachment; filename="${tableId}.xlsx"`);
      return res.send(exportResult); // Send binary data
    }
    
    return res.send(exportResult);
  } catch (error) {
    console.error('Error exporting table:', error);
    return res.status(500).json({ 
      error: 'Failed to export table',
      message: error.message
    });
  }
});

/**
 * Get a specific table by ID
 */
router.get('/api/tables/:tableId', async (req, res) => {
  try {
    const tableId = req.params.tableId;
    
    const table = await tableService.getTableById(tableId);
    
    if (!table) {
      return res.status(404).json({ error: 'Table not found' });
    }
    
    return res.json({
      status: 'success',
      table: table
    });
  } catch (error) {
    console.error('Error getting table:', error);
    return res.status(500).json({ error: 'Failed to retrieve table' });
  }
});

// Export the router
module.exports = router;
