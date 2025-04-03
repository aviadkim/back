"""
Storage client utility for handling document uploads to AWS Lightsail Object Storage
or local filesystem based on environment.
"""
import os
import logging
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

class StorageClient:
    """
    A client for handling document storage, either in a local filesystem
    or in AWS Lightsail Object Storage (compatible with S3).
    """
    
    def __init__(self):
        """Initialize the storage client based on environment."""
        self.use_cloud_storage = os.environ.get('USE_CLOUD_STORAGE', 'False').lower() == 'true'
        self.local_upload_dir = os.path.join(os.getcwd(), 'uploads')
        
        # Create local upload directory if it doesn't exist
        os.makedirs(self.local_upload_dir, exist_ok=True)
        
        if self.use_cloud_storage:
            self._init_cloud_storage()
            logger.info("Using AWS Lightsail Object Storage for document uploads")
        else:
            logger.info("Using local filesystem for document uploads")
    
    def _init_cloud_storage(self):
        """Initialize cloud storage client."""
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError, ClientError
            
            # Get bucket configuration from environment variables or AWS SSM
            from utils.aws_helpers import get_secret
            
            self.bucket_name = os.environ.get('BUCKET_NAME') or get_secret('BUCKET_NAME')
            self.bucket_region = os.environ.get('BUCKET_REGION') or get_secret('BUCKET_REGION') or 'us-east-1'
            self.access_key_id = os.environ.get('BUCKET_ACCESS_KEY_ID') or get_secret('BUCKET_ACCESS_KEY_ID')
            self.secret_access_key = os.environ.get('BUCKET_SECRET_ACCESS_KEY') or get_secret('BUCKET_SECRET_ACCESS_KEY')
            
            if not self.bucket_name:
                logger.warning("Bucket name not found. Falling back to local storage.")
                self.use_cloud_storage = False
                return
            
            # Create S3 client (compatible with Lightsail object storage)
            self.s3_client = boto3.client(
                's3',
                region_name=self.bucket_region,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                endpoint_url=f'https://s3.{self.bucket_region}.amazonaws.com'
            )
            
            # Test connection
            try:
                self.s3_client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
                logger.info(f"Successfully connected to bucket: {self.bucket_name}")
            except (NoCredentialsError, ClientError) as e:
                logger.error(f"Failed to connect to AWS bucket: {e}")
                self.use_cloud_storage = False
                
        except ImportError:
            logger.warning("boto3 not installed. Falling back to local storage.")
            self.use_cloud_storage = False
        except Exception as e:
            logger.error(f"Error initializing cloud storage: {e}")
            self.use_cloud_storage = False
    
    def save_file(self, file_obj, filename=None, folder=None):
        """
        Save a file to storage (cloud or local).
        
        Args:
            file_obj: File-like object to save
            filename: Optional filename to use (will be sanitized)
            folder: Optional folder path to save within (e.g., 'invoices')
            
        Returns:
            dict with file info including path, url, and metadata
        """
        if filename is None:
            # Generate a unique filename if none provided
            original_filename = getattr(file_obj, 'filename', None)
            if original_filename:
                filename = secure_filename(original_filename)
            else:
                # Generate a random filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                filename = f"{timestamp}-{uuid.uuid4().hex[:8]}.bin"
        else:
            filename = secure_filename(filename)
        
        # Add folder prefix if provided
        if folder:
            folder = folder.strip('/')
            file_path = f"{folder}/{filename}"
        else:
            file_path = filename
            
        # Generate a file hash for integrity checking
        file_obj.seek(0)
        file_hash = hashlib.sha256(file_obj.read()).hexdigest()
        file_obj.seek(0)
        
        # Store file in either cloud storage or local filesystem
        if self.use_cloud_storage:
            return self._save_to_cloud(file_obj, file_path, file_hash)
        else:
            return self._save_to_local(file_obj, file_path, file_hash)
    
    def _save_to_cloud(self, file_obj, file_path, file_hash):
        """Save a file to cloud storage."""
        try:
            # Upload the file to the bucket
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_path,
                ExtraArgs={
                    'ContentType': getattr(file_obj, 'content_type', 'application/octet-stream'),
                    'Metadata': {
                        'sha256': file_hash,
                        'uploaded_at': datetime.now().isoformat()
                    }
                }
            )
            
            # Generate the URL for accessing the file
            url = f"https://s3.{self.bucket_region}.amazonaws.com/{self.bucket_name}/{file_path}"
            
            return {
                'success': True,
                'storage_type': 'cloud',
                'bucket': self.bucket_name,
                'path': file_path,
                'url': url,
                'hash': file_hash,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error saving to cloud storage: {e}")
            # Fall back to local storage if cloud storage fails
            return self._save_to_local(file_obj, file_path, file_hash)
    
    def _save_to_local(self, file_obj, file_path, file_hash):
        """Save a file to local filesystem."""
        try:
            # Create directory structure if it doesn't exist
            full_path = os.path.join(self.local_upload_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Save the file
            file_obj.seek(0)
            with open(full_path, 'wb') as f:
                f.write(file_obj.read())
            
            # Generate a relative URL for the file
            url = f"/uploads/{file_path}"
            
            return {
                'success': True,
                'storage_type': 'local',
                'path': file_path,
                'full_path': full_path,
                'url': url,
                'hash': file_hash,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error saving to local storage: {e}")
            return {
                'success': False,
                'error': str(e),
                'path': file_path
            }
    
    def get_file(self, file_path):
        """
        Retrieve a file from storage.
        
        Args:
            file_path: Path of the file to retrieve
            
        Returns:
            File content as bytes, or None if the file doesn't exist
        """
        if self.use_cloud_storage:
            return self._get_from_cloud(file_path)
        else:
            return self._get_from_local(file_path)
    
    def _get_from_cloud(self, file_path):
        """Retrieve a file from cloud storage."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Error retrieving file from cloud storage: {e}")
            return None
    
    def _get_from_local(self, file_path):
        """Retrieve a file from local filesystem."""
        try:
            full_path = os.path.join(self.local_upload_dir, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"Error retrieving file from local storage: {e}")
            return None
    
    def delete_file(self, file_path):
        """
        Delete a file from storage.
        
        Args:
            file_path: Path of the file to delete
            
        Returns:
            Boolean indicating success or failure
        """
        if self.use_cloud_storage:
            return self._delete_from_cloud(file_path)
        else:
            return self._delete_from_local(file_path)
    
    def _delete_from_cloud(self, file_path):
        """Delete a file from cloud storage."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting file from cloud storage: {e}")
            return False
    
    def _delete_from_local(self, file_path):
        """Delete a file from local filesystem."""
        try:
            full_path = os.path.join(self.local_upload_dir, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file from local storage: {e}")
            return False
    
    def list_files(self, prefix=None):
        """
        List files in storage.
        
        Args:
            prefix: Optional path prefix to filter files
            
        Returns:
            List of file information dictionaries
        """
        if self.use_cloud_storage:
            return self._list_cloud_files(prefix)
        else:
            return self._list_local_files(prefix)
    
    def _list_cloud_files(self, prefix=None):
        """List files in cloud storage."""
        try:
            params = {'Bucket': self.bucket_name}
            if prefix:
                params['Prefix'] = prefix
                
            response = self.s3_client.list_objects_v2(**params)
            
            if 'Contents' not in response:
                return []
                
            files = []
            for obj in response['Contents']:
                files.append({
                    'storage_type': 'cloud',
                    'path': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': f"https://s3.{self.bucket_region}.amazonaws.com/{self.bucket_name}/{obj['Key']}"
                })
            return files
        except Exception as e:
            logger.error(f"Error listing files from cloud storage: {e}")
            return []
    
    def _list_local_files(self, prefix=None):
        """List files in local filesystem."""
        try:
            files = []
            base_path = self.local_upload_dir
            
            if prefix:
                base_path = os.path.join(base_path, prefix)
                
            if not os.path.exists(base_path):
                return []
                
            for root, _, filenames in os.walk(base_path):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, self.local_upload_dir)
                    
                    stats = os.stat(full_path)
                    files.append({
                        'storage_type': 'local',
                        'path': rel_path,
                        'full_path': full_path,
                        'size': stats.st_size,
                        'last_modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                        'url': f"/uploads/{rel_path}"
                    })
            return files
        except Exception as e:
            logger.error(f"Error listing files from local storage: {e}")
            return []

# Create a singleton instance for application-wide use
storage = StorageClient()
