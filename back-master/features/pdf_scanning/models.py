from datetime import datetime
from typing import Dict, List, Any, Optional
from shared.database import Base, db
from sqlalchemy import Column, String, DateTime, Integer, Text, JSON

class ScannedDocument:
    """
    מודל מסמך סרוק במונגו DB
    """
    def __init__(self,
                 document_id: str,
                 original_filename: str,
                 stored_filename: str,
                 file_path: str,
                 language: str = 'he',
                 text_content: str = '',
                 tables: List[Dict[str, Any]] = None,
                 financial_data: Dict[str, Any] = None):
        """
        אתחול מסמך סרוק
        
        Args:
            document_id: מזהה המסמך
            original_filename: שם הקובץ המקורי
            stored_filename: שם הקובץ בשרת
            file_path: נתיב הקובץ
            language: שפת המסמך
            text_content: תוכן הטקסט
            tables: טבלאות שחולצו
            financial_data: מידע פיננסי שחולץ
        """
        self.document_id = document_id
        self.original_filename = original_filename
        self.stored_filename = stored_filename
        self.file_path = file_path
        self.language = language
        self.text_content = text_content
        self.tables = tables or []
        self.financial_data = financial_data or {}
        self.processing_date = datetime.now()
        self.text_length = len(text_content) if text_content else 0
        self.table_count = len(tables) if tables else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        המרה למילון
        
        Returns:
            Dict: המסמך כמילון
        """
        return {
            "document_id": self.document_id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_path": self.file_path,
            "language": self.language,
            "text_content": self.text_content,
            "tables": self.tables,
            "financial_data": self.financial_data,
            "processing_date": self.processing_date.isoformat(),
            "text_length": self.text_length,
            "table_count": self.table_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScannedDocument':
        """
        יצירת מופע ממילון
        
        Args:
            data: המילון עם הנתונים
            
        Returns:
            ScannedDocument: המסמך הסרוק
        """
        # המרת תאריך אם הוא מחרוזת
        if isinstance(data.get('processing_date'), str):
            try:
                processing_date = datetime.fromisoformat(data['processing_date'])
            except ValueError:
                processing_date = datetime.now()
        else:
            processing_date = data.get('processing_date', datetime.now())
        
        doc = cls(
            document_id=data.get('document_id', ''),
            original_filename=data.get('original_filename', ''),
            stored_filename=data.get('stored_filename', ''),
            file_path=data.get('file_path', ''),
            language=data.get('language', 'he'),
            text_content=data.get('text_content', ''),
            tables=data.get('tables', []),
            financial_data=data.get('financial_data', {})
        )
        
        doc.processing_date = processing_date
        doc.text_length = data.get('text_length', len(doc.text_content))
        doc.table_count = data.get('table_count', len(doc.tables))
        
        return doc

class SQLScannedDocument(Base):
    """
    מודל מסמך סרוק עבור SQLAlchemy
    """
    __tablename__ = 'scanned_documents'
    
    id = Column(String(50), primary_key=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    language = Column(String(10), nullable=False, default='he')
    processing_date = Column(DateTime, default=datetime.utcnow)
    text_length = Column(Integer, default=0)
    table_count = Column(Integer, default=0)
    text_content = Column(Text, nullable=True)
    tables = Column(JSON, nullable=True)
    financial_data = Column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        המרה למילון
        """
        return {
            "document_id": self.id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_path": self.file_path,
            "language": self.language,
            "text_content": self.text_content,
            "tables": self.tables,
            "financial_data": self.financial_data,
            "processing_date": self.processing_date.isoformat(),
            "text_length": self.text_length,
            "table_count": self.table_count
        }
