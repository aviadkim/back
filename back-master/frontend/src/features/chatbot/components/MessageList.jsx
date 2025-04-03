import React, { useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Avatar,
  Divider,
  Chip,
  Link,
  Alert
} from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import WarningIcon from '@mui/icons-material/Warning';
import DescriptionIcon from '@mui/icons-material/Description';
import ReactMarkdown from 'react-markdown';

/**
 * MessageList component displays the conversation between user and AI assistant
 * 
 * Features:
 * - Displays messages with appropriate styling based on role (user/assistant/system)
 * - Renders markdown content in assistant messages
 * - Shows document references when available
 * - Displays timestamps for messages
 */
function MessageList({ messages = [], language = 'he' }) {
  // Reference for scrolling to the latest message
  const bottomRef = useRef(null);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  /**
   * Formats a timestamp for display
   */
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString(language === 'he' ? 'he-IL' : 'en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return '';
    }
  };
  
  /**
   * Renders a single message
   */
  const renderMessage = (message, index) => {
    const { role, content, timestamp, document_references, isError } = message;
    
    // Determine message styles based on role
    const isUser = role === 'user';
    const isAssistant = role === 'assistant';
    const isSystem = role === 'system';
    const theme = useTheme(); // Access theme object

    // Alignment and style based on role
    const messageAlign = isUser ? 'flex-end' : 'flex-start';

    // Theme-aware colors
    let messageBgColor;
    let messageTextColor;

    if (isUser) {
      messageBgColor = theme.palette.primary.main; // Use main primary color
      messageTextColor = theme.palette.primary.contrastText; // Use contrast text
    } else if (isAssistant) {
      messageBgColor = theme.palette.mode === 'dark' ? theme.palette.grey[800] : theme.palette.grey[200]; // Darker grey for assistant
      messageTextColor = theme.palette.text.primary;
    } else { // System message (keep warning style)
      messageBgColor = 'warning.light';
      messageTextColor = 'warning.contrastText'; // Ensure contrast for warning
    }

    // Override for explicit error messages
    if (isError) {
      messageBgColor = theme.palette.error.light;
      messageTextColor = theme.palette.error.contrastText;
    }

    return (
      <Box
        key={index}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: messageAlign,
          mb: 2,
          maxWidth: '100%'
        }}
      >
        {/* Message content */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', maxWidth: '80%' }}>
          {/* Avatar for assistant and system messages */}
          {!isUser && (
            <Avatar
              sx={{ 
                bgcolor: isAssistant ? 'primary.main' : 'warning.main',
                mr: 1,
                width: 36,
                height: 36
              }}
            >
              {isAssistant ? <SmartToyIcon /> : <WarningIcon />}
            </Avatar>
          )}
          
          <Box sx={{ maxWidth: 'calc(100% - 48px)' }}>
            {/* Message bubble */}
            <Paper
              elevation={1}
              sx={{
                p: 2,
                bgcolor: isError ? 'error.light' : messageBgColor,
                color: isError ? 'error.contrastText' : messageTextColor,
                borderRadius: 2,
                borderTopLeftRadius: !isUser ? 0 : undefined,
                borderTopRightRadius: isUser ? 0 : undefined,
                wordBreak: 'break-word'
              }}
            >
              {isError ? (
                <Typography variant="body1">
                  {content}
                </Typography>
              ) : isAssistant ? (
                <ReactMarkdown
                  components={{
                    p: ({ node, ...props }) => (
                      <Typography variant="body1" sx={{ my: 1 }} {...props} />
                    ),
                    h1: ({ node, ...props }) => (
                      <Typography variant="h5" sx={{ mt: 2, mb: 1 }} {...props} />
                    ),
                    h2: ({ node, ...props }) => (
                      <Typography variant="h6" sx={{ mt: 2, mb: 1 }} {...props} />
                    ),
                    h3: ({ node, ...props }) => (
                      <Typography variant="subtitle1" sx={{ mt: 1.5, mb: 0.75, fontWeight: 'bold' }} {...props} />
                    ),
                    li: ({ node, ...props }) => (
                      <li style={{ marginBottom: '0.25rem' }} {...props} />
                    ),
                    code: ({ node, inline, ...props }) => (
                      inline ? (
                        <Typography 
                          component="code" 
                          sx={{ 
                            bgcolor: 'grey.200', 
                            p: 0.3, 
                            borderRadius: 0.5,
                            fontFamily: 'monospace'
                          }}
                          {...props} 
                        />
                      ) : (
                        <Paper 
                          variant="outlined" 
                          sx={{ 
                            bgcolor: 'grey.900', 
                            color: 'grey.100',
                            p: 1.5, 
                            my: 1.5,
                            borderRadius: 1,
                            fontFamily: 'monospace',
                            fontSize: '0.875rem',
                            overflowX: 'auto'
                          }}
                        >
                          <pre style={{ margin: 0 }}>
                            <code {...props} />
                          </pre>
                        </Paper>
                      )
                    ),
                    a: ({ node, ...props }) => (
                      <Link {...props} target="_blank" rel="noopener" />
                    ),
                    table: ({ node, ...props }) => (
                      <Paper variant="outlined" sx={{ my: 1, overflow: 'auto' }}>
                        <table style={{ 
                          borderCollapse: 'collapse', 
                          width: '100%'
                        }} {...props} />
                      </Paper>
                    ),
                    th: ({ node, ...props }) => (
                      <th style={{ 
                        borderBottom: '1px solid rgba(0,0,0,0.12)',
                        padding: '0.5rem',
                        textAlign: 'left',
                        backgroundColor: 'rgba(0,0,0,0.04)'
                      }} {...props} />
                    ),
                    td: ({ node, ...props }) => (
                      <td style={{ 
                        borderBottom: '1px solid rgba(0,0,0,0.12)',
                        padding: '0.5rem',
                        textAlign: 'left'
                      }} {...props} />
                    )
                  }}
                >
                  {content}
                </ReactMarkdown>
              ) : (
                <Typography variant="body1">
                  {content}
                </Typography>
              )}
            </Paper>
            
            {/* Timestamp */}
            <Typography 
              variant="caption" 
              color="text.secondary"
              sx={{ 
                display: 'block', 
                mt: 0.5,
                textAlign: isUser ? 'right' : 'left'
              }}
            >
              {formatTimestamp(timestamp)}
            </Typography>
            
            {/* Document references */}
            {isAssistant && document_references && document_references.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {language === 'he' ? 'מקורות מידע:' : 'References:'}
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                  {document_references.map((ref, idx) => (
                    <Chip
                      key={idx}
                      size="small"
                      icon={<DescriptionIcon />}
                      label={ref.title || ref.document_id}
                      variant="outlined"
                      sx={{ fontSize: '0.75rem' }}
                    />
                  ))}
                </Box>
              </Box>
            )}
          </Box>
          
          {/* Avatar for user messages */}
          {isUser && (
            <Avatar
              sx={{ 
                bgcolor: 'primary.dark',
                ml: 1,
                width: 36,
                height: 36
              }}
            >
              <PersonIcon />
            </Avatar>
          )}
        </Box>
      </Box>
    );
  };
  
  // If there are no messages
  if (!messages || messages.length === 0) {
    return null;
  }
  
  return (
    <Box sx={{ width: '100%' }}>
      {messages.map(renderMessage)}
      <div ref={bottomRef} />
    </Box>
  );
}

export default MessageList;
