"""
Enhanced API endpoints for financial document processing
Import and use these functions in your app.py
"""

from flask import jsonify, request
import os
import json
import logging
from datetime import datetime

# Import enhanced extractors
from enhanced_financial_extractor import analyze_portfolio, generate_custom_table

logger = logging.getLogger("app")

def register_enhanced_endpoints(app):
    """Register enhanced endpoints with the Flask app"""
    
    @app.route('/api/documents/<document_id>/advanced_analysis', methods=['GET'])
    def get_document_advanced_analysis(document_id):
        """Get advanced portfolio analysis for a document"""
        try:
            # Check for financial data
            financial_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_financial.json")
            
            if not os.path.exists(financial_path):
                return jsonify({"error": "Financial data not found"}), 404
            
            # Load the financial data
            with open(financial_path, 'r', encoding='utf-8') as f:
                financial_data = json.load(f)
            
            # Convert list to dictionary keyed by ISIN if necessary
            if isinstance(financial_data, list):
                holdings_data = {item['isin']: item for item in financial_data}
            else:
                holdings_data = financial_data
            
            # Perform portfolio analysis
            analysis_results = analyze_portfolio(holdings_data)
            
            return jsonify({
                "document_id": document_id,
                "analysis": analysis_results
            }), 200
            
        except Exception as e:
            logger.error(f"Error analyzing document {document_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/documents/<document_id>/custom_table', methods=['POST'])
    def generate_document_custom_table(document_id):
        """Generate a custom table from document data"""
        try:
            # Get request data
            table_spec = request.json
            
            if not table_spec:
                return jsonify({"error": "No table specification provided"}), 400
            
            # Check for financial data
            financial_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_financial.json")
            
            if not os.path.exists(financial_path):
                return jsonify({"error": "Financial data not found"}), 404
            
            # Load the financial data
            with open(financial_path, 'r', encoding='utf-8') as f:
                financial_data = json.load(f)
            
            # Convert list to dictionary keyed by ISIN if necessary
            if isinstance(financial_data, list):
                holdings_data = {item['isin']: item for item in financial_data}
            else:
                holdings_data = financial_data
            
            # Generate custom table
            custom_table = generate_custom_table(holdings_data, table_spec)
            
            # Convert to format suitable for JSON
            table_data = {
                "columns": custom_table.columns.tolist(),
                "data": custom_table.to_dict(orient='records')
            }
            
            return jsonify({
                "document_id": document_id,
                "table": table_data
            }), 200
            
        except Exception as e:
            logger.error(f"Error generating custom table for {document_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Return the app with new endpoints
    return app
