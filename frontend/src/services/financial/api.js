/**
 * Financial document analysis API service
 */

const API_URL = 'http://localhost:8000';

export const analyzeDocument = async (file, options = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('request_data', JSON.stringify(options));

  const response = await fetch(`${API_URL}/analyze_document`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }

  return await response.json();
};

export const listDocuments = async () => {
  const response = await fetch(`${API_URL}/list_documents`);
  if (!response.ok) {
    throw new Error(`Failed to list documents: ${response.statusText}`);
  }
  return await response.json();
};

export const generateReport = async (docId, reportType = 'summary', config = {}) => {
  const response = await fetch(`${API_URL}/generate_report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      doc_id: docId,
      report_type: reportType,
      config
    }),
  });

  if (!response.ok) {
    throw new Error(`Report generation failed: ${response.statusText}`);
  }

  return await response.json();
};
