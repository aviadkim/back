// frontend/src/services/tableService.js
import api from './api';

// שירות לניהול טבלאות
const tableService = {
  // קבלת טבלאות ממסמך
  getTables: async (documentId) => {
    if (!documentId) {
        throw new Error("Document ID is required");
    }
    try {
      // Using the AWS endpoint
      const response = await api.get(`/aws/documents/${documentId}/tables`);
      // Ensure data is an array, default to empty array if not
      return Array.isArray(response.data) ? response.data : [];
    } catch (error) {
      console.error('Error fetching tables:', error.response?.data?.error || error.message);
      throw new Error(error.response?.data?.error || 'Failed to fetch tables');
    }
  },

  // יצירת טבלה מותאמת אישית
  createCustomTable: async (documentId, tableData) => {
     if (!documentId || !tableData) {
        throw new Error("Document ID and table data are required");
     }
    try {
      // Using the AWS endpoint (assuming it exists)
      const response = await api.post(`/aws/documents/${documentId}/custom-table`, tableData);
      return response.data; // Expects the generated table data
    } catch (error) {
      console.error('Error creating custom table:', error.response?.data?.error || error.message);
      throw new Error(error.response?.data?.error || 'Failed to create custom table');
    }
  },

  // ייצוא טבלה
  exportTable: (tableId, format = 'csv') => {
    // Note: This directly navigates the browser. Error handling is limited.
    if (!tableId) {
        console.error("Table ID is required for export");
        // Optionally throw an error or show a UI message
        return;
    }
    try {
      // Construct the URL using the base URL from the axios instance
      const exportUrl = `${api.defaults.baseURL}/aws/tables/${tableId}/export?format=${format}`;
      console.log(`Attempting to export table: ${exportUrl}`);
      window.location.href = exportUrl; // Trigger download
    } catch (error) {
      // This catch block might not be effective for window.location.href errors
      console.error('Error initiating table export:', error);
      // Consider showing a UI error message here
      alert(`Failed to initiate table export: ${error.message}`);
    }
  }
};

export default tableService;