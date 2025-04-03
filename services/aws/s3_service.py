import boto3
import os
import logging
from botocore.exceptions import ClientError
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config.aws_config import S3_BUCKET_NAME, S3_REGION

class S3Service:
    """שירות לאחסון וניהול מסמכים ב-S3"""

    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=S3_REGION
        )
        self.bucket_name = S3_BUCKET_NAME
        self.logger = logging.getLogger(__name__)

    def upload_document(self, file_path, doc_id, original_filename):
        """העלאת מסמך ל-S3"""
        try:
            extension = os.path.splitext(original_filename)[1]
            s3_key = f"documents/{doc_id}{extension}"

            self.s3.upload_file(
                file_path,
                self.bucket_name,
                s3_key
            )

            self.logger.info(f"File uploaded to S3: {s3_key}")
            return s3_key
        except Exception as e:
            self.logger.error(f"Error uploading to S3: {str(e)}")
            raise

    def download_document(self, s3_key, local_path):
        """הורדת מסמך מ-S3"""
        try:
            self.s3.download_file(
                self.bucket_name,
                s3_key,
                local_path
            )
            self.logger.info(f"File downloaded from S3: {s3_key} to {local_path}")
            return local_path
        except Exception as e:
            self.logger.error(f"Error downloading from S3: {str(e)}")
            raise

    def get_document_url(self, s3_key, expiration=3600):
        """יצירת URL זמני לגישה למסמך"""
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            self.logger.error(f"Error generating URL: {str(e)}")
            raise