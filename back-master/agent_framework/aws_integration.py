import os
import logging
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from services.aws.s3_service import S3Service
from services.aws.dynamodb_service import DynamoDBService
from services.aws.textract_service import TextractService
from services.aws.ai_service import AIService
from pdf_processor.aws.aws_pdf_processor import AWSPDFProcessor
from pdf_processor.aws.aws_table_extractor import AWSTableExtractor
from config.aws_config import USE_AWS_STORAGE, USE_AWS_OCR, USE_CLOUD_AI

class AWSAgentIntegration:
    """מודול אינטגרציה בין סוכני AI לשירותי AWS"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # יצירת מופעים של השירותים
        self.s3_service = S3Service()
        self.dynamodb_service = DynamoDBService()
        self.textract_service = TextractService()
        self.ai_service = AIService()
        self.pdf_processor = AWSPDFProcessor()
        self.table_extractor = AWSTableExtractor()

        self.logger.info("AWS Agent Integration initialized")

        # בדיקת דגלי תכונות
        self.use_aws_storage = USE_AWS_STORAGE
        self.use_aws_ocr = USE_AWS_OCR
        self.use_cloud_ai = USE_CLOUD_AI

        self.logger.info(f"Feature flags: Storage={self.use_aws_storage}, OCR={self.use_aws_ocr}, AI={self.use_cloud_ai}")

    def process_document(self, file_path, document_id=None, language="auto"):
        """עיבוד מסמך באמצעות שירותי AWS"""
        try:
            # עיבוד המסמך
            result = self.pdf_processor.process_document(file_path, language)

            self.logger.info(f"Document processed with AWS: {result['document_id']}")
            return result

        except Exception as e:
            self.logger.error(f"Error in AWS document processing: {str(e)}")
            raise

    def get_document_data(self, document_id):
        """קבלת נתוני מסמך מעובד"""
        try:
            result = self.pdf_processor.get_document_contents(document_id)
            return result
        except Exception as e:
            self.logger.error(f"Error getting document data: {str(e)}")
            raise

    def ask_question(self, document_id, question):
        """שאילת שאלה על מסמך"""
        try:
            result = self.pdf_processor.ask_question_about_document(document_id, question)
            return result
        except Exception as e:
            self.logger.error(f"Error asking question: {str(e)}")
            raise

    def extract_tables(self, document_id):
        """חילוץ טבלאות ממסמך"""
        try:
            document = self.dynamodb_service.get_document(document_id)
            if not document:
                raise ValueError(f"Document not found: {document_id}")

            s3_path = document.get('s3_path')
            tables = self.table_extractor.extract_tables(
                self.s3_service.bucket_name,
                s3_path
            )

            return tables
        except Exception as e:
            self.logger.error(f"Error extracting tables: {str(e)}")
            raise