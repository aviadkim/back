import os
import logging
import uuid
import tempfile
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from services.aws.s3_service import S3Service
from services.aws.textract_service import TextractService
from services.aws.dynamodb_service import DynamoDBService
from services.aws.ai_service import AIService
from pdf_processor.aws.aws_table_extractor import AWSTableExtractor

class AWSPDFProcessor:
    """מעבד PDF המשתמש בשירותי AWS"""

    def __init__(self):
        self.s3_service = S3Service()
        self.textract_service = TextractService()
        self.dynamodb_service = DynamoDBService()
        self.ai_service = AIService()
        self.table_extractor = AWSTableExtractor()
        self.logger = logging.getLogger(__name__)

    def process_document(self, file_path, language="auto"):
        """עיבוד מסמך מלא"""
        try:
            # יצירת מזהה ייחודי
            document_id = str(uuid.uuid4())
            original_filename = os.path.basename(file_path)

            # העלאה ל-S3
            s3_key = self.s3_service.upload_document(file_path, document_id, original_filename)

            # שמירת מטא-נתונים התחלתיים
            metadata = {
                'id': document_id,
                'filename': original_filename,
                's3_path': s3_key,
                'upload_date': datetime.now().isoformat(),
                'language': language,
                'status': 'processing'
            }
            self.dynamodb_service.save_document_metadata(metadata)

            # עיבוד המסמך בתהליך נפרד (במערכת אמיתית)
            self._process_document_async(document_id, s3_key, language)

            return {
                'document_id': document_id,
                's3_key': s3_key,
                'status': 'processing'
            }
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            raise

    def _process_document_async(self, document_id, s3_key, language):
        """עיבוד מסמך (במערכת אמיתית יהיה אסינכרוני)"""
        try:
            # חילוץ טקסט
            textract_result = self.textract_service.analyze_document(
                self.s3_service.bucket_name,
                s3_key
            )

            # חילוץ טבלאות
            tables = self.table_extractor.extract_tables(
                self.s3_service.bucket_name,
                s3_key
            )

            # ניתוח התוכן באמצעות AI
            ai_analysis = self.ai_service.analyze_text(textract_result['text'])

            # שמירת התוצאות
            processed_data = {
                'text_content': textract_result['text'],
                'tables': tables,
                'ai_analysis': ai_analysis
            }

            self.dynamodb_service.save_processed_data(document_id, processed_data)

            # עדכון סטטוס
            self.dynamodb_service.update_document_status(document_id, 'completed')

            return True
        except Exception as e:
            self.logger.error(f"Error in async processing: {str(e)}")
            self.dynamodb_service.update_document_status(document_id, 'error', str(e))
            raise

    def get_document_contents(self, document_id):
        """קבלת תוכן המסמך המעובד"""
        try:
            # קבלת מטא-נתונים
            metadata = self.dynamodb_service.get_document(document_id)
            if not metadata:
                raise Exception(f"Document not found: {document_id}")

            # בדיקת סטטוס
            if metadata.get('status') != 'completed':
                return {
                    'metadata': metadata,
                    'processing_status': metadata.get('status'),
                    'message': f"Document is not ready yet. Status: {metadata.get('status')}"
                }

            # קבלת נתונים מעובדים
            processed_data = self.dynamodb_service.get_processed_data(document_id)

            # קבלת URL לגישה למסמך
            document_url = self.s3_service.get_document_url(metadata.get('s3_path'))

            return {
                'metadata': metadata,
                'processed_data': processed_data,
                'document_url': document_url
            }

        except Exception as e:
            self.logger.error(f"Error getting document contents: {str(e)}")
            raise

    def ask_question_about_document(self, document_id, question):
        """שאל שאלה על המסמך"""
        try:
            # קבלת תוכן המסמך
            document_contents = self.get_document_contents(document_id)

            # לקיחת הטקסט המעובד והניתוח
            text_content = document_contents.get('processed_data', {}).get('text_content', '')
            ai_analysis = document_contents.get('processed_data', {}).get('ai_analysis', {})

            # יצירת הקשר מהתוכן והניתוח
            context = f"""
            Document Text:
            {text_content[:4000]}

            Document Analysis:
            {str(ai_analysis)}
            """

            # שאילת השאלה
            answer = self.ai_service.ask_question(question, context)

            return {
                'document_id': document_id,
                'question': question,
                'answer': answer
            }

        except Exception as e:
            self.logger.error(f"Error asking question: {str(e)}")
            raise