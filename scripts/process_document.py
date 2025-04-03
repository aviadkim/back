#!/usr/bin/env python3
# scripts/process_document.py
import sys
import os
import json
import argparse
import cv2
import numpy as np
from PIL import Image
import re
from pdf2image import convert_from_path
import easyocr

def main():
    # פרסור ארגומנטים
    parser = argparse.ArgumentParser(description='Process financial document')
    parser.add_argument('document_id', help='Document ID')
    parser.add_argument('file_path', help='Path to the document file')
    parser.add_argument('file_type', help='Document file type')
    parser.add_argument('output_dir', help='Output directory for results')
    args = parser.parse_args()
    
    try:
        # עיבוד המסמך בהתאם לסוג הקובץ
        if args.file_type.lower() == 'pdf':
            result = process_pdf(args.file_path, args.output_dir)
        elif args.file_type.lower() in ['jpg', 'jpeg', 'png']:
            result = process_image(args.file_path, args.output_dir)
        else:
            result = {
                'error': f'סוג קובץ לא נתמך: {args.file_type}'
            }
        
        # הוספת מזהה המסמך לתוצאה
        if isinstance(result, dict):
            result['document_id'] = args.document_id
        
        # החזרת התוצאה כ-JSON
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            'error': str(e),
            'document_id': args.document_id
        }, ensure_ascii=False))
        sys.exit(1)

