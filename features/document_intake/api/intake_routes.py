from flask import Blueprint, request, jsonify

# Assuming pdf_processor is available globally or imported correctly
# This might need adjustment based on actual project structure
# For now, adding a placeholder import
try:
    from utils import pdf_processor  # Placeholder path
except ImportError:
    print("Warning: pdf_processor not found at utils.pdf_processor. Using placeholder.")

    class MockPdfProcessor:
        def extract_text(self, file):
            print("Warning: Using mock pdf_processor.extract_text")
            # Simulate reading some text for testing purposes
            try:
                return file.read(2000).decode('utf-8', errors='ignore')
            except Exception:
                return "Mock PDF text content."
    pdf_processor = MockPdfProcessor()

# Assuming document_service is available globally or imported correctly
# Placeholder import
try:
    from services import document_service  # Placeholder path
except ImportError:
    print("Warning: document_service not found at services.document_service. Using placeholder.")

    class MockDocumentService:
        def get_document(self, document_id):
            print(f"Warning: Using mock document_service.get_document for ID: {document_id}")
            # Return a mock document structure
            return {"id": document_id, "content": "Mock document content from service.", "type": "MockType"}
    document_service = MockDocumentService()


# Import the service for this feature
try:
    from features.document_intake.services.document_classifier_service import get_classifier
except ImportError:
    print("Error: Failed to import get_classifier from document_intake service.")
    # Define a dummy function if import fails

    def get_classifier():
        return None

intake_routes = Blueprint('intake', __name__, url_prefix='/api/documents')


@intake_routes.route('/classify', methods=['POST'])
def classify_document():
    """
    API endpoint to classify an uploaded document.
    Expects a file named 'file' in the multipart/form-data.
    """
    classifier = get_classifier()
    if not classifier:
        return jsonify({"error": "Classifier service not available"}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            # Use pdf_processor to extract text
            # Ensure pdf_processor handles file-like objects correctly
            document_text = pdf_processor.extract_text(file.stream)  # Pass the stream

            # Classify document
            document_type, confidence, metadata = classifier.classify(document_text)

            return jsonify({
                "document_type": document_type,
                "confidence": confidence,
                "suggested_metadata": metadata
            })
        except Exception as e:
            print(f"Error processing file for classification: {e}")
            # Consider more specific error logging/handling
            return jsonify({"error": "Failed to process document for classification"}), 500
    else:
        # This case should ideally be caught by filename check, but included for safety
        return jsonify({"error": "Invalid file provided"}), 400


@intake_routes.route('/<string:document_id>/validate', methods=['GET'])
def validate_document_route(document_id):
    """
    API endpoint to validate a document based on its ID.
    """
    classifier = get_classifier()
    if not classifier:
        return jsonify({"error": "Classifier service not available"}), 500

    try:
        # Retrieve document from your service
        # Ensure document_service is correctly implemented/imported
        document = document_service.get_document(document_id)
        if not document:
            return jsonify({"error": f"Document with ID {document_id} not found"}), 404

        # Validate document completeness using the classifier service method
        validation_results = classifier.validate_document(document)

        return jsonify(validation_results)
    except Exception as e:
        print(f"Error validating document {document_id}: {e}")
        # Consider more specific error logging/handling
        return jsonify({"error": f"Failed to validate document {document_id}"}), 500

# Note: Renamed validate_document function to validate_document_route
# to avoid potential name collision if imported directly elsewhere.