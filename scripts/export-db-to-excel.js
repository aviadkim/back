const ExcelJS = require('exceljs');
const { sequelize } = require('../backend/config/database');
const { User, Document, Table, FinancialItem } = require('../backend/models');

// פונקציה ליצירת קובץ Excel מבסיס הנתונים
async function exportDatabaseToExcel(outputPath) {
  console.log('מייצא נתונים לקובץ Excel...');
  
  const workbook = new ExcelJS.Workbook();
  
  // הוספת גליון עבור מסמכים
  const documentsSheet = workbook.addWorksheet('Documents');
  documentsSheet.columns = [
    { header: 'ID', key: 'id', width: 36 },
    { header: 'User ID', key: 'userId', width: 36 },
    { header: 'File Name', key: 'originalFileName', width: 30 },
    { header: 'File Type', key: 'fileType', width: 10 },
    { header: 'Status', key: 'processingStatus', width: 15 },
    { header: 'Document Type', key: 'documentType', width: 20 },
    { header: 'Company', key: 'companyName', width: 20 },
    { header: 'Upload Date', key: 'createdAt', width: 20 },
    { header: 'Page Count', key: 'pageCount', width: 10 }
  ];
  
  // הוספת גליון עבור טבלאות
  const tablesSheet = workbook.addWorksheet('Tables');
  tablesSheet.columns = [
    { header: 'ID', key: 'id', width: 36 },
    { header: 'Document ID', key: 'documentId', width: 36 },
    { header: 'Table Name', key: 'tableName', width: 30 },
    { header: 'Page Number', key: 'pageNumber', width: 12 },
    { header: 'Table Type', key: 'tableType', width: 15 },
    { header: 'Confidence', key: 'extractionConfidence', width: 12 },
    { header: 'Header Count', key: 'headerCount', width: 15 },
    { header: 'Row Count', key: 'rowCount', width: 12 },
    { header: 'Created At', key: 'createdAt', width: 20 }
  ];
  
  // הוספת גליון עבור פריטים פיננסיים
  const itemsSheet = workbook.addWorksheet('Financial Items');
  itemsSheet.columns = [
    { header: 'ID', key: 'id', width: 36 },
    { header: 'Document ID', key: 'documentId', width: 36 },
    { header: 'Table ID', key: 'tableId', width: 36 },
    { header: 'Item Type', key: 'itemType', width: 15 },
    { header: 'Value', key: 'itemValue', width: 20 },
    { header: 'Numeric Value', key: 'numericValue', width: 15 },
    { header: 'Currency', key: 'currency', width: 10 },
    { header: 'Page Number', key: 'pageNumber', width: 12 },
    { header: 'Confidence', key: 'confidence', width: 12 },
    { header: 'Created At', key: 'createdAt', width: 20 }
  ];
  
  // שליפת נתונים מהמסד וייצוא לגליונות
  try {
    // שליפת מסמכים
    const documents = await Document.findAll({
      attributes: ['id', 'userId', 'originalFileName', 'fileType', 'processingStatus', 
        'documentType', 'companyName', 'createdAt', 'pageCount']
    });
    
    for (const doc of documents) {
      documentsSheet.addRow({
        id: doc.id,
        userId: doc.userId,
        originalFileName: doc.originalFileName,
        fileType: doc.fileType,
        processingStatus: doc.processingStatus,
        documentType: doc.documentType,
        companyName: doc.companyName,
        createdAt: doc.createdAt,
        pageCount: doc.pageCount
      });
    }
    
    // שליפת טבלאות
    const tables = await Table.findAll();
    
    for (const table of tables) {
      tablesSheet.addRow({
        id: table.id,
        documentId: table.documentId,
        tableName: table.tableName,
        pageNumber: table.pageNumber,
        tableType: table.tableType,
        extractionConfidence: table.extractionConfidence,
        headerCount: Array.isArray(table.headerRow) ? table.headerRow.length : 0,
        rowCount: Array.isArray(table.dataRows) ? table.dataRows.length : 0,
        createdAt: table.createdAt
      });
    }
    
    // שליפת פריטים פיננסיים
    const items = await FinancialItem.findAll();
    
    for (const item of items) {
      itemsSheet.addRow({
        id: item.id,
        documentId: item.documentId,
        tableId: item.tableId,
        itemType: item.itemType,
        itemValue: item.itemValue,
        numericValue: item.numericValue,
        currency: item.currency,
        pageNumber: item.pageNumber,
        confidence: item.confidence,
        createdAt: item.createdAt
      });
    }
    
    // שמירת הקובץ
    await workbook.xlsx.writeFile(outputPath);
    console.log(`מסד הנתונים יוצא בהצלחה לקובץ: ${outputPath}`);
    
  } catch (error) {
    console.error('שגיאה בייצוא מסד הנתונים:', error);
  }
}

// הפעלת הפונקציה כאשר הסקריפט מורץ ישירות
if (require.main === module) {
  const outputPath = process.argv[2] || './database_export.xlsx';
  
  // אתחול מסד הנתונים ואז ייצוא
  const { setupDatabase } = require('../backend/config/database');
  setupDatabase()
    .then(() => exportDatabaseToExcel(outputPath))
    .catch(err => {
      console.error('שגיאה:', err);
      process.exit(1);
    });
}

module.exports = exportDatabaseToExcel; 