def process_pdf(pdf_path, output_dir, target_page=None):
    """עיבוד קובץ PDF עם EasyOCR"""
    try:
        # יצירת מופע של EasyOCR עם תמיכה באנגלית
        reader = easyocr.Reader(['en'])
        
        # המרת PDF לתמונות
        print("ממיר PDF לתמונות...")
        poppler_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                  "test_documents", "poppler-23.11.0", "poppler-23.11.0", "Library", "bin"))
        print(f"נתיב Poppler: {poppler_path}")
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        
        # בדיקת מספר העמוד המבוקש
        if target_page is not None:
            if target_page < 1 or target_page > len(images):
                raise Exception(f"מספר עמוד לא חוקי. המסמך מכיל {len(images)} עמודים")
            target_page = target_page - 1  # המרה לאינדקס מבוסס-0
            print(f"\nמעבד עמוד {target_page + 1}...")
            image = images[target_page]
            
            # שמירת התמונה
            image_path = os.path.join(output_dir, f'page_{target_page + 1}.jpg')
            image.save(image_path, 'JPEG')
            
            # המרת תמונה לפורמט OpenCV
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # זיהוי טקסט
            ocr_result = reader.readtext(img)
            
            # עיבוד התוצאות
            page_data = {
                'page_number': target_page + 1,
                'text_blocks': [],
                'tables': [],
                'fullText': '',
                'financialItems': [],
                'securities': [],
                'detailed_tables': []
            }
            
            full_text = []
            for detection in ocr_result:
                bbox, text, confidence = detection
                # המרת numpy.int32 למספר רגיל
                bbox = [[float(x) for x in point] for point in bbox]
                page_data['text_blocks'].append({
                    'text': text,
                    'confidence': float(confidence),
                    'bbox': bbox
                })
                full_text.append(text)
            
            # שמירת הטקסט המלא
            page_data['fullText'] = ' '.join(full_text)
            
            # זיהוי טבלאות
            tables = extract_tables_from_image(img, target_page)
            if tables:
                # המרת numpy.int32 למספרים רגילים
                for table in tables:
                    table['bbox'] = [float(x) for x in table['bbox']]
                page_data['tables'].extend(tables)
                print(f"נמצאו {len(tables)} טבלאות בעמוד {target_page + 1}")
                
                # ניסיון לחלץ מידע מפורט מכל טבלה
                for table in tables:
                    detailed_data = extract_detailed_table_data(img, table['bbox'])
                    if detailed_data:
                        page_data['detailed_tables'].append({
                            'tableIndex': int(table['tableIndex']),  # המרה ל-int רגיל
                            'headers': detailed_data['headers'],
                            'data': detailed_data['data']
                        })
                        print(f"\nכותרות טבלה {table['tableIndex'] + 1}:")
                        print(" | ".join(detailed_data['headers']))
                        print("\nנתונים:")
                        for row in detailed_data['data']:
                            print(row)
            
            # זיהוי מידע פיננסי
            page_data['financialItems'] = extract_financial_items(page_data['fullText'], page_data['tables'])
            
            # זיהוי ניירות ערך
            securities = extract_securities(page_data['text_blocks'], page_data['tables'], img)
            if securities:
                page_data['securities'].extend(securities)
                print(f"\nנמצאו {len(securities)} ניירות ערך בעמוד {target_page + 1}:")
                for sec in securities:
                    print(f"- {sec['name']}: {sec['isin']} ({sec['type']})")
            
            # זיהוי שפת המסמך
            page_data['language'] = detect_language(page_data['fullText'])
            
            # ניסיון לזהות סוג מסמך ושם חברה
            doc_info = detect_document_info(page_data['fullText'])
            page_data.update(doc_info)
            
            # שמירת התוצאות
            output_file = os.path.join(output_dir, f'ocr_results_page_{target_page + 1}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, ensure_ascii=False, indent=2)
            
            print(f"\nהתוצאות נשמרו ב: {output_file}")
            return page_data
            
        else:
            # עיבוד כל העמודים
            results = []
            for i, image in enumerate(images):
                print(f"\nמעבד עמוד {i + 1}...")
                # המשך הקוד הקיים לעיבוד כל העמודים...
                
            return results
            
    except Exception as e:
        print(f"שגיאה בעיבוד המסמך: {str(e)}", file=sys.stderr)
        return {'error': str(e)}

def process_image(file_path, output_dir):
    """עיבוד קובץ תמונה עם EasyOCR"""
    try:
        # יצירת מופע של EasyOCR עם תמיכה באנגלית
        reader = easyocr.Reader(['en'])
        
        # קריאת התמונה
        img = cv2.imread(file_path)
        if img is None:
            raise Exception(f"נכשל בקריאת התמונה: {file_path}")
        
        # זיהוי טקסט
        ocr_result = reader.readtext(img)
        
        # עיבוד התוצאות
        results = {
            'page_number': 1,
            'text_blocks': [],
            'tables': [],
            'fullText': '',
            'financialItems': [],
            'language': 'auto'
        }
        
        full_text = []
        for detection in ocr_result:
            bbox, text, confidence = detection
            results['text_blocks'].append({
                'text': text,
                'confidence': float(confidence),
                'bbox': bbox
            })
            full_text.append(text)
        
        # שמירת הטקסט המלא
        results['fullText'] = ' '.join(full_text)
        
        # זיהוי טבלאות
        tables = extract_tables_from_image(img, 0)
        if tables:
            results['tables'].extend(tables)
        
        # זיהוי שפת המסמך
        results['language'] = detect_language(results['fullText'])
        
        # זיהוי מידע פיננסי
        results['financialItems'] = extract_financial_items(results['fullText'], results['tables'])
        
        # ניסיון לזהות סוג מסמך ושם חברה
        doc_info = detect_document_info(results['fullText'])
        results.update(doc_info)
        
        # שמירת התוצאות
        output_file = os.path.join(output_dir, 'ocr_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"התוצאות נשמרו ב: {output_file}")
        return results
        
    except Exception as e:
        print(f"שגיאה בעיבוד התמונה: {str(e)}", file=sys.stderr)
        return {'error': str(e)}

def extract_tables_from_image(img, page_number):
    """זיהוי טבלאות בתמונה"""
    tables = []
    try:
        # המרה לתמונת אפור
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # שיפור ניגודיות
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # שימוש בסף אדפטיבי
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 8)
        
        # ניסיון לזהות קווים אופקיים ואנכיים בגדלים שונים
        line_detection_results = []
        
        # מערך של גדלי גרעין שונים לניסוי
        kernel_sizes = [(15, 1), (25, 1), (35, 1), (int(gray.shape[1]/30), 1)]
        vertical_kernel_sizes = [(1, 15), (1, 25), (1, 35), (1, int(gray.shape[0]/30))]
        
        for h_size, v_size in zip(kernel_sizes, vertical_kernel_sizes):
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, h_size)
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, v_size)
            
            horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
            vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
            
            # שילוב הקווים
            table_mask = cv2.add(horizontal_lines, vertical_lines)
            
            # מציאת קונטורים
            contours, hierarchy = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # מיון קונטורים לפי גודל
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            # שמירת התוצאות
            if contours:
                line_detection_results.append((contours, h_size[0], v_size[1]))
        
        # אם לא נמצאו קונטורים בכל הניסיונות, ננסה גישה אחרת
        if not line_detection_results:
            # זיהוי לפי אזורים עם צפיפות גבוהה של טקסט
            # פילטר גאוסיאני לריכוך התמונה
            blurred = cv2.GaussianBlur(thresh, (25, 25), 0)
            
            # דילול להקטנת רעש
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated = cv2.dilate(blurred, kernel, iterations=3)
            
            # מציאת קונטורים על התמונה המדוללת
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            # פילטור לפי גודל מינימלי
            contours = [c for c in contours if cv2.contourArea(c) > img.shape[0] * img.shape[1] / 100]
            
            if contours:
                line_detection_results.append((contours, 0, 0))  # הערכים 0, 0 הם רק פלייסהולדר
        
        # גמלון ראשוני - חלוקה לאזורים גדולים
        min_table_area = img.shape[0] * img.shape[1] / 50  # לפחות 2% משטח התמונה
        
        detected_tables = []
        
        # עיבוד כל אחת מתוצאות זיהוי הקווים
        for contours, _, _ in line_detection_results:
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # בדיקה שהאזור גדול מספיק כדי להיות טבלה
                if w > 100 and h > 100 and w * h > min_table_area:
                    detected_tables.append((x, y, w, h))
        
        # הסרת כפילויות - אם שני אזורים חופפים ביותר מ-50%, השאר רק את הגדול יותר
        filtered_tables = []
        detected_tables.sort(key=lambda box: box[2] * box[3], reverse=True)  # מיון לפי שטח
        
        for table in detected_tables:
            x1, y1, w1, h1 = table
            is_duplicate = False
            
            for filtered_table in filtered_tables:
                x2, y2, w2, h2 = filtered_table
                
                # חישוב שטח החפיפה
                x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                overlap_area = x_overlap * y_overlap
                
                # בדיקה אם יש חפיפה משמעותית
                table1_area = w1 * h1
                if overlap_area / table1_area > 0.5:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_tables.append(table)
        
        # יצירת אובייקטי טבלה
        for i, (x, y, w, h) in enumerate(filtered_tables):
            tables.append({
                'tableIndex': i,
                'bbox': [x, y, x + w, y + h],
                'confidence': 0.9
            })
        
        # אם לא זוהו טבלאות, ננסה לזהות לפי אזור שמכיל את רוב הטקסט
        if not tables:
            # הנחה: אזור הטבלה נמצא בחצי התחתון של העמוד ותופס חלק ניכר מהרוחב
            # חלוקה גסה של העמוד
            page_height, page_width = img.shape[:2]
            
            # האזור שבו סביר שתהיה טבלה (חצי תחתון, 80% מהרוחב)
            table_area_x = int(page_width * 0.1)
            table_area_y = int(page_height * 0.3)  # מתחיל ב-30% מהגובה
            table_area_w = int(page_width * 0.8)
            table_area_h = int(page_height * 0.6)  # 60% מהגובה
            
            tables.append({
                'tableIndex': 0,
                'bbox': [table_area_x, table_area_y, table_area_x + table_area_w, table_area_y + table_area_h],
                'confidence': 0.7  # ביטחון נמוך יותר
            })
            
        return tables
        
    except Exception as e:
        print(f"שגיאה בזיהוי טבלאות בעמוד {page_number}: {str(e)}", file=sys.stderr)
        return []

