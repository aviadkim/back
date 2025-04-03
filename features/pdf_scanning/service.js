/**
 * PDF Scanning Service
 * 
 * Service layer for PDF document processing.
 * Implements business logic for the PDF scanning feature.
 */

const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const { promisify } = require('util');
const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);

// For a real implementation, you would use a proper database
// This is just a simple in-memory store for demonstration
const documentStore = {};

// Import the coordinator from agent framework
let agentCoordinator;
try {
  const agentFramework = require('../../agent_framework');
  agentCoordinator = agentFramework.get_coordinator();
} catch (error) {
  console.warn('Agent framework not available:', error.message);
  // Create a mock coordinator if the real one is not available
  agentCoordinator = {
    process_document: (path) => ({
      document_id: path.split('/').pop().replace('.', '_'),
      processed_at: new Date().toISOString(),
      chunks_count: 0,
      metadata: { title: 'Unknown', language: 'he', confidence: 0 }
    })
  };
}

/**
 * Process a PDF document
 * 
 * @param {string} filePath - Path to the uploaded PDF file
 * @param {Object} options - Processing options
 * @returns {Object} Processing result details
 */
async function processPdf(filePath, options = {}) {
  console.log(`Processing PDF: ${filePath} with options:`, options);
  
  const filename = path.basename(filePath);
  const documentId = filename.replace('.', '_');
  
  // In a real implementation, this would actually process the PDF
  // For now, we'll simulate processing with a delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Use the agent coordinator to process the document
  const processingResult = agentCoordinator.process_document(filePath, options);
  
  // Create document metadata
  const documentData = {
    metadata: {
      id: documentId,
      filename: filename,
      upload_date: new Date().toISOString(),
      status: 'completed',
      page_count: 10, // Mock data
      language: options.language || 'he',
      type: 'PDF',
      size_bytes: 1024000 // Mock data
    },
    processed_data: {
      isin_data: [
        { isin: "US0378331005", company: "Apple Inc.", market: "NASDAQ", type: "מניה" },
        { isin: "US88160R1014", company: "Tesla Inc.", market: "NASDAQ", type: "מניה" },
        { isin: "DE000BAY0017", company: "Bayer AG", market: "XETRA", type: "מניה" }
      ],
      financial_data: {
        is_financial: true,
        document_type: "דו\"ח שנתי",
        metrics: {
          assets: [
            { name: "סך נכסים", value: 1200000, unit: "₪" },
            { name: "נכסים נזילים", value: 550000, unit: "₪" }
          ],
          returns: [
            { name: "תשואה שנתית", value: 8.7, unit: "%" },
            { name: "תשואה ממוצעת 5 שנים", value: 7.2, unit: "%" }
          ],
          ratios: [
            { name: "יחס שארפ", value: 1.3 },
            { name: "יחס P/E ממוצע", value: 22.4 }
          ]
        }
      },
      tables: {
        "1": [
          {
            id: `${documentId}_table_1`,
            name: "חלוקת נכסים",
            page: 1,
            header: ["סוג נכס", "אחוז מהתיק", "שווי (₪)"],
            rows: [
              ["מניות", "45%", "450,000"],
              ["אג\"ח ממשלתי", "30%", "300,000"],
              ["אג\"ח קונצרני", "15%", "150,000"],
              ["מזומן", "10%", "100,000"]
            ]
          }
        ],
        "2": [
          {
            id: `${documentId}_table_2`,
            name: "התפלגות מטבעית",
            page: 2,
            header: ["מטבע", "אחוז מהתיק", "שווי (₪)"],
            rows: [
              ["שקל (₪)", "60%", "600,000"],
              ["דולר ($)", "25%", "250,000"],
              ["אירו (€)", "10%", "100,000"],
              ["אחר", "5%", "50,000"]
            ]
          }
        ]
      }
    }
  };
  
  // Store document data
  documentStore[documentId] = documentData;
  
  // In a real implementation, you would persist this to a database
  
  return {
    documentId,
    processingResult,
    status: 'success'
  };
}

/**
 * Get document data by ID
 * 
 * @param {string} documentId - Document ID
 * @returns {Object|null} Document data or null if not found
 */
async function getDocumentData(documentId) {
  // In a real implementation, this would query a database
  return documentStore[documentId] || null;
}

module.exports = {
  processPdf,
  getDocumentData
};
