"""API endpoints for document export feature."""
from flask import Blueprint, request, jsonify, send_file
import os
from .service import DocumentExportService

export_bp = Blueprint('export', __name__, url_prefix='/api/export')
service = DocumentExportService()

def register_routes(app):
    """Register all routes for this feature"""
    app.register_blueprint(export_bp)

@export_bp.route('/excel/<document_id>', methods=['GET'])
def export_to_excel(document_id):
    """Export document data to Excel"""
    try:
        excel_path = service.export_document_to_excel(document_id)
        if excel_path:
            return send_file(
                excel_path,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"{document_id}_export.xlsx"
            )
        else:
            return jsonify({'error': 'Failed to generate Excel export'}), 500
    except FileNotFoundError:
        return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@export_bp.route('/formats', methods=['GET'])
def get_export_formats():
    """Get available export formats"""
    formats = service.get_available_formats()
    return jsonify({'formats': formats})