def extract_financial_items(text, tables):
    """חילוץ מידע פיננסי מטקסט וטבלאות"""
    items = []
    
    try:
        # חיפוש מספרי ISIN
        isin_pattern = r'[A-Z]{2}[0-9A-Z]{10}'
        isin_matches = re.findall(isin_pattern, text)
        
        for isin in set(isin_matches):
            items.append({
                "type": "ISIN",
                "value": isin,
                "confidence": 0.95
            })
        
        # חיפוש ערכים כספיים
        currency_pattern = r'(?:[\$\€\₪\£\¥]\s*[\d,]+(?:\.\d+)?)|(?:[\d,]+(?:\.\d+)?\s*(?:USD|EUR|ILS|GBP|JPY))'
        currency_matches = re.findall(currency_pattern, text)
        
        for value in set(currency_matches):
            items.append({
                "type": "CURRENCY",
                "value": value,
                "confidence": 0.9
            })
        
        # חיפוש אחוזים
        percentage_pattern = r'[\d,]+(?:\.\d+)?\s*\%'
        percentage_matches = re.findall(percentage_pattern, text)
        
        for value in set(percentage_matches):
            items.append({
                "type": "PERCENTAGE",
                "value": value,
                "confidence": 0.9
            })
        
        return items
        
    except Exception as e:
        print(f"שגיאה בחילוץ מידע פיננסי: {str(e)}", file=sys.stderr)
        return []

