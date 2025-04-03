import boto3
import os
import logging
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config.aws_config import TEXTRACT_REGION

class TextractService:
    """שירות OCR מבוסס AWS Textract"""

    def __init__(self):
        self.textract = boto3.client(
            'textract',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=TEXTRACT_REGION
        )
        self.logger = logging.getLogger(__name__)

    def extract_text_from_s3(self, bucket_name, document_key):
        """חילוץ טקסט ממסמך המאוחסן ב-S3"""
        try:
            response = self.textract.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': document_key
                    }
                }
            )

            # חילוץ טקסט מהתשובה
            text = ""
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    text += item['Text'] + "\n"

            return text
        except Exception as e:
            self.logger.error(f"Error in Textract: {str(e)}")
            raise

    def extract_text_from_file(self, file_path):
        """חילוץ טקסט מקובץ מקומי"""
        try:
            with open(file_path, 'rb') as document:
                bytes_data = document.read()

            response = self.textract.detect_document_text(
                Document={
                    'Bytes': bytes_data
                }
            )

            # חילוץ טקסט מהתשובה
            text = ""
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    text += item['Text'] + "\n"

            return text
        except Exception as e:
            self.logger.error(f"Error in Textract: {str(e)}")
            raise

    def analyze_document(self, bucket_name, document_key):
        """ניתוח מתקדם של מסמך וזיהוי טבלאות"""
        try:
            response = self.textract.analyze_document(
                Document={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': document_key
                    }
                },
                FeatureTypes=['TABLES', 'FORMS']
            )

            # חילוץ מבנה הטבלאות וטקסט
            result = {
                'text': [],
                'tables': []
            }

            # מעבר על כל הבלוקים ברשומה
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    result['text'].append(block['Text'])
                elif block['BlockType'] == 'TABLE':
                    table = self._extract_table_structure(block, response['Blocks'])
                    result['tables'].append(table)

            result['text'] = "\n".join(result['text'])
            return result
        except Exception as e:
            self.logger.error(f"Error in Textract analysis: {str(e)}")
            raise

    def _extract_table_structure(self, table_block, all_blocks):
        """חילוץ מבנה טבלה מבלוקים של Textract"""
        table_id = table_block['Id']
        cells = []

        # איסוף כל תאי הטבלה
        for block in all_blocks:
            if block['BlockType'] == 'CELL' and 'Relationships' in block:
                for relationship in block['Relationships']:
                    if relationship['Type'] == 'CHILD':
                        parent_id = block.get('Id')
                        if parent_id:
                            cell_contents = []
                            for child_id in relationship['Ids']:
                                for child_block in all_blocks:
                                    if child_block['Id'] == child_id and child_block['BlockType'] == 'WORD':
                                        cell_contents.append(child_block['Text'])
                            if block.get('RowIndex') and block.get('ColumnIndex'):
                                cells.append({
                                    'row_index': block['RowIndex'],
                                    'column_index': block['ColumnIndex'],
                                    'text': ' '.join(cell_contents)
                                })

        # ארגון התאים למבנה שורות ועמודות
        max_row = max([cell['row_index'] for cell in cells]) if cells else 0
        max_col = max([cell['column_index'] for cell in cells]) if cells else 0

        # יצירת מטריצה ריקה
        table_data = [['' for _ in range(max_col)] for _ in range(max_row)]

        # מילוי המטריצה בתוכן התאים
        for cell in cells:
            row = cell['row_index'] - 1  # אינדקסים מתחילים מ-1 ב-Textract
            col = cell['column_index'] - 1
            table_data[row][col] = cell['text']

        # הפרדה בין כותרת ושורות
        header = table_data[0] if table_data else []
        rows = table_data[1:] if len(table_data) > 1 else []

        return {
            'id': table_id,
            'header': header,
            'rows': rows
        }