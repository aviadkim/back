"""API endpoints for document Q&A feature."""
from flask import Blueprint, request, jsonify
from .service import DocumentQAService

qa_bp = Blueprint('qa', __name__, url_prefix='/api/qa')
service = DocumentQAService()

def register_routes(app):
    """Register all routes for this feature"""
    app.register_blueprint(qa_bp)

@qa_bp.route('/ask', methods=['POST'])
def ask_question():
    """Ask a question about a document"""
    data = request.json
    
    if not data or 'question' not in data or 'document_id' not in data:
        return jsonify({'error': 'Question and document_id required'}), 400
    
    question = data['question']
    document_id = data['document_id']
    
    # Use the service to answer the question
    answer = service.answer_question(document_id, question)
    
    return jsonify({
        'status': 'success',
        'question': question,
        'answer': answer,
        'document_id': document_id
    })
