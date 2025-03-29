import React, { useState, useEffect, useRef } from 'react';
import documentService from '../../services/documentService'; // Assuming service exists
import './DocumentChat.css';

/**
 * רכיב צ'אט לשאילת שאלות על המסמך
 * @param {Object} props - מאפייני הרכיב
 * @param {string} props.documentId - מזהה המסמך לשאילת שאלות
 */
const DocumentChat = ({ documentId }) => {
  const [messages, setMessages] = useState([
    {
      type: 'system',
      content: 'ברוכים הבאים לצ\'אט המסמך החכם. מה תרצו לדעת על המסמך?'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null); // Ref for textarea height adjustment

  // גלילה לתחתית הצ'אט בכל פעם שנוספת הודעה
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Adjust textarea height based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset height
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`; // Set to scroll height
    }
  }, [inputValue]);


  // שליחת שאלה לשרת
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const question = inputValue.trim();
    setInputValue(''); // Clear input immediately
    if (textareaRef.current) { // Reset textarea height
        textareaRef.current.style.height = 'auto';
    }


    // הוספת הודעת המשתמש לרשימת ההודעות
    setMessages(prevMessages => [
      ...prevMessages,
      { type: 'user', content: question }
    ]);

    // הגדרת סטטוס טעינה
    setIsLoading(true);

    try {
      // שליחת השאלה לשרת
      const response = await documentService.askQuestion(documentId, question);

      // הוספת תשובת המערכת
      setMessages(prevMessages => [
        ...prevMessages,
        {
          type: 'assistant',
          // Ensure response.answer exists and is a string
          content: (response?.answer && typeof response.answer === 'string')
                     ? response.answer
                     : 'לא הצלחתי למצוא תשובה לשאלה זו.'
        }
      ]);
    } catch (error) {
      console.error('Error asking question:', error);

      // הוספת הודעת שגיאה
      setMessages(prevMessages => [
        ...prevMessages,
        {
          type: 'error',
          content: `אירעה שגיאה בעת עיבוד השאלה: ${error.message || 'שגיאה לא ידועה'}.`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // שליחת השאלה בלחיצה על Enter
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { // Send on Enter, allow Shift+Enter for newline
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle suggested question click
  const handleSuggestedQuestion = (question) => {
      setInputValue(question);
      // Optionally trigger send immediately:
      // handleSendMessage(); // Be careful if this clears the input before sending
  };


  return (
    <div className="document-chat">
      <div className="chat-header">
        <h3>שאל את המסמך</h3>
        <div className="chat-info">
          <i className="fas fa-info-circle"></i>
          <span>שאל שאלות בשפה טבעית על תוכן המסמך</span>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            <div className="message-icon">
              {message.type === 'user' && <i className="fas fa-user"></i>}
              {message.type === 'assistant' && <i className="fas fa-robot"></i>}
              {message.type === 'system' && <i className="fas fa-info-circle"></i>}
              {message.type === 'error' && <i className="fas fa-exclamation-triangle"></i>}
            </div>
            {/* Render content, potentially handling markdown or newlines later */}
            <div className="message-content">{message.content}</div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant loading">
            <div className="message-icon">
              <i className="fas fa-robot"></i>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area"> {/* Renamed class */}
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="הקלד את שאלתך כאן..."
          disabled={isLoading}
          rows={1} // Start with one row, auto-adjust height
        />
        <button
          className="send-button"
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isLoading}
          title="שלח שאלה"
        >
          <i className="fas fa-paper-plane"></i>
        </button>
      </div>

      <div className="chat-footer">
        <div className="suggested-questions">
          <span className="suggested-label">שאלות לדוגמה:</span>
          <button
            className="suggested-question"
            onClick={() => handleSuggestedQuestion('מה הנתונים הפיננסיים העיקריים במסמך?')}
          >
            מה הנתונים הפיננסיים העיקריים במסמך?
          </button>
          <button
            className="suggested-question"
            onClick={() => handleSuggestedQuestion('האם יש קודי ISIN במסמך?')}
          >
            האם יש קודי ISIN במסמך?
          </button>
          <button
            className="suggested-question"
            onClick={() => handleSuggestedQuestion('סכם את המסמך בקצרה')}
          >
            סכם את המסמך בקצרה
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentChat;