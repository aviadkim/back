import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner, ListGroup, Table } from 'react-bootstrap'; // Added Table
import axios from 'axios';
import './NaturalLanguageQueryInterface.css'; // Assuming this CSS file exists

const NaturalLanguageQueryInterface = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [query, setQuery] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [suggestions, setSuggestions] = useState([
    'מה סה"כ ערך התיק?',
    'הצג את כל ניירות הערך מסוג אג"ח',
    'מהם 5 ההשקעות הגדולות ביותר?',
    'איזה ניירות ערך מגיעים לפדיון בשנה הקרובה?',
    'כמה מניות יש בתיק?'
  ]);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    // Scroll to bottom of messages
    scrollToBottom();
  }, [conversation]);

  const fetchDocuments = async () => {
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
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleDocumentChange = (e) => {
    const docId = e.target.value;

    if (selectedDocuments.includes(docId)) {
      setSelectedDocuments(selectedDocuments.filter(id => id !== docId));
    } else {
      setSelectedDocuments([...selectedDocuments, docId]);
    }
  };

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    if (selectedDocuments.length === 0) {
      setError('Please select at least one document');
      return;
    }

    setLoading(true);
    setError(null);

    // Add user query to conversation
    const userMessage = {
      type: 'user',
      content: query,
      timestamp: new Date().toISOString()
    };

    // Update conversation state immediately with user message
    setConversation(prevConversation => [...prevConversation, userMessage]);
    const currentQuery = query; // Store query before clearing
    setQuery(''); // Clear input field

    try {
      // TODO: Replace with actual API endpoint
      // const response = await axios.post('/api/query', {
      //   query: currentQuery,
      //   documentIds: selectedDocuments
      // });

      // Mock response
      await new Promise(resolve => setTimeout(resolve, 1200)); // Simulate network delay
      let responseData = { answer: `Processed query: "${currentQuery}" for documents: ${selectedDocuments.join(', ')}`, data: null };
      if (currentQuery.toLowerCase().includes('table') || currentQuery.toLowerCase().includes('list')) {
          responseData.data = {
              type: 'table',
              headers: ['Col A', 'Col B', 'Col C'],
              rows: [['Data 1A', 'Data 1B', 100], ['Data 2A', 'Data 2B', 250]]
          };
      } else if (currentQuery.toLowerCase().includes('value')) {
           responseData.answer = 'The total value is $1,234,567.89.';
      }


      // Add system response to conversation
      const systemResponse = {
        type: 'system',
        content: responseData.answer,
        data: responseData.data || null,
        timestamp: new Date().toISOString()
      };

      // Update conversation state with system response
      setConversation(prevConversation => [...prevConversation, systemResponse]);

    } catch (error) {
      console.error('Error submitting query:', error);

      // Add error response to conversation
      const errorResponse = {
        type: 'system',
        content: 'Sorry, I was unable to process your query. Please try again.',
        isError: true,
        timestamp: new Date().toISOString()
      };

      // Update conversation state with error response
      setConversation(prevConversation => [...prevConversation, errorResponse]);
      setError('Failed to process query. Please try again.'); // Keep error message in footer too
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    // Optionally submit immediately? Or just fill the input? Let's just fill.
  };

  const renderMessage = (message, index) => {
    const isUser = message.type === 'user';

    return (
      <div
        key={index}
        className={`message ${isUser ? 'user-message' : 'system-message'} ${message.isError ? 'error-message' : ''}`}
      >
        <div className="message-header">
          <span className="message-sender">{isUser ? 'You' : 'Assistant'}</span>
          <span className="message-time">
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        <div className="message-content">
          {message.content}

          {/* Render data if present (e.g., table, list) */}
          {!isUser && message.data && (
            <div className="message-data mt-2">
              {message.data.type === 'table' && message.data.headers && message.data.rows && (
                <div className="table-responsive">
                  <Table striped bordered hover size="sm">
                    <thead>
                      <tr>{message.data.headers.map((h, i) => <th key={i}>{h}</th>)}</tr>
                    </thead>
                    <tbody>
                      {message.data.rows.map((row, i) => (
                        <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              )}

              {message.data.type === 'list' && message.data.items && (
                <ListGroup variant="flush" className="mt-2">
                  {message.data.items.map((item, i) => (
                    <ListGroup.Item key={i} className="py-1">{item}</ListGroup.Item>
                  ))}
                </ListGroup>
              )}
              {/* Add rendering for other data types (charts?) here */}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <Container fluid className="natural-language-query-interface p-3">
      <Row>
        {/* Document Selection & Suggestions Column */}
        <Col md={3}>
          <Card className="documents-card shadow-sm mb-3">
            <Card.Header as="h5">Select Documents</Card.Header>
            <Card.Body style={{ maxHeight: '30vh', overflowY: 'auto' }}>
              {documents.length === 0 ? (
                <Alert variant="info" size="sm">No processed documents available.</Alert>
              ) : (
                <Form>
                  {documents.map(doc => (
                    <Form.Check
                      key={doc._id}
                      type="checkbox"
                      id={`doc-check-${doc._id}`}
                      label={doc.originalFileName}
                      value={doc._id}
                      checked={selectedDocuments.includes(doc._id)}
                      onChange={handleDocumentChange}
                      className="mb-2 text-truncate"
                      title={doc.originalFileName} // Show full name on hover
                    />
                  ))}
                </Form>
              )}
            </Card.Body>
          </Card>

          <Card className="suggestions-card shadow-sm">
            <Card.Header as="h5">Suggestions</Card.Header>
            <Card.Body style={{ maxHeight: 'calc(60vh - 180px)', overflowY: 'auto' }}>
              <ListGroup variant="flush">
                {suggestions.map((suggestion, index) => (
                  <ListGroup.Item
                    key={index}
                    action
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="suggestion-item py-1"
                  >
                    {suggestion}
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card.Body>
          </Card>
        </Col>

        {/* Conversation Column */}
        <Col md={9}>
          <Card className="conversation-card shadow-sm" style={{ height: 'calc(90vh - 50px)' }}>
            <Card.Header as="h5">Financial Document Assistant</Card.Header>
            <Card.Body className="conversation-container d-flex flex-column">
              <div className="messages-area flex-grow-1">
                {conversation.length === 0 ? (
                  <div className="empty-conversation text-center text-muted p-5">
                    <i className="fas fa-comments fa-3x mb-3"></i>
                    <p>Select documents and ask questions about their content.</p>
                    <p>Examples: "What is the total portfolio value?" or "List all ISINs found."</p>
                  </div>
                ) : (
                  conversation.map((message, index) => renderMessage(message, index))
                )}
                <div ref={messagesEndRef} /> {/* Anchor for scrolling */}
              </div>
            </Card.Body>
            <Card.Footer className="query-input-footer">
              <Form onSubmit={handleQuerySubmit}>
                <Row className="g-2 align-items-center">
                  <Col>
                    <Form.Control
                      type="text"
                      value={query}
                      onChange={handleQueryChange}
                      placeholder={selectedDocuments.length > 0 ? "Ask a question..." : "Select documents first..."}
                      disabled={loading || selectedDocuments.length === 0}
                      aria-label="Query input"
                    />
                    {error && <Form.Text className="text-danger ms-2">{error}</Form.Text>}
                  </Col>
                  <Col xs="auto">
                    <Button
                      type="submit"
                      variant="primary"
                      disabled={loading || !query.trim() || selectedDocuments.length === 0}
                      title="Send Query"
                    >
                      {loading ? <Spinner animation="border" size="sm" /> : <i className="fas fa-paper-plane"></i>}
                    </Button>
                  </Col>
                </Row>
              </Form>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default NaturalLanguageQueryInterface;