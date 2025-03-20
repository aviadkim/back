#!/usr/bin/env python3
import os
import sys
from easyocr import easyocr
from transformers import TableTransformerForObjectDetection, AutoModelForCausalLM, AutoTokenizer
import torch
from tqdm import tqdm
import shutil

def download_models():
    """הורדת כל המודלים הנדרשים למערכת"""
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(models_dir, exist_ok=True)

    print("מוריד את כל המודלים הנדרשים למערכת המשופרת...")
    
    try:
        # הורדת מודלים של EasyOCR
        print("\n[1/3] מוריד מודלים של EasyOCR...")
        # יצירת מופע של EasyOCR יוריד אוטומטית את המודלים הנדרשים
        ocr = easyocr.Reader(['heb', 'eng'])
        print("✓ מודלי EasyOCR הורדו בהצלחה!")
        
        # הורדת מודל TableTransformer לזיהוי טבלאות
        print("\n[2/3] מוריד מודל TableTransformer לזיהוי טבלאות...")
        table_model = TableTransformerForObjectDetection.from_pretrained(
            "microsoft/table-transformer-detection", 
            cache_dir=os.path.join(models_dir, "table-transformer")
        )
        print("✓ מודל TableTransformer הורד בהצלחה!")
        
        # הורדת מודל TinyLlama לזיהוי ניירות ערך
        print("\n[3/3] מוריד מודל TinyLlama לזיהוי ניירות ערך...")
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        # הורדת ושמירת המודל והטוקנייזר
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            cache_dir=os.path.join(models_dir, "tiny-llama")
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            cache_dir=os.path.join(models_dir, "tiny-llama")
        )
        print("✓ מודל TinyLlama הורד בהצלחה!")
        
        print("\nכל המודלים הורדו בהצלחה!")
        print(f"המודלים נשמרו בתיקייה: {models_dir}")
        print("\nנפח אחסון מוערך:")
        print("- EasyOCR: ~120MB")
        print("- TableTransformer: ~360MB") 
        print("- TinyLlama: ~600MB")
        print("סה\"כ: ~1.1GB")
        
    except Exception as e:
        print(f"\nשגיאה בהורדת המודלים: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    download_models() 