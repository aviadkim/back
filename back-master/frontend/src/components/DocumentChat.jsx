import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

/**
 * Document Chat Component
 * 
 * Provides a chat interface for interacting with financial documents
 */
const DocumentChat = ({ documentId, documentName }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  
  const messagesEndRef = useRef(null);
  
  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  // Create a new chat session when component mounts
  useEffect(() => {
    if (documentId) {
      createChatSession();
      fetchSuggestedQuestions();
    }
  }, [documentId]);
  
  // Scroll to bottom whenever messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Create a new chat session
  const createChatSession = async () => {
    try {
      const response = await axios.post('/api/chat/sessions', {
        userId: 'anonymous', // In a real app, this would be the actual user ID
        documents: [documentId]
      });
      
      setSessionId(response.data.session_id);
      
      // Add a welcome message
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: `שלום! אני יכול לעזור לך לנתח את המסמך "${documentName || 'שנבחר'}". מה תרצה לדעת?`,
        timestamp: new Date().toISOString()
      }]);
    } catch (error) {
      setError('שגיאה ביצירת שיחה חדשה. אנא נסה שוב.');
      console.error('Error creating chat session:', error);
    }
  };
  
  // Fetch suggested questions for this document
  const fetchSuggestedQuestions = async () => {
    try {
      const response = await axios.get(`/api/chat/documents/${documentId}/suggestions`);
      setSuggestedQuestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Error fetching suggested questions:', error);
      // Don't show an error message to the user, as this is not critical
    }
  };
  
  // Handle sending a message
  const handleSendMessage = async (content = inputValue) => {
    if (!content.trim() || !sessionId) return;
    
    // Add user message to the list
    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      const response = await axios.post(`/api/chat/sessions/${sessionId}/messages`, {
        message: content
      });
      
      // Add the assistant's response
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.data.response.answer,
        timestamp: new Date().toISOString(),
        model: response.data.response.model_used,
        sources: response.data.response.sources || []
      };
      
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
    } catch (error) {
      setError('שגיאה בשליחת ההודעה. אנא נסה שוב.');
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle input changes
  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };
  
  // Handle form submission
  const handleSubmit = (event) => {
    event.preventDefault();
    handleSendMessage();
  };
  
  // Handle clicking on a suggested question
  const handleSuggestedQuestionClick = (question) => {
    handleSendMessage(question.text);
  };
  
  return (
    <div className="chat-container bg-white rounded-lg shadow-md h-full flex flex-col">
      <div className="chat-header p-4 border-b">
        <h2 className="text-xl font-semibold text-primary-700">
          שיחה עם המסמך: {documentName || documentId}
        </h2>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 m-4 rounded">
          {error}
          <button 
            onClick={() => setError('')}
            className="float-left text-red-700 font-bold"
          >
            &times;
          </button>
        </div>
      )}
      
      <div className="chat-messages flex-grow p-4 overflow-y-auto space-y-4">
        {messages.map((message) => (
          <div 
            key={message.id}
            className={`message flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className={`max-w-3/4 p-3 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-primary-100 text-primary-800 rounded-tr-none' 
                  : 'bg-gray-100 text-gray-800 rounded-tl-none'
              }`}
            >
              <div className="message-content whitespace-pre-wrap">{message.content}</div>
              
              {message.sources && message.sources.length > 0 && (
                <div className="message-sources mt-2 text-xs text-gray-500">
                  <p className="font-semibold">מקורות:</p>
                  <ul className="list-disc list-inside">
                    {message.sources.map((source, index) => (
                      <li key={index}>{source}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="message-meta text-xs text-gray-500 mt-1 text-start">
                {message.model && (
                  <span className="model-badge inline-block ml-2 bg-gray-200 rounded px-1">
                    {message.model}
                  </span>
                )}
                <span className="message-time">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message flex justify-start">
            <div className="max-w-3/4 p-3 rounded-lg bg-gray-100 text-gray-800 rounded-tl-none">
              <div className="typing-indicator flex space-x-1">
                <div className="dot w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="dot w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                <div className="dot w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {suggestedQuestions.length > 0 && messages.length <= 3 && (
        <div className="suggested-questions p-3 border-t">
          <p className="text-sm text-gray-600 mb-2">שאלות מוצעות:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question) => (
              <button
                key={question.id}
                onClick={() => handleSuggestedQuestionClick(question)}
                className="text-sm bg-primary-50 text-primary-700 px-3 py-1 rounded-full border border-primary-200 hover:bg-primary-100"
              >
                {question.text}
              </button>
            ))}
          </div>
        </div>
      )}
      
      <div className="chat-input p-4 border-t">
        <form onSubmit={handleSubmit} className="flex items-center">
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="שאל שאלה על המסמך..."
            className="flex-grow px-4 py-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            disabled={isLoading || !sessionId}
          />
          <button
            type="submit"
            className="bg-primary-600 text-white px-4 py-2 rounded-r-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!inputValue.trim() || isLoading || !sessionId}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
};

export default DocumentChat;
