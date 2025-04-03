import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging
import uuid
import json

# Import your PDF processor components
from pdf_processor.extraction.text_extractor import PDFTextExtractor
from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer
from pdf_processor.tables.table_extractor import TableExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize components
text_extractor = PDFTextExtractor()
financial_analyzer = FinancialAnalyzer()
table_extractor = TableExtractor()

# In-memory data store for simplicity
documents = []

# Routes for frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    else:
        return send_from_directory('frontend/build', 'index.html')

# API routes
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{filename}")
        file.save(file_path)
        
        try:
            # Process document with your components
            logger.info(f"Processing document: {filename}")
            
            # Extract text from PDF
            document_content = text_extractor.extract_document(file_path)
            
            # Extract tables from PDF
            tables_data = table_extractor.extract_tables(file_path, None)
            
            # Check for financial content
            is_financial = any(
                text_extractor.is_potentially_financial(page_data['text']) 
                for page_data in document_content.values()
            )
            
            # Extract financial metrics
            financial_metrics = {}
            if is_financial:
                for page_num, page_data in document_content.items():
                    page_metrics = financial_analyzer.extract_financial_metrics(page_data['text'])
                    if page_metrics:
                        financial_metrics[f"page_{page_num}"] = page_metrics
            
            # Store document metadata
            doc_info = {
                'id': file_id,
                'filename': filename,
                'file_path': file_path,
                'upload_date': os.path.getmtime(file_path),
                'size': os.path.getsize(file_path),
                'page_count': len(document_content),
                'is_financial': is_financial,
                'has_tables': len(tables_data) > 0,
                'processed': True
            }
            documents.append(doc_info)
            
            return jsonify({
                'message': 'File uploaded and processed successfully',
                'document_id': file_id,
                'financial_metrics': financial_metrics,
                'table_count': len(tables_data)
            }), 200
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return jsonify({'error': f'Error processing document: {str(e)}'}), 500
    
    return jsonify({'error': 'Unknown error occurred'}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    return jsonify(documents), 200

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    doc = next((doc for doc in documents if doc['id'] == document_id), None)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    # Process document to get detailed information
    try:
        file_path = doc['file_path']
        
        # Extract text
        document_content = text_extractor.extract_document(file_path)
        
        # Extract tables
        tables_data = table_extractor.extract_tables(file_path, None)
        formatted_tables = []
        
        for page_num, tables in tables_data.items():
            for table in tables:
                # Convert table to DataFrame for detailed analysis
                df = table_extractor.convert_to_dataframe(table)
                table_type = financial_analyzer.classify_table(df)
                
                # Analyze financial table if possible
                table_analysis = {}
                if table_type in ["income_statement", "balance_sheet", "cash_flow", "ratios"]:
                    table_analysis = financial_analyzer.analyze_financial_table(df, table_type)
                
                formatted_tables.append({
                    'page': page_num,
                    'id': table['id'],
                    'headers': table.get('header', []),
                    'rows': table.get('rows', []),
                    'row_count': table.get('row_count', 0),
                    'col_count': table.get('col_count', 0),
                    'type': table_type,
                    'analysis': table_analysis
                })
        
        # Extract financial metrics from text
        financial_metrics = {}
        for page_num, page_data in document_content.items():
            if text_extractor.is_potentially_financial(page_data['text']):
                page_metrics = financial_analyzer.extract_financial_metrics(page_data['text'])
                if page_metrics:
                    financial_metrics[f"page_{page_num}"] = page_metrics
        
        # Prepare response
        response = {
            'document': doc,
            'text_content': {page: data['text'] for page, data in document_content.items()},
            'tables': formatted_tables,
            'financial_metrics': financial_metrics
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error retrieving document details: {str(e)}")
        return jsonify({'error': f'Error retrieving document details: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)