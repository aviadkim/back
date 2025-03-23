import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Avatar,
  Divider,
  IconButton,
  CircularProgress,
  Card,
  CardContent,
} from '@mui/material';
import {
  Send as SendIcon,
  DeleteOutline as DeleteIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { chatApi } from '../services/api';

const ChatBot = ({ documentId, documentData }) => {
  const [messages, setMessages] = useState([
    {
      text: 'שלום, אני העוזר הדיגיטלי שלך לניתוח מסמכים פיננסיים. כיצד אוכל לעזור לך היום?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const context = {
        documentId: documentId || '',
        documentData: documentData || {},
      };

      const response = await chatApi.sendMessage(input, JSON.stringify(context));
      
      const botMessage = {
        text: response.message || 'אירעה שגיאה בקבלת תשובה. אנא נסה שוב.',
        sender: 'bot',
        timestamp: new Date(),
        data: response.data || null,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        text: 'אירעה שגיאה בתקשורת עם השרת. אנא נסה שוב מאוחר יותר.',
        sender: 'bot',
        timestamp: new Date(),
        isError: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        text: 'השיחה נוקתה. במה אוכל לעזור לך?',
        sender: 'bot',
        timestamp: new Date(),
      },
    ]);
    
    // ניקוי היסטוריית צ'אט בשרת
    chatApi.clearHistory().catch(error => {
      console.error('Error clearing chat history:', error);
    });
  };

  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        borderRadius: 2,
      }}
    >
      <Box
        sx={{
          p: 2,
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BotIcon /> עוזר דיגיטלי
        </Typography>
        <IconButton 
          onClick={clearChat} 
          color="inherit" 
          aria-label="נקה צ'אט"
          title="נקה צ'אט"
        >
          <DeleteIcon />
        </IconButton>
      </Box>
      
      <Divider />
      
      <Box
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          bgcolor: '#f9fafb',
        }}
      >
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: message.sender === 'user' ? 'flex-start' : 'flex-start',
              gap: 1,
            }}
          >
            <Avatar
              sx={{
                bgcolor: message.sender === 'user' ? 'secondary.main' : 'primary.main',
                width: 36,
                height: 36,
              }}
            >
              {message.sender === 'user' ? <PersonIcon /> : <BotIcon />}
            </Avatar>
            
            <Card
              sx={{
                maxWidth: '80%',
                bgcolor: message.sender === 'user' ? 'secondary.light' : 'white',
                color: message.sender === 'user' ? 'white' : 'text.primary',
                borderRadius: message.sender === 'user' ? '18px 18px 0 18px' : '18px 18px 18px 0',
                boxShadow: message.isError ? '0 0 0 1px #ef4444' : 'none',
                border: message.isError ? '1px solid #ef4444' : '1px solid #e0e0e0',
              }}
            >
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.text}
                </Typography>
                
                {message.data && (
                  <Box sx={{ mt: 2 }}>
                    {message.data.tableData && (
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        *נתונים זמינים להצגה כטבלה
                      </Typography>
                    )}
                  </Box>
                )}
                
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, textAlign: 'right' }}>
                  {formatTimestamp(message.timestamp)}
                </Typography>
              </CardContent>
            </Card>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Box>
      
      <Divider />
      
      <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            placeholder="הקלד את שאלתך כאן..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '20px',
              },
            }}
          />
          <Button
            variant="contained"
            color="primary"
            disableElevation
            onClick={handleSendMessage}
            disabled={!input.trim() || loading}
            sx={{ 
              borderRadius: '50%', 
              minWidth: '48px',
              width: '48px',
              height: '48px',
              p: 0, 
            }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : <SendIcon />}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default ChatBot;