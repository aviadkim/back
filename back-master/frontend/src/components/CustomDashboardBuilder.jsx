import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner, Tabs, Tab } from 'react-bootstrap';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import axios from 'axios';
import './CustomDashboardBuilder.css';

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
      filters: [],
      fields: []
    },
    config: {
      xAxis: '',
      yAxis: '',
      groupBy: ''
    }
  });
  const [isEditing, setIsEditing] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dashboardName, setDashboardName] = useState('New Dashboard');
  const [activeTabKey, setActiveTabKey] = useState('design');
  const [previewMode, setPreviewMode] = useState(false);

  useEffect(() => {
    // Load documents when component mounts
    fetchDocuments();
  }, []);

  useEffect(() => {
    // Update available fields when selected documents change
    if (selectedDocuments.length > 0) {
      fetchAvailableFields(selectedDocuments);
    } else {
      setAvailableFields([]);
    }
  }, [selectedDocuments]);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('/api/documents');

      // Filter for processed documents only
      const processedDocs = response.data.filter(doc => doc.processingStatus === 'completed');
      setDocuments(processedDocs);
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError('Failed to load documents. Please try again.');
    }
  };

  const fetchAvailableFields = async (documentIds) => {
    try {
      const response = await axios.post('/api/documents/fields', { documentIds });
      setAvailableFields(response.data.fields);
    } catch (error) {
      console.error('Error fetching fields:', error);
      setError('Failed to load document fields. Please try again.');
    }
  };

  const handleDocumentSelection = (e) => {
    const options = e.target.options;
    const selectedValues = [];

    for (let i = 0; i < options.length; i++) {
      if (options[i].selected) {
        selectedValues.push(options[i].value);
      }
    }

    setSelectedDocuments(selectedValues);

    // Update current widget's document selection
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

  const handleWidgetTypeChange = (e) => {
    setCurrentWidget(prev => ({
      ...prev,
      type: e.target.value
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

  const handleAddWidget = async () => {
    // Validate widget configuration
    if (!currentWidget.title) {
      setError('Widget title is required');
      return;
    }

    if (currentWidget.dataSource.documentIds.length === 0) {
      setError('Please select at least one document');
      return;
    }

    const requiredFields = currentWidget.type === 'table' ?
      ['fields'] : ['xAxis', 'yAxis'];

    for (const field of requiredFields) {
      if (!currentWidget.config[field]) {
        setError(`Please select a ${field.replace('Axis', ' axis')}`);
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      // Generate preview data
      const response = await axios.post('/api/dashboard/preview-widget', currentWidget);
      setPreviewData(response.data);

      // Add widget to dashboard
      const newWidget = {
        ...currentWidget,
        id: isEditing ? currentWidget.id : `widget-${Date.now()}`
      };

      if (isEditing) {
        // Update existing widget
        setWidgets(widgets.map(w => w.id === newWidget.id ? newWidget : w));
        setIsEditing(false);
      } else {
        // Add new widget
        setWidgets([...widgets, newWidget]);
      }

      // Reset current widget
      setCurrentWidget({
        id: '',
        title: '',
        type: 'bar',
        size: 'medium',
        dataSource: {
          documentIds: selectedDocuments,
          filters: [],
          fields: []
        },
        config: {
          xAxis: '',
          yAxis: '',
          groupBy: ''
        }
      });

      setLoading(false);
    } catch (error) {
      console.error('Error generating widget preview:', error);
      setError('Failed to generate widget. Please check your configuration.');
      setLoading(false);
    }
  };

  const handleEditWidget = (widget) => {
    setCurrentWidget(widget);
    setIsEditing(true);
    setSelectedDocuments(widget.dataSource.documentIds);
  };

  const handleRemoveWidget = (widgetId) => {
    setWidgets(widgets.filter(w => w.id !== widgetId));
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const reorderedWidgets = [...widgets];
    const [removed] = reorderedWidgets.splice(result.source.index, 1);
    reorderedWidgets.splice(result.destination.index, 0, removed);

    setWidgets(reorderedWidgets);
  };

  const handleSaveDashboard = async () => {
    if (!dashboardName) {
      setError('Dashboard name is required');
      return;
    }

    if (widgets.length === 0) {
      setError('Please add at least one widget to the dashboard');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const dashboardData = {
        name: dashboardName,
        widgets: widgets,
        createdAt: new Date().toISOString()
      };

      await axios.post('/api/dashboards', dashboardData);

      // Navigate to dashboards list or show success message
      setLoading(false);
      setActiveTabKey('preview');
      setPreviewMode(true);

    } catch (error) {
      console.error('Error saving dashboard:', error);
      setError('Failed to save dashboard. Please try again.');
      setLoading(false);
    }
  };

  const renderWidgetPreview = (widget) => {
    if (!widget || !widget.id) return null;

    // Find widget data in preview data
    const widgetData = previewData?.find(data => data.widgetId === widget.id);

    if (!widgetData || !widgetData.data) {
      return (
        <div className="widget-preview-placeholder">
          <span>No data available for preview</span>
        </div>
      );
    }

    switch (widget.type) {
      case 'bar':
        return (
          <Bar
            data={widgetData.data}
            options={widgetData.options || {
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  text: widget.title
                }
              }
            }}
          />
        );

      case 'line':
        return (
          <Line
            data={widgetData.data}
            options={widgetData.options || {
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  text: widget.title
                }
              }
            }}
          />
        );

      case 'pie':
        return (
          <Pie
            data={widgetData.data}
            options={widgetData.options || {
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  text: widget.title
                }
              }
            }}
          />
        );

      case 'doughnut':
        return (
          <Doughnut
            data={widgetData.data}
            options={widgetData.options || {
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  text: widget.title
                }
              }
            }}
          />
        );

      case 'table':
        return (
          <div className="table-responsive">
            <table className="table table-striped table-bordered">
              <thead>
                <tr>
                  {widgetData.data.headers.map((header, index) => (
                    <th key={index}>{header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {widgetData.data.rows.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.map((cell, cellIndex) => (
                      <td key={cellIndex}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );

      default:
        return (
          <div className="widget-preview-placeholder">
            <span>Unsupported widget type</span>
          </div>
        );
    }
  };

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
        <Col md={4}>
          <Card className="widget-config-card">
            <Card.Header>Widget Configuration</Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Widget Title</Form.Label>
                  <Form.Control
                    type="text"
                    value={currentWidget.title}
                    onChange={handleWidgetTitleChange}
                    placeholder="Enter widget title"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Widget Type</Form.Label>
                  <Form.Select
                    value={currentWidget.type}
                    onChange={handleWidgetTypeChange}
                  >
                    {chartTypes.map(type => (
                      <option key={type.id} value={type.id}>
                        {type.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Widget Size</Form.Label>
                  <Form.Select
                    value={currentWidget.size}
                    onChange={handleWidgetSizeChange}
                  >
                    {widgetSizes.map(size => (
                      <option key={size.id} value={size.id}>
                        {size.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Data Source</Form.Label>
                  <Form.Select
                    multiple
                    value={selectedDocuments}
                    onChange={handleDocumentSelection}
                    className="document-selector"
                  >
                    {documents.map(doc => (
                      <option key={doc._id} value={doc._id}>
                        {doc.originalFileName}
                      </option>
                    ))}
                  </Form.Select>
                  <Form.Text className="text-muted">
                    Hold Ctrl (Windows) or Cmd (Mac) to select multiple documents
                  </Form.Text>
                </Form.Group>

                {currentWidget.type !== 'table' && (
                  <>
                    <Form.Group className="mb-3">
                      <Form.Label>X-Axis</Form.Label>
                      <Form.Select
                        value={currentWidget.config.xAxis}
                        onChange={(e) => handleFieldSelection('xAxis', e)}
                      >
                        <option value="">Select X-Axis Field</option>
                        {availableFields.map(field => (
                          <option key={field.id} value={field.id}>
                            {field.name}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Y-Axis</Form.Label>
                      <Form.Select
                        value={currentWidget.config.yAxis}
                        onChange={(e) => handleFieldSelection('yAxis', e)}
                      >
                        <option value="">Select Y-Axis Field</option>
                        {availableFields.filter(f => f.type === 'numeric').map(field => (
                          <option key={field.id} value={field.id}>
                            {field.name}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Group By (Optional)</Form.Label>
                      <Form.Select
                        value={currentWidget.config.groupBy}
                        onChange={(e) => handleFieldSelection('groupBy', e)}
                      >
                        <option value="">No Grouping</option>
                        {availableFields.map(field => (
                          <option key={field.id} value={field.id}>
                            {field.name}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </>
                )}

                {currentWidget.type === 'table' && (
                  <Form.Group className="mb-3">
                    <Form.Label>Table Fields</Form.Label>
                    <Form.Select
                      multiple
                      value={currentWidget.dataSource.fields}
                      onChange={(e) => {
                        const options = e.target.options;
                        const selectedFields = [];

                        for (let i = 0; i < options.length; i++) {
                          if (options[i].selected) {
                            selectedFields.push(options[i].value);
                          }
                        }

                        setCurrentWidget(prev => ({
                          ...prev,
                          dataSource: {
                            ...prev.dataSource,
                            fields: selectedFields
                          }
                        }));
                      }}
                      className="field-selector"
                    >
                      {availableFields.map(field => (
                        <option key={field.id} value={field.id}>
                          {field.name}
                        </option>
                      ))}
                    </Form.Select>
                    <Form.Text className="text-muted">
                      Hold Ctrl (Windows) or Cmd (Mac) to select multiple fields
                    </Form.Text>
                  </Form.Group>
                )}

                <div className="d-grid gap-2">
                  <Button
                    variant="primary"
                    onClick={handleAddWidget}
                    disabled={loading}
                  >
                    {loading ? (
                      <Spinner animation="border" size="sm" />
                    ) : isEditing ? (
                      'Update Widget'
                    ) : (
                      'Add Widget'
                    )}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col md={8}>
          <Card className="dashboard-preview-card">
            <Card.Header>Dashboard Layout</Card.Header>
            <Card.Body>
              {error && (
                <Alert variant="danger" onClose={() => setError(null)} dismissible>
                  {error}
                </Alert>
              )}

              {widgets.length === 0 ? (
                <div className="empty-dashboard-message">
                  <p>Your dashboard is empty. Configure and add widgets using the form on the left.</p>
                </div>
              ) : (
                <DragDropContext onDragEnd={handleDragEnd}>
                  <Droppable droppableId="dashboard-widgets">
                    {(provided) => (
                      <div
                        className="dashboard-widgets-container"
                        {...provided.droppableProps}
                        ref={provided.innerRef}
                      >
                        <Row>
                          {widgets.map((widget, index) => (
                            <Draggable
                              key={widget.id}
                              draggableId={widget.id}
                              index={index}
                            >
                              {(provided) => (
                                <Col
                                  md={widgetSizes.find(s => s.id === widget.size)?.cols || 6}
                                  className="mb-4"
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                >
                                  <Card className="widget-card">
                                    <Card.Header
                                      className="d-flex justify-content-between align-items-center"
                                      {...provided.dragHandleProps}
                                    >
                                      <span>{widget.title}</span>
                                      <div className="widget-actions">
                                        <Button
                                          variant="outline-secondary"
                                          size="sm"
                                          onClick={() => handleEditWidget(widget)}
                                          className="me-2"
                                        >
                                          <i className="fas fa-edit"></i>
                                        </Button>
                                        <Button
                                          variant="outline-danger"
                                          size="sm"
                                          onClick={() => handleRemoveWidget(widget.id)}
                                        >
                                          <i className="fas fa-trash"></i>
                                        </Button>
                                      </div>
                                    </Card.Header>
                                    <Card.Body>
                                      <div className="widget-type-indicator">
                                        <i className={`fas fa-${chartTypes.find(t => t.id === widget.type)?.icon || 'chart-bar'}`}></i>
                                        <span>{chartTypes.find(t => t.id === widget.type)?.name || 'Widget'}</span>
                                      </div>
                                      {previewData && renderWidgetPreview(widget)}
                                    </Card.Body>
                                  </Card>
                                </Col>
                              )}
                            </Draggable>
                          ))}
                        </Row>
                        {provided.placeholder}
                      </div>
                    )}
                  </Droppable>
                </DragDropContext>
              )}

              {widgets.length > 0 && (
                <div className="dashboard-actions mt-4">
                  <Button
                    variant="success"
                    onClick={handleSaveDashboard}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Saving Dashboard...
                      </>
                    ) : (
                      'Save Dashboard'
                    )}
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
    <Container fluid className="dashboard-preview-container">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h2>{dashboardName}</h2>
            {previewMode && (
              <Button
                variant="outline-primary"
                onClick={() => {
                  setActiveTabKey('design');
                  setPreviewMode(false);
                }}
              >
                Edit Dashboard
              </Button>
            )}
          </div>
        </Col>
      </Row>

      <Row>
        {widgets.map((widget) => (
          <Col
            key={widget.id}
            md={widgetSizes.find(s => s.id === widget.size)?.cols || 6}
            className="mb-4"
          >
            <Card className="widget-card">
              <Card.Header>{widget.title}</Card.Header>
              <Card.Body>
                {previewData ? renderWidgetPreview(widget) : (
                  <div className="d-flex justify-content-center align-items-center" style={{ height: '200px' }}>
                    <Spinner animation="border" />
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );

  return (
    <div className="custom-dashboard-builder">
      <Tabs
        activeKey={activeTabKey}
        onSelect={(key) => setActiveTabKey(key)}
        className="mb-4"
      >
        <Tab eventKey="design" title="Design">
          {renderDesignTab()}
        </Tab>
        <Tab eventKey="preview" title="Preview">
          {renderPreviewTab()}
        </Tab>
      </Tabs>
    </div>
  );
};

export default CustomDashboardBuilder;