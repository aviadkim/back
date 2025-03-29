// src/components/documents/ExtractedDataView.jsx
import React, { useState } from 'react';
import ISINTable from './ISINTable'; // Assuming this component exists
import FinancialMetrics from './FinancialMetrics'; // Assuming this component exists
import './ExtractedDataView.css';

function ExtractedDataView({ document }) {
  const [activeSection, setActiveSection] = useState('summary');

  // Destructure with safe defaults
  const { metadata = {}, processed_data = {} } = document || {};
  const { ai_analysis = {}, tables = {}, text_content = "" } = processed_data; // Further destructure processed_data

  // Extract potential data points from ai_analysis or other parts if needed
  const isinData = ai_analysis?.isin_codes || []; // Example: Assuming ISINs are in ai_analysis
  const financialMetrics = ai_analysis?.financial_metrics || {}; // Example
  const documentType = ai_analysis?.document_type || 'לא זוהה'; // Example
  const companyNames = ai_analysis?.company_names || []; // Example
  const keyRatios = ai_analysis?.key_financial_ratios || {}; // Example

  // Calculate table count
  const tableCount = Object.values(tables).flat().length;

  // Check if there's any meaningful data to display
  const hasData = metadata.id || text_content || tableCount > 0 || isinData.length > 0 || Object.keys(financialMetrics).length > 0;

  if (!hasData) {
    return (
      <div className="extracted-data-view empty">
        <div className="empty-state">
          <i className="icon-document-search"></i>
          <h3>אין נתונים זמינים</h3>
          <p>המסמך עדיין בעיבוד או שלא זוהו נתונים רלוונטיים בו</p>
        </div>
      </div>
    );
  }

  const renderSectionContent = () => {
    switch (activeSection) {
      case 'summary':
        return (
          <div className="summary-section">
            <div className="document-stats">
              {/* Page Count */}
              {metadata.page_count && (
                <div className="stat-card">
                  <div className="stat-icon"><i className="icon-pages"></i></div>
                  <div className="stat-content">
                    <div className="stat-value">{metadata.page_count}</div>
                    <div className="stat-label">עמודים</div>
                  </div>
                </div>
              )}
              {/* Table Count */}
              <div className="stat-card">
                <div className="stat-icon"><i className="icon-table"></i></div>
                <div className="stat-content">
                  <div className="stat-value">{tableCount}</div>
                  <div className="stat-label">טבלאות</div>
                </div>
              </div>
              {/* ISIN Count */}
              <div className="stat-card">
                <div className="stat-icon"><i className="icon-barcode"></i></div>
                <div className="stat-content">
                  <div className="stat-value">{isinData.length}</div>
                  <div className="stat-label">קודי ISIN</div>
                </div>
              </div>
              {/* Upload Date */}
              {metadata.upload_date && (
                <div className="stat-card">
                  <div className="stat-icon"><i className="icon-clock"></i></div>
                  <div className="stat-content">
                    <div className="stat-value">
                      {new Date(metadata.upload_date).toLocaleDateString('he-IL')}
                    </div>
                    <div className="stat-label">תאריך העלאה</div>
                  </div>
                </div>
              )}
            </div>

            {/* Document Type from AI Analysis */}
            <div className="document-type">
              <h3>סוג המסמך (מזוהה): {documentType}</h3>
            </div>

            {/* Company Names */}
             {companyNames.length > 0 && (
                <div className="preview-section">
                    <h3>חברות שזוהו</h3>
                    <ul className="company-list">
                        {companyNames.slice(0, 5).map((name, index) => <li key={index}>{name}</li>)}
                        {companyNames.length > 5 && <li>...ועוד</li>}
                    </ul>
                     {/* Add button to view all if needed */}
                </div>
             )}


            <div className="extracted-preview">
              {/* ISIN Preview */}
              {isinData.length > 0 && (
                <div className="preview-section">
                  <h3>קודי ISIN שזוהו (תצוגה מקדימה)</h3>
                  {/* Pass the actual ISIN data */}
                  <ISINTable data={isinData.slice(0, 5)} isPreview={true} />
                  <button
                    className="btn-link"
                    onClick={() => setActiveSection('isin')}
                  >
                    לצפייה בכל קודי ה-ISIN <i className="icon-arrow-left"></i>
                  </button>
                </div>
              )}

              {/* Financial Metrics Preview */}
              {Object.keys(financialMetrics).length > 0 && (
                <div className="preview-section">
                  <h3>מדדים פיננסיים (תצוגה מקדימה)</h3>
                  {/* Pass the actual financial metrics */}
                  <FinancialMetrics
                    data={financialMetrics}
                    isPreview={true}
                  />
                  <button
                    className="btn-link"
                    onClick={() => setActiveSection('metrics')}
                  >
                    לצפייה בכל המדדים הפיננסיים <i className="icon-arrow-left"></i>
                  </button>
                </div>
              )}
            </div>
          </div>
        );

      case 'isin':
        return (
          <div className="isin-section">
            <h2>קודי ISIN במסמך</h2>
            {isinData.length > 0 ? (
              <ISINTable data={isinData} />
            ) : (
              <div className="empty-state">
                <p>לא זוהו קודי ISIN במסמך זה</p>
              </div>
            )}
          </div>
        );

      case 'metrics':
        return (
          <div className="metrics-section">
            <h2>מדדים פיננסיים</h2>
            {Object.keys(financialMetrics).length > 0 ? (
              <FinancialMetrics data={financialMetrics} />
            ) : (
              <div className="empty-state">
                <p>לא זוהו מדדים פיננסיים במסמך זה</p>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="extracted-data-view">
      <div className="section-tabs">
        <button
          className={`tab-button ${activeSection === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveSection('summary')}
        >
          סיכום כללי
        </button>
        <button
          className={`tab-button ${activeSection === 'isin' ? 'active' : ''}`}
          onClick={() => setActiveSection('isin')}
          disabled={isinData.length === 0} // Disable if no ISIN data
        >
          קודי ISIN
        </button>
        <button
          className={`tab-button ${activeSection === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveSection('metrics')}
          disabled={Object.keys(financialMetrics).length === 0} // Disable if no metrics
        >
          מדדים פיננסיים
        </button>
      </div>

      <div className="section-content">
        {renderSectionContent()}
      </div>
    </div>
  );
}

export default ExtractedDataView;