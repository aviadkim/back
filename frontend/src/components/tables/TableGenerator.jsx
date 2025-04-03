// src/components/tables/TableGenerator.jsx
import React from 'react';
import './TableGenerator.css';

function TableGenerator({ headers, rows }) {
  // פונקציה לעיצוב ערכים מספריים
  const formatValue = (value) => {
    // Handle null or undefined values
    if (value === null || typeof value === 'undefined') {
      return ''; // Return empty string for null/undefined
    }

    const stringValue = String(value); // Convert to string for checks

    // Check if it looks like a number (potentially with commas, periods, minus sign)
    // Allow percentage sign
    if (/^-?[\d,]*\.?\d*%?$/.test(stringValue.trim())) {
        let numStr = stringValue.trim().replace(/,/g, ''); // Remove existing commas
        const isPercent = numStr.endsWith('%');
        if (isPercent) {
            numStr = numStr.slice(0, -1); // Remove % for parsing
        }

        const num = parseFloat(numStr);

        if (!isNaN(num)) {
            // Format number with commas and up to 2 decimal places
            const formattedNum = num.toLocaleString('he-IL', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 2
            });
            return isPercent ? `${formattedNum}%` : formattedNum; // Add % back if needed
        }
    }

    // Return the original value if it's not a number or formatting fails
    return stringValue;
  };

  // Handle cases where headers or rows might be missing or empty
  const displayHeaders = headers || [];
  const displayRows = rows || [];

  return (
    <div className="table-generator-wrapper"> {/* Added a wrapper for scrolling */}
      <div className="table-generator">
        <table>
          <thead>
            <tr>
              {displayHeaders.map((header, index) => (
                <th key={index}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayRows.length > 0 ? (
              displayRows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {/* Ensure row is an array and handle potential missing cells */}
                  {(Array.isArray(row) ? row : []).map((cell, cellIndex) => (
                    <td key={cellIndex}>{formatValue(cell)}</td>
                  ))}
                  {/* Add empty cells if row is shorter than header */}
                  {Array.isArray(row) && row.length < displayHeaders.length &&
                    Array(displayHeaders.length - row.length).fill().map((_, i) => <td key={`empty-${rowIndex}-${i}`}></td>)
                  }
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={displayHeaders.length || 1} className="empty-table-message">
                  אין נתונים להצגה בטבלה זו.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TableGenerator;