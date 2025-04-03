/**
 * Table Extraction Service
 * 
 * Service layer for table extraction functionality.
 * Implements business logic for the table extraction feature.
 */

// In a real implementation, these would be retrieved from a database
// For now, we'll use in-memory storage
const documentTables = {};

// Sample table data
const sampleAssetAllocation = {
  id: "sample_document_table_1",
  name: "חלוקת נכסים",
  page: 1,
  header: ["סוג נכס", "אחוז מהתיק", "שווי (₪)"],
  rows: [
    ["מניות", "45%", "450,000"],
    ["אג\"ח ממשלתי", "30%", "300,000"],
    ["אג\"ח קונצרני", "15%", "150,000"],
    ["מזומן", "10%", "100,000"]
  ]
};

const sampleCurrencyAllocation = {
  id: "sample_document_table_2",
  name: "התפלגות מטבעית",
  page: 2,
  header: ["מטבע", "אחוז מהתיק", "שווי (₪)"],
  rows: [
    ["שקל (₪)", "60%", "600,000"],
    ["דולר ($)", "25%", "250,000"],
    ["אירו (€)", "10%", "100,000"],
    ["אחר", "5%", "50,000"]
  ]
};

// Initialize with some sample data
documentTables["sample_document"] = {
  "1": [sampleAssetAllocation],
  "2": [sampleCurrencyAllocation]
};

/**
 * Get tables from a document
 * 
 * @param {string} documentId - Document ID
 * @param {string|number} page - Optional page number
 * @returns {Array} Tables found in the document
 */
async function getDocumentTables(documentId, page) {
  console.log(`Getting tables for document ${documentId}${page ? ` on page ${page}` : ''}`);
  
  // Check if we have tables for this document
  if (!documentTables[documentId]) {
    // Create sample tables if we don't have any for the document
    documentTables[documentId] = {
      "1": [{
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
      }],
      "2": [{
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
      }]
    };
  }
  
  // If page is specified, return tables only from that page
  if (page) {
    return documentTables[documentId][page] || [];
  }
  
  // Otherwise, return all tables as a flattened array
  return Object.values(documentTables[documentId]).flat();
}

/**
 * Get a specific table by ID
 * 
 * @param {string} tableId - Table ID
 * @returns {Object|null} Table object or null if not found
 */
async function getTableById(tableId) {
  console.log(`Getting table by ID: ${tableId}`);
  
  // Search through all documents and pages for the table
  for (const docId in documentTables) {
    for (const page in documentTables[docId]) {
      const tables = documentTables[docId][page];
      for (const table of tables) {
        if (table.id === tableId) {
          return table;
        }
      }
    }
  }
  
  return null;
}

/**
 * Generate a specialized view of tables
 * 
 * @param {string} documentId - Document ID
 * @param {Array} tableIds - Array of table IDs to include
 * @param {string} format - Format of the view (default, summary, comparison)
 * @param {Object} options - Additional options
 * @returns {Object} The generated table view
 */
async function generateTableView(documentId, tableIds, format = 'default', options = {}) {
  console.log(`Generating ${format} table view for document ${documentId} with tables:`, tableIds);
  
  // Get all the requested tables
  const tables = [];
  for (const tableId of tableIds) {
    const table = await getTableById(tableId);
    if (table) {
      tables.push(table);
    }
  }
  
  // Format doesn't match any supported view
  if (!['default', 'summary', 'comparison'].includes(format)) {
    format = 'default';
  }
  
  // Generate the view based on the format
  if (format === 'summary') {
    return generateSummaryView(tables, options);
  } else if (format === 'comparison') {
    return generateComparisonView(tables, options);
  } else {
    // Default view just combines all tables
    return {
      id: `view_${documentId}_${Date.now()}`,
      name: options.name || "מבט משולב",
      type: "default",
      tables: tables,
      created_at: new Date().toISOString()
    };
  }
}

