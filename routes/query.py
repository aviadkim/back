# routes/query.py
from flask import Blueprint, request, jsonify
import logging
from transformers import pipeline
from pymongo import MongoClient
import re

# Import configuration (assuming configuration.py exists in config/)
# Adjust the import path if necessary based on your project structure
try:
    from config.configuration import MONGO_URI
except ImportError:
    # Fallback or default value if config is not found
    # Replace with your actual MongoDB URI or handle appropriately
    MONGO_URI = "mongodb://localhost:27017/" 
    logging.warning("MONGO_URI not found in config. Using default.")


# Create blueprint for query API
query_api = Blueprint('query_api', __name__)
logger = logging.getLogger(__name__)

# Placeholder for NLP pipeline (replace with actual model loading)
# Example: Using a question-answering pipeline
try:
    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
except Exception as e:
    logger.error(f"Failed to load QA pipeline: {e}")
    qa_pipeline = None # Handle cases where the model fails to load

# MongoDB connection
def get_db():
    """Establishes connection to MongoDB."""
    try:
        client = MongoClient(MONGO_URI)
        # Consider adding database name selection here if needed
        # return client.your_database_name 
        return client.financial_documents # Defaulting based on original code
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise # Re-raise the exception to handle it upstream

# Natural language query endpoint
@query_api.route('/document/<document_id>/query', methods=['POST'])
def query_document(document_id):
    """Process natural language query about a document."""
    if not qa_pipeline:
        return jsonify({
            'status': 'error',
            'message': 'NLP Query processing service is unavailable.'
        }), 503 # Service Unavailable

    try:
        # Get query from request
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No query provided'
            }), 400
        
        query = data['query']
        
        # Get document from database
        db = get_db()
        # Assuming 'documents' collection and '_id' field
        # You might need to adjust based on your actual schema
        document = db.documents.find_one({"_id": document_id}) 
        
        if not document:
            return jsonify({
                'status': 'error',
                'message': 'Document not found'
            }), 404
        
        # Process query using the document content
        # Assuming the document has a 'text_content' field or similar
        # Adjust the field name based on your document structure
        context = document.get('text_content', '') 
        if not context:
             return jsonify({
                'status': 'error',
                'message': 'Document content is empty or missing.'
            }), 404

        result = process_query_with_nlp(query, context)
        
        return jsonify({
            'status': 'success',
            'data': result,
            'message': 'Query processed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error processing query for document {document_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error processing query: {str(e)}"
        }), 500

def process_query_with_nlp(query, context):
    """Process a natural language query against document context using NLP."""
    # Use the loaded QA pipeline
    if qa_pipeline:
        try:
            result = qa_pipeline(question=query, context=context)
            # Format the result as needed
            return {
                'answer': result.get('answer', 'Could not find an answer.'),
                'score': result.get('score', 0.0),
                'start': result.get('start'),
                'end': result.get('end')
            }
        except Exception as e:
            logger.error(f"Error during NLP query processing: {e}")
            return {'answer': 'Error processing query with NLP model.', 'score': 0.0}
    else:
        # Fallback if pipeline isn't loaded
        return {'answer': 'NLP model not available.', 'score': 0.0}

# Example of how to register this blueprint in your main Flask app (e.g., app.py)
# from routes.query import query_api
# app.register_blueprint(query_api, url_prefix='/api') # Adjust url_prefix as needed