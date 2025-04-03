import React, { useState } from 'react';
import { useCopilotAction, CopilotChatbox } from '@copilotkit/react-core';

// Placeholder for displaying extracted data (tables, metrics)
const ExtractedDataViewer = ({ data }) => (
  <div style={{ border: '1px solid #eee', padding: '10px', marginTop: '10px', whiteSpace: 'pre-wrap', maxHeight: '400px', overflowY: 'auto' }}>
    <h4>Extracted Data / Metrics:</h4>
    {data ? (
      <pre>{JSON.stringify(data, null, 2)}</pre>
    ) : (
      <p>No data extracted or metrics calculated yet.</p>
    )}
  </div>
);

// Assume documentId is passed as a prop or obtained from context
function FinancialDataAssistant({ documentId }) {
  const [extractedData, setExtractedData] = useState(null);
  const [calculatedMetrics, setCalculatedMetrics] = useState(null);

  // Action to extract tables
  useCopilotAction({
    name: "extractFinancialTables",
    description: "Extract all tables containing financial data from the current document",
    parameters: [
      // documentId is available from props, so not needed as a parameter here
      // unless we want to allow specifying a different ID via chat.
      // For simplicity, we'll use the prop documentId.
    ],
    handler: async () => {
      if (!documentId) {
        return "No document is currently selected to extract tables from.";
      }
      try {
        // Using the POST endpoint to trigger extraction/retrieval
        const response = await fetch(`/api/documents/${documentId}/tables`, { method: 'POST' });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Table extraction failed: ${response.status} ${response.statusText}. ${errorData.error || ''}`);
        }

        const data = await response.json();
        setExtractedData(data); // Store extracted tables
        setCalculatedMetrics(null); // Clear previous metrics
        if (data && data.length > 0) {
          return `Successfully extracted ${data.length} table(s) from document ${documentId}. You can now ask to calculate metrics using a table ID (e.g., ${data[0].id}).`;
        } else {
          return `No tables were found or extracted from document ${documentId}.`;
        }
      } catch (error) {
        console.error("Error extracting tables:", error);
        return `Error during table extraction: ${error.message}`;
      }
    }
  });

  // Action to calculate metrics from a specific table
  useCopilotAction({
    name: "calculateFinancialMetrics",
    description: "Calculate key financial metrics from an extracted table using its ID",
    parameters: [
      {
        name: "tableId",
        type: "string",
        description: "ID of the extracted table to analyze (e.g., table-uuid)"
      }
    ],
    handler: async ({ tableId }) => {
      if (!tableId) {
        return "Please provide the ID of the table to calculate metrics for.";
      }
      // Optional: Check if tableId exists in extractedData state first
      // const tableExists = extractedData?.some(table => table.id === tableId);
      // if (!tableExists) {
      //   return `Table with ID ${tableId} was not found in the recently extracted data. Please extract tables first.`;
      // }

      try {
        const queryParams = new URLSearchParams({ tableId }).toString();
        const response = await fetch(`/api/analysis/financial-metrics?${queryParams}`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Metrics calculation failed: ${response.status} ${response.statusText}. ${errorData.error || ''}`);
        }

        const data = await response.json();
        setCalculatedMetrics(data); // Store calculated metrics
        // Format response for chat
        let responseText = `Metrics calculated for table ${data.table_id} (${data.table_title}):\n`;
        responseText += ` - Row Count: ${data.metrics.row_count}\n`;
        responseText += ` - Column Count: ${data.metrics.column_count}\n`;
        responseText += ` - Column Totals:\n`;
        for (const [col, total] of Object.entries(data.metrics.column_totals)) {
           responseText += `    * ${col}: ${total}\n`;
        }
        return responseText;
      } catch (error) {
        console.error("Error calculating metrics:", error);
        return `Error during metrics calculation: ${error.message}`;
      }
    }
  });

  return (
    <div className="financial-extraction-container">
      <h2>Financial Data Extraction Assistant</h2>
      {/* Display extracted tables or calculated metrics */}
      <ExtractedDataViewer data={calculatedMetrics || extractedData} />
      <CopilotChatbox
        placeholder="Ask me to extract tables or calculate metrics..."
        initialMessages={[
            {
                id: "0",
                role: "assistant",
                content: `I can help extract tables and calculate metrics for document ${documentId || '(select a document)'}. Try 'extract tables' or 'calculate metrics for table [table-id]'.`
            }
        ]}
        // Add other necessary props
      />
    </div>
  );
}

export default FinancialDataAssistant;