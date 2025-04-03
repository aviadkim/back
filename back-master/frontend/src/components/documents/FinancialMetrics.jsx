import React, { useState, useMemo } from 'react';
import './FinancialMetrics.css';

/**
 * רכיב להצגת מדדים פיננסיים שחולצו מהמסמך
 * @param {Object} props - מאפייני הרכיב
 * @param {Object} props.data - אובייקט המכיל את המדדים הפיננסיים שחולצו (מ-ai_analysis.financial_metrics)
 * @param {boolean} props.loading - האם הנתונים בטעינה
 * @param {boolean} props.isPreview - האם זו תצוגה מקדימה
 */
const FinancialMetrics = ({ data = {}, loading = false, isPreview = false }) => {
  const [selectedCategory, setSelectedCategory] = useState('all');

  // פונקציה עזר לעיצוב ערכים כספיים
  const formatCurrency = (value, currency = 'ILS') => { // Default to ILS
    if (value === undefined || value === null) return 'לא זמין';
    const numValue = typeof value === 'string' ? parseFloat(value.replace(/[^\d.-]/g, '')) : value;
    if (isNaN(numValue)) return value; // Return original if not a number
    try {
      return new Intl.NumberFormat('he-IL', {
        style: 'currency',
        currency: currency, // Use provided currency
        maximumFractionDigits: 2,
        minimumFractionDigits: 0,
      }).format(numValue).replace(/\s/g, ''); // Remove space often added by formatter
    } catch (e) {
      console.warn("Currency formatting failed:", e);
      return value; // Fallback
    }
  };

  // פונקציה עזר לעיצוב אחוזים
  const formatPercentage = (value) => {
    if (value === undefined || value === null) return 'לא זמין';
    const numValue = typeof value === 'string' ? parseFloat(value.replace(/[^\d.%]/g, '')) : value; // Allow % sign
    if (isNaN(numValue)) return value;
    try {
      // Assuming the value is already a percentage (e.g., 25 means 25%)
      // If it's a decimal (e.g., 0.25 means 25%), multiply by 100 before formatting
      const valueToFormat = numValue; // Adjust if needed: numValue / 100 if input is decimal
      return new Intl.NumberFormat('he-IL', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 2
      }).format(valueToFormat / 100); // Intl expects decimal for percent style
    } catch (e) {
      console.warn("Percentage formatting failed:", e);
      return `${value}%`; // Basic fallback
    }
  };


  // פונקציה עזר לעיצוב תאריכים
  const formatDate = (dateStr) => {
    if (!dateStr) return 'לא זמין';
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return dateStr; // Return original if invalid date
      return new Intl.DateTimeFormat('he-IL', {
        year: 'numeric',
        month: '2-digit', // Use numeric month
        day: '2-digit'   // Use numeric day
      }).format(date);
    } catch (error) {
      console.warn("Date formatting failed:", error);
      return dateStr; // Fallback
    }
  };

  // פונקציה עזר לעיצוב מספרים כלליים
   const formatNumber = (value) => {
       if (value === undefined || value === null) return 'לא זמין';
       const numValue = typeof value === 'string' ? parseFloat(value.replace(/[^\d.-]/g, '')) : value;
       if (isNaN(numValue)) return value;
       try {
           return new Intl.NumberFormat('he-IL', {
               maximumFractionDigits: 2
           }).format(numValue);
       } catch (e) {
           console.warn("Number formatting failed:", e);
           return value;
       }
   };


  // ארגון המדדים לקטגוריות (יכול להגיע מה-backend או להיות מוגדר כאן)
  // This structure assumes `data` itself contains the metrics directly.
  // Adjust if `data` has nested structures like `data.income_statement`.
  const categorizedMetrics = useMemo(() => {
      const categories = {
          // Define potential categories and their keywords/logic
          incomeStatement: { title: 'דוח רווח והפסד', icon: 'fa-file-invoice-dollar', metrics: {} },
          balanceSheet: { title: 'מאזן', icon: 'fa-balance-scale', metrics: {} },
          cashFlow: { title: 'תזרים מזומנים', icon: 'fa-coins', metrics: {} },
          ratios: { title: 'יחסים פיננסיים', icon: 'fa-percentage', metrics: {} },
          general: { title: 'מדדים כלליים', icon: 'fa-chart-line', metrics: {} }
      };

      // Attempt to categorize metrics based on keys (simple example)
      Object.entries(data).forEach(([key, value]) => {
          const lowerKey = key.toLowerCase();
          if (lowerKey.includes('revenue') || lowerKey.includes('profit') || lowerKey.includes('expense') || lowerKey.includes('income')) {
              categories.incomeStatement.metrics[key] = value;
          } else if (lowerKey.includes('asset') || lowerKey.includes('liability') || lowerKey.includes('equity')) {
              categories.balanceSheet.metrics[key] = value;
          } else if (lowerKey.includes('cash_flow') || lowerKey.includes('operating') || lowerKey.includes('investing') || lowerKey.includes('financing')) {
              categories.cashFlow.metrics[key] = value;
          } else if (lowerKey.includes('ratio') || lowerKey.includes('margin') || lowerKey.includes('return')) {
              categories.ratios.metrics[key] = value;
          } else {
              categories.general.metrics[key] = value;
          }
      });

      // Filter out categories with no metrics
      return Object.entries(categories)
                   .filter(([_, category]) => Object.keys(category.metrics).length > 0)
                   .reduce((acc, [key, value]) => { acc[key] = value; return acc; }, {});

  }, [data]);


  const availableCategories = Object.keys(categorizedMetrics);

  // פילטור המדדים לפי הקטגוריה שנבחרה
  const getFilteredMetrics = () => {
    if (selectedCategory === 'all') {
      return Object.values(categorizedMetrics);
    }
    return categorizedMetrics[selectedCategory] ? [categorizedMetrics[selectedCategory]] : [];
  };

  // בדיקה אם יש מדדים בכלל
  const hasMetrics = availableCategories.length > 0;

  // אם הנתונים בטעינה, הצג אינדיקטור טעינה
  if (loading) {
    return (
      <div className="financial-metrics-loading">
        <div className="loading-spinner"></div>
        <p>טוען מדדים פיננסיים...</p>
      </div>
    );
  }

  // אם אין מדדים לאחר הטעינה, הצג הודעה
  if (!loading && !hasMetrics) {
    return (
      <div className="financial-metrics-empty">
        <i className="fas fa-info-circle"></i>
        <p>לא זוהו מדדים פיננסיים במסמך זה</p>
      </div>
    );
  }

  // Function to format value based on key hints or type
  const formatMetricValue = (key, value) => {
      const lowerKey = key.toLowerCase();
      if (lowerKey.includes('date') || lowerKey.includes('time')) return formatDate(value);
      if (lowerKey.includes('percent') || lowerKey.includes('ratio') || lowerKey.includes('margin') || String(value).includes('%')) return formatPercentage(value);
      // Basic currency check (can be improved)
      if (lowerKey.includes('revenue') || lowerKey.includes('profit') || lowerKey.includes('cost') || lowerKey.includes('asset') || lowerKey.includes('liability') || lowerKey.includes('equity') || lowerKey.includes('cash') || lowerKey.includes('price') || lowerKey.includes('value') || String(value).match(/[₪$€£]/)) return formatCurrency(value);
      if (typeof value === 'number') return formatNumber(value);
      return value; // Return as string if no specific format applies
  };

   // Function to generate a readable label from a key
   const formatMetricLabel = (key) => {
       return key
           .replace(/_/g, ' ') // Replace underscores with spaces
           .replace(/([A-Z])/g, ' $1') // Add space before capital letters (for camelCase)
           .replace(/\b\w/g, l => l.toUpperCase()) // Capitalize first letter of each word
           .trim();
   };


  return (
    <div className={`financial-metrics-container ${isPreview ? 'preview-mode' : ''}`}>
      {!isPreview && (
          <div className="financial-metrics-header">
            <h3>מדדים פיננסיים</h3>
            {availableCategories.length > 1 && ( // Show filter only if more than one category
                <div className="category-filter">
                  <label htmlFor="metric-category-select">הצג לפי קטגוריה:</label>
                  <select
                    id="metric-category-select"
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                  >
                    <option value="all">כל הקטגוריות</option>
                    {availableCategories.map(categoryKey => (
                      <option key={categoryKey} value={categoryKey}>
                        {categorizedMetrics[categoryKey].title}
                      </option>
                    ))}
                  </select>
                </div>
            )}
          </div>
      )}

      <div className={`metrics-panels ${isPreview ? 'preview-grid' : ''}`}>
        {getFilteredMetrics().map((category) => (
          <div key={category.title} className="metrics-panel">
            {!isPreview && (
                <div className="metrics-panel-header">
                  <i className={`fas ${category.icon}`}></i>
                  <h4>{category.title}</h4>
                </div>
            )}
            <div className={`metrics-panel-body ${isPreview ? 'preview-body' : ''}`}>
              {Object.entries(category.metrics)
                .slice(0, isPreview ? 5 : undefined) // Limit items in preview mode
                .map(([key, value]) => (
                  <div key={key} className="metric-item">
                    <div className="metric-label" title={key}>{formatMetricLabel(key)}</div>
                    <div className="metric-value">{formatMetricValue(key, value)}</div>
                  </div>
              ))}
            </div>
             {isPreview && Object.keys(category.metrics).length > 5 && (
                 <div className="preview-more">...ועוד</div>
             )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default FinancialMetrics;