import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner, Tabs, Tab, ListGroup, Badge } from 'react-bootstrap';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Table } from 'react-bootstrap'; // Moved import to top
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import axios from 'axios';
import './CustomDashboardBuilder.css'; // Assuming this CSS file exists

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);


const chartTypes = [
  { id: 'bar', name: 'Bar Chart', icon: 'chart-bar' },
  { id: 'line', name: 'Line Chart', icon: 'chart-line' },
  { id: 'pie', name: 'Pie Chart', icon: 'chart-pie' },
  { id: 'doughnut', name: 'Doughnut Chart', icon: 'circle' },
  { id: 'table', name: 'Table', icon: 'table' }
];

const widgetSizes = [
  { id: 'small', name: 'Small', cols: 4 },
  { id: 'medium', name: 'Medium', cols: 6 },
  { id: 'large', name: 'Large', cols: 12 }
];

// Helper function to generate unique IDs
const generateId = () => `widget-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

const CustomDashboardBuilder = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [availableFields, setAvailableFields] = useState([]);
  const [widgets, setWidgets] = useState([]);
  const [currentWidget, setCurrentWidget] = useState({
    id: '',
    title: '',
    type: 'bar',
    size: 'medium',
    dataSource: {
      documentIds: [],
      filters: [], // Placeholder for future filter implementation
      fields: [] // Used for table type
    },
    config: {
      xAxis: '',
      yAxis: '',
      groupBy: '' // Optional grouping field
    }
  });
  const [isEditing, setIsEditing] = useState(false);
  const [previewData, setPreviewData] = useState({}); // Store preview data per widget ID
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dashboardName, setDashboardName] = useState('New Dashboard');
  const [activeTabKey, setActiveTabKey] = useState('design');
  const [previewMode, setPreviewMode] = useState(false); // Controls if preview tab shows saved state or live preview
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [loadingFields, setLoadingFields] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [loadingSave, setLoadingSave] = useState(false);


  // Fetch documents on mount
  const fetchDocuments = useCallback(async () => {
    setLoadingDocuments(true);
    setError(null);
    try {
      // TODO: Replace with actual API endpoint
      // const response = await axios.get('/api/documents');
      // Mock data for now
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
      const response = {
          data: [
              { _id: 'doc1', originalFileName: 'Report_Q1_2024.pdf', processingStatus: 'completed' },
              { _id: 'doc2', originalFileName: 'Financial_Statement_2023.pdf', processingStatus: 'completed' },
              { _id: 'doc3', originalFileName: 'Investment_Summary.pdf', processingStatus: 'pending' },
              { _id: 'doc4', originalFileName: 'Analysis_Market_Trends.pdf', processingStatus: 'completed' },
          ]
      };

      const processedDocs = response.data.filter(doc => doc.processingStatus === 'completed');
      setDocuments(processedDocs);
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError('Failed to load documents. Please try again.');
    } finally {
      setLoadingDocuments(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Fetch available fields when selected documents change
  const fetchAvailableFields = useCallback(async (documentIds) => {
    if (!documentIds || documentIds.length === 0) {
      setAvailableFields([]);
      return;
    }
    setLoadingFields(true);
    setError(null);
    try {
      // TODO: Replace with actual API endpoint
      // const response = await axios.post('/api/documents/fields', { documentIds });
      // Mock data based on selected docs
      await new Promise(resolve => setTimeout(resolve, 300)); // Simulate network delay
      let fields = [
          { id: 'field_date', name: 'Date', type: 'date' },
          { id: 'field_category', name: 'Category', type: 'text' },
          { id: 'field_amount', name: 'Amount', type: 'numeric' },
          { id: 'field_isin', name: 'ISIN', type: 'text' },
      ];
      if (documentIds.includes('doc2')) {
          fields.push({ id: 'field_balance', name: 'Balance', type: 'numeric' });
          fields.push({ id: 'field_currency', name: 'Currency', type: 'text' });
      }
       if (documentIds.includes('doc4')) {
          fields.push({ id: 'field_trend', name: 'Trend Score', type: 'numeric' });
          fields.push({ id: 'field_sector', name: 'Sector', type: 'text' });
      }
      // Remove duplicates just in case
      const uniqueFields = Array.from(new Map(fields.map(item => [item.id, item])).values());
      setAvailableFields(uniqueFields);

    } catch (error) {
      console.error('Error fetching fields:', error);
      setError('Failed to load document fields. Please try again.');
      setAvailableFields([]); // Clear fields on error
    } finally {
      setLoadingFields(false);
    }
  }, []);

  useEffect(() => {
    fetchAvailableFields(selectedDocuments);
  }, [selectedDocuments, fetchAvailableFields]);

  // Reset current widget form
  const resetCurrentWidget = useCallback(() => {
      setCurrentWidget({
        id: '',
        title: '',
        type: 'bar',
        size: 'medium',
        dataSource: {
          documentIds: selectedDocuments, // Keep selected docs
          filters: [],
          fields: []
        },
        config: {
          xAxis: '',
          yAxis: '',
          groupBy: ''
        }
      });
      setIsEditing(false);
      // Don't clear preview data here, it's per widget
  }, [selectedDocuments]);

  const handleDocumentSelection = (e) => {
    const selectedValues = Array.from(e.target.selectedOptions, option => option.value);
    setSelectedDocuments(selectedValues);

    // Update current widget's document selection immediately
    setCurrentWidget(prev => ({
      ...prev,
      dataSource: {
        ...prev.dataSource,
        documentIds: selectedValues
      }
    }));
  };

  const handleFieldSelection = (fieldType, e) => {
    const fieldId = e.target.value;
    setCurrentWidget(prev => ({
      ...prev,
      config: {
        ...prev.config,
        [fieldType]: fieldId
      }
    }));
  };

   const handleTableFieldSelection = (e) => {
        const selectedFields = Array.from(e.target.selectedOptions, option => option.value);
        setCurrentWidget(prev => ({
          ...prev,
          dataSource: {
            ...prev.dataSource,
            fields: selectedFields
          }
        }));
      };

  const handleWidgetTypeChange = (e) => {
    setCurrentWidget(prev => ({
      ...prev,
      type: e.target.value,
      // Reset config fields that might not apply to the new type
      config: {
          xAxis: prev.type === 'table' ? '' : prev.config.xAxis, // Keep if switching from non-table
          yAxis: prev.type === 'table' ? '' : prev.config.yAxis,
          groupBy: prev.type === 'table' ? '' : prev.config.groupBy,
      },
      dataSource: {
          ...prev.dataSource,
          fields: prev.type !== 'table' ? [] : prev.dataSource.fields // Keep if switching from table
      }
    }));
  };

  const handleWidgetSizeChange = (e) => {
    setCurrentWidget(prev => ({
      ...prev,
      size: e.target.value
    }));
  };

  const handleWidgetTitleChange = (e) => {
    setCurrentWidget(prev => ({
      ...prev,
      title: e.target.value
    }));
  };

  // Function to generate preview for the *current* widget config
  const generateCurrentWidgetPreview = async () => {
      // Basic validation before preview
      if (!currentWidget.title) { setError('Widget title is required for preview'); return; }
      if (currentWidget.dataSource.documentIds.length === 0) { setError('Please select at least one document'); return; }
      if (currentWidget.type !== 'table' && (!currentWidget.config.xAxis || !currentWidget.config.yAxis)) { setError('X-Axis and Y-Axis fields are required for chart preview'); return; }
      if (currentWidget.type === 'table' && currentWidget.dataSource.fields.length === 0) { setError('Please select fields for table preview'); return; }

      setLoadingPreview(true);
      setError(null);
      const tempWidgetId = currentWidget.id || 'preview-widget'; // Use existing ID or a temp one

      try {
          // TODO: Replace with actual API endpoint
          // const response = await axios.post('/api/dashboard/preview-widget', { ...currentWidget, id: tempWidgetId });

          // Mock preview data generation
          await new Promise(resolve => setTimeout(resolve, 700)); // Simulate network delay
          const mockPreview = generateMockWidgetData(currentWidget, tempWidgetId);

          setPreviewData(prev => ({
              ...prev,
              [tempWidgetId]: mockPreview // Store preview data by widget ID
          }));

      } catch (error) {
          console.error('Error generating widget preview:', error);
          setError('Failed to generate widget preview. Please check configuration.');
          setPreviewData(prev => ({ ...prev, [tempWidgetId]: null })); // Clear preview on error
      } finally {
          setLoadingPreview(false);
      }
  };

  // Mock data generation function
  const generateMockWidgetData = (widgetConfig, widgetId) => {
      const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
      const data = labels.map(() => Math.floor(Math.random() * 100));
      const data2 = labels.map(() => Math.floor(Math.random() * 80));

      const commonOptions = {
          responsive: true,
          maintainAspectRatio: false, // Allow chart to fill container
          plugins: {
              legend: { position: 'top' },
              title: { display: true, text: widgetConfig.title },
          },
      };

      switch (widgetConfig.type) {
          case 'bar':
          case 'line':
              return {
                  widgetId: widgetId,
                  data: {
                      labels,
                      datasets: [
                          { label: widgetConfig.config.yAxis || 'Dataset 1', data, backgroundColor: 'rgba(75, 192, 192, 0.6)' },
                          ...(widgetConfig.config.groupBy ? [{ label: widgetConfig.config.groupBy || 'Dataset 2', data: data2, backgroundColor: 'rgba(255, 99, 132, 0.6)' }] : [])
                      ],
                  },
                  options: commonOptions
              };
          case 'pie':
          case 'doughnut':
              return {
                  widgetId: widgetId,
                  data: {
                      labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple'],
                      datasets: [{ data: [12, 19, 3, 5, 2], backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'] }],
                  },
                  options: commonOptions
              };
          case 'table':
              const headers = widgetConfig.dataSource.fields.map(fieldId => availableFields.find(f => f.id === fieldId)?.name || fieldId);
              const rows = Array.from({ length: 5 }, (_, i) =>
                  headers.map(header => `${header} Data ${i + 1}`)
              );
              return {
                  widgetId: widgetId,
                  data: { headers, rows },
                  options: {} // No specific options for table rendering here
              };
          default:
              return { widgetId: widgetId, data: null, options: {} };
      }
  };


  const handleAddOrUpdateWidget = async () => {
    // Validation (similar to preview validation)
    if (!currentWidget.title) { setError('Widget title is required'); return; }
    if (currentWidget.dataSource.documentIds.length === 0) { setError('Please select at least one document'); return; }
    if (currentWidget.type !== 'table' && (!currentWidget.config.xAxis || !currentWidget.config.yAxis)) { setError('X-Axis and Y-Axis fields are required'); return; }
    if (currentWidget.type === 'table' && currentWidget.dataSource.fields.length === 0) { setError('Please select fields for the table'); return; }

    setError(null);

    const widgetToSave = {
      ...currentWidget,
      id: isEditing ? currentWidget.id : generateId() // Assign new ID if not editing
    };

    // Optimistically update UI or wait for preview? Let's update UI first.
    if (isEditing) {
      setWidgets(widgets.map(w => w.id === widgetToSave.id ? widgetToSave : w));
    } else {
      setWidgets([...widgets, widgetToSave]);
    }

    // Generate preview for the newly added/updated widget
    setLoadingPreview(true);
     try {
          // const response = await axios.post('/api/dashboard/preview-widget', widgetToSave);
          await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
          const mockPreview = generateMockWidgetData(widgetToSave, widgetToSave.id);
          setPreviewData(prev => ({ ...prev, [widgetToSave.id]: mockPreview }));
     } catch (error) {
         console.error('Error generating preview after add/update:', error);
         // Keep the widget in the list, but maybe show a preview error?
         setPreviewData(prev => ({ ...prev, [widgetToSave.id]: { error: 'Preview failed' } }));
     } finally {
         setLoadingPreview(false);
     }


    resetCurrentWidget(); // Clear the form
  };

  const handleEditWidget = (widget) => {
    setCurrentWidget(widget);
    setIsEditing(true);
    setSelectedDocuments(widget.dataSource.documentIds); // Sync selected docs
    // Fetch fields again in case context changed, handled by useEffect
  };

  const handleCancelEdit = () => {
      resetCurrentWidget();
  };

  const handleRemoveWidget = (widgetId) => {
    setWidgets(widgets.filter(w => w.id !== widgetId));
    // Remove preview data for the deleted widget
    setPreviewData(prev => {
        const { [widgetId]: _, ...rest } = prev;
        return rest;
    });
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const reorderedWidgets = [...widgets];
    const [removed] = reorderedWidgets.splice(result.source.index, 1);
    reorderedWidgets.splice(result.destination.index, 0, removed);

    setWidgets(reorderedWidgets);
  };

  const handleSaveDashboard = async () => {
    if (!dashboardName.trim()) { setError('Dashboard name is required'); return; }
    if (widgets.length === 0) { setError('Please add at least one widget'); return; }

    setLoadingSave(true);
    setError(null);

    try {
      const dashboardData = {
        name: dashboardName,
        widgets: widgets,
        // Add layout information if needed, e.g., widget order
        layout: widgets.map(w => w.id),
        createdAt: new Date().toISOString()
      };

      // TODO: Replace with actual API endpoint
      // await axios.post('/api/dashboards', dashboardData);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate save
      console.log('Dashboard saved:', dashboardData);


      // Switch to preview tab to show the saved state
      setActiveTabKey('preview');
      setPreviewMode(true); // Indicate this is the saved state

    } catch (error) {
      console.error('Error saving dashboard:', error);
      setError('Failed to save dashboard. Please try again.');
    } finally {
      setLoadingSave(false);
    }
  };

  // Render a single widget based on its config and preview data
  const renderWidget = (widget) => {
      const widgetPreview = previewData[widget.id];

      if (loadingPreview && currentWidget.id === widget.id) {
          return <div className="d-flex justify-content-center align-items-center h-100"><Spinner animation="border" size="sm" /></div>;
      }

      if (!widgetPreview || widgetPreview.error) {
          return <div className="widget-preview-placeholder text-danger">{widgetPreview?.error || 'Preview not available'}</div>;
      }
      if (!widgetPreview.data) {
           return <div className="widget-preview-placeholder">No data for preview</div>;
      }

      const chartOptions = { ...(widgetPreview.options || {}), maintainAspectRatio: false };

      switch (widget.type) {
          case 'bar': return <Bar data={widgetPreview.data} options={chartOptions} />;
          case 'line': return <Line data={widgetPreview.data} options={chartOptions} />;
          case 'pie': return <Pie data={widgetPreview.data} options={chartOptions} />;
          case 'doughnut': return <Doughnut data={widgetPreview.data} options={chartOptions} />;
          case 'table':
              if (!widgetPreview.data.headers || !widgetPreview.data.rows) {
                  return <div className="widget-preview-placeholder text-danger">Invalid table data format</div>;
              }
              return (
                  <div className="table-responsive widget-table-container">
                      <Table striped bordered hover size="sm">
                          <thead>
                              <tr>{widgetPreview.data.headers.map((h, i) => <th key={i}>{h}</th>)}</tr>
                          </thead>
                          <tbody>
                              {widgetPreview.data.rows.map((row, i) => (
                                  <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>
                              ))}
                          </tbody>
                      </Table>
                  </div>
              );
          default: return <div className="widget-preview-placeholder">Unsupported type</div>;
      }
  };


  // --- Render Functions for Tabs ---

  const renderDesignTab = () => (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <Form.Group>
            <Form.Label>Dashboard Name</Form.Label>
            <Form.Control
              type="text"
              value={dashboardName}
              onChange={(e) => setDashboardName(e.target.value)}
              placeholder="Enter dashboard name"
            />
          </Form.Group>
        </Col>
      </Row>

      <Row>
        {/* Configuration Column */}
        <Col md={4}>
          <Card className="widget-config-card shadow-sm mb-4">
            <Card.Header as="h5">{isEditing ? 'Edit Widget' : 'Configure New Widget'}</Card.Header>
            <Card.Body>
              <Form>
                {/* Widget Title */}
                <Form.Group className="mb-3">
                  <Form.Label>Widget Title</Form.Label>
                  <Form.Control type="text" value={currentWidget.title} onChange={handleWidgetTitleChange} placeholder="Enter widget title" />
                </Form.Group>

                {/* Widget Type */}
                <Form.Group className="mb-3">
                  <Form.Label>Widget Type</Form.Label>
                  <Form.Select value={currentWidget.type} onChange={handleWidgetTypeChange}>
                    {chartTypes.map(type => <option key={type.id} value={type.id}>{type.name}</option>)}
                  </Form.Select>
                </Form.Group>

                {/* Widget Size */}
                <Form.Group className="mb-3">
                  <Form.Label>Widget Size</Form.Label>
                  <Form.Select value={currentWidget.size} onChange={handleWidgetSizeChange}>
                    {widgetSizes.map(size => <option key={size.id} value={size.id}>{size.name}</option>)}
                  </Form.Select>
                </Form.Group>

                {/* Data Source (Documents) */}
                <Form.Group className="mb-3">
                  <Form.Label>Data Source (Documents)</Form.Label>
                  {loadingDocuments ? <Spinner animation="border" size="sm" /> : (
                    <Form.Select multiple value={selectedDocuments} onChange={handleDocumentSelection} style={{ height: '100px' }}>
                      {documents.map(doc => <option key={doc._id} value={doc._id}>{doc.originalFileName}</option>)}
                    </Form.Select>
                  )}
                  <Form.Text className="text-muted">Hold Ctrl/Cmd to select multiple.</Form.Text>
                </Form.Group>

                {/* Fields Configuration */}
                {loadingFields ? <Spinner animation="border" size="sm" /> : availableFields.length > 0 && (
                  <>
                    {currentWidget.type !== 'table' && (
                      <>
                        <Form.Group className="mb-3">
                          <Form.Label>X-Axis</Form.Label>
                          <Form.Select value={currentWidget.config.xAxis} onChange={(e) => handleFieldSelection('xAxis', e)}>
                            <option value="">Select Field</option>
                            {availableFields.map(f => <option key={f.id} value={f.id}>{f.name} ({f.type})</option>)}
                          </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                          <Form.Label>Y-Axis</Form.Label>
                          <Form.Select value={currentWidget.config.yAxis} onChange={(e) => handleFieldSelection('yAxis', e)}>
                            <option value="">Select Field</option>
                            {availableFields.filter(f => f.type === 'numeric').map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
                          </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                          <Form.Label>Group By (Optional)</Form.Label>
                          <Form.Select value={currentWidget.config.groupBy} onChange={(e) => handleFieldSelection('groupBy', e)}>
                            <option value="">No Grouping</option>
                            {availableFields.map(f => <option key={f.id} value={f.id}>{f.name} ({f.type})</option>)}
                          </Form.Select>
                        </Form.Group>
                      </>
                    )}
                    {currentWidget.type === 'table' && (
                      <Form.Group className="mb-3">
                        <Form.Label>Table Fields</Form.Label>
                        <Form.Select multiple value={currentWidget.dataSource.fields} onChange={handleTableFieldSelection} style={{ height: '100px' }}>
                          {availableFields.map(f => <option key={f.id} value={f.id}>{f.name} ({f.type})</option>)}
                        </Form.Select>
                         <Form.Text className="text-muted">Hold Ctrl/Cmd to select multiple.</Form.Text>
                      </Form.Group>
                    )}
                  </>
                )}
                 {availableFields.length === 0 && selectedDocuments.length > 0 && !loadingFields && (
                     <Alert variant="warning" size="sm">No fields available for the selected document(s).</Alert>
                 )}


                {/* Action Buttons */}
                <div className="d-flex justify-content-between mt-4">
                   <Button variant="secondary" onClick={generateCurrentWidgetPreview} disabled={loadingPreview || loadingFields}>
                       {loadingPreview ? <Spinner animation="border" size="sm" /> : 'Preview Widget'}
                   </Button>
                   <div className="d-flex gap-2">
                       {isEditing && <Button variant="outline-secondary" size="sm" onClick={handleCancelEdit}>Cancel Edit</Button>}
                       <Button variant="primary" onClick={handleAddOrUpdateWidget} disabled={loadingPreview || loadingFields}>
                           {isEditing ? 'Update Widget' : 'Add Widget'}
                       </Button>
                   </div>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        {/* Dashboard Layout Column */}
        <Col md={8}>
          <Card className="dashboard-preview-card shadow-sm">
            <Card.Header as="h5">Dashboard Layout</Card.Header>
            <Card.Body>
              {error && <Alert variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}

              {widgets.length === 0 ? (
                <div className="empty-dashboard-message text-center text-muted py-5">
                  <i className="fas fa-plus-circle fa-3x mb-3"></i>
                  <p>Your dashboard is empty.<br />Configure and add widgets using the form on the left.</p>
                </div>
              ) : (
                <DragDropContext onDragEnd={handleDragEnd}>
                  <Droppable droppableId="dashboard-widgets">
                    {(provided) => (
                      <div className="dashboard-widgets-container" {...provided.droppableProps} ref={provided.innerRef}>
                        <Row>
                          {widgets.map((widget, index) => (
                            <Draggable key={widget.id} draggableId={widget.id} index={index}>
                              {(provided) => (
                                <Col md={widgetSizes.find(s => s.id === widget.size)?.cols || 6} className="mb-4" ref={provided.innerRef} {...provided.draggableProps}>
                                  <Card className="widget-card h-100 shadow-sm">
                                    <Card.Header className="d-flex justify-content-between align-items-center widget-header" {...provided.dragHandleProps}>
                                      <span className="fw-bold">{widget.title}</span>
                                      <div className="widget-actions">
                                        <Button variant="outline-primary" size="sm" onClick={() => handleEditWidget(widget)} className="me-1 py-0 px-1"><i className="fas fa-edit fa-xs"></i></Button>
                                        <Button variant="outline-danger" size="sm" onClick={() => handleRemoveWidget(widget.id)} className="py-0 px-1"><i className="fas fa-trash fa-xs"></i></Button>
                                      </div>
                                    </Card.Header>
                                    <Card.Body className="widget-body">
                                      {/* Render actual widget content/preview */}
                                      {renderWidget(widget)}
                                    </Card.Body>
                                     <Card.Footer className="text-muted small widget-footer">
                                         Type: {chartTypes.find(t => t.id === widget.type)?.name || 'N/A'} | Size: {widgetSizes.find(s => s.id === widget.size)?.name || 'N/A'}
                                     </Card.Footer>
                                  </Card>
                                </Col>
                              )}
                            </Draggable>
                          ))}
                          {provided.placeholder}
                        </Row>
                      </div>
                    )}
                  </Droppable>
                </DragDropContext>
              )}

              {widgets.length > 0 && (
                <div className="dashboard-actions text-end mt-4">
                  <Button variant="success" onClick={handleSaveDashboard} disabled={loadingSave}>
                    {loadingSave ? <><Spinner animation="border" size="sm" className="me-2" />Saving...</> : 'Save Dashboard'}
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );

  const renderPreviewTab = () => (
    <Container fluid className="dashboard-preview-container mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h2>{dashboardName} <Badge bg="info" pill>{previewMode ? 'Saved View' : 'Live Preview'}</Badge></h2>
            {previewMode && (
              <Button variant="outline-primary" onClick={() => { setActiveTabKey('design'); setPreviewMode(false); }}>
                <i className="fas fa-edit me-2"></i>Edit Dashboard
              </Button>
            )}
             {!previewMode && widgets.length > 0 && (
                 <Button variant="success" onClick={handleSaveDashboard} disabled={loadingSave}>
                    {loadingSave ? <><Spinner animation="border" size="sm" className="me-2" />Saving...</> : 'Save Dashboard'}
                 </Button>
             )}
          </div>
           {widgets.length === 0 && (
               <Alert variant="info">This dashboard has no widgets yet. Go to the 'Design' tab to add some.</Alert>
           )}
        </Col>
      </Row>

      <Row>
        {widgets.map((widget) => (
          <Col key={widget.id} md={widgetSizes.find(s => s.id === widget.size)?.cols || 6} className="mb-4">
            <Card className="widget-card h-100 shadow-sm">
              <Card.Header className="fw-bold">{widget.title}</Card.Header>
              <Card.Body className="widget-body">
                {/* Render widget based on preview data */}
                {renderWidget(widget)}
              </Card.Body>
               <Card.Footer className="text-muted small widget-footer">
                   Type: {chartTypes.find(t => t.id === widget.type)?.name || 'N/A'}
               </Card.Footer>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );

  // --- Main Component Return ---

  return (
    <div className="custom-dashboard-builder p-3">
      <Tabs activeKey={activeTabKey} onSelect={(k) => setActiveTabKey(k)} id="dashboard-tabs" className="mb-3" fill>
        <Tab eventKey="design" title={<><i className="fas fa-drafting-compass me-2"></i>Design</>}>
          {renderDesignTab()}
        </Tab>
        <Tab eventKey="preview" title={<><i className="fas fa-eye me-2"></i>Preview</>} disabled={widgets.length === 0 && !previewMode}>
          {renderPreviewTab()}
        </Tab>
      </Tabs>
    </div>
  );
};

export default CustomDashboardBuilder;