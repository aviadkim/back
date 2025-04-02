"""API endpoints for document upload feature."""
from flask import Blueprint, request, jsonify
from .service import DocumentUploadService

# Create blueprint for this feature
upload_bp = Blueprint('document_upload', __name__, url_prefix='/api/documents')
service = DocumentUploadService()

def register_routes(app):
    """Register all routes for this feature"""
    app.register_blueprint(upload_bp)

@upload_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload a document and queue it for processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'File must be PDF'}), 400
        
    language = request.form.get('language', 'heb+eng')
    
    # Save and process the document
    result = service.handle_upload(file, language)
    
    if result:
        return jsonify({
            'status': 'success',
            'message': 'Document uploaded successfully',
            'document_id': result['document_id'],
            'filename': result['filename']
        })
    else:
        return jsonify({'error': 'Upload failed'}), 500

@upload_bp.route('/', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    documents = service.list_documents()
    return jsonify({'documents': documents})

@upload_bp.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details"""
    document = service.get_document(document_id)
    
    if document:
        return jsonify(document)
    else:
        return jsonify({'error': 'Document not found'}), 404

@upload_bp.route('/<document_id>/financial', methods=['GET'])
def get_financial_data(document_id):
    """Get financial data for a document"""
    # This would be better in the financial_analysis feature
    # but we'll keep it here for compatibility
    financial_data = service.get_financial_data(document_id)
    
    if financial_data:
        return jsonify({'financial_data': financial_data})
    else:
        return jsonify({'error': 'Financial data not found'}), 404

@upload_bp.route('/<document_id>/advanced_analysis', methods=['GET'])
def get_advanced_analysis(document_id):
    """Get advanced analysis for a document"""
    # For now, return dummy data
    analysis = {
        'total_value': 1500000,
        'security_count': 10,
        'asset_allocation': {
            'Stocks': {'value': 800000, 'percentage': 53.3},
            'Bonds': {'value': 450000, 'percentage': 30.0},
            'Cash': {'value': 150000, 'percentage': 10.0},
            'Other': {'value': 100000, 'percentage': 6.7}
        },
        'top_holdings': [
            {'name': 'Apple Inc.', 'isin': 'US0378331005', 'market_value': 250000, 'percentage': 16.7},
            {'name': 'Microsoft Corp', 'isin': 'US5949181045', 'market_value': 200000, 'percentage': 13.3},
            {'name': 'Amazon', 'isin': 'US0231351067', 'market_value': 180000, 'percentage': 12.0},
            {'name': 'Tesla Inc', 'isin': 'US88160R1014', 'market_value': 120000, 'percentage': 8.0},
            {'name': 'Google', 'isin': 'US02079K1079', 'market_value': 100000, 'percentage': 6.7}
        ]
    }
    
    return jsonify({'status': 'success', 'analysis': analysis})

@upload_bp.route('/<document_id>/custom_table', methods=['POST'])
def generate_custom_table(document_id):
    """Generate a custom table for a document"""
    spec = request.json
    
    if not spec or 'columns' not in spec:
        return jsonify({'error': 'Table specification required'}), 400
    
    # For now, return dummy data
    columns = spec['columns']
    data = [
        {'isin': 'US0378331005', 'name': 'Apple Inc.', 'currency': 'USD', 'price': 175.34, 'quantity': 1425, 'market_value': 250000},
        {'isin': 'US5949181045', 'name': 'Microsoft Corp', 'currency': 'USD', 'price': 380.55, 'quantity': 525, 'market_value': 200000},
        {'isin': 'US0231351067', 'name': 'Amazon', 'currency': 'USD', 'price': 178.35, 'quantity': 1009, 'market_value': 180000},
        {'isin': 'US88160R1014', 'name': 'Tesla Inc', 'currency': 'USD', 'price': 173.80, 'quantity': 690, 'market_value': 120000},
        {'isin': 'US02079K1079', 'name': 'Google', 'currency': 'USD', 'price': 145.62, 'quantity': 687, 'market_value': 100000}
    ]
    
    # Filter data if needed
    if 'filters' in spec:
        filtered_data = []
        for item in data:
            match = True
            for field, value in spec['filters'].items():
                if field in item and str(item[field]).lower() != str(value).lower():
                    match = False
                    break
            if match:
                filtered_data.append(item)
        data = filtered_data
    
    # Sort if needed
    if 'sort_by' in spec and spec['sort_by'] in columns:
        sort_key = spec['sort_by']
        reverse = spec.get('sort_order', 'asc').lower() == 'desc'
        data = sorted(data, key=lambda x: x.get(sort_key, ''), reverse=reverse)
    
    # Filter columns
    result_data = []
    for item in data:
        result_item = {}
        for column in columns:
            if column in item:
                result_item[column] = item[column]
            else:
                result_item[column] = None
        result_data.append(result_item)
    
    return jsonify({'status': 'success', 'table': {'columns': columns, 'data': result_data}})
