import logging
import boto3
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config.aws_config import TEXTRACT_REGION

class AWSTableExtractor:
    """מחלץ טבלאות המשתמש ב-AWS Textract"""

    def __init__(self):
        self.textract = boto3.client(
            'textract',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=TEXTRACT_REGION
        )
        self.logger = logging.getLogger(__name__)

    def extract_tables(self, bucket_name, document_key):
        """חילוץ טבלאות ממסמך ב-S3"""
        try:
            # קריאה ל-Textract לניתוח המסמך
            response = self.textract.analyze_document(
                Document={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': document_key
                    }
                },
                FeatureTypes=['TABLES']
            )

            # מבני נתונים לאחסון טבלאות
            tables = []
            table_blocks = {}
            cells_by_table = {}

            # מעבר ראשון: זיהוי טבלאות ותאים
            for block in response['Blocks']:
                if block['BlockType'] == 'TABLE':
                    table_blocks[block['Id']] = block
                    cells_by_table[block['Id']] = []
                elif block['BlockType'] == 'CELL':
                    # מציאת לאיזו טבלה התא שייך
                    if 'Relationships' in block:
                        for relationship in block['Relationships']:
                            if relationship['Type'] == 'CHILD':
                                cell_content = self._get_cell_content(block, relationship['Ids'], response['Blocks'])
                                cell_data = {
                                    'row_index': block['RowIndex'],
                                    'column_index': block['ColumnIndex'],
                                    'text': cell_content,
                                    'id': block['Id']
                                }
                            elif relationship['Type'] == 'TABLE':
                                table_id = relationship['Ids'][0]
                                if table_id in cells_by_table:
                                    cells_by_table[table_id].append(cell_data)

            # מעבר שני: ארגון התאים לטבלאות
            for table_id, table_block in table_blocks.items():
                cells = cells_by_table.get(table_id, [])
                if cells:
                    # מציאת מספר השורות והעמודות המקסימלי
                    max_row = max([cell['row_index'] for cell in cells])
                    max_col = max([cell['column_index'] for cell in cells])

                    # יצירת מטריצה ריקה
                    table_data = [['' for _ in range(max_col)] for _ in range(max_row)]

                    # מילוי המטריצה בתוכן התאים
                    for cell in cells:
                        row = cell['row_index'] - 1  # אינדקסים מתחילים מ-1 ב-Textract
                        col = cell['column_index'] - 1
                        if 0 <= row < max_row and 0 <= col < max_col:
                            table_data[row][col] = cell['text']

                    # הפרדה בין כותרת ושורות
                    header = table_data[0] if table_data else []
                    rows = table_data[1:] if len(table_data) > 1 else []

                    # הוספת הטבלה לרשימה
                    tables.append({
                        'id': table_id,
                        'header': header,
                        'rows': rows,
                        'row_count': len(rows) + 1,  # כולל שורת כותרת
                        'col_count': max_col
                    })

            return tables

        except Exception as e:
            self.logger.error(f"Error extracting tables: {str(e)}")
            raise

    def _get_cell_content(self, cell_block, child_ids, all_blocks):
        """חילוץ תוכן התא מהבלוקים של Textract"""
        content = []

        child_blocks = [block for block in all_blocks if block['Id'] in child_ids]

        # מיון הבלוקים לפי מיקום שמאל-לימין, עליון-לתחתון
        sorted_blocks = sorted(child_blocks,
                             key=lambda b: (b['Geometry']['BoundingBox']['Top'],
                                         b['Geometry']['BoundingBox']['Left']))

        for block in sorted_blocks:
            if block['BlockType'] == 'WORD':
                content.append(block['Text'])
            elif block['BlockType'] == 'LINE':
                content.append(block['Text'])

        return ' '.join(content)