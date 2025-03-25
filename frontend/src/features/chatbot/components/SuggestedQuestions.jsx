import React from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  Alert
} from '@mui/material';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';

/**
 * SuggestedQuestions component displays AI-generated question suggestions
 * that users can click to quickly ask common or relevant questions
 */
function SuggestedQuestions({ 
  suggestions = [], 
  onSelect, 
  language = 'he',
  disabled = false
}) {
  // Default suggestions when none are provided
  const defaultSuggestions = [
    language === 'he' 
      ? 'מה המצב הכללי של התיק הפיננסי שלי?' 
      : 'What is the overall status of my financial portfolio?',
    language === 'he'
      ? 'מהם הנכסים עם הביצועים הטובים ביותר בתיק שלי?'
      : 'What are the best performing assets in my portfolio?',
    language === 'he'
      ? 'תוכל להסביר את היתרות בחשבון שלי?'
      : 'Can you explain the balances in my account?',
    language === 'he'
      ? 'האם יש המלצות לשיפור המצב הפיננסי שלי?'
      : 'Are there any recommendations to improve my financial situation?'
  ];
  
  // Use provided suggestions or defaults if none available
  const questionsToShow = suggestions.length > 0 ? suggestions : defaultSuggestions;
  
  /**
   * Handles question selection
   */
  const handleSelectQuestion = (question) => {
    if (onSelect && !disabled) {
      onSelect(question);
    }
  };
  
  return (
    <Box>
      {questionsToShow.length === 0 ? (
        <Alert severity="info">
          {language === 'he'
            ? 'אין שאלות מוצעות זמינות'
            : 'No suggested questions available'}
        </Alert>
      ) : (
        <List disablePadding>
          {questionsToShow.map((question, index) => (
            <React.Fragment key={index}>
              {index > 0 && <Divider component="li" />}
              <ListItem disablePadding>
                <ListItemButton
                  onClick={() => handleSelectQuestion(question)}
                  disabled={disabled}
                  sx={{
                    py: 1.5,
                    px: 2,
                    borderRadius: 1,
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    }
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <QuestionAnswerIcon 
                          fontSize="small" 
                          color="primary" 
                          sx={{ mr: 1, opacity: 0.8 }}
                        />
                        <Typography variant="body2">
                          {question}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItemButton>
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      )}
      
      {/* Refresh suggestions button */}
      {onSelect && suggestions.length > 0 && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Button
            size="small"
            variant="outlined"
            onClick={() => handleSelectQuestion(
              language === 'he'
                ? 'תוכל להציע שאלות נוספות לשאול על המסמכים שלי?'
                : 'Can you suggest more questions to ask about my documents?'
            )}
            disabled={disabled}
          >
            {language === 'he' 
              ? 'הצע שאלות נוספות'
              : 'Suggest more questions'}
          </Button>
        </Box>
      )}
    </Box>
  );
}

export default SuggestedQuestions;
