import os
from dotenv import load_dotenv
from huggingface_hub import HfApi

load_dotenv()

def test_huggingface_connection():
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        print("מפתח API לא מוגדר ב-.env")
        return False
    
    try:
        api = HfApi(token=api_key)
        # בדיקה בסיסית של החיבור
        models = api.list_models(limit=1)
        print(f"מחובר בהצלחה ל-Hugging Face. מודל לדוגמה: {models[0].id if models else 'אין מודלים'}")
        return True
    except Exception as e:
        print(f"שגיאה בחיבור ל-Hugging Face: {e}")
        return False

if __name__ == "__main__":
    test_huggingface_connection()