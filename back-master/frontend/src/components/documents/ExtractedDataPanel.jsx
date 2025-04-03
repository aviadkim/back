import React, { useState } from 'react';
import '../../styles/ExtractedDataPanel.css';

const ExtractedDataPanel = ({ document }) => {
  const [viewMode, setViewMode] = useState('structured');
  
  // This would be replaced with the actual extracted data from your backend
  const extractedData = document.extractedData || {
    clientInfo: {
      name: "Sample Client",
      accountNumber: "123456789",
      date: "2023-04-01"
    },
    financialData: {
      totalAssets: 1250000,
      assetAllocation: {
        equity: 45,
        bonds: 30,
        cash: 15,
        alternatives: 10
      },
      currencyExposure: {
        USD: 65,
        EUR: 20,
        ILS: 15
      }
    },
    performance: {
      ytd: 7.5,
      oneYear: 12.3,
      threeYear: 32.8
    }
  };

  const renderRawData = () => {
    return (
      <div className="raw-data">
        <pre>{document.text_content || 'No raw text available'}</pre>
      </div>
    );
  };

  const renderStructuredData = () => {
    return (
      <div className="structured-data">
        <div className="data-section">
          <h3>Client Information</h3>
          <table>
            <tbody>
              {Object.entries(extractedData.clientInfo).map(([key, value]) => (
                <tr key={key}>
                  <td className="field-name">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</td>
                  <td className="field-value">{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="data-section">
          <h3>Financial Overview</h3>
          <table>
            <tbody>
              <tr>
                <td className="field-name">Total Assets</td>
                <td className="field-value">${extractedData.financialData.totalAssets.toLocaleString()}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div className="data-section">
          <h3>Asset Allocation</h3>
          <table>
            <tbody>
              {Object.entries(extractedData.financialData.assetAllocation).map(([key, value]) => (
                <tr key={key}>
                  <td className="field-name">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</td>
                  <td className="field-value">{value}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="data-section">
          <h3>Currency Exposure</h3>
          <table>
            <tbody>
              {Object.entries(extractedData.financialData.currencyExposure).map(([key, value]) => (
                <tr key={key}>
                  <td className="field-name">{key}</td>
                  <td className="field-value">{value}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="data-section">
          <h3>Performance</h3>
          <table>
            <tbody>
              {Object.entries(extractedData.performance).map(([key, value]) => (
                <tr key={key}>
                  <td className="field-name">{key === 'ytd' ? 'YTD' : `${key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())} Return`}</td>
                  <td className="field-value">{value}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="extracted-data-panel">
      <div className="view-toggle">
        <button 
          className={viewMode === 'structured' ? 'active' : ''}
          onClick={() => setViewMode('structured')}
        >
          Structured Data
        </button>
        <button 
          className={viewMode === 'raw' ? 'active' : ''}
          onClick={() => setViewMode('raw')}
        >
          Raw Text
        </button>
      </div>
      
      <div className="data-content">
        {viewMode === 'structured' ? renderStructuredData() : renderRawData()}
      </div>
    </div>
  );
};

export default ExtractedDataPanel;
