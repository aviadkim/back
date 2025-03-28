from flask import Blueprint, request, jsonify

# Assuming document_service is available globally or imported correctly
# Placeholder import
try:
    from services import document_service  # Placeholder path
except ImportError:
    print("Warning: document_service not found at services.document_service. Using placeholder.")

    class MockDocumentService:
        _mock_docs = {
            "doc1": {"id": "doc1", "content": "This is the content of document 1.", "type": "Report", "title": "Document One"},
            "doc2": {"id": "doc2", "content": "Document 2 contains different information.", "type": "Letter", "title": "Document Two"},
            "doc3": {"id": "doc3", "content": "A third document for comparison purposes.", "type": "Report", "title": "Document Three"},
        }

        def get_document(self, document_id):
            print(f"Warning: Using mock document_service.get_document for ID: {document_id}")
            return self._mock_docs.get(document_id)  # Return None if not found

    document_service = MockDocumentService()

# Import the service for this feature
try:
    from features.summarization.services.summarization_service import get_summarizer
except ImportError:
    print("Error: Failed to import get_summarizer from summarization service.")
    # Define a dummy function if import fails

    def get_summarizer():
        return None

summarization_routes = Blueprint('summarization', __name__, url_prefix='/api/documents')


@summarization_routes.route('/<string:document_id>/summary', methods=['GET'])
def generate_summary_route(document_id):
    """
    API endpoint to generate a summary for a specific document.
    Accepts 'format' and 'maxLength' query parameters.
    """
    summarizer = get_summarizer()
    if not summarizer:
        return jsonify({"error": "Summarizer service not available"}), 500

    format_type = request.args.get('format', 'narrative')
    try:
        max_length = int(request.args.get('maxLength', 250))
    except ValueError:
        return jsonify({"error": "Invalid maxLength parameter, must be an integer."}), 400

    try:
        # Get document
        document = document_service.get_document(document_id)
        if not document:
            return jsonify({"error": f"Document with ID {document_id} not found"}), 404

        # Generate summary
        summary_result = summarizer.generate_summary(document, format_type, max_length)

        return jsonify(summary_result)
    except Exception as e:
        print(f"Error generating summary for document {document_id}: {e}")
        return jsonify({"error": f"Failed to generate summary for document {document_id}"}), 500


@summarization_routes.route('/compare-summary', methods=['GET'])
def compare_documents_route():
    """
    API endpoint to generate a comparative summary for multiple documents.
    Accepts 'documentIds' query parameter (comma-separated).
    """
    summarizer = get_summarizer()
    if not summarizer:
        return jsonify({"error": "Summarizer service not available"}), 500

    document_ids_str = request.args.get('documentIds', '')
    if not document_ids_str:
        return jsonify({"error": "Missing documentIds query parameter"}), 400

    document_ids = [doc_id.strip() for doc_id in document_ids_str.split(',') if doc_id.strip()]

    if len(document_ids) < 2:
        return jsonify({"error": "At least two document IDs are required for comparison"}), 400

    try:
        # Get documents
        documents = []
        missing_docs = []
        for doc_id in document_ids:
            document = document_service.get_document(doc_id)
            if document:
                documents.append(document)
            else:
                missing_docs.append(doc_id)

        if missing_docs:
            return jsonify({"error": f"Documents not found: {', '.join(missing_docs)}"}), 404

        # Generate comparative summary
        comparison_result = summarizer.compare_documents(documents)

        return jsonify(comparison_result)
    except Exception as e:
        print(f"Error generating comparison summary for documents {document_ids}: {e}")
        # Corrected: Removed unnecessary f-string
        return jsonify({"error": "Failed to generate comparison summary"}), 500

# Renamed functions to avoid potential name collisions