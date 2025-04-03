/**
 * Document Chat Feature Module
 * 
 * This module provides functionality for interacting with documents via a chat interface.
 * It implements a complete vertical slice for the document chat feature.
 */

const express = require('express');
const router = express.Router();

// Import service layer
const chatService = require('./service');

/**
 * Create a new chat session
 */
router.post('/api/chat/sessions', async (req, res) => {
  try {
    const userId = req.body.userId || 'anonymous';
    const documents = req.body.documents || [];
    
    const sessionId = await chatService.createSession(userId, documents);
    
    return res.json({
      status: 'success',
      session_id: sessionId
    });
  } catch (error) {
    console.error('Error creating chat session:', error);
    return res.status(500).json({ 
      error: 'Failed to create chat session',
      message: error.message
    });
  }
});

/**
 * Get chat session history
 */
router.get('/api/chat/sessions/:sessionId/history', async (req, res) => {
  try {
    const sessionId = req.params.sessionId;
    const history = await chatService.getSessionHistory(sessionId);
    
    if (!history) {
      return res.status(404).json({ error: 'Session not found' });
    }
    
    return res.json({
      status: 'success',
      session_id: sessionId,
      history: history
    });
  } catch (error) {
    console.error('Error getting chat history:', error);
    return res.status(500).json({ error: 'Failed to get chat history' });
  }
});

/**
 * Send a message to the chat
 */
router.post('/api/chat/sessions/:sessionId/messages', async (req, res) => {
  try {
    const sessionId = req.params.sessionId;
    const query = req.body.message;
    const context = req.body.context || {};
    
    if (!query) {
      return res.status(400).json({ error: 'Message is required' });
    }
    
    const response = await chatService.processQuery(sessionId, query, context);
    
    return res.json({
      status: 'success',
      session_id: sessionId,
      response: response
    });
  } catch (error) {
    console.error('Error processing chat message:', error);
    return res.status(500).json({ 
      error: 'Failed to process message',
      message: error.message
    });
  }
});

/**
 * Get suggested questions for a document
 */
router.get('/api/chat/documents/:documentId/suggestions', async (req, res) => {
  try {
    const documentId = req.params.documentId;
    const suggestions = await chatService.getSuggestedQuestions(documentId);
    
    return res.json({
      status: 'success',
      document_id: documentId,
      suggestions: suggestions
    });
  } catch (error) {
    console.error('Error getting suggested questions:', error);
    return res.status(500).json({ error: 'Failed to get suggestions' });
  }
});

// Export the router
module.exports = router;
