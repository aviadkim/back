#!/bin/bash

# הגדרת משתנים
BUCKET_NAME=${S3_BUCKET_NAME:-financial-documents-bucket}
REGION=${AWS_REGION:-us-east-1}
DOCUMENTS_TABLE=${DYNAMODB_DOCUMENTS_TABLE:-financial-documents}
PROCESSED_DATA_TABLE=${DYNAMODB_PROCESSED_DATA_TABLE:-financial-processed-data}
CUSTOM_TABLES_TABLE=${DYNAMODB_CUSTOM_TABLES_TABLE:-financial-custom-tables}

echo "Setting up AWS services..."

# בדיקה שיש הגדרות AWS
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Error: AWS credentials not set. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    exit 1
fi

# התקנת AWS CLI אם צריך
if ! command -v aws &> /dev/null; then
    echo "Installing AWS CLI..."
    pip install awscli
fi

# יצירת דלי S3
echo "Creating S3 bucket: $BUCKET_NAME"
if aws s3api head-bucket --bucket $BUCKET_NAME 2>/dev/null; then
    echo "Bucket already exists"
else
    aws s3 mb s3://$BUCKET_NAME --region $REGION
    echo "Bucket created"
fi

# הגדרת CORS ל-S3
echo "Setting up CORS for S3 bucket..."
cat > cors.json << 'EOCORS'
{
    "CORSRules": [
        {
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
            "AllowedOrigins": ["*"],
            "ExposeHeaders": []
        }
    ]
}
EOCORS

aws s3api put-bucket-cors --bucket $BUCKET_NAME --cors-configuration file://cors.json
rm cors.json

# יצירת טבלאות DynamoDB
echo "Creating DynamoDB tables..."

# טבלת מסמכים
echo "Creating $DOCUMENTS_TABLE table..."
aws dynamodb create-table \
    --table-name $DOCUMENTS_TABLE \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $REGION || echo "Table $DOCUMENTS_TABLE already exists"

# טבלת נתונים מעובדים
echo "Creating $PROCESSED_DATA_TABLE table..."
aws dynamodb create-table \
    --table-name $PROCESSED_DATA_TABLE \
    --attribute-definitions AttributeName=document_id,AttributeType=S \
    --key-schema AttributeName=document_id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $REGION || echo "Table $PROCESSED_DATA_TABLE already exists"

# טבלת טבלאות מותאמות אישית
echo "Creating $CUSTOM_TABLES_TABLE table..."
aws dynamodb create-table \
    --table-name $CUSTOM_TABLES_TABLE \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $REGION || echo "Table $CUSTOM_TABLES_TABLE already exists"

echo "AWS services setup complete!"