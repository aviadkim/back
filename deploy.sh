#!/bin/bash
# סקריפט לפריסת האפליקציה לסביבת ענן

# קביעת סביבת הענן (aws, gcp, azure)
CLOUD_PROVIDER=${1:-aws}
ENV_NAME=${2:-production}

echo "מתחיל פריסה ל-$CLOUD_PROVIDER, סביבה: $ENV_NAME"

# יצירת קובץ .env לייצור
cp .env .env.production
echo "עדכון קובץ .env.production..."
sed -i 's/FLASK_ENV=development/FLASK_ENV=production/g' .env.production
sed -i 's/PORT=5000/PORT=8080/g' .env.production

# פריסה לפי ספק הענן
case $CLOUD_PROVIDER in
  aws)
    echo "פורס ל-AWS Elastic Beanstalk..."
    # בדיקה אם EB CLI מותקן
    if ! command -v eb &> /dev/null; then
        echo "מתקין את EB CLI..."
        pip install awsebcli
    fi
    
    # אתחול EB
    if [ ! -d .elasticbeanstalk ]; then
        echo "מאתחל את EB..."
        eb init -p docker financial-docs-analyzer
    fi
    
    # יצירת סביבה חדשה או עדכון קיימת
    if eb list | grep -q "$ENV_NAME"; then
        echo "מעדכן סביבה קיימת: $ENV_NAME..."
        eb deploy $ENV_NAME
    else
        echo "יוצר סביבה חדשה: $ENV_NAME..."
        eb create $ENV_NAME
    fi
    ;;
    
  gcp)
    echo "פורס ל-Google Cloud Run..."
    # בדיקה אם Google Cloud SDK מותקן
    if ! command -v gcloud &> /dev/null; then
        echo "יש להתקין את Google Cloud SDK תחילה."
        exit 1
    fi
    
    # בניית התמונה
    IMAGE_NAME="gcr.io/$(gcloud config get-value project)/financial-docs:v1"
    echo "בונה תמונת Docker: $IMAGE_NAME"
    docker build -t $IMAGE_NAME .
    
    # דחיפה לרג'יסטרי
    echo "דוחף את התמונה ל-Google Container Registry..."
    docker push $IMAGE_NAME
    
    # פריסה ל-Cloud Run
    echo "פורס ל-Cloud Run..."
    gcloud run deploy financial-docs --image $IMAGE_NAME --platform managed --region us-central1 --env-vars-file .env.production
    ;;
    
  azure)
    echo "פורס ל-Azure Container Apps..."
    # בדיקה אם Azure CLI מותקן
    if ! command -v az &> /dev/null; then
        echo "יש להתקין את Azure CLI תחילה."
        exit 1
    fi
    
    # התחברות ל-Azure (אם צריך)
    # az login
    
    # בניית התמונה ודחיפה לרג'יסטרי
    ACR_NAME=$(az acr list --query "[0].name" -o tsv)
    if [ -z "$ACR_NAME" ]; then
        echo "לא נמצא Container Registry ב-Azure."
        exit 1
    fi
    
    IMAGE_NAME="$ACR_NAME.azurecr.io/financial-docs:v1"
    echo "בונה ודוחף תמונת Docker: $IMAGE_NAME"
    az acr build --registry $ACR_NAME --image financial-docs:v1 .
    
    # פריסה ל-Container Apps
    echo "פורס ל-Container Apps..."
    az containerapp up --name financial-docs --resource-group myResourceGroup --image $IMAGE_NAME --target-port 8080 --ingress external --env-vars-file .env.production
    ;;
    
  *)
    echo "ספק ענן לא נתמך: $CLOUD_PROVIDER"
    echo "אפשרויות: aws, gcp, azure"
    exit 1
    ;;
esac

echo "פריסה הושלמה בהצלחה!"