/**
 * Generate a summary view of multiple tables
 * 
 * @param {Array} tables - Array of tables
 * @param {Object} options - Additional options
 * @returns {Object} The generated summary view
 */
function generateSummaryView(tables, options = {}) {
  // Extract key metrics from tables
  const metrics = [];
  
  for (const table of tables) {
    // Extract metric from each row of the table
    if (table.header && table.rows) {
      for (const row of table.rows) {
        if (row.length >= 2) {
          metrics.push({
            category: table.name,
            name: row[0],
            value: row[1],
            additional: row.slice(2).join(', ')
          });
        }
      }
    }
  }
  
  return {
    id: `summary_${Date.now()}`,
    name: options.name || "תקציר נתונים",
    type: "summary",
    metrics: metrics,
    source_tables: tables.map(t => t.id),
    created_at: new Date().toISOString()
  };
}

/**
 * Generate a comparison view of multiple tables
 * 
 * @param {Array} tables - Array of tables
 * @param {Object} options - Additional options
 * @returns {Object} The generated comparison view
 */
function generateComparisonView(tables, options = {}) {
  // Only proceed if we have at least 2 tables
  if (tables.length < 2) {
    return {
      id: `comparison_${Date.now()}`,
      name: "השוואה",
      type: "comparison",
      error: "נדרשות לפחות שתי טבלאות להשוואה",
      created_at: new Date().toISOString()
    };
  }
  
  // Find common categories between tables
  const categories = [];
  const comparisonData = [];
  
  // Simplified example - in reality this would be more sophisticated
  // to match similar categories across tables
  for (const table of tables) {
    if (table.header && table.rows) {
      // Assuming first column is category name
      const tableCategories = table.rows.map(row => row[0]);
      
      for (const category of tableCategories) {
        if (!categories.includes(category)) {
          categories.push(category);
        }
      }
    }
  }
  
  // For each category, gather data from all tables
  for (const category of categories) {
    const categoryData = {
      category: category,
      values: []
    };
    
    for (const table of tables) {
      // Find the row with this category
      const row = table.rows.find(r => r[0] === category);
      
      if (row) {
        categoryData.values.push({
          table: table.name,
          value: row[1],
          additional: row.slice(2).join(', ')
        });
      } else {
        categoryData.values.push({
          table: table.name,
          value: "N/A",
          additional: ""
        });
      }
    }
    
    comparisonData.push(categoryData);
  }
  
  return {
    id: `comparison_${Date.now()}`,
    name: options.name || "השוואת נתונים",
    type: "comparison",
    tables: tables.map(t => ({ id: t.id, name: t.name })),
    categories: categories,
    comparison_data: comparisonData,
    created_at: new Date().toISOString()
  };
}

/**
 * Export table data in a specific format
 * 
 * @param {string} documentId - Document ID
 * @param {string} tableId - Table ID
 * @param {string} format - Export format (csv, json, xlsx)
 * @returns {string|Buffer} Exported table data
 */
async function exportTable(documentId, tableId, format = 'csv') {
  console.log(`Exporting table ${tableId} from document ${documentId} in ${format} format`);
  
  // Get the table
  const table = await getTableById(tableId);
  
  if (!table) {
    throw new Error(`Table not found: ${tableId}`);
  }
  
  // Export in the requested format
  if (format === 'json') {
    return JSON.stringify(table, null, 2);
  } else if (format === 'xlsx') {
    // In a real implementation, this would create an Excel file
    // For this example, we'll return a string representation
    return `XLSX export of ${table.name} (mock data)`;
  } else {
    // Default to CSV
    let csv = '';
    
    // Add header
    if (table.header) {
      csv += table.header.map(h => `"${h}"`).join(',') + '\n';
    }
    
    // Add rows
    if (table.rows) {
      for (const row of table.rows) {
        csv += row.map(cell => `"${cell}"`).join(',') + '\n';
      }
    }
    
    return csv;
  }
}

module.exports = {
  getDocumentTables,
  getTableById,
  generateTableView,
  exportTable
};
