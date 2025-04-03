import os
import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple, BinaryIO
from datetime import datetime
from werkzeug.datastructures import FileStorage

from shared.pdf_utils import PDFProcessor
from shared.file_utils import save_uploaded_file, save_json_data
from shared.database import db
from .models import ScannedDocument

# הגדרת לוגר
logger = logging.getLogger(__name__)

class PDFScanningService:
    """
    שירות לסריקת קבצי PDF
    """
    def __init__(self):
        """אתחול השירות"""
        self.pdf_processor = None
    
    def scan_pdf(self, file: FileStorage, language: str = 'he') -> Optional[Dict[str, Any]]:
        """
        סריקת קובץ PDF וחילוץ מידע
        
        Args:
            file: קובץ ה-PDF
            language: שפת המסמך
            
        Returns:
            Dict: תוצאות הסריקה, או None אם הייתה שגיאה
        """
        try:
            # שמירת הקובץ
            file_path, stored_filename = save_uploaded_file(file, file.filename)
            logger.info(f"File saved: {file_path}")
            
            # יצירת מזהה ייחודי למסמך
            document_id = os.path.basename(file_path)
            
            # חילוץ הטקסט והמידע מהקובץ
            return self._process_pdf_file(
                document_id=document_id,
                original_filename=file.filename,
                stored_filename=stored_filename,
                file_path=file_path,
                language=language
            )
            
        except Exception as e:
            logger.error(f"Error scanning PDF: {str(e)}", exc_info=True)
            return None
    
    def _process_pdf_file(self, document_id: str, original_filename: str, 
                          stored_filename: str, file_path: str,
                          language: str = 'he') -> Dict[str, Any]:
        """
        עיבוד קובץ PDF
        
        Args:
            document_id: מזהה המסמך
            original_filename: שם הקובץ המקורי
            stored_filename: שם הקובץ בשרת
            file_path: נתיב הקובץ
            language: שפת המסמך
            
        Returns:
            Dict: תוצאות העיבוד
        """
        # יצירת מעבד PDF עם OCR מופעל
        self.pdf_processor = PDFProcessor(
            ocr_enabled=True,
            lang="heb+eng" if language == "he" else "eng"
        )
        
        # חילוץ טקסט
        text = self.pdf_processor.extract_text(file_path)
        logger.info(f"Extracted text ({len(text)} chars) from {file_path}")
        
        # חילוץ טבלאות
        tables = self.pdf_processor.extract_tables(file_path)
        logger.info(f"Extracted {len(tables)} tables from {file_path}")
        
        # חילוץ מידע פיננסי
        financial_data = self.pdf_processor.extract_financial_data(file_path)
        logger.info(f"Extracted financial data from {file_path}")
        
        # יצירת מסמך סרוק
        document = ScannedDocument(
            document_id=document_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            language=language,
            text_content=text,
            tables=tables,
            financial_data=financial_data
        )
        
        # שמירת הנתונים
        self._save_document(document)
        
        return document.to_dict()
    
    def _save_document(self, document: ScannedDocument) -> bool:
        """
        שמירת מסמך סרוק במסד הנתונים ובמערכת הקבצים
        
        Args:
            document: המסמך הסרוק
            
        Returns:
            bool: האם השמירה הצליחה
        """
        try:
            # שמירה במסד הנתונים
            if db.use_mongo:
                # שמירה ב-MongoDB
                db.store_document("scanned_documents", document.to_dict())
            else:
                # שמירה באמצעות SQLAlchemy
                from .models import SQLScannedDocument
                session = db.get_session()
                sql_doc = SQLScannedDocument(
                    id=document.document_id,
                    original_filename=document.original_filename,
                    stored_filename=document.stored_filename,
                    file_path=document.file_path,
                    language=document.language,
                    text_content=document.text_content,
                    tables=document.tables,
                    financial_data=document.financial_data,
                    text_length=document.text_length,
                    table_count=document.table_count
                )
                session.add(sql_doc)
                session.commit()
                session.close()
            
            # שמירה כקובץ JSON
            json_filename = f"{document.document_id}.json"
            save_json_data(document.to_dict(), json_filename)
            
            logger.info(f"Document saved: {document.document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}", exc_info=True)
            return False
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        קבלת מסמך סרוק לפי מזהה
        
        Args:
            document_id: מזהה המסמך
            
        Returns:
            Dict: המסמך הסרוק, או None אם לא נמצא
        """
        try:
            if db.use_mongo:
                # חיפוש ב-MongoDB
                doc_data = db.find_document("scanned_documents", {"document_id": document_id})
                if not doc_data:
                    return None
                
                return doc_data
            else:
                # חיפוש באמצעות SQLAlchemy
                from .models import SQLScannedDocument
                session = db.get_session()
                sql_doc = session.query(SQLScannedDocument).filter_by(id=document_id).first()
                if not sql_doc:
                    session.close()
                    return None
                
                result = sql_doc.to_dict()
                session.close()
                return result
                
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {str(e)}", exc_info=True)
            return None
    
    def get_all_documents(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        קבלת רשימת מסמכים סרוקים
        
        Args:
            limit: מספר מקסימלי של מסמכים להחזרה
            offset: היסט למיון
            
        Returns:
            List[Dict]: רשימת המסמכים
        """
        try:
            if db.use_mongo:
                # חיפוש ב-MongoDB
                collection = db.get_collection("scanned_documents")
                if not collection:
                    return []
                
                docs = list(collection.find().sort("processing_date", -1).skip(offset).limit(limit))
                return docs
            else:
                # חיפוש באמצעות SQLAlchemy
                from .models import SQLScannedDocument
                session = db.get_session()
                query = session.query(SQLScannedDocument).order_by(
                    SQLScannedDocument.processing_date.desc()
                ).offset(offset).limit(limit)
                
                docs = [doc.to_dict() for doc in query.all()]
                session.close()
                return docs
                
        except Exception as e:
            logger.error(f"Error getting all documents: {str(e)}", exc_info=True)
            return []

# יצירת מופע singleton של השירות
pdf_scanning_service = PDFScanningService()