def detect_language(text):
    """זיהוי שפת הטקסט"""
    try:
        # ספירת תווים עבריים ולטיניים
        hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', text))
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        russian_chars = len(re.findall(r'[А-Яа-я]', text))
        
        char_counts = {
            'heb': hebrew_chars,
            'eng': latin_chars,
            'ara': arabic_chars,
            'chi': chinese_chars,
            'rus': russian_chars
        }
        
        # מציאת השפה הדומיננטית
        dominant_lang = max(char_counts.items(), key=lambda x: x[1])
        
        if dominant_lang[1] > 0:
            return dominant_lang[0]
        else:
            return 'unknown'
            
    except Exception as e:
        print(f"שגיאה בזיהוי שפה: {str(e)}", file=sys.stderr)
        return 'unknown'

def detect_document_info(text):
    """זיהוי מידע כללי על המסמך"""
    info = {
        'documentType': None,
        'companyName': None
    }
    
    try:
        # ניסיון לזהות סוג מסמך
        doc_types = {
            'דוח שנתי': ['דוח שנתי', 'annual report'],
            'דוח רבעוני': ['דוח רבעוני', 'quarterly report'],
            'מאזן': ['מאזן', 'balance sheet'],
            'דוח רווח והפסד': ['דוח רווח והפסד', 'profit & loss'],
            'הערכת שווי': ['הערכת שווי', 'valuation']
        }
        
        for doc_type, keywords in doc_types.items():
            for keyword in keywords:
                if keyword in text.lower():
                    info['documentType'] = doc_type
                    break
            if info['documentType']:
                break
        
        # ניסיון לזהות שם חברה
        company_pattern = r'(?:חברת|קבוצת|חב׳|חב\')\s+([\u0590-\u05FFa-zA-Z0-9\s]+?)(?:\s+בע״מ|\s+בע"מ|\s+בעמ|\s+Ltd\.|\s+Inc\.)?'
        company_match = re.search(company_pattern, text)
        if company_match:
            info['companyName'] = company_match.group(1).strip()
        
        return info
        
    except Exception as e:
        print(f"שגיאה בזיהוי מידע על המסמך: {str(e)}", file=sys.stderr)
        return info

