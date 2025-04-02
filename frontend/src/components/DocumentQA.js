import React, { useState, useEffect } from 'react';
import { Card, CardContent, TextField, Button, Typography, CircularProgress, Box } from '@mui/material';

function DocumentQA({ documentId }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [previousQuestions, setPreviousQuestions] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/qa/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          document_id: documentId,
          question: question
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to get answer');
      }
      
      setAnswer(data.answer);
      setPreviousQuestions([
        { question, answer: data.answer, timestamp: new Date().toLocaleTimeString() },
        ...previousQuestions
      ]);
      setQuestion('');
    } catch (err) {
      console.error('Error asking question:', err);
      setError(err.message || 'An error occurred while getting your answer');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card variant="outlined" sx={{ marginTop: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Ask Questions About This Document
        </Typography>
        
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Ask a question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={isLoading}
            margin="normal"
            variant="outlined"
          />
          
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={isLoading || !question.trim()}
            sx={{ mt: 1 }}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Ask'}
          </Button>
        </form>
        
        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}
        
        {answer && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Typography variant="subtitle1" fontWeight="bold">Answer:</Typography>
            <Typography variant="body1" component="div" whiteSpace="pre-wrap">
              {answer}
            </Typography>
          </Box>
        )}
        
        {previousQuestions.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Previous Questions
            </Typography>
            
            {previousQuestions.map((item, index) => (
              <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  {item.timestamp}
                </Typography>
                <Typography variant="subtitle1" fontWeight="bold">
                  Q: {item.question}
                </Typography>
                <Typography variant="body1" whiteSpace="pre-wrap">
                  A: {item.answer}
                </Typography>
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

export default DocumentQA;
