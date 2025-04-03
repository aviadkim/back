"""
Routes for Table Extraction Feature
"""

from flask import request, jsonify, send_file
from . import table_extraction_bp
from .service import get_document_tables, get_table_by_id, generate_table_view, export_table

@table_extraction_bp.route('/api/tables/document/<document_id>', methods=['GET'])
def get_tables(document_id):
    """Get tables from a document"""
    try:
        page = request.args.get('page')
        if page:
            page = int(page)
        
        tables = get_document_tables(document_id, page)
        
        return jsonify({
            'status': 'success',
            'document_id': document_id,
            'tables': tables
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@table_extraction_bp.route('/api/tables/<table_id>', methods=['GET'])
def get_table(table_id):
    """Get a table by ID"""
    try:
        table = get_table_by_id(table_id)
        
        if not table:
            return jsonify({
                'status': 'error',
                'message': 'Table not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'table': table
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@table_extraction_bp.route('/api/tables/generate', methods=['POST'])
def generate_view():
    """Generate a specialized table view"""
    try:
        data = request.json
        document_id = data.get('documentId')
        table_ids = data.get('tableIds')
        view_format = data.get('format', 'default')
        options = data.get('options', {})
        
        if not document_id or not table_ids or not isinstance(table_ids, list):
            return jsonify({
                'status': 'error',
                'message': 'Invalid request parameters'
            }), 400
        
        table_view = generate_table_view(document_id, table_ids, view_format, options)
        
        return jsonify({
            'status': 'success',
            'table': table_view
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@table_extraction_bp.route('/api/tables/export', methods=['POST'])
def export():
    """Export table data in various formats"""
    try:
        data = request.json
        document_id = data.get('documentId')
        table_id = data.get('tableId')
        export_format = data.get('format', 'csv')
        
        if not document_id or not table_id:
            return jsonify({
                'status': 'error',
                'message': 'Document ID and table ID are required'
            }), 400
        
        result = export_table(document_id, table_id, export_format)
        
        # Set appropriate headers based on format
        if export_format == 'csv':
            return result, 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename="{table_id}.csv"'
            }
        elif export_format == 'json':
            return result, 200, {
                'Content-Type': 'application/json'
            }
        elif export_format == 'xlsx':
            return send_file(
                result,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"{table_id}.xlsx"
            )
        
        return result
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
