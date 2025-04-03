import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent
} from '@mui/material';
import {
  Send as SendIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  TableChart as TableIcon
} from '@mui/icons-material';
import api from '../services/api';

const SmartPdfBot = ({ pdfText, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // טעינת היסטוריית הצ'אט בטעינה ראשונית
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const history = await api.chat.getHistory();
      setMessages(history);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const clearHistory = async () => {
    try {
      await api.chat.clearHistory();
      setMessages([]);
    } catch (error) {
      console.error('Error clearing chat history:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'human', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.chat.sendMessage(input, pdfText);
      const botMessage = {
        role: 'assistant',
        content: response.message,
        table: response.table
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'מצטער, אירעה שגיאה בעיבוד ההודעה שלך. אנא נסה שוב.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const renderTable = (table) => {
    if (!table || !table.headers || !table.rows) return null;

    return (
      <Box sx={{ overflowX: 'auto', mt: 2 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              {table.headers.map((header, i) => (
                <th key={i} style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5' }}>
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) => (
                  <td key={j} style={{ border: '1px solid #ddd', padding: '8px' }}>
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        p: 2,
        borderBottom: '1px solid #ddd'
      }}>
        <Typography variant="h6">עוזר PDF חכם</Typography>
        <IconButton onClick={clearHistory} color="error" title="נקה היסטוריה">
          <DeleteIcon />
        </IconButton>
      </Box>

      <Box sx={{ 
        flex: 1, 
        overflowY: 'auto', 
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        {messages.map((msg, idx) => (
          <Paper 
            key={idx} 
            elevation={1}
            sx={{
              p: 2,
              maxWidth: '80%',
              alignSelf: msg.role === 'human' ? 'flex-end' : 'flex-start',
              backgroundColor: msg.role === 'human' ? '#e3f2fd' : '#fff'
            }}
          >
            <Typography>{msg.content}</Typography>
            {msg.table && renderTable(msg.table)}
          </Paper>
        ))}
        <div ref={messagesEndRef} />
      </Box>

      <Box sx={{ 
        p: 2, 
        borderTop: '1px solid #ddd',
        display: 'flex',
        gap: 1
      }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="הקלד את שאלתך כאן..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          disabled={loading}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleSend}
          disabled={loading || !input.trim()}
          endIcon={<SendIcon />}
        >
          שלח
        </Button>
      </Box>
    </Box>
  );
};

export default SmartPdfBot; 