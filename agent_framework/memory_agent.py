# agent_framework/memory_agent.py
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
import os
import json

# מבני נתונים פשוטים שיכולים להחליף את המודלים מ-SQLAlchemy
class Document:
    def __init__(self, user_id, filename, original_file_path, **kwargs):
        self.id = kwargs.get('id', str(datetime.now().timestamp()))
        self.user_id = user_id
        self.filename = filename
        self.original_file_path = original_file_path
        self.document_type = kwargs.get('document_type')
        self.upload_date = kwargs.get('upload_date', datetime.now())
        self.processing_status = kwargs.get('processing_status', 'pending')
        self.extracted_text = {}
        self.tables = {}
        self.financial_data = {}
        self.analysis_results = {}
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_file_path": self.original_file_path,
            "document_type": self.document_type,
            "upload_date": self.upload_date,
            "processing_status": self.processing_status,
            "extracted_text": self.extracted_text,
            "tables": self.tables,
            "financial_data": self.financial_data,
            "analysis_results": self.analysis_results
        }
    
    @classmethod
    def from_dict(cls, data):
        doc = cls(
            id=data.get("_id", ""),
            user_id=data.get("user_id", ""),
            filename=data.get("filename", ""),
            original_file_path=data.get("original_file_path", ""),
            document_type=data.get("document_type"),
            upload_date=data.get("upload_date"),
            processing_status=data.get("processing_status", "pending")
        )
        doc.extracted_text = data.get("extracted_text", {})
        doc.tables = data.get("tables", {})
        doc.financial_data = data.get("financial_data", {})
        doc.analysis_results = data.get("analysis_results", {})
        return doc

class Query:
    def __init__(self, user_id, query_text, structured_query, results, document_ids=None, **kwargs):
        self.id = kwargs.get('id', str(datetime.now().timestamp()))
        self.user_id = user_id
        self.query_text = query_text
        self.structured_query = structured_query
        self.results = results
        self.document_ids = document_ids or []
        self.timestamp = kwargs.get('timestamp', datetime.now())
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "query_text": self.query_text,
            "structured_query": self.structured_query,
            "results": self.results,
            "document_ids": self.document_ids,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("_id", ""),
            user_id=data.get("user_id", ""),
            query_text=data.get("query_text", ""),
            structured_query=data.get("structured_query", {}),
            results=data.get("results", {}),
            document_ids=data.get("document_ids", []),
            timestamp=data.get("timestamp")
        )

class MemoryAgent:
    """סוכן זיכרון שמדמה עבודה עם מסד נתונים באמצעות קבצי JSON."""
    
    def __init__(self, mongodb_uri=None):
        self.logger = logging.getLogger(__name__)
        self.documents = {}
        self.queries = {}
        self.data_dir = "data_store"
        os.makedirs(self.data_dir, exist_ok=True)
        self._load_data()
        
    def _load_data(self):
        """טעינת נתונים מקבצי JSON (אם קיימים)."""
        try:
            docs_path = os.path.join(self.data_dir, "documents.json")
            if os.path.exists(docs_path):
                with open(docs_path, 'r') as f:
                    docs_data = json.load(f)
                    for doc_id, doc_data in docs_data.items():
                        self.documents[doc_id] = Document.from_dict(doc_data)
            
            queries_path = os.path.join(self.data_dir, "queries.json")
            if os.path.exists(queries_path):
                with open(queries_path, 'r') as f:
                    queries_data = json.load(f)
                    for query_id, query_data in queries_data.items():
                        self.queries[query_id] = Query.from_dict(query_data)
                        
            self.logger.info(f"Loaded {len(self.documents)} documents and {len(self.queries)} queries from local storage")
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
    
    def _save_data(self):
        """שמירת נתונים לקבצי JSON."""
        try:
            docs_data = {doc_id: doc.to_dict() for doc_id, doc in self.documents.items()}
            with open(os.path.join(self.data_dir, "documents.json"), 'w') as f:
                json.dump(docs_data, f, default=str)
            
            queries_data = {query_id: query.to_dict() for query_id, query in self.queries.items()}
            with open(os.path.join(self.data_dir, "queries.json"), 'w') as f:
                json.dump(queries_data, f, default=str)
                
            self.logger.info("Data saved to local storage")
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
    
    def store_document(self, document):
        """שמירת מסמך."""
        try:
            doc_id = document.id
            self.documents[doc_id] = document
            self._save_data()
            self.logger.info(f"Document stored: {doc_id}")
            return doc_id
        except Exception as e:
            self.logger.error(f"Error storing document: {str(e)}")
            raise
    
    def retrieve_document(self, document_id):
        """שליפת מסמך."""
        try:
            doc = self.documents.get(document_id)
            if not doc:
                self.logger.warning(f"Document not found: {document_id}")
                return None
            return doc
        except Exception as e:
            self.logger.error(f"Error retrieving document: {str(e)}")
            return None
    
    def store_query(self, query):
        """שמירת שאילתה."""
        try:
            query_id = query.id
            self.queries[query_id] = query
            self._save_data()
            self.logger.info(f"Query stored: {query_id}")
            return query_id
        except Exception as e:
            self.logger.error(f"Error storing query: {str(e)}")
            raise
    
    def find_similar_documents(self, text_query, user_id=None, limit=5):
        """חיפוש מסמכים דומים (מודמה)."""
        try:
            results = []
            for doc in self.documents.values():
                if user_id and doc.user_id != user_id:
                    continue
                results.append(doc)
            return results[:limit]
        except Exception as e:
            self.logger.error(f"Error finding similar documents: {str(e)}")
            return []
    
    def find_similar_queries(self, query_text, user_id=None, limit=5):
        """חיפוש שאילתות דומות (מודמה)."""
        try:
            results = []
            for query in self.queries.values():
                if user_id and query.user_id != user_id:
                    continue
                results.append(query)
            return results[:limit]
        except Exception as e:
            self.logger.error(f"Error finding similar queries: {str(e)}")
            return []
    
    def get_user_documents(self, user_id, limit=20, sort_by="upload_date", sort_direction=-1):
        """שליפת מסמכים של משתמש."""
        try:
            results = [doc for doc in self.documents.values() if doc.user_id == user_id]
            return results[:limit]
        except Exception as e:
            self.logger.error(f"Error retrieving user documents: {str(e)}")
            return []
    
    def compare_documents(self, doc_id_1, doc_id_2):
        """השוואה בין מסמכים."""
        try:
            doc1 = self.retrieve_document(doc_id_1)
            doc2 = self.retrieve_document(doc_id_2)
            
            if not doc1 or not doc2:
                return {"error": "One or both documents not found"}
            
            return {
                "documents": {
                    "doc1": {
                        "id": doc_id_1,
                        "filename": doc1.filename
                    },
                    "doc2": {
                        "id": doc_id_2,
                        "filename": doc2.filename
                    }
                },
                "comparison_result": "Documents compared successfully (dummy result)"
            }
        except Exception as e:
            self.logger.error(f"Error comparing documents: {str(e)}")
            return {"error": str(e)}