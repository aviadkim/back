import React, { useState } from 'react';
import { useCopilotAction, CopilotChatbox } from '@copilotkit/react-core'; // Assuming Chatbox is from core

// Placeholder for displaying summary results
const SummaryViewer = ({ summary }) => (
  <div style={{ border: '1px solid #eee', padding: '10px', marginTop: '10px', whiteSpace: 'pre-wrap' }}>
    <h4>Summary Results:</h4>
    {summary ? (
      <pre>{JSON.stringify(summary, null, 2)}</pre>
    ) : (
      <p>No summary generated yet.</p>
    )}
  </div>
);

function SummarizationAssistant() {
  const [summary, setSummary] = useState(null);

  useCopilotAction({
    name: "generateExecutiveSummary",
    description: "Generate an executive summary of a financial document using its ID",
    parameters: [
      {
        name: "documentId",
        type: "string",
        description: "ID of the document to summarize"
      },
      {
        name: "format",
        type: "string",
        description: "Summary format (narrative, bullet-points, key-metrics)",
        optional: true, // Mark as optional if default is handled by backend/service
        default: "narrative" // Default value hint
      },
      {
        name: "maxLength",
        type: "number",
        description: "Maximum length of summary in words (approximate)",
        optional: true,
        default: 250 // Default value hint
      }
    ],
    handler: async ({ documentId, format = 'narrative', maxLength = 250 }) => {
      if (!documentId) {
        return "Please provide the ID of the document to summarize.";
      }
      try {
        // Construct query parameters
        const queryParams = new URLSearchParams({ format, maxLength }).toString();
        const response = await fetch(`/api/documents/${documentId}/summary?${queryParams}`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Summary generation failed: ${response.status} ${response.statusText}. ${errorData.error || ''}`);
        }

        const data = await response.json();
        setSummary(data); // Update state to display summary
        // Format response for chat
        return `Summary generated for document ${documentId}:\nFormat: ${data.summary_format}\nWord Count: ${data.word_count}\n\n${data.summary_text}`;
      } catch (error) {
        console.error("Error generating summary:", error);
        return `Error during summary generation: ${error.message}`;
      }
    }
  });

  useCopilotAction({
    name: "compareDocuments",
    description: "Generate a comparative summary of multiple documents using their IDs",
    parameters: [
      {
        name: "documentIds",
        type: "string",
        description: "Comma-separated list of document IDs to compare"
      }
    ],
    handler: async ({ documentIds }) => {
      if (!documentIds || documentIds.split(',').length < 2) {
        return "Please provide at least two comma-separated document IDs to compare.";
      }
      try {
        const queryParams = new URLSearchParams({ documentIds }).toString();
        const response = await fetch(`/api/documents/compare-summary?${queryParams}`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Comparison summary failed: ${response.status} ${response.statusText}. ${errorData.error || ''}`);
        }

        const data = await response.json();
        setSummary(data); // Update state to display comparison
        // Format response for chat
        return `Comparison summary generated for documents: ${data.document_ids.join(', ')}\nWord Count: ${data.word_count}\n\n${data.comparison_text}`;
      } catch (error) {
        console.error("Error generating comparison summary:", error);
        return `Error during comparison summary generation: ${error.message}`;
      }
    }
  });

  return (
    <div className="summarization-container">
      <h2>Document Summarization Assistant</h2>
      <SummaryViewer summary={summary} />
      <CopilotChatbox
        placeholder="Ask me to summarize or compare documents..."
        initialMessages={[
            {
                id: "0",
                role: "assistant",
                content: "I can create concise summaries or compare financial documents. What would you like?"
            }
        ]}
        // Add other necessary props
      />
    </div>
  );
}

export default SummarizationAssistant;