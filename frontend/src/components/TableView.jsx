// frontend/src/components/TableView.jsx
import React, { useState } from 'react';
import { Table, Button, Input, Space } from 'antd';
import { SearchOutlined, DownloadOutlined } from '@ant-design/icons';
import * as XLSX from 'xlsx';

const TableView = ({ columns, dataSource, title }) => {
  const [searchText, setSearchText] = useState('');
  const [searchedColumn, setSearchedColumn] = useState('');
  
  // Handle search functionality
  const handleSearch = (selectedKeys, confirm, dataIndex) => {
    confirm();
    setSearchText(selectedKeys[0]);
    setSearchedColumn(dataIndex);
  };

  const handleReset = clearFilters => {
    clearFilters();
    setSearchText('');
  };
  
  // Configure search functionality for columns
  const getColumnSearchProps = dataIndex => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
      <div style={{ padding: 8 }}>
        <Input
          placeholder={`Search ${dataIndex}`}
          value={selectedKeys[0]}
          onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => handleSearch(selectedKeys, confirm, dataIndex)}
          style={{ width: 188, marginBottom: 8, display: 'block' }}
        />
        <Space>
          <Button
            type="primary"
            onClick={() => handleSearch(selectedKeys, confirm, dataIndex)}
            icon={<SearchOutlined />}
            size="small"
            style={{ width: 90 }}
          >
            Search
          </Button>
          <Button onClick={() => handleReset(clearFilters)} size="small" style={{ width: 90 }}>
            Reset
          </Button>
        </Space>
      </div>
    ),
    filterIcon: filtered => <SearchOutlined style={{ color: filtered ? '#1890ff' : undefined }} />,
    onFilter: (value, record) =>
      record[dataIndex]
        ? record[dataIndex].toString().toLowerCase().includes(value.toLowerCase())
        : '',
  });
  
  // Add search props to each column
  const enhancedColumns = columns.map(col => ({
    ...col,
    ...getColumnSearchProps(col.dataIndex),
  }));
  
  // Export table data to Excel
  const exportToExcel = () => {
    const worksheet = XLSX.utils.json_to_sheet(dataSource);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "TableData");
    
    // Generate filename
    const fileName = title ? 
      `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${new Date().toISOString().slice(0,10)}.xlsx` : 
      `table_export_${new Date().toISOString().slice(0,10)}.xlsx`;
    
    XLSX.writeFile(workbook, fileName);
  };
  
  return (
    <div className="table-view">
      <div className="table-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        {title && <h3>{title}</h3>}
        <Button 
          type="primary" 
          icon={<DownloadOutlined />} 
          onClick={exportToExcel}
          disabled={!dataSource || dataSource.length === 0}
        >
          Export to Excel
        </Button>
      </div>
      
      <Table 
        columns={enhancedColumns} 
        dataSource={dataSource}
        rowKey={(record, index) => index}
        pagination={{ 
          pageSize: 10, 
          showSizeChanger: true, 
          pageSizeOptions: ['10', '20', '50', '100']
        }}
        scroll={{ x: 'max-content' }}
      />
    </div>
  );
};

export default TableView;