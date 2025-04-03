from flask import Blueprint, request, jsonify

# Placeholder imports - adjust based on actual project structure
try:
    from services import document_service  # Assuming a global/shared document service
except ImportError:
    print("Warning: document_service not found at services.document_service. Using placeholder.")

    class MockDocumentService:
        _mock_docs = {
            "doc1": {"id": "doc1", "content": "Doc 1 content.", "type": "Report", "title": "Document One"},
            "doc2": {"id": "doc2", "content": "Doc 2 content.", "type": "Letter", "title": "Document Two"},
        }

        def get_document(self, document_id):
            print(f"Warning: Using mock document_service.get_document for ID: {document_id}")
            return self._mock_docs.get(document_id)

    document_service = MockDocumentService()

# Import services for this feature
try:
    from features.financial_insights.services import financial_analysis_service
    # Import the placeholder data service needed by the analysis service
    from features.financial_insights.services import financial_data_service
except ImportError:
    print("Error: Failed to import financial_insights services.")
    # Define dummy modules/functions if import fails

    class MockAnalysisService:

        def analyze_health(self, data):
            return {"error": "Analysis service unavailable"}

        def get_comparison_data(self, doc, period):
            return {}

        def compare_performance(self, current, comp):
            return {"error": "Analysis service unavailable"}

    class MockDataService:

        def get_financial_data(self, doc_id):
            return None

    financial_analysis_service = MockAnalysisService()
    financial_data_service = MockDataService()


insights_routes = Blueprint('insights', __name__, url_prefix='/api/analysis')


@insights_routes.route('/financial-health', methods=['GET'])
def analyze_financial_health_route():
    """
    API endpoint to analyze financial health for a document.
    Accepts 'documentId' query parameter.
    """
    document_id = request.args.get('documentId')
    if not document_id:
        return jsonify({"error": "Missing documentId query parameter"}), 400

    analyzer = financial_analysis_service  # Assuming singleton or module-level instance
    data_service = financial_data_service

    if not analyzer or not data_service:
        return jsonify({"error": "Financial analysis services not available"}), 500

    try:
        # Get document data (using placeholder service)
        # In a real app, this might involve more complex data fetching/aggregation
        financial_data = data_service.get_financial_data(document_id)
        if not financial_data:
            # Could also check document_service.get_document here if needed
            return jsonify({"error": f"Financial data for document ID {document_id} not found or could not be generated"}), 404

        # Analyze financial health
        health_assessment = analyzer.analyze_health(financial_data)

        return jsonify(health_assessment)
    except Exception as e:
        print(f"Error analyzing financial health for document {document_id}: {e}")
        return jsonify({"error": "Failed to analyze financial health"}), 500


@insights_routes.route('/performance-comparison', methods=['GET'])
def compare_performance_route():
    """
    API endpoint to compare financial performance across periods.
    Accepts 'documentId' and 'period' query parameters.
    """
    document_id = request.args.get('documentId')
    comparison_period = request.args.get('period')

    if not document_id:
        return jsonify({"error": "Missing documentId query parameter"}), 400
    if not comparison_period:
        return jsonify({"error": "Missing period query parameter"}), 400

    analyzer = financial_analysis_service
    data_service = financial_data_service  # Needed to get current data
    doc_service = document_service  # Needed for context for comparison data

    if not analyzer or not data_service or not doc_service:
        return jsonify({"error": "Financial analysis services not available"}), 500

    try:
        # Get current document context and financial data
        document = doc_service.get_document(document_id)
        current_financial_data = data_service.get_financial_data(document_id)

        if not document or not current_financial_data:
            return jsonify({"error": f"Data for document ID {document_id} not found"}), 404

        # Get comparison data (using placeholder service)
        comparison_data = analyzer.get_comparison_data(document, comparison_period)
        if not comparison_data:
            return jsonify({"error": f"Comparison data for period '{comparison_period}' not available"}), 404

        # Perform comparison
        comparison_results = analyzer.compare_performance(current_financial_data, comparison_data)

        return jsonify(comparison_results)
    except Exception as e:
        print(f"Error comparing performance for document {document_id} against {comparison_period}: {e}")
        return jsonify({"error": "Failed to compare performance"}), 500

# Renamed functions to avoid potential name collisions