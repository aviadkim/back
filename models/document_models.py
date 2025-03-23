"""
מודלים למסד נתונים לניהול מסמכים, התראות ואנליטיקות.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    """מודל לייצוג מסמך במערכת."""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)  # גודל בבייטים
    mime_type = Column(String(128), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    # מידע לאחר עיבוד
    page_count = Column(Integer, nullable=True)
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")
    
    # יחסים עם מודלים אחרים
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    tables = relationship("DocumentTable", back_populates="document", cascade="all, delete-orphan")
    analytics = relationship("DocumentAnalytics", back_populates="document", cascade="all, delete-orphan")
    memory_entries = relationship("MemoryEntry", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.original_name}')>"


class DocumentPage(Base):
    """מודל לייצוג עמוד במסמך."""
    __tablename__ = 'document_pages'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    page_number = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=True)
    image_path = Column(String(512), nullable=True)
    
    # יחסים
    document = relationship("Document", back_populates="pages")
    tables = relationship("DocumentTable", back_populates="page", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DocumentPage(document_id={self.document_id}, page_number={self.page_number})>"


class DocumentTable(Base):
    """מודל לייצוג טבלה שחולצה ממסמך."""
    __tablename__ = 'document_tables'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    page_id = Column(Integer, ForeignKey('document_pages.id'), nullable=False)
    table_number = Column(Integer, nullable=False)  # המספר הסידורי של הטבלה בעמוד
    table_data = Column(JSON, nullable=False)  # נתוני הטבלה כ-JSON
    table_type = Column(String(50), nullable=True)  # סוג הטבלה (למשל, "balance_sheet", "income_statement")
    
    # יחסים
    document = relationship("Document", back_populates="tables")
    page = relationship("DocumentPage", back_populates="tables")
    
    def __repr__(self):
        return f"<DocumentTable(document_id={self.document_id}, page_id={self.page_id}, table_number={self.table_number})>"


class DocumentAnalytics(Base):
    """מודל לניתוח אנליטי של מסמך."""
    __tablename__ = 'document_analytics'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    analysis_type = Column(String(50), nullable=False)  # סוג הניתוח ("financial", "textual", etc.)
    analysis_data = Column(JSON, nullable=False)  # נתוני הניתוח כ-JSON
    
    # יחסים
    document = relationship("Document", back_populates="analytics")
    
    def __repr__(self):
        return f"<DocumentAnalytics(document_id={self.document_id}, analysis_type='{self.analysis_type}')>"


class MemoryEntry(Base):
    """מודל לייצוג פריט זיכרון הקשור למסמך."""
    __tablename__ = 'memory_entries'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    entry_type = Column(String(50), nullable=False)  # סוג הזיכרון ("query", "insight", "alert")
    content = Column(Text, nullable=False)  # תוכן הזיכרון
    metadata = Column(JSON, nullable=True)  # מטא-דאטה נוסף
    creation_date = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=0)  # כמה פעמים פריט זה נצפה
    is_pinned = Column(Boolean, default=False)  # האם הפריט מקובע לצפייה מהירה
    
    # יחסים
    document = relationship("Document", back_populates="memory_entries")
    
    def __repr__(self):
        return f"<MemoryEntry(id={self.id}, document_id={self.document_id}, entry_type='{self.entry_type}')>"
