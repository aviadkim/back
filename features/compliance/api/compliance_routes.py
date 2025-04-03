from flask import Blueprint, request, jsonify

# Placeholder imports - adjust based on actual project structure
try:
    from services import document_service  # Assuming a global/shared document service
except ImportError:
    print("Warning: document_service not found at services.document_service. Using placeholder.")

    class MockDocumentService:
        _mock_docs = {
            "doc1": {"id": "doc1", "content": "Doc 1 content mentioning SEC filing deadline.", "type": "Financial Report"},
            "doc2": {"id": "doc2", "content": "Doc 2 content with GDPR reference.", "type": "Policy"},
        }

        def get_document(self, document_id):
            print(f"Warning: Using mock document_service.get_document for ID: {document_id}")
            return self._mock_docs.get(document_id)

    document_service = MockDocumentService()

# Import the service for this feature
try:
    from features.compliance.services import compliance_service
except ImportError:
    print("Error: Failed to import compliance_service.")
    # Define dummy module/function if import fails

    class MockComplianceService:

        def check_compliance(self, doc, juris):
            return {"error": "Compliance service unavailable"}

        def identify_requirements(self, doc):
            return {"error": "Compliance service unavailable"}

    compliance_service = MockComplianceService()


compliance_routes = Blueprint('compliance', __name__, url_prefix='/api/compliance')


@compliance_routes.route('/check', methods=['GET'])
def check_compliance_route():
    """
    API endpoint to check document compliance against jurisdictions.
    Accepts 'documentId' and 'jurisdictions' (comma-separated) query parameters.
    """
    document_id = request.args.get('documentId')
    jurisdictions_str = request.args.get('jurisdictions', '')

    if not document_id:
        return jsonify({"error": "Missing documentId query parameter"}), 400

    # Split jurisdictions string into a list, handling empty strings
    jurisdictions = [j.strip() for j in jurisdictions_str.split(',') if j.strip()]

    checker = compliance_service  # Assuming singleton or module-level instance

    if not checker:
        return jsonify({"error": "Compliance service not available"}), 500

    try:
        # Get document
        document = document_service.get_document(document_id)
        if not document:
            return jsonify({"error": f"Document with ID {document_id} not found"}), 404

        # Check compliance
        compliance_results = checker.check_compliance(document, jurisdictions)

        return jsonify(compliance_results)
    except Exception as e:
        print(f"Error checking compliance for document {document_id}: {e}")
        return jsonify({"error": "Failed to check compliance"}), 500


@compliance_routes.route('/requirements', methods=['GET'])
def identify_requirements_route():
    """
    API endpoint to identify regulatory requirements mentioned in a document.
    Accepts 'documentId' query parameter.
    """
    document_id = request.args.get('documentId')
    if not document_id:
        return jsonify({"error": "Missing documentId query parameter"}), 400

    checker = compliance_service

    if not checker:
        return jsonify({"error": "Compliance service not available"}), 500

    try:
        # Get document
        document = document_service.get_document(document_id)
        if not document:
            return jsonify({"error": f"Document with ID {document_id} not found"}), 404

        # Identify requirements
        requirements_results = checker.identify_requirements(document)

        return jsonify(requirements_results)
    except Exception as e:
        print(f"Error identifying requirements for document {document_id}: {e}")
        return jsonify({"error": "Failed to identify requirements"}), 500

# Renamed functions to avoid potential name collisions