# file: storage.py
import os
import logging
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from config import Config # Assuming AWS keys/bucket might be configured here later

logger = logging.getLogger("storage")

# --- Configuration (Ideally move to Config class later) ---
# Example: Read from environment variables or Config object
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1') # Default region
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
# --- End Configuration ---

s3_client = None

def get_s3_client():
    """Initializes and returns the S3 client."""
    global s3_client
    if s3_client is None:
        if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
            logger.warning("AWS credentials or S3 bucket name not fully configured. S3 operations will fail.")
            # Depending on requirements, could raise an error or allow fallback to local
            return None # Indicate failure to initialize

        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
            # Test connection/credentials by checking bucket existence
            s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            logger.info(f"S3 client initialized for bucket '{S3_BUCKET_NAME}' in region '{AWS_REGION}'.")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")
            s3_client = None
        except ClientError as e:
             # Handle specific errors like NoSuchBucket
             error_code = e.response.get('Error', {}).get('Code')
             if error_code == 'NoSuchBucket':
                 logger.error(f"S3 Bucket '{S3_BUCKET_NAME}' not found or access denied.")
             elif error_code == 'InvalidAccessKeyId' or error_code == 'SignatureDoesNotMatch':
                  logger.error("Invalid AWS credentials provided.")
             else:
                 logger.error(f"Failed to initialize S3 client due to ClientError: {e}")
             s3_client = None
        except Exception as e:
            logger.error(f"An unexpected error occurred initializing S3 client: {e}")
            s3_client = None
    return s3_client

def upload_file_to_s3(file_path, object_name=None):
    """
    Upload a file to the configured S3 bucket.

    :param file_path: Path to the file to upload.
    :param object_name: S3 object name. If not specified, file_path's base name is used.
    :return: S3 object key (object_name) if successful, else None.
    """
    client = get_s3_client()
    if not client:
        logger.error("S3 client not available. Cannot upload file.")
        return None
    if not S3_BUCKET_NAME:
         logger.error("S3_BUCKET_NAME not configured. Cannot upload file.")
         return None

    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        logger.info(f"Uploading '{file_path}' to S3 bucket '{S3_BUCKET_NAME}' as '{object_name}'")
        client.upload_file(file_path, S3_BUCKET_NAME, object_name)
        logger.info(f"Successfully uploaded to S3: {object_name}")
        return object_name # Return the key used
    except FileNotFoundError:
        logger.error(f"Upload failed: The file was not found at {file_path}")
        return None
    except NoCredentialsError:
        logger.error("Upload failed: AWS credentials not available.")
        return None
    except ClientError as e:
        logger.error(f"Upload failed: S3 ClientError: {e}")
        return None
    except Exception as e:
        logger.error(f"Upload failed: An unexpected error occurred: {e}")
        return None

def download_file_from_s3(object_name, destination_path):
    """
    Download a file from the configured S3 bucket.

    :param object_name: S3 object name (key).
    :param destination_path: Local path to save the downloaded file.
    :return: True if download successful, else False.
    """
    client = get_s3_client()
    if not client:
        logger.error("S3 client not available. Cannot download file.")
        return False
    if not S3_BUCKET_NAME:
         logger.error("S3_BUCKET_NAME not configured. Cannot download file.")
         return False

    try:
        logger.info(f"Downloading S3 object '{object_name}' from bucket '{S3_BUCKET_NAME}' to '{destination_path}'")
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        client.download_file(S3_BUCKET_NAME, object_name, destination_path)
        logger.info(f"Successfully downloaded '{object_name}' to '{destination_path}'")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            logger.error(f"Download failed: The object '{object_name}' does not exist in bucket '{S3_BUCKET_NAME}'.")
        else:
            logger.error(f"Download failed: S3 ClientError: {e}")
        return False
    except Exception as e:
        logger.error(f"Download failed: An unexpected error occurred: {e}")
        return False


def create_presigned_url(object_name, expiration=3600):
    """
    Generate a presigned URL to share an S3 object for temporary access (e.g., download).

    :param object_name: S3 object name (key).
    :param expiration: Time in seconds for the presigned URL to remain valid. Default 1 hour.
    :return: Presigned URL as string if successful, else None.
    """
    client = get_s3_client()
    if not client:
        logger.error("S3 client not available. Cannot create presigned URL.")
        return None
    if not S3_BUCKET_NAME:
         logger.error("S3_BUCKET_NAME not configured. Cannot create presigned URL.")
         return None

    try:
        response = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': object_name},
            ExpiresIn=expiration
        )
        logger.info(f"Generated presigned URL for '{object_name}' (expires in {expiration}s)")
        return response
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL for '{object_name}': {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred generating presigned URL: {e}")
        return None

def delete_file_from_s3(object_name):
    """
    Delete an object from the configured S3 bucket.

    :param object_name: S3 object name (key).
    :return: True if deletion successful or object didn't exist, else False.
    """
    client = get_s3_client()
    if not client:
        logger.error("S3 client not available. Cannot delete file.")
        return False
    if not S3_BUCKET_NAME:
         logger.error("S3_BUCKET_NAME not configured. Cannot delete file.")
         return False

    try:
        logger.info(f"Deleting S3 object '{object_name}' from bucket '{S3_BUCKET_NAME}'")
        client.delete_object(Bucket=S3_BUCKET_NAME, Key=object_name)
        logger.info(f"Successfully deleted S3 object '{object_name}' (or it didn't exist).")
        return True
    except ClientError as e:
        logger.error(f"Failed to delete S3 object '{object_name}': {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred deleting S3 object: {e}")
        return False

# Example Usage (can be removed or kept for testing)
# if __name__ == '__main__':
#     # Ensure AWS credentials and bucket name are set as environment variables
#     # Create a dummy file
#     with open("dummy_upload.txt", "w") as f:
#         f.write("This is a test file for S3 upload.")
#
#     # Upload
#     s3_key = upload_file_to_s3("dummy_upload.txt", "test/dummy_upload.txt")
#
#     if s3_key:
#         # Get presigned URL
#         url = create_presigned_url(s3_key)
#         if url:
#             print(f"Presigned URL: {url}")
#
#         # Download
#         download_success = download_file_from_s3(s3_key, "dummy_downloaded.txt")
#         if download_success:
#             print("File downloaded successfully.")
#             os.remove("dummy_downloaded.txt") # Clean up download
#
#         # Delete
#         delete_success = delete_file_from_s3(s3_key)
#         if delete_success:
#             print("File deleted successfully from S3.")
#
#     os.remove("dummy_upload.txt") # Clean up dummy file