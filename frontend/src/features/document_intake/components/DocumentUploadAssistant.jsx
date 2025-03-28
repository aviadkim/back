import React from 'react';
import { useCopilotAction, CopilotChatbox } from '@copilotkit/react-core'; // Assuming Chatbox is from core now, adjust if needed from react-ui

// Placeholder for your actual uploader component
const DocumentUploader = () => (
  <div>
    <input type="file" />
    <button>Upload</button>
    <p>(Placeholder: Replace with your actual document uploader component)</p>
  </div>
);

function DocumentUploadAssistant() {
  useCopilotAction({
    name: "classifyDocument",
    description: "Analyze and classify an uploaded financial document",
    parameters: [
      {
        name: "documentFile",
        type: "file", // Note: CopilotKit file handling might require specific setup
        description: "The financial document to classify"
      }
    ],
    handler: async ({ documentFile }) => {
      // This handler assumes the 'file' type parameter works directly.
      // You might need to adjust how the file is obtained from the user interaction
      // if CopilotKit doesn't automatically handle file inputs via chat.
      if (!documentFile) {
        return "Please provide a file to classify.";
      }

      const formData = new FormData();
      formData.append('file', documentFile);

      try {
        // Using the API endpoint defined in the backend routes
        const response = await fetch('/api/documents/classify', {
          method: 'POST',
          body: formData
          // Headers are automatically set for FormData by fetch
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({})); // Try to parse error
          throw new Error(`Classification failed: ${response.status} ${response.statusText}. ${errorData.error || ''}`);
        }

        const data = await response.json();
        // Format the response for the user
        return `Document classified as: ${data.document_type} (Confidence: ${data.confidence}%). Suggested Metadata: ${JSON.stringify(data.suggested_metadata)}`;
      } catch (error) {
        console.error("Error classifying document:", error);
        return `Error during classification: ${error.message}`;
      }
    }
  });

  useCopilotAction({
    name: "validateDocument",
    description: "Validate a document for completeness and quality using its ID",
    parameters: [
      {
        name: "documentId",
        type: "string",
        description: "ID of the document to validate (obtained after upload/processing)"
      }
    ],
    handler: async ({ documentId }) => {
      if (!documentId) {
        return "Please provide the ID of the document to validate.";
      }
      try {
        // Using the API endpoint defined in the backend routes
        const response = await fetch(`/api/documents/${documentId}/validate`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({})); // Try to parse error
          throw new Error(`Validation failed: ${response.status} ${response.statusText}. ${errorData.error || ''}`);
        }

        const data = await response.json();
        // Format the response for the user
        let responseText = `Validation for document ${documentId}:\n`;
        responseText += `Is Valid: ${data.is_valid}\n`;
        responseText += `Score: ${data.validation_score}\n`;
        if (data.missing_elements && data.missing_elements.length > 0) {
          responseText += `Missing Elements: ${data.missing_elements.join(', ')}\n`;
        }
        if (data.suggestions && data.suggestions.length > 0) {
          responseText += `Suggestions:\n${data.suggestions.join('\n')}`;
        }
        return responseText;
      } catch (error) {
        console.error("Error validating document:", error);
        return `Error during validation: ${error.message}`;
      }
    }
  });

  return (
    <div className="document-upload-container">
      <h2>Upload & Intake Assistant</h2>
      <DocumentUploader />
      <CopilotChatbox
        // CopilotChatbox props might differ based on version, adjust as needed
        // For example, placeholder and greeting might be part of CopilotProvider config
        // or passed directly. Check CopilotKit documentation.
        placeholder="Ask me about uploading or classifying your financial documents..."
        initialMessages={[ // Example initial message
            {
                id: "0",
                role: "assistant",
                content: "I can help you upload and classify your financial documents. How can I assist?"
            }
        ]}
        // Other props like `labels`, `components`, etc. might be needed
      />
    </div>
  );
}

export default DocumentUploadAssistant;