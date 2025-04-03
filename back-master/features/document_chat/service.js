/**
 * Document Chat Service
 * 
 * Service layer for document chat functionality.
 * Implements business logic for the document chat feature.
 */

const { v4: uuidv4 } = require('uuid');

// Import the coordinator from agent framework
let agentCoordinator;
try {
  const agentFramework = require('../../agent_framework');
  agentCoordinator = agentFramework.get_coordinator();
} catch (error) {
  console.warn('Agent framework not available:', error.message);
  // Create a mock coordinator if the real one is not available
  agentCoordinator = {
    create_session: (userId, documents) => uuidv4(),
    process_query: (sessionId, query) => ({
      answer: `This is a mock response to: ${query}`,
      session_id: sessionId,
      model_used: 'mock',
      sources: []
    }),
    get_session_history: () => []
  };
}

/**
 * Create a new chat session
 * 
 * @param {string} userId - User ID
 * @param {Array} documents - Array of document IDs to associate with the session
 * @returns {string} New session ID
 */
async function createSession(userId, documents = []) {
  console.log(`Creating session for user ${userId} with documents:`, documents);
  
  // Use the agent coordinator to create a session
  const sessionId = agentCoordinator.create_session(userId, documents);
  
  return sessionId;
}

/**
 * Get chat session history
 * 
 * @param {string} sessionId - Session ID
 * @returns {Array} Session history messages
 */
async function getSessionHistory(sessionId) {
  console.log(`Getting history for session ${sessionId}`);
  
  // Use the agent coordinator to get session history
  const history = agentCoordinator.get_session_history(sessionId);
  
  return history;
}

/**
 * Process a chat query
 * 
 * @param {string} sessionId - Session ID
 * @param {string} query - User query
 * @param {Object} context - Additional context
 * @returns {Object} Response with answer and metadata
 */
async function processQuery(sessionId, query, context = {}) {
  console.log(`Processing query for session ${sessionId}: ${query}`);
  
  // Use the agent coordinator to process the query
  const response = agentCoordinator.process_query(sessionId, query, context);
  
  return response;
}

/**
 * Get suggested questions for a document
 * 
 * @param {string} documentId - Document ID
 * @returns {Array} Suggested questions
 */
async function getSuggestedQuestions(documentId) {
  console.log(`Getting suggested questions for document ${documentId}`);
  
  // In a real implementation, this would analyze the document content
  // and generate contextually relevant questions
  
  // For now, return sample questions based on financial documents
  return [
    {
      id: `sq_${documentId}_1`,
      text: "מהם מספרי ה-ISIN המופיעים במסמך?",
      category: "מזהים"
    },
    {
      id: `sq_${documentId}_2`,
      text: "מהי התשואה השנתית המוצגת במסמך?",
      category: "ביצועים"
    },
    {
      id: `sq_${documentId}_3`,
      text: "מהי חלוקת הנכסים בתיק?",
      category: "אלוקציה"
    },
    {
      id: `sq_${documentId}_4`,
      text: "מהי החשיפה המטבעית של התיק?",
      category: "מטבעות"
    },
    {
      id: `sq_${documentId}_5`,
      text: "מהן הנתונים הפיננסיים העיקריים במסמך?",
      category: "סיכום"
    }
  ];
}

module.exports = {
  createSession,
  getSessionHistory,
  processQuery,
  getSuggestedQuestions
};
