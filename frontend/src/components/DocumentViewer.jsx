// frontend/src/components/DocumentViewer.jsx
import React, { useState, useEffect } from 'react';
import { Tabs, Spin, Alert, Button } from 'antd';
import { FileTextOutlined, TableOutlined, LineChartOutlined, SettingOutlined } from '@ant-design/icons';
import CustomTableGenerator from './CustomTableGenerator';
import TableView from './TableView';

const { TabPane } = Tabs;

const DocumentViewer = ({ documentId }) => {
  const [loading, setLoading] = useState(true);
  const [document, setDocument] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Fetch document data when component mounts
  useEffect(() => {
    const fetchDocument = async () => {
      if (!documentId) return;
      
      setLoading(true);
      try {
        const response = await fetch(`/api/documents/${documentId}`);
        if (!response.ok) {
          throw new Error(`Error fetching document: ${response.statusText}`);
        }
        
        const data = await response.json();
        setDocument(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDocument();
  }, [documentId]);
  
  // If loading or error, show appropriate message
  if (loading) {
    return <Spin tip="Loading document..." />;
  }
  
  if (error) {
    return <Alert message="Error" description={error} type="error" />;
  }
  
  if (!document) {
    return <Alert message="No document selected" description="Please select or upload a document to view." type="info" />;
  }
  
  // Prepare table data for the tables tab
  const extractedTables = document.tables || {};
  const tableList = [];
  
  for (const pageNum in extractedTables) {
    extractedTables[pageNum].forEach((table, index) => {
      tableList.push({
        id: `page_${pageNum}_table_${index}`,
        pageNumber: parseInt(pageNum) + 1,
        tableIndex: index + 1,
        rowCount: table.row_count,
        colCount: table.col_count,
        tableData: table
      });
    });
  }
  
  return (
    <div className="document-viewer">
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane 
          tab={<span><FileTextOutlined /> Overview</span>} 
          key="overview"
        >
          <h2>{document.filename || 'Document Overview'}</h2>
          <p><strong>Pages:</strong> {document.pageCount}</p>
          <p><strong>Tables detected:</strong> {tableList.length}</p>
          {document.documentType && (
            <p><strong>Document type:</strong> {document.documentType}</p>
          )}
          {document.languageDetected && (
            <p><strong>Language detected:</strong> {document.languageDetected}</p>
          )}
          {document.processingTime && (
            <p><strong>Processing time:</strong> {document.processingTime} seconds</p>
          )}
        </TabPane>
        
        <TabPane 
          tab={<span><TableOutlined /> Extracted Tables</span>} 
          key="tables"
        >
          <h2>Extracted Tables</h2>
          {tableList.length > 0 ? (
            <TableView 
              columns={[
                { title: 'Page', dataIndex: 'pageNumber', key: 'pageNumber' },
                { title: 'Table', dataIndex: 'tableIndex', key: 'tableIndex' },
                { title: 'Rows', dataIndex: 'rowCount', key: 'rowCount' },
                { title: 'Columns', dataIndex: 'colCount', key: 'colCount' },
                {
                  title: 'Actions',
                  key: 'actions',
                  render: (_, record) => (
                    <Button 
                      type="primary" 
                      onClick={() => {
                        // View table detail logic
                      }}
                    >
                      View
                    </Button>
                  ),
                },
              ]}
              dataSource={tableList}
              title="Extracted Tables"
            />
          ) : (
            <Alert message="No tables found in this document" type="info" />
          )}
        </TabPane>
        
        <TabPane 
          tab={<span><SettingOutlined /> Custom Tables</span>} 
          key="custom"
        >
          <CustomTableGenerator documentId={documentId} />
        </TabPane>
      </Tabs>
    </div>
  );
};

export default DocumentViewer;