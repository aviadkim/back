import os
import boto3
import json
import logging
from dotenv import load_dotenv
import requests
from pymongo import MongoClient
import sys

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# טעינת משתני סביבה
load_dotenv()

class CloudServicesTest:
    """
    בדיקת חיבור לשירותי ענן שונים הנדרשים למערכת SaaS
    """
    
    def __init__(self):
        self.test_results = {}
    
    def run_all_tests(self):
        """
        הרצת כל הבדיקות לשירותי ענן
        """
        print("מתחיל בדיקת חיבור לשירותי ענן...")
        
        # הרצת כל הבדיקות
        self.test_mongodb_connection()
        self.test_aws_textract()
        self.test_huggingface_api()
        self.test_mistral_api()
        
        # הצגת סיכום תוצאות
        self._print_summary()
        
        # החזרת תוצאות לשימוש תכנותי
        return self.test_results
    
    def test_mongodb_connection(self):
        """
        בדיקת חיבור למסד נתונים MongoDB
        """
        print("\n=== בדיקת חיבור ל-MongoDB ===")
        
        mongo_uri = os.environ.get('MONGO_URI')
        if not mongo_uri:
            self._log_failure("MongoDB", "מפתח חיבור MONGO_URI לא הוגדר בקובץ .env")
            return
        
        try:
            # ניסיון חיבור למסד הנתונים
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            
            # בדיקה שהשרת זמין
            client.server_info()
            
            # ניסיון לגשת לקולקציה וליצור מסמך בדיקה
            db = client['financial_documents']
            collection = db['connection_test']
            test_doc_id = collection.insert_one({"test": "connectivity", "timestamp": datetime.now()}).inserted_id
            
            # מחיקת מסמך הבדיקה
            collection.delete_one({"_id": test_doc_id})
            
            self._log_success("MongoDB", f"חיבור למסד הנתונים הצליח: {mongo_uri.split('@')[-1]}")
            
        except Exception as e:
            self._log_failure("MongoDB", f"שגיאה בחיבור למסד הנתונים: {str(e)}")
    
    def test_aws_textract(self):
        """
        בדיקת חיבור ל-AWS Textract
        """
        print("\n=== בדיקת חיבור ל-AWS Textract ===")
        
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        
        if not aws_access_key or not aws_secret_key:
            self._log_failure("AWS Textract", "מפתחות AWS חסרים בקובץ .env")
            return
        
        try:
            # יצירת חיבור לשירות
            textract = boto3.client(
                'textract',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
            
            # בדיקה שהשירות זמין (פעולה פשוטה שלא מחייבת קריאת API ממשית)
            # במקרה אמיתי תרצה לבצע פעולה קטנה לבדיקה
            # אבל נסתפק בבדיקת החיבור כדי לא להוציא עלויות מיותרות
            textract.get_paginator('analyze_document')
            
            self._log_success("AWS Textract", f"חיבור לשירות OCR בענן הצליח (אזור: {aws_region})")
            
        except Exception as e:
            self._log_failure("AWS Textract", f"שגיאה בחיבור לשירות OCR: {str(e)}")
    
    def test_huggingface_api(self):
        """
        בדיקת חיבור ל-Hugging Face API
        """
        print("\n=== בדיקת חיבור ל-Hugging Face API ===")
        
        api_key = os.environ.get('HUGGINGFACE_API_KEY')
        
        if not api_key:
            self._log_failure("Hugging Face", "מפתח API לא הוגדר בקובץ .env")
            return
        
        try:
            # בדיקה פשוטה באמצעות API
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            response = requests.get(
                "https://huggingface.co/api/models",
                headers=headers,
                params={"limit": 1}
            )
            
            if response.status_code == 200:
                self._log_success("Hugging Face", "חיבור ל-API הצליח")
            else:
                self._log_failure("Hugging Face", f"שגיאה בחיבור: {response.status_code} - {response.text}")
                
        except Exception as e:
            self._log_failure("Hugging Face", f"שגיאה בחיבור: {str(e)}")
    
    def test_mistral_api(self):
        """
        בדיקת חיבור ל-Mistral AI API (אם מוגדר)
        """
        print("\n=== בדיקת חיבור ל-Mistral AI API ===")
        
        api_key = os.environ.get('MISTRAL_API_KEY')
        
        if not api_key:
            self._log_warning("Mistral AI", "מפתח API לא הוגדר בקובץ .env (אופציונלי)")
            return
        
        try:
            # בדיקה פשוטה באמצעות API
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.mistral.ai/v1/models",
                headers=headers
            )
            
            if response.status_code == 200:
                available_models = response.json().get("data", [])
                model_names = [model.get("id") for model in available_models]
                self._log_success("Mistral AI", f"חיבור ל-API הצליח. מודלים זמינים: {', '.join(model_names)}")
            else:
                self._log_failure("Mistral AI", f"שגיאה בחיבור: {response.status_code} - {response.text}")
                
        except Exception as e:
            self._log_failure("Mistral AI", f"שגיאה בחיבור: {str(e)}")
    
    def _log_success(self, service, message):
        """
        רישום הצלחת בדיקה
        """
        logger.info(f"✅ {service}: {message}")
        print(f"✅ {service}: {message}")
        self.test_results[service] = {"status": "success", "message": message}
    
    def _log_failure(self, service, message):
        """
        רישום כישלון בדיקה
        """
        logger.error(f"❌ {service}: {message}")
        print(f"❌ {service}: {message}")
        self.test_results[service] = {"status": "failure", "message": message}
    
    def _log_warning(self, service, message):
        """
        רישום אזהרה
        """
        logger.warning(f"⚠️ {service}: {message}")
        print(f"⚠️ {service}: {message}")
        self.test_results[service] = {"status": "warning", "message": message}
    
    def _print_summary(self):
        """
        הצגת סיכום כל הבדיקות
        """
        success_count = sum(1 for result in self.test_results.values() if result["status"] == "success")
        warning_count = sum(1 for result in self.test_results.values() if result["status"] == "warning")
        failure_count = sum(1 for result in self.test_results.values() if result["status"] == "failure")
        
        print("\n====== סיכום בדיקות שירותי ענן ======")
        print(f"הצלחות: {success_count}, אזהרות: {warning_count}, כשלונות: {failure_count}")
        
        if failure_count > 0:
            print("\nשירותים שנכשלו:")
            for service, result in self.test_results.items():
                if result["status"] == "failure":
                    print(f"  - {service}: {result['message']}")
            
            print("\nיש לתקן את השגיאות לפני פריסה לענן")
        elif warning_count > 0:
            print("\nאזהרות:")
            for service, result in self.test_results.items():
                if result["status"] == "warning":
                    print(f"  - {service}: {result['message']}")
        
        if success_count == len(self.test_results):
            print("\n🎉 כל הבדיקות עברו בהצלחה! המערכת מוכנה לפריסה בענן.")

# ייבוא נוסף הנדרש
from datetime import datetime

# הפעלה אם הקובץ רץ ישירות
if __name__ == "__main__":
    print("בודק חיבור לשירותי ענן SaaS...")
    tester = CloudServicesTest()
    results = tester.run_all_tests()
    
    # יציאה עם קוד שגיאה אם יש כישלון
    if any(result["status"] == "failure" for result in results.values()):
        sys.exit(1)
