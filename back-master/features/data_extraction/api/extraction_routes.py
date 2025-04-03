from flask import Blueprint, request, jsonify

# Placeholder imports - adjust based on actual project structure
try:
    from services import document_service  # Assuming a global/shared document service
except ImportError:
    print("Warning: document_service not found at services.document_service. Using placeholder.")

    class MockDocumentService:
        _mock_docs = {
            "doc1": {"id": "doc1", "content": "Doc 1 content with tables.", "type": "Report", "title": "Document One", "file_path": "/path/to/doc1.pdf"},
            "doc2": {"id": "doc2", "content": "Doc 2 content.", "type": "Letter", "title": "Document Two", "file_path": "/path/to/doc2.pdf"},
        }

        def get_document(self, document_id):
            print(f"Warning: Using mock document_service.get_document for ID: {document_id}")
            return self._mock_docs.get(document_id)

    document_service = MockDocumentService()

# Import services for this feature
try:
    from features.data_extraction.services import table_extraction_service
    from features.data_extraction.services import financial_metrics_service
except ImportError:
    print("Error: Failed to import data_extraction services.")
    # Define dummy modules/functions if import fails

    class MockTableService:
        def extract_and_store_tables(self, doc):
            return []

        def get_tables_for_document(self, doc_id):
            return []

        def get_table_by_id(self, table_id):
            return None

    class MockMetricsService:
        def calculate_metrics(self, table_data):
            return {"error": "Metrics service unavailable"}

    table_extraction_service = MockTableService()
    financial_metrics_service = MockMetricsService()


# No url_prefix needed if registered under /api/documents or /api/analysis
extraction_routes = Blueprint('extraction', __name__)


# Endpoint to extract (or retrieve) tables for a document
# Changed from GET in spec to POST to potentially trigger extraction if not done yet
@extraction_routes.route('/api/documents/<string:document_id>/tables', methods=['POST', 'GET'])
def handle_document_tables(document_id):
    """
    API endpoint to extract and/or retrieve tables for a document.
    POST: Triggers extraction if not already done (or re-extraction).
    GET: Retrieves previously extracted tables.
    """
    try:
        # Get document from your service
        document = document_service.get_document(document_id)
        if not document:
            return jsonify({"error": f"Document with ID {document_id} not found"}), 404

        if request.method == 'POST':
            # Trigger extraction and storage
            extracted_tables = table_extraction_service.extract_and_store_tables(document)
            if not extracted_tables:
                # Check if extraction failed or simply no tables found
                # For now, assume success but no tables
                print(f"No tables extracted or extraction failed for doc {document_id}")
                # Return empty list if no tables, maybe different status if error occurred
            return jsonify(extracted_tables)  # Return newly extracted tables

        elif request.method == 'GET':
            # Retrieve already extracted tables
            tables = table_extraction_service.get_tables_for_document(document_id)
            return jsonify(tables)

    except Exception as e:
        print(f"Error handling tables for document {document_id}: {e}")
        return jsonify({"error": "Failed to process tables for document"}), 500


# Endpoint to calculate financial metrics for a specific table
@extraction_routes.route('/api/analysis/financial-metrics', methods=['GET'])
def calculate_metrics_route():
    """
    API endpoint to calculate financial metrics for a specific table ID.
    Accepts 'tableId' query parameter.
    """
    table_id = request.args.get('tableId')
    if not table_id:
        return jsonify({"error": "Missing tableId query parameter"}), 400

    try:
        # Get table data using the table service
        table_data = table_extraction_service.get_table_by_id(table_id)
        if not table_data:
            return jsonify({"error": f"Table with ID {table_id} not found"}), 404

        # Calculate financial metrics using the metrics service
        metrics_result = financial_metrics_service.calculate_metrics(table_data)

        return jsonify(metrics_result)
    except Exception as e:
        print(f"Error calculating metrics for table {table_id}: {e}")
        return jsonify({"error": "Failed to calculate metrics for table"}), 500

# Renamed function to avoid potential name collisions