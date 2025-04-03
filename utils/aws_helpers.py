"""
AWS helper utilities for the Financial Document Analysis System
"""
import os
import logging
import json

logger = logging.getLogger(__name__)

def get_secret(secret_name):
    """
    Get a secret from AWS Secrets Manager if running in AWS,
    otherwise falls back to environment variables.
    
    Args:
        secret_name: The name of the secret to retrieve
        
    Returns:
        The secret value or None if not found
    """
    # Check if we're running in AWS (by checking for AWS-specific env vars)
    is_aws = os.environ.get('AWS_EXECUTION_ENV') is not None or os.environ.get('AWS_REGION') is not None
    
    if is_aws:
        try:
            # Import boto3 only when needed
            import boto3
            from botocore.exceptions import ClientError
            
            region_name = os.environ.get('AWS_REGION', 'us-east-1')
            service_prefix = os.environ.get('SECRET_PREFIX', 'financial-docs')
            
            # Create a Secrets Manager client
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=region_name
            )
            
            try:
                # Attempt to get the full secret name with prefix
                full_secret_name = f"{service_prefix}/{secret_name}"
                get_secret_value_response = client.get_secret_value(
                    SecretId=full_secret_name
                )
                
                # Extract the secret string
                if 'SecretString' in get_secret_value_response:
                    return get_secret_value_response['SecretString']
                    
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    # Try without prefix
                    try:
                        get_secret_value_response = client.get_secret_value(
                            SecretId=secret_name
                        )
                        
                        # Extract the secret string
                        if 'SecretString' in get_secret_value_response:
                            return get_secret_value_response['SecretString']
                            
                    except ClientError:
                        logger.warning(f"Secret '{secret_name}' not found in AWS Secrets Manager")
                        # Fall back to environment variable
                        return os.environ.get(secret_name)
                else:
                    logger.error(f"Error retrieving secret '{secret_name}': {str(e)}")
                    # Fall back to environment variable
                    return os.environ.get(secret_name)
                    
        except (ImportError, Exception) as e:
            logger.error(f"Error with AWS Secrets Manager: {str(e)}")
            # Fall back to environment variable
            return os.environ.get(secret_name)
    else:
        # Not running in AWS, use environment variable
        return os.environ.get(secret_name)

def init_aws_secrets():
    """
    Initialize environment variables from AWS Secrets Manager
    if running in AWS environment.
    """
    # List of secrets to fetch
    secrets = [
        'HUGGINGFACE_API_KEY',
        'MONGO_URI',
        'SECRET_KEY',
        'JWT_SECRET'
    ]
    
    # Try to get each secret and set as environment variable if found
    for secret_name in secrets:
        secret_value = get_secret(secret_name)
        if secret_value:
            try:
                # Check if the secret value is a JSON string
                json_value = json.loads(secret_value)
                if isinstance(json_value, dict) and secret_name in json_value:
                    # Extract the value from the JSON
                    os.environ[secret_name] = json_value[secret_name]
                else:
                    # Use the value as is
                    os.environ[secret_name] = secret_value
            except (json.JSONDecodeError, TypeError):
                # Not JSON, use the value directly
                os.environ[secret_name] = secret_value
