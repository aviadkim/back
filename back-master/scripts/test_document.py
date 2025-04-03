#!/usr/bin/env python3
# scripts/test_document.py
import os
import sys
import argparse
import json
import time
from pathlib import Path

# ודא שתיקיית הפרויקט נמצאת בנתיב החיפוש
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    parser = argparse.ArgumentParser(description='בדיקת זיהוי מסמך בודד')
    parser.add_argument('file_path', help='נתיב לקובץ מסמך')
    parser.add_argument('--output', help='נתיב לשמירת התוצאות', default='./test_results.json')
    parser.add_argument('--model-path', help='נתיב לתיקיית מודלים', default='./models')
    parser.add_argument('--page', type=int, help='מספר עמוד ספציפי לבדיקה')
    args = parser.parse_args()
    
    # בדיקה שהקובץ קיים
    if not os.path.isfile(args.file_path):
        print(f"קובץ לא קיים: {args.file_path}")
        sys.exit(1)
    
    # קבלת סוג הקובץ
    file_extension = os.path.splitext(args.file_path)[1].lower().replace('.', '')
    
    # הפעלת סקריפט העיבוד
    try:
        print(f"מתחיל עיבוד קובץ: {args.file_path}")
        if args.page:
            print(f"מתמקד בעמוד: {args.page}")
        start_time = time.time()
        
        # הפעלת תהליך עיבוד
        from scripts.process_document import process_pdf, process_image
        
        if file_extension in ['pdf']:
            result = process_pdf(args.file_path, args.model_path, target_page=args.page)
        elif file_extension in ['jpg', 'jpeg', 'png']:
            result = process_image(args.file_path, args.model_path)
        else:
            print(f"סוג קובץ לא נתמך: {file_extension}")
            sys.exit(1)
        
        elapsed_time = time.time() - start_time
        
        # הוספת מידע על זמן עיבוד
        result['processing_time'] = elapsed_time
        result['file_path'] = args.file_path
        result['file_type'] = file_extension
        
        # שמירת התוצאות
        output_file = args.output
        if args.page:
            base, ext = os.path.splitext(output_file)
            output_file = f"{base}_page_{args.page}{ext}"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"עיבוד הסתיים בהצלחה! זמן עיבוד: {elapsed_time:.2f} שניות")
        print(f"תוצאות נשמרו בקובץ: {output_file}")
        
        # הצגת סטטיסטיקות
        print("\nסטטיסטיקות:")
        print(f"- מספר עמודים: {result.get('pageCount', 0)}")
        print(f"- מספר טבלאות שזוהו: {len(result.get('tables', []))}")
        print(f"- מספר פריטים פיננסיים שזוהו: {len(result.get('financialItems', []))}")
        print(f"- שפה: {result.get('language', 'לא זוהתה')}")
        
        # הצגת פריטי ISIN שזוהו
        isin_items = [item for item in result.get('financialItems', []) if item.get('itemType') == 'ISIN']
        if isin_items:
            print("\nמספרי ISIN שזוהו:")
            for item in isin_items:
                print(f"- {item.get('itemValue')} (רמת ביטחון: {item.get('confidence', 0):.2f})")
        
        # הצגת נתונים מלאים לכל נייר ערך
        if 'securities' in result:
            print("\nנתונים מלאים לניירות ערך:")
            for security in result['securities']:
                print("\nנייר ערך:")
                print(f"ISIN: {security.get('isin')}")
                print(f"שם: {security.get('name')}")
                print(f"סוג: {security.get('type')}")
                
                # הצגת מידע נוסף אם קיים
                additional_info = security.get('additional_info', {})
                if additional_info:
                    if 'currency' in additional_info:
                        print(f"מטבע: {additional_info['currency']}")
                    else:
                        print("מטבע: None")
                        
                    if 'nominal' in additional_info:
                        print(f"ערך נקוב: {additional_info['nominal']}")
                    else:
                        print("ערך נקוב: None")
                        
                    if 'price' in additional_info:
                        print(f"מחיר נוכחי: {additional_info['price']}")
                    else:
                        print("מחיר נוכחי: None")
                        
                    if 'maturity' in additional_info:
                        print(f"תאריך פירעון: {additional_info['maturity']}")
                        
                    if 'coupon' in additional_info:
                        print(f"קופון: {additional_info['coupon']}")
                else:
                    print("מטבע: None")
                    print("ערך נקוב: None")
                    print("מחיר נוכחי: None")
        
    except Exception as e:
        print(f"שגיאה בעיבוד המסמך: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 