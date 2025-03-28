import React, { useState, useEffect } from 'react';

// Import the Phase 1 assistant components
import DocumentUploadAssistant from '../features/document_intake/components/DocumentUploadAssistant';
import SummarizationAssistant from '../features/summarization/components/SummarizationAssistant';
// Import the Phase 2 assistant component
import FinancialDataAssistant from '../features/data_extraction/components/FinancialDataAssistant';
// Import the Phase 3 assistant component
import FinancialInsightAssistant from '../features/financial_insights/components/FinancialInsightAssistant';
// Import the Phase 4 assistant component
import ComplianceAssistant from '../features/compliance/components/ComplianceAssistant';

// Placeholder Components (Implement or replace later)
const AssistantSelector = ({ active, onChange, options }) => (
  <div style={{ marginBottom: '15px', borderBottom: '1px solid #ccc', paddingBottom: '10px' }}>
    <label htmlFor="assistant-select">Select Assistant: </label>
    <select id="assistant-select" value={active} onChange={(e) => onChange(e.target.value)}>
      <option value="auto" disabled>Auto (Not Implemented)</option>
      {options.map(option => (
        <option key={option} value={option}>{option.charAt(0).toUpperCase() + option.slice(1)}</option>
      ))}
    </select>
    <p>(Placeholder: Basic assistant selector)</p>
  </div>
);

const DocumentContextPanel = ({ document, onSelect }) => (
  <div style={{ border: '1px dashed #aaa', padding: '10px', marginBottom: '15px' }}>
    <h4>Document Context</h4>
    {document ? (
      <p>Current Document: {document.id} (Stage: {document.stage || 'N/A'})</p>
    ) : (
      <p>No document selected.</p>
    )}
    <button onClick={() => onSelect({ id: 'doc1', stage: 'processed' })}>Load Mock Doc 1</button>
    <button onClick={() => onSelect(null)}>Clear Document</button>
    <p>(Placeholder: Document context panel - Needs integration with actual document state)</p>
  </div>
);


function FinancialDocumentAssistantHub() {
  // Default to 'intake' for Phase 1 simplicity, 'auto' logic can be added later
  const [activeAssistant, setActiveAssistant] = useState('intake');
  // Placeholder for document context state management
  const [documentContext, setDocumentContext] = useState(null);

  // Define the available assistants
  const assistants = {
    'intake': <DocumentUploadAssistant />,
    'summarization': <SummarizationAssistant />,
    // Added Phase 2 assistant, passing documentId
    'extraction': <FinancialDataAssistant documentId={documentContext?.id} />,
    // Added Phase 3 assistant, passing documentId
    'insights': <FinancialInsightAssistant documentId={documentContext?.id} />,
    // Added Phase 4 assistant, passing documentId
    'compliance': <ComplianceAssistant documentId={documentContext?.id} />,
    // Add other assistants here in later phases
  };

  // Basic effect to switch based on context (simplified from spec for Phase 1)
  // In a real app, this logic would be more robust and tied to actual app state.
  useEffect(() => {
    // If no document is selected, default to intake
    if (!documentContext) {
      setActiveAssistant('intake');
    }
    // Add more sophisticated auto-selection logic later if needed
  }, [documentContext]);


  return (
    // Note: CopilotProvider should wrap this component higher up in the tree (e.g., in App.jsx)
    // as per the plan. This component assumes it's rendered within a Provider.
    <div className="financial-assistant-hub" style={{ border: '2px solid green', padding: '15px' }}>
      <header style={{ borderBottom: '2px solid green', marginBottom: '15px', paddingBottom: '10px' }}>
        <h1>Financial Document Analysis Hub</h1>
        <AssistantSelector
          active={activeAssistant}
          onChange={setActiveAssistant}
          options={Object.keys(assistants)} // Pass available assistant keys
        />
      </header>

      <main>
        <DocumentContextPanel
          document={documentContext}
          onSelect={setDocumentContext} // Allow placeholder to update context
        />

        <div className="assistant-container">
          {/* Render the currently active assistant */}
          {assistants[activeAssistant] || assistants['intake']}
        </div>
      </main>
    </div>
  );
}

export default FinancialDocumentAssistantHub;