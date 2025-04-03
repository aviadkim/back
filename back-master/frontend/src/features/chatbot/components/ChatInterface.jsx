import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Paper, 
  TextField, 
  Button, 
  Typography, 
  CircularProgress,
  IconButton,
  Divider,
  Grid,
  Alert
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MessageList from './MessageList';
import DocumentContext from './DocumentContext';
import SuggestedQuestions from './SuggestedQuestions';

/**
 * ChatInterface component provides a complete chat experience with the AI assistant
 * 
 * This component:
 * - Creates and manages chat sessions
 * - Sends user queries to the backend
 * - Displays conversation history
 * - Shows document context
 * - Provides suggested follow-up questions
 * 
 * @param {Object} props Component props
 * @param {Array} props.documentIds IDs of documents to use as context for the chat
 * @param {string} props.language Language code for the chat (default: 'he')
 */
function ChatInterface({ documentIds = [], language = 'he' }) {
  // State for chat session management
  const [sessionId, setSessionId] = useState(null);
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [sessionError, setSessionError] = useState(null);
  
  // State for chat messages
  const [messages, setMessages] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  
  // State for message input and sending
  const [messageInput, setMessageInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  
  // State for suggested questions
  const [suggestions, setSuggestions] = useState([]);
  
  // Ref for auto-scrolling to latest messages
  const messagesEndRef = useRef(null);
  
  // Initialize chat session when component mounts or document IDs change
  useEffect(() => {
    initializeSession();
  }, [JSON.stringify(documentIds)]); // Re-run when document IDs change
  
  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  /**
   * Initializes a new chat session
   */
  const initializeSession = async () => {
    // Skip if already creating a session or there are no documents
    if (isCreatingSession) return;
    
    setIsCreatingSession(true);
    setSessionError(null);
    
    try {
      // Create a new session
      const response = await fetch('/api/chat/session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          document_ids: documentIds,
          language: language
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error creating chat session');
      }
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to create chat session');
      }
      
      setSessionId(result.session_id);
      
      // Load chat history for this session
      await loadChatHistory(result.session_id);
      
      // Generate document-specific suggestions if available
      if (documentIds.length > 0) {
        await loadDocumentSuggestions(documentIds[0]);
      }
    } catch (error) {
      console.error('Error initializing chat session:', error);
      setSessionError(error.message || 'Failed to initialize chat. Please try again.');
    } finally {
      setIsCreatingSession(false);
    }
  };
  
  /**
   * Loads chat history for a session
   */
  const loadChatHistory = async (sid) => {
    setIsLoadingHistory(true);
    
    try {
      const response = await fetch(`/api/chat/session/${sid}`);
      
      if (!response.ok) {
        throw new Error('Failed to load chat history');
      }
      
      const result = await response.json();
      
      if (result.success && result.messages) {
        // Messages come in reverse chronological order, so reverse them back
        setMessages(result.messages.reverse());
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      // Don't show an error to the user since this is not critical
    } finally {
      setIsLoadingHistory(false);
    }
  };
  
  /**
   * Loads suggested questions for a document
   */
  const loadDocumentSuggestions = async (documentId) => {
    try {
      const response = await fetch(`/api/chat/document-suggestions/${documentId}`);
      
      if (!response.ok) {
        return; // Silently fail, not critical
      }
      
      const result = await response.json();
      
      if (result.success && result.suggestions) {
        setSuggestions(result.suggestions);
      }
    } catch (error) {
      console.error('Error loading document suggestions:', error);
      // Silently fail, not critical
    }
  };
  
  /**
   * Handles sending a message
   */
  const sendMessage = async (message) => {
    // Validation checks
    if (!sessionId) {
      setSessionError('Chat session not initialized. Please reload the page.');
      return;
    }
    
    if (!message.trim()) {
      return;
    }
    
    // Optimistically add user message to UI
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setMessageInput(''); // Clear input field
    setIsSending(true);
    
    try {
      // Send the message to the API
      const response = await fetch('/api/chat/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          query: message,
          document_ids: documentIds,
          language: language
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error sending message');
      }
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to process query');
      }
      
      // Add AI response to messages
      const assistantMessage = {
        role: 'assistant',
        content: result.answer,
        timestamp: new Date().toISOString(),
        document_references: result.document_references || []
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update suggested questions if available
      if (result.suggested_questions && result.suggested_questions.length > 0) {
        setSuggestions(result.suggested_questions);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message to chat
      setMessages(prev => [
        ...prev,
        {
          role: 'system',
          content: `Error: ${error.message || 'Failed to get response'}. Please try again.`,
          timestamp: new Date().toISOString(),
          isError: true
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };
  
  /**
   * Handles form submission
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(messageInput);
  };
  
  /**
   * Scrolls to the bottom of the message list
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  return (
    <Grid container spacing={2} sx={{ height: '100%' }}>
      {/* Main chat panel */}
      <Grid item xs={12} md={8}>
        <Paper 
          elevation={3} 
          sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            height: '80vh',
            maxHeight: '80vh',
            overflow: 'hidden'
          }}
        >
          {/* Chat header */}
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6" component="div">
              {language === 'he' ? 'שיחה עם העוזר הפיננסי' : 'Financial Assistant Chat'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {documentIds.length > 0 
                ? `${language === 'he' ? 'מקושר ל-' : 'Connected to '} ${documentIds.length} ${language === 'he' ? 'מסמכים' : 'documents'}`
                : language === 'he' ? 'לא מקושר למסמכים' : 'No documents connected'}
            </Typography>
          </Box>
          
          {/* Session error alert */}
          {sessionError && (
            <Alert severity="error" sx={{ m: 2 }}>
              {sessionError}
            </Alert>
          )}
          
          {/* Message list */}
          <Box 
            sx={{ 
              flexGrow: 1, 
              overflow: 'auto', 
              p: 2,
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {isLoadingHistory ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
                <CircularProgress size={40} />
              </Box>
            ) : messages.length === 0 ? (
              <Box 
                sx={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  height: '100%',
                  color: 'text.secondary',
                  textAlign: 'center'
                }}
              >
                <Typography variant="h6" gutterBottom>
                  {language === 'he' ? 'שאל שאלה על המסמכים הפיננסיים שלך' : 'Ask a question about your financial documents'}
                </Typography>
                <Typography variant="body2">
                  {language === 'he' 
                    ? 'אני יכול לעזור לך להבין את המסמכים הפיננסיים שלך, לנתח את הנתונים, וליצור טבלאות מותאמות אישית.'
                    : 'I can help you understand your financial documents, analyze the data, and create custom tables.'}
                </Typography>
              </Box>
            ) : (
              <MessageList 
                messages={messages} 
                language={language} 
              />
            )}
            <div ref={messagesEndRef} />
          </Box>
          
          {/* Message input */}
          <Box 
            component="form" 
            onSubmit={handleSubmit}
            sx={{ 
              p: 2, 
              borderTop: 1, 
              borderColor: 'divider',
              backgroundColor: 'background.paper'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder={language === 'he' ? 'הקלד שאלה...' : 'Type a message...'}
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                disabled={!sessionId || isSending}
                size="small"
                sx={{ 
                  mr: 1,
                  direction: language === 'he' ? 'rtl' : 'ltr'
                }}
              />
              <IconButton 
                color="primary" 
                type="submit" 
                disabled={!sessionId || isSending || !messageInput.trim()}
                sx={{ p: 1 }}
              >
                {isSending ? <CircularProgress size={24} /> : <SendIcon />}
              </IconButton>
            </Box>
          </Box>
        </Paper>
      </Grid>
      
      {/* Context panel */}
      <Grid item xs={12} md={4}>
        <Paper 
          elevation={3} 
          sx={{ 
            p: 2, 
            height: '80vh',
            maxHeight: '80vh',
            overflow: 'auto'
          }}
        >
          {/* Document context */}
          <Typography variant="h6" gutterBottom>
            {language === 'he' ? 'מסמכים בהקשר' : 'Document Context'}
          </Typography>
          <DocumentContext documentIds={documentIds} language={language} />
          
          <Divider sx={{ my: 2 }} />
          
          {/* Suggested questions */}
          <Typography variant="h6" gutterBottom>
            {language === 'he' ? 'שאלות מוצעות' : 'Suggested Questions'}
          </Typography>
          <SuggestedQuestions 
            suggestions={suggestions} 
            onSelect={sendMessage}
            language={language} 
            disabled={!sessionId || isSending}
          />
        </Paper>
      </Grid>
    </Grid>
  );
}

export default ChatInterface;
