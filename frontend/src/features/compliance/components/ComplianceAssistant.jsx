import React, { useState } from 'react';
import { useCopilotAction, CopilotChatbox } from '@copilotkit/react-core';

// Placeholder for displaying compliance results
const ComplianceChecklist = ({ results }) => (
  <div style={{ border: '1px solid #eee', padding: '10px', marginTop: '10px', whiteSpace: 'pre-wrap', maxHeight: '400px', overflowY: 'auto' }}>
    <h4>Compliance Check / Requirements:</h4>
    {results ? (
      <pre>{JSON.stringify(results, null, 2)}</pre>
    ) : (
      <p>No compliance check run or requirements identified yet.</p>
    )}
  </div>
);

// Assume documentId is passed as a prop or obtained from context
function ComplianceAssistant({ documentId }) {
  const [complianceResults, setComplianceResults] = useState(null);

  // Action to check compliance
  useCopilotAction({
    name: "checkCompliance",
    description: "Check document for compliance with financial regulations in specified jurisdictions",
    parameters: [
      {
        name: "jurisdictions",
        type: "string",
        description: "Comma-separated list of relevant jurisdictions (e.g., 'US,EU,Israel')"
      }
      // documentId is available from props
    ],
    handler: async ({ jurisdictions }) => {
      if (!documentId) {
        return "No document is currently selected to check compliance for.";
      }
      if (!jurisdictions) {
        return "Please specify the jurisdictions (e.g., 'US,EU').";
      }
      try {
        const queryParams = new URLSearchParams({ documentId, jurisdictions }).toString();
        const response = await fetch(`/api/compliance/check?${queryParams}`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Compliance check failed: ${response.status} ${response.statusText}. ${errorData.error || ''}`);
        }

        const data = await response.json();
        setComplianceResults(data); // Store results
        // Format response for chat - maybe summarize the score and analysis
        return `Compliance check for document ${documentId} (Jurisdictions: ${data.jurisdictions.join(', ')}):\nScore: ${data.compliance_score}\n\nAnalysis:\n${data.compliance_analysis}`;
      } catch (error) {
        console.error("Error checking compliance:", error);
        return `Error during compliance check: ${error.message}`;
      }
    }
  });

  // Action to identify requirements
  useCopilotAction({
    name: "identifyRequirements",
    description: "Identify regulatory requirements mentioned in the document",
    parameters: [
      // documentId is available from props
    ],
    handler: async () => {
      if (!documentId) {
        return "No document is currently selected to identify requirements from.";
      }
      try {
        const queryParams = new URLSearchParams({ documentId }).toString();
        const response = await fetch(`/api/compliance/requirements?${queryParams}`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Requirement identification failed: ${response.status} ${response.statusText}. ${errorData.error || ''}`);
        }

        const data = await response.json();
        setComplianceResults(data); // Store results
        // Format response for chat
        let responseText = `Identified ${data.requirement_count} potential requirement(s) in document ${documentId}:\n`;
        if (data.extracted_requirements_list && data.extracted_requirements_list.length > 0) {
           responseText += data.extracted_requirements_list.map(req => `- ${req}`).join('\n');
        } else {
           responseText += "(No specific requirements parsed from list, see raw text below)";
           responseText += `\n\nRaw Text:\n${data.extracted_requirements_text}`;
        }
        return responseText;
      } catch (error) {
        console.error("Error identifying requirements:", error);
        return `Error during requirement identification: ${error.message}`;
      }
    }
  });

  return (
    <div className="compliance-assistant-container">
      <h2>Regulatory Compliance Assistant</h2>
      {/* Display compliance check results or identified requirements */}
      <ComplianceChecklist results={complianceResults} />
      <CopilotChatbox
        placeholder="Ask me about compliance checks or requirements..."
        initialMessages={[
            {
                id: "0",
                role: "assistant",
                content: `I can help check compliance or identify requirements for document ${documentId || '(select a document)'}. Try 'check compliance for US,EU' or 'identify requirements'.`
            }
        ]}
        // Add other necessary props
      />
    </div>
  );
}

export default ComplianceAssistant;