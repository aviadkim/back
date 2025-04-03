import React, { useState } from 'react';
import { useCopilotAction, CopilotChatbox } from '@copilotkit/react-core';

// Placeholder for displaying insights
const InsightsViewer = ({ insights }) => (
  <div style={{ border: '1px solid #eee', padding: '10px', marginTop: '10px', whiteSpace: 'pre-wrap', maxHeight: '400px', overflowY: 'auto' }}>
    <h4>Financial Insights / Comparison:</h4>
    {insights ? (
      <pre>{JSON.stringify(insights, null, 2)}</pre>
    ) : (
      <p>No insights generated yet.</p>
    )}
  </div>
);

// Assume documentId is passed as a prop or obtained from context
function FinancialInsightAssistant({ documentId }) {
  const [insights, setInsights] = useState(null);

  // Action to analyze financial health
  useCopilotAction({
    name: "analyzeFinancialHealth",
    description: "Analyze the financial health based on the current document's data",
    parameters: [
      // documentId is available from props
    ],
    handler: async () => {
      if (!documentId) {
        return "No document is currently selected to analyze financial health.";
      }
      try {
        const queryParams = new URLSearchParams({ documentId }).toString();
        const response = await fetch(`/api/analysis/financial-health?${queryParams}`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Health analysis failed: ${response.status} ${response.statusText}. ${errorData.error || ''}`);
        }

        const data = await response.json();
        setInsights(data); // Store analysis results
        // Format response for chat
        let responseText = `Financial Health Analysis for document ${documentId}:\n`;
        responseText += `Score: ${data.health_score}\n`;
        responseText += `Metrics:\n`;
        responseText += `  - Current Ratio: ${data.metrics.current_ratio}\n`;
        responseText += `  - Profit Margin: ${data.metrics.profit_margin}\n`;
        responseText += `  - Debt to Equity: ${data.metrics.debt_to_equity}\n`;
        responseText += `Assessment:\n${data.assessment}`;
        return responseText;
      } catch (error) {
        console.error("Error analyzing financial health:", error);
        return `Error during health analysis: ${error.message}`;
      }
    }
  });

  // Action to compare performance
  useCopilotAction({
    name: "comparePerformance",
    description: "Compare financial performance of the current document against another period",
    parameters: [
      {
        name: "comparisonPeriod",
        type: "string",
        description: "Period to compare against (e.g., 'previous-year', 'industry-average')"
      }
      // documentId is available from props
    ],
    handler: async ({ comparisonPeriod }) => {
      if (!documentId) {
        return "No document is currently selected for comparison.";
      }
      if (!comparisonPeriod) {
        return "Please specify the comparison period (e.g., 'previous-year', 'industry-average').";
      }
      try {
        const queryParams = new URLSearchParams({ documentId, period: comparisonPeriod }).toString();
        const response = await fetch(`/api/analysis/performance-comparison?${queryParams}`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Performance comparison failed: ${response.status} ${response.statusText}. ${errorData.error || ''}`);
        }

        const data = await response.json();
        setInsights(data); // Store comparison results
        // Format response for chat
        let responseText = `Performance Comparison for document ${documentId} vs ${comparisonPeriod}:\n`;
        responseText += `Changes:\n`;
        responseText += `  - Revenue: ${data.changes.revenue}\n`;
        responseText += `  - Expenses: ${data.changes.expenses}\n`;
        responseText += `  - Net Income: ${data.changes.net_income}\n`;
        responseText += `Analysis:\n${data.analysis}`;
        return responseText;
      } catch (error) {
        console.error("Error comparing performance:", error);
        return `Error during performance comparison: ${error.message}`;
      }
    }
  });

  return (
    <div className="financial-insights-container">
      <h2>Financial Insights Assistant</h2>
      <InsightsViewer insights={insights} />
      <CopilotChatbox
        placeholder="Ask me to analyze health or compare performance..."
        initialMessages={[
            {
                id: "0",
                role: "assistant",
                content: `I can help analyze financial health or compare performance for document ${documentId || '(select a document)'}. Try 'analyze health' or 'compare performance against previous-year'.`
            }
        ]}
        // Add other necessary props
      />
    </div>
  );
}

export default FinancialInsightAssistant;