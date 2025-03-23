import pytesseract
from PyPDF2 import PdfReader
from PIL import Image
import io
import re
import os
import tempfile
import logging
from typing import Dict, List, Tuple, Optional, Any

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    מעבד קבצי PDF - מחלץ טקסט, טבלאות ומידע פיננסי מדוחות.
    """
    
    def __init__(self, ocr_enabled: bool = True, lang: str = "heb+eng"):
        """
        אתחול מעבד ה-PDF
        
        Args:
            ocr_enabled: האם להפעיל זיהוי תווים אוטומטי
            lang: שפת הטקסט לזיהוי ב-OCR
        """
        self.ocr_enabled = ocr_enabled
        self.lang = lang
        
        # אם OCR מופעל, וודא שהספרייה זמינה
        if self.ocr_enabled:
            try:
                pytesseract.get_tesseract_version()
            except Exception as e:
                logger.warning(f"OCR לא זמין: {e}. מבטל OCR.")
                self.ocr_enabled = False
    
    def extract_text(self, pdf_path: str) -> str:
        """
        חילוץ טקסט מקובץ PDF
        
        Args:
            pdf_path: נתיב לקובץ PDF
            
        Returns:
            str: הטקסט המחולץ
        """
        logger.info(f"מחלץ טקסט מ-{pdf_path}")
        
        try:
            # פתיחת קובץ PDF
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file)
                text = ""
                
                # חילוץ טקסט מכל עמוד
                for page_num, page in enumerate(reader.pages):
                    logger.info(f"מעבד עמוד {page_num + 1}/{len(reader.pages)}")
                    
                    # ניסיון לחלץ טקסט ישירות
                    page_text = page.extract_text() or ""
                    
                    # אם הטקסט חסר או OCR מופעל, מנסה OCR
                    if self.ocr_enabled and (not page_text or len(page_text) < 100):
                        logger.info(f"משתמש ב-OCR עבור עמוד {page_num + 1}")
                        page_text = self._extract_text_with_ocr(page)
                    
                    text += page_text + "\n\n"
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"שגיאה בחילוץ טקסט מ-PDF: {e}")
            return ""
    
    def extract_tables(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        חילוץ טבלאות מקובץ PDF
        
        Args:
            pdf_path: נתיב לקובץ PDF
            
        Returns:
            List[Dict]: רשימת טבלאות מחולצות עם מטה-דאטה
        """
        logger.info(f"מחלץ טבלאות מ-{pdf_path}")
        
        # רשימת הטבלאות שיוחזרו
        tables = []
        
        try:
            # מחלץ טקסט מלא
            full_text = self.extract_text(pdf_path)
            
            # מחפש תבניות טבלאות בטקסט
            # חיפוש פשוט של שורות שנראות כמו טבלה
            table_candidates = self._identify_table_patterns(full_text)
            
            for i, candidate in enumerate(table_candidates):
                tables.append({
                    "id": f"table_{i+1}",
                    "page": candidate.get("page", 0),
                    "content": candidate.get("content", ""),
                    "rows": candidate.get("rows", []),
                    "columns": candidate.get("columns", [])
                })
            
            return tables
            
        except Exception as e:
            logger.error(f"שגיאה בחילוץ טבלאות מ-PDF: {e}")
            return []
    
    def extract_financial_data(self, pdf_path: str) -> Dict[str, Any]:
        """
        חילוץ מידע פיננסי ספציפי מדוחות
        
        Args:
            pdf_path: נתיב לקובץ PDF
            
        Returns:
            Dict: מידע פיננסי מחולץ
        """
        logger.info(f"מחלץ מידע פיננסי מ-{pdf_path}")
        
        financial_data = {
            "amounts": [],
            "percentages": [],
            "dates": [],
            "securities": []
        }
        
        try:
            # מחלץ טקסט מלא
            full_text = self.extract_text(pdf_path)
            
            # חיפוש סכומי כסף
            financial_data["amounts"] = self._extract_money_amounts(full_text)
            
            # חיפוש אחוזים
            financial_data["percentages"] = self._extract_percentages(full_text)
            
            # חיפוש תאריכים
            financial_data["dates"] = self._extract_dates(full_text)
            
            # חיפוש מספרי ISIN וקודי ניירות ערך
            financial_data["securities"] = self._extract_securities_identifiers(full_text)
            
            return financial_data
            
        except Exception as e:
            logger.error(f"שגיאה בחילוץ מידע פיננסי מ-PDF: {e}")
            return financial_data
    
    def _extract_text_with_ocr(self, page) -> str:
        """
        חילוץ טקסט מעמוד PDF באמצעות OCR
        
        Args:
            page: עמוד PDF
            
        Returns:
            str: הטקסט המחולץ
        """
        try:
            # המרת עמוד ל-PIL Image
            # זוהי פונקציה מורכבת שדורשת הפיכת PDF לתמונה
            # עבור הדגמה זו, נחזיר טקסט ריק
            return "טקסט OCR יופיע כאן"
            
        except Exception as e:
            logger.error(f"שגיאה ב-OCR: {e}")
            return ""
    
    def _identify_table_patterns(self, text: str) -> List[Dict[str, Any]]:
        """
        זיהוי תבניות טבלה בטקסט
        
        Args:
            text: טקסט לחיפוש
            
        Returns:
            List[Dict]: רשימת טבלאות מזוהות
        """
        table_candidates = []
        
        # חיפוש שורות שנראות כמו טבלה (עם מספר ערכים מופרדים)
        lines = text.split('\n')
        
        # מעקב אחר שורות רציפות שעשויות להיות טבלה
        current_table = {"content": "", "rows": [], "columns": []}
        table_active = False
        
        for line in lines:
            # בדיקה אם השורה עשויה להיות חלק מטבלה
            is_table_row = bool(re.findall(r'[\t|]+', line)) or len(re.findall(r'\s{3,}', line)) >= 2
            
            if is_table_row:
                if not table_active:
                    # התחלת טבלה חדשה
                    table_active = True
                    current_table = {"content": line, "rows": [line], "columns": []}
                else:
                    # המשך הטבלה הנוכחית
                    current_table["content"] += "\n" + line
                    current_table["rows"].append(line)
            elif table_active and line.strip():
                # שורה שאינה חלק מהטבלה, אך הטבלה היתה פעילה וזו אינה שורה ריקה
                # ייתכן שזה התיאור של הטבלה או תוכן אחר
                current_table["content"] += "\n" + line
            elif table_active and not line.strip():
                # שורה ריקה אחרי טבלה פעילה - סיום הטבלה
                if len(current_table["rows"]) > 1:  # לפחות שתי שורות לטבלה תקפה
                    table_candidates.append(current_table)
                table_active = False
        
        # בדיקה האם הטבלה האחרונה עדיין פעילה בסוף הטקסט
        if table_active and len(current_table["rows"]) > 1:
            table_candidates.append(current_table)
        
        return table_candidates
    
    def _extract_money_amounts(self, text: str) -> List[Dict[str, Any]]:
        """חילוץ סכומי כסף מטקסט"""
        amounts = []
        
        # חיפוש סכומים בפורמט ישראלי/אירופאי (נקודה כמפריד אלפים, פסיק כמפריד עשרוני)
        # ש"ח, ₪, אלפי ₪, אלף ₪, מיליון ₪, מיליוני ₪, מיליארד ₪, מיליארדי ₪, דולר, יורו, €, $
        money_pattern = r'([\d.,]+)(\s*)(אלפי|אלף|מיליון|מיליוני|מיליארד|מיליארדי)?(\s*)(₪|ש"ח|דולר|יורו|€|\$)'
        
        matches = re.finditer(money_pattern, text)
        for match in matches:
            value_str = match.group(1).replace(',', '')
            try:
                value = float(value_str)
                multiplier = match.group(3) or ""
                currency = match.group(5)
                
                # המרת מכפיל למספר
                if multiplier in ["אלף", "אלפי"]:
                    value *= 1_000
                elif multiplier in ["מיליון", "מיליוני"]:
                    value *= 1_000_000
                elif multiplier in ["מיליארד", "מיליארדי"]:
                    value *= 1_000_000_000
                
                amounts.append({
                    "value": value,
                    "original_text": match.group(0),
                    "currency": currency
                })
            except ValueError:
                pass
        
        return amounts
    
    def _extract_percentages(self, text: str) -> List[Dict[str, float]]:
        """חילוץ אחוזים מטקסט"""
        percentages = []
        
        # חיפוש אחוזים (מספר כלשהו ואז סימן אחוז)
        percent_pattern = r'([\d.,]+)(\s*)(%|אחוז|אחוזים)'
        
        matches = re.finditer(percent_pattern, text)
        for match in matches:
            value_str = match.group(1).replace(',', '')
            try:
                value = float(value_str)
                percentages.append({
                    "value": value,
                    "original_text": match.group(0)
                })
            except ValueError:
                pass
        
        return percentages
    
    def _extract_dates(self, text: str) -> List[Dict[str, str]]:
        """חילוץ תאריכים מטקסט"""
        dates = []
        
        # חיפוש תאריכים בפורמט ישראלי (DD/MM/YYYY)
        date_pattern = r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})'
        
        matches = re.finditer(date_pattern, text)
        for match in matches:
            day, month, year = match.groups()
            
            # תיקון שנה דו-ספרתית
            if len(year) == 2:
                year = '20' + year
            
            dates.append({
                "day": int(day),
                "month": int(month),
                "year": int(year),
                "original_text": match.group(0)
            })
        
        return dates
    
    def _extract_securities_identifiers(self, text: str) -> List[Dict[str, str]]:
        """חילוץ מזהי ניירות ערך כמו מספרי ISIN"""
        securities = []
        
        # חיפוש מספרי ISIN (מתחילים ב-IL או US ולאחר מכן 10 תווים)
        isin_pattern = r'(IL|US)[0-9A-Z]{10}'
        
        matches = re.finditer(isin_pattern, text)
        for match in matches:
            securities.append({
                "type": "ISIN",
                "value": match.group(0),
                "original_text": match.group(0)
            })
        
        # חיפוש מספרי נייר ערך ישראליים (בד"כ 6 ספרות)
        il_security_pattern = r'נייר\s*ערך\s*(\d{6})'
        
        matches = re.finditer(il_security_pattern, text)
        for match in matches:
            securities.append({
                "type": "IL_SECURITY",
                "value": match.group(1),
                "original_text": match.group(0)
            })
        
        return securities