def extract_detailed_table_data(img, bbox):
    """חילוץ מידע מפורט מטבלה באמצעות זיהוי תאים וקווים"""
    try:
        # חיתוך אזור הטבלה
        x1, y1, x2, y2 = [int(coord) for coord in bbox]  # ודא שהמיקומים הם מספרים שלמים
        
        # בדיקת תקינות הגבולות
        if x1 < 0: x1 = 0
        if y1 < 0: y1 = 0
        if x2 > img.shape[1]: x2 = img.shape[1]
        if y2 > img.shape[0]: y2 = img.shape[0]
        
        # בדיקה שהטבלה לא ריקה
        if x1 >= x2 or y1 >= y2:
            print("גבולות הטבלה לא תקינים")
            return None
        
        table_roi = img[y1:y2, x1:x2]
        
        # בדיקה שהחיתוך הצליח
        if table_roi.size == 0:
            print("לא ניתן לחתוך את אזור הטבלה")
            return None
        
        # המרה לתמונת גווני אפור
        gray = cv2.cvtColor(table_roi, cv2.COLOR_BGR2GRAY)
        
        # שיפור ניגודיות עם CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # בינריזציה על ידי סף אדפטיבי
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        
        # יצירת kernel לקווים אנכיים ואופקיים - שימוש בגדלים קטנים יותר עבור קווים דקים יותר
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(gray.shape[1]/30), 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(gray.shape[0]/30)))
        
        # זיהוי קווים אופקיים
        horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
        horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=1)
        
        # זיהוי קווים אנכיים
        vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
        vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=1)
        
        # שילוב הקווים
        table_mask = cv2.add(horizontal_lines, vertical_lines)
        
        # הגדלת הקווים כדי לסגור פערים
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        table_mask = cv2.dilate(table_mask, kernel, iterations=1)
        
        # מציאת קונטורים
        contours, hierarchy = cv2.findContours(table_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # סינון קונטורים קטנים מדי
        min_area = (table_roi.shape[0] * table_roi.shape[1]) / 3000  # הקטנת הסף לסינון
        contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
        
        # מיון קונטורים לפי מיקום
        contours = sorted(contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
        
        # חילוץ תאים
        cells = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # סינון תאים קטנים מדי
            if w < 10 or h < 5:  # הקטנת הסף המינימלי עוד יותר
                continue
            cells.append((x, y, w, h))
        
        # ארגון תאים בשורות
        row_threshold = max(5, gray.shape[0] / 30)  # הקטנת המרווח המקסימלי בין שורות
        rows = []
        current_row = []
        last_y = -1
        
        for cell in sorted(cells, key=lambda c: (c[1], c[0])):
            x, y, w, h = cell
            if last_y == -1 or abs(y - last_y) < row_threshold:
                current_row.append(cell)
                last_y = y  # עדכון Y רק אם התא שייך לשורה הנוכחית
            else:
                if current_row:
                    rows.append(sorted(current_row, key=lambda c: c[0]))
                current_row = [cell]
                last_y = y
        
        if current_row:
            rows.append(sorted(current_row, key=lambda c: c[0]))
        
        # הדפסת מידע דיאגנוסטי
        print(f"זוהו {len(rows)} שורות בטבלה")
        
        # המרת תאים לטקסט
        reader = easyocr.Reader(['en'])
        
        # לוגיקה משופרת לזיהוי הכותרות
        header_candidates = []
        header_row_idx = 0
        
        # זיהוי שורת הכותרות - בדרך כלל השורה הראשונה
        has_headers = False
        
        # עיבוד השורות
        table_data = []
        headers = []
        
        for i, row_cells in enumerate(rows):
            row_text = []
            for x, y, w, h in row_cells:
                # חיתוך התא
                cell_roi = gray[y:y+h, x:x+w]
                
                # בדיקה אם תא ריק
                if cv2.countNonZero(cell_roi) < 10:  # כמעט שחור לחלוטין
                    row_text.append("")
                    continue
                    
                # שיפור איכות התמונה לפני OCR
                cell_roi = cv2.GaussianBlur(cell_roi, (3,3), 0)
                _, cell_roi = cv2.threshold(cell_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # הוספת שוליים לבנים כדי למנוע חיתוך של טקסט בקצוות
                padding = 8  # שוליים גדולים יותר
                cell_roi = cv2.copyMakeBorder(cell_roi, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=255)
                
                # זיהוי טקסט
                result = reader.readtext(cell_roi)
                if result:
                    # לקיחת התוצאה עם הביטחון הגבוה ביותר
                    text = max(result, key=lambda x: x[2])[1]
                    row_text.append(text.strip())
                else:
                    row_text.append("")
            
            # התעלמות משורות ריקות
            if not any(text.strip() for text in row_text):
                continue
                
            # בדיקה אם זו שורת כותרות
            is_header_row = False
            if i == 0:  # השורה הראשונה
                is_header_row = True
                # בדיקה שהשורה הראשונה מכילה מילים שנראות כמו כותרות
                for cell in row_text:
                    cell_lower = cell.lower()
                    if any(keyword in cell_lower for keyword in ['isin', 'description', 'currency', 'price', 'nominal', 'coupon', 'maturity']):
                        has_headers = True
                        break
            
            if is_header_row and has_headers:
                headers = row_text
            else:
                table_data.append(row_text)
        
        # אם לא זוהו כותרות, ננסה לזהות אותן באמצעות חיפוש בטקסט
        if not headers or all(h == "" for h in headers):
            # כותרות טיפוסיות שמופיעות בטבלאות של ניירות ערך
            common_headers = ['ISIN', 'Description', 'Currency', 'Nominal', 'Price', 'Coupon', 'Maturity', 'Valuation']
            
            # ננסה להתאים את הראשי עמודות לפי התוכן שלהן
            if table_data and len(table_data) > 0:
                first_row = table_data[0]
                inferred_headers = []
                
                for i, cell in enumerate(first_row):
                    # בדיקה אם התא מכיל ISIN
                    if re.search(r'[A-Z]{2}[0-9A-Z]{10}', cell):
                        inferred_headers.append('ISIN')
                    # בדיקה אם התא מכיל מטבע
                    elif re.search(r'\b(USD|EUR|CHF|GBP|JPY)\b', cell):
                        inferred_headers.append('Currency')
                    # בדיקה אם התא מכיל מספר כאחוז
                    elif re.search(r'-?\d+\.\d+%', cell):
                        inferred_headers.append('Perf YTD')
                    # בדיקה אם התא מכיל מספר עם נקודה עשרונית (מחיר)
                    elif re.search(r'\d+\.\d+', cell) and not re.search(r'%', cell):
                        inferred_headers.append('Price')
                    # בדיקה אם התא מכיל מספר גדול (ערך נקוב)
                    elif re.search(r'\d{4,}', cell):
                        inferred_headers.append('Nominal')
                    # אם התא מכיל טקסט ארוך, כנראה תיאור
                    elif len(cell) > 10 and re.search(r'[a-zA-Z]{3,}', cell):
                        inferred_headers.append('Description')
                    # אחרת, השאר ריק
                    else:
                        inferred_headers.append('')
                
                # אם מצאנו כותרות מתאימות, השתמש בהן
                if any(h != '' for h in inferred_headers):
                    headers = inferred_headers
                else:
                    # ברירת מחדל: השתמש בכותרות סטנדרטיות
                    headers = common_headers[:len(first_row)] if len(first_row) < len(common_headers) else common_headers
            else:
                # אם אין שורות נתונים, השתמש בכותרות ברירת מחדל
                headers = common_headers
        
        if not table_data:
            print("לא נמצאו נתונים בטבלה")
            return None
        
        print(f"נמצאו {len(headers)} כותרות ו-{len(table_data)} שורות נתונים")
        
        return {
            'headers': headers,
            'data': table_data
        }
        
    except Exception as e:
        import traceback
        print(f"שגיאה בחילוץ מידע מפורט מטבלה: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return None

def extract_securities(text_blocks, tables=None, img=None):
    """חילוץ מידע על ניירות ערך מהטקסט והטבלאות"""
    securities = []
    
    try:
        # אחזור הטקסט המלא מכל הבלוקים
        full_text = " ".join([block['text'] for block in text_blocks])
        
        # חיפוש מספרי ISIN
        isin_pattern = r'[A-Z]{2}[0-9A-Z]{10}'
        isin_matches = re.findall(isin_pattern, full_text)
        
        if not isin_matches:
            return []
            
        print(f"נמצאו {len(set(isin_matches))} מספרי ISIN ייחודיים")
        
        # מיפוי לשמירת מידע על כל ISIN
        securities_data = {}
        
        # עבור כל ISIN, נחפש את המידע הרלוונטי בטקסט המלא
        for isin in set(isin_matches):
            # חיפוש הטקסט סביב ה-ISIN
            isin_position = full_text.find(isin)
            
            if isin_position > -1:
                # חיפוש קטע לפני ואחרי ה-ISIN (300 תווים בכל כיוון)
                start_pos = max(0, isin_position - 300)
                end_pos = min(len(full_text), isin_position + 300)
                
                isin_context = full_text[start_pos:end_pos]
                
                # חילוץ מידע מהקונטקסט
                description = None
                currency = None
                nominal = None
                price = None
                maturity = None
                coupon = None
                securities_type = "לא ידוע"
                
                # זיהוי סוג נייר ערך
                type_patterns = [
                    (r'ordinary bonds', "אגח"),
                    (r'zero bonds', "אגח"),
                    (r'structured bonds', "אגח"),
                    (r'bond funds', "קרן"),
                    (r'equity', "מניה"),
                    (r'share', "מניה"),
                    (r'stock', "מניה"),
                    (r'etf', "קרן"),
                    (r'fund', "קרן"),
                    (r'certificate', "תעודה")
                ]
                
                for pattern, sec_type in type_patterns:
                    if re.search(pattern, isin_context.lower()):
                        securities_type = sec_type
                        break
                
                # חיפוש מטבע ומספר (יופיעו בדרך כלל יחד)
                currency_amount_pattern = r'(USD|EUR|CHF|GBP|JPY)\s+([\d\',]+)'
                currency_match = re.search(currency_amount_pattern, isin_context)
                
                if currency_match:
                    currency = currency_match.group(1)
                    nominal = currency_match.group(2)
                
                # חיפוש שם/תיאור (בדרך כלל בין המטבע לבין המחיר)
                if currency and nominal:
                    # חיפוש הטקסט אחרי המטבע והכמות
                    curr_pos = isin_context.find(f"{currency} {nominal}")
                    if curr_pos > -1:
                        # חיפוש עד לתחילת המחיר (בדרך כלל מספר עם נקודה עשרונית)
                        desc_end = re.search(r'\d+\.\d+', isin_context[curr_pos+len(f"{currency} {nominal}"):])
                        if desc_end:
                            desc_end_pos = curr_pos + len(f"{currency} {nominal}") + desc_end.start()
                            description = isin_context[curr_pos+len(f"{currency} {nominal}"):desc_end_pos].strip()
                
                # אם לא מצאנו תיאור, ננסה למצוא שורה/מילים ארוכות בין מטבע למחיר
                if not description or len(description) < 5:
                    long_words = re.findall(r'[A-Z][A-Z\s]{5,}[A-Z]', isin_context)
                    if long_words:
                        description = max(long_words, key=len)
                
                # חיפוש מחיר (בדרך כלל שני מספרים עם נקודה עשרונית אחד אחרי השני)
                price_pattern = r'(\d+\.\d+)\s+(\d+\.\d+)'
                price_match = re.search(price_pattern, isin_context)
                
                if price_match:
                    # המחיר הנוכחי הוא השני
                    price = price_match.group(2)
                
                # חיפוש תאריך פירעון
                maturity_pattern = r'maturity:\s*(\d{2}\.\d{2}\.\d{4})'
                maturity_match = re.search(maturity_pattern, isin_context.lower())
                
                if maturity_match:
                    maturity = maturity_match.group(1)
                
                # חיפוש קופון
                coupon_pattern = r'coupon:.*?([\d\.]+)%'
                coupon_match = re.search(coupon_pattern, isin_context.lower())
                
                if coupon_match:
                    coupon = f"{coupon_match.group(1)}%"
                elif "0%" in isin_context or "0 %" in isin_context:
                    coupon = "0%"
                
                # שמירת המידע
                securities_data[isin] = {
                    'isin': isin,
                    'name': description if description else "שם לא ידוע",
                    'type': securities_type,
                    'additional_info': {}
                }
                
                if currency:
                    securities_data[isin]['additional_info']['currency'] = currency
                if nominal:
                    securities_data[isin]['additional_info']['nominal'] = nominal
                if price:
                    securities_data[isin]['additional_info']['price'] = price
                if maturity:
                    securities_data[isin]['additional_info']['maturity'] = maturity
                if coupon:
                    securities_data[isin]['additional_info']['coupon'] = coupon
                
                # שיפור שם - בדיקה אם יש חברה/מוסד פיננסי בתיאור
                institutions = ["GOLDMAN SACHS", "JPMORGAN", "DEUTSCHE BANK", "BANK OF AMERICA", "JULIUS BAER"]
                if not description or len(description) < 5:
                    for institution in institutions:
                        if institution in isin_context:
                            desc_pos = isin_context.find(institution)
                            if desc_pos > -1:
                                # חיפוש תיאור עד הסימן הבא כמו אחוז או מחיר
                                end_marker = re.search(r'[%\d\.]+%|\d+\.\d+', isin_context[desc_pos+len(institution):])
                                if end_marker:
                                    end_pos = desc_pos + len(institution) + end_marker.start()
                                    new_desc = isin_context[desc_pos:end_pos].strip()
                                    securities_data[isin]['name'] = new_desc
                                    break
        
        # המרה לרשימת תוצאות
        for isin, data in securities_data.items():
            securities.append(data)
        
        return securities
        
    except Exception as e:
        import traceback
        print(f"שגיאה בחילוץ מידע על ניירות ערך: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return []

if __name__ == '__main__':
    main()