import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Select, Space, Tabs } from 'antd';

const { Option } = Select;
const { TabPane } = Tabs;

const CustomTableGenerator = ({ documentId }) => {
  const [loading, setLoading] = useState(false);
  const [tableData, setTableData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [availableFields, setAvailableFields] = useState([]);
  const [selectedFields, setSelectedFields] = useState([]);
  const [filters, setFilters] = useState([]);
  const [sortConfig, setSortConfig] = useState(null);
  const [groupByField, setGroupByField] = useState(null);
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState('');

  // Fetch available fields when component mounts
  useEffect(() => {
    const fetchFields = async () => {
      try {
        const response = await fetch(`/api/documents/${documentId}/available-fields`);
        const data = await response.json();
        setAvailableFields(data.fields);
      } catch (error) {
        console.error('Error fetching available fields:', error);
      }
    };

    if (documentId) {
      fetchFields();
    }
  }, [documentId]);

  // Generate table based on current configuration
  const generateTable = async () => {
    setLoading(true);
    
    try {
      const queryConfig = {
        columns: selectedFields,
        filters: filters,
        sort_by: sortConfig,
        group_by: groupByField
      };
      
      const response = await fetch(`/api/documents/${documentId}/generate-table`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(queryConfig),
      });
      
      const data = await response.json();
      
      // Transform the data into table format
      const tableColumns = data.columns.map(col => ({
        title: col,
        dataIndex: col,
        key: col,
        sorter: (a, b) => {
          if (typeof a[col] === 'number') {
            return a[col] - b[col];
          }
          return String(a[col]).localeCompare(String(b[col]));
        },
      }));
      
      setColumns(tableColumns);
      setTableData(data.rows);
    } catch (error) {
      console.error('Error generating table:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Generate table from natural language query
  const generateFromNaturalLanguage = async () => {
    if (!naturalLanguageQuery) return;
    
    setLoading(true);
    
    try {
      const response = await fetch(`/api/documents/${documentId}/natural-language-query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: naturalLanguageQuery }),
      });
      
      const data = await response.json();
      
      // Transform the data into table format
      const tableColumns = data.columns.map(col => ({
        title: col,
        dataIndex: col,
        key: col,
      }));
      
      setColumns(tableColumns);
      setTableData(data.rows);
      
      // Update UI to reflect the query parameters
      setSelectedFields(data.query.columns || []);
      setFilters(data.query.filters || []);
      setSortConfig(data.query.sort_by || null);
      setGroupByField(data.query.group_by || null);
    } catch (error) {
      console.error('Error processing natural language query:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Add a new filter
  const addFilter = () => {
    setFilters([...filters, { field: availableFields[0], operator: '=', value: '' }]);
  };
  
  // Remove a filter
  const removeFilter = (index) => {
    const newFilters = [...filters];
    newFilters.splice(index, 1);
    setFilters(newFilters);
  };
  
  // Update a filter
  const updateFilter = (index, field, value) => {
    const newFilters = [...filters];
    newFilters[index] = { ...newFilters[index], [field]: value };
    setFilters(newFilters);
  };
  
  return (
    <Card title="יוצר טבלאות מותאמות אישית" className="custom-table-generator">
      <Tabs defaultActiveKey="builder">
        <TabPane tab="בונה טבלאות" key="builder">
          <div className="table-builder">
            <Card title="בחירת שדות" size="small">
              <Select
                mode="multiple"
                style={{ width: '100%' }}
                placeholder="בחר שדות להצגה"
                value={selectedFields}
                onChange={setSelectedFields}
              >
                {availableFields.map(field => (
                  <Option key={field} value={field}>{field}</Option>
                ))}
              </Select>
            </Card>
            
            <Card title="מסננים" size="small" extra={<Button type="primary" onClick={addFilter}>הוסף מסנן</Button>}>
              {filters.map((filter, index) => (
                <div key={index} className="filter-row">
                  <Space>
                    <Select value={filter.field} onChange={(value) => updateFilter(index, 'field', value)}>
                      {availableFields.map(field => (
                        <Option key={field} value={field}>{field}</Option>
                      ))}
                    </Select>
                    
                    <Select value={filter.operator} onChange={(value) => updateFilter(index, 'operator', value)}>
                      <Option value="=">=</Option>
                      <Option value="!=">!=</Option>
                      <Option value=">">></Option>
                      <Option value="<"><</Option>
                      <Option value=">=">>=</Option>
                      <Option value="<="><=</Option>
                      <Option value="contains">מכיל</Option>
                    </Select>
                    
                    <Input 
                      value={filter.value} 
                      onChange={(e) => updateFilter(index, 'value', e.target.value)} 
                      placeholder="ערך" 
                    />
                    
                    <Button danger onClick={() => removeFilter(index)}>הסר</Button>
                  </Space>
                </div>
              ))}
            </Card>
            
            <Card title="מיון" size="small">
              <Space>
                <Select
                  style={{ width: 200 }}
                  placeholder="מיין לפי שדה"
                  value={sortConfig?.field || undefined}
                  onChange={(value) => setSortConfig({ ...sortConfig, field: value })}
                  allowClear
                >
                  {availableFields.map(field => (
                    <Option key={field} value={field}>{field}</Option>
                  ))}
                </Select>
                
                <Select
                  style={{ width: 120 }}
                  placeholder="כיוון"
                  value={sortConfig?.direction || undefined}
                  onChange={(value) => setSortConfig({ ...sortConfig, direction: value })}
                  disabled={!sortConfig?.field}
                  allowClear
                >
                  <Option value="asc">עולה</Option>
                  <Option value="desc">יורד</Option>
                </Select>
              </Space>
            </Card>
            
            <Card title="קיבוץ לפי" size="small">
              <Select
                style={{ width: '100%' }}
                placeholder="קבץ לפי שדה"
                value={groupByField}
                onChange={setGroupByField}
                allowClear
              >
                {availableFields.map(field => (
                  <Option key={field} value={field}>{field}</Option>
                ))}
              </Select>
            </Card>
            
            <Button 
              type="primary" 
              onClick={generateTable} 
              loading={loading}
              disabled={selectedFields.length === 0}
              style={{ marginTop: 16 }}
            >
              יצירת טבלה
            </Button>
          </div>
        </TabPane>
        
        <TabPane tab="שאילתה בשפה טבעית" key="nlq">
          <div className="nlq-interface">
            <Input.TextArea
              rows={4}
              value={naturalLanguageQuery}
              onChange={(e) => setNaturalLanguageQuery(e.target.value)}
              placeholder="הכנס שאילתה בשפה טבעית. לדוגמה: 'הצג לי את כל האג״ח עם תאריכי פדיון ב-2025 ותשואה מעל 3%, ממויינים לפי תשואה בסדר יורד'"
              dir="rtl"
            />
            
            <Button 
              type="primary" 
              onClick={generateFromNaturalLanguage} 
              loading={loading}
              disabled={!naturalLanguageQuery}
              style={{ marginTop: 16 }}
            >
              חפש
            </Button>
          </div>
        </TabPane>
      </Tabs>
      
      <div className="results-section" style={{ marginTop: 24 }}>
        <Card title="טבלה מותאמת אישית">
          {tableData.length > 0 ? (
            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    {columns.map((col) => (
                      <th key={col.key}>{col.title}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tableData.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {columns.map((col) => (
                        <td key={`${rowIndex}-${col.key}`}>{row[col.dataIndex]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-table-message">
              אין נתונים להצגה. בחר שדות ולחץ על "יצירת טבלה" או השתמש בשאילתה בשפה טבעית.
            </div>
          )}
        </Card>
      </div>
    </Card>
  );
};

export default CustomTableGenerator;
