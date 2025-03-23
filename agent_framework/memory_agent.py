# agent_framework/memory_agent.py
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
import pymongo
from pymongo import MongoClient
from models.document_models import Document, Query

class MemoryAgent:
    """סוכן זיכרון המטפל בשמירה ואחזור מידע ממסד הנתונים."""
    
    def __init__(self, mongodb_uri="mongodb://localhost:27017/"):
        self.logger = logging.getLogger(__name__)
        self.client = MongoClient(mongodb_uri)
        self.db = self.client.financial_documents_db
        
        # וידוא קיום האוספים
        if "documents" not in self.db.list_collection_names():
            self.db.create_collection("documents")
            self.db.documents.create_index([("user_id", pymongo.ASCENDING)])
            self.db.documents.create_index([("filename", pymongo.TEXT)])
        
        if "queries" not in self.db.list_collection_names():
            self.db.create_collection("queries")
            self.db.queries.create_index([("user_id", pymongo.ASCENDING)])
            self.db.queries.create_index([("query_text", pymongo.TEXT)])
    
    def store_document(self, document: Document) -> str:
        """שמירת מסמך במסד הנתונים."""
        try:
            doc_dict = document.to_dict()
            
            # בדיקה אם המסמך כבר קיים
            existing_doc = self.db.documents.find_one({"_id": document.id})
            
            if existing_doc:
                # עדכון מסמך קיים
                self.db.documents.update_one(
                    {"_id": document.id},
                    {"$set": doc_dict}
                )
                self.logger.info(f"Document updated: {document.id}")
            else:
                # הוספת מסמך חדש
                result = self.db.documents.insert_one(doc_dict)
                document.id = str(result.inserted_id)
                self.logger.info(f"Document stored: {document.id}")
            
            return document.id
            
        except Exception as e:
            self.logger.error(f"Error storing document: {str(e)}")
            raise
    
    def retrieve_document(self, document_id: str) -> Optional[Document]:
        """שליפת מסמך ממסד הנתונים."""
        try:
            doc_dict = self.db.documents.find_one({"_id": document_id})
            
            if doc_dict:
                return Document.from_dict(doc_dict)
            
            self.logger.warning(f"Document not found: {document_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving document: {str(e)}")
            return None
    
    def store_query(self, query: Query) -> str:
        """שמירת שאילתה במסד הנתונים."""
        try:
            query_dict = query.to_dict()
            
            # בדיקה אם השאילתה כבר קיימת
            existing_query = self.db.queries.find_one({"_id": query.id})
            
            if existing_query:
                # עדכון שאילתה קיימת
                self.db.queries.update_one(
                    {"_id": query.id},
                    {"$set": query_dict}
                )
                self.logger.info(f"Query updated: {query.id}")
            else:
                # הוספת שאילתה חדשה
                result = self.db.queries.insert_one(query_dict)
                query.id = str(result.inserted_id)
                self.logger.info(f"Query stored: {query.id}")
            
            return query.id
            
        except Exception as e:
            self.logger.error(f"Error storing query: {str(e)}")
            raise
    
    def find_similar_documents(self, text_query: str, user_id: Optional[str] = None, 
                               limit: int = 5) -> List[Document]:
        """חיפוש מסמכים דומים על סמך שאילתת טקסט."""
        try:
            query = {"$text": {"$search": text_query}}
            
            if user_id:
                query["user_id"] = user_id
                
            docs = self.db.documents.find(
                query,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            return [Document.from_dict(doc) for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Error finding similar documents: {str(e)}")
            return []
    
    def find_similar_queries(self, query_text: str, user_id: Optional[str] = None,
                             limit: int = 5) -> List[Query]:
        """חיפוש שאילתות דומות על סמך טקסט."""
        try:
            query = {"$text": {"$search": query_text}}
            
            if user_id:
                query["user_id"] = user_id
                
            queries = self.db.queries.find(
                query,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            return [Query.from_dict(q) for q in queries]
            
        except Exception as e:
            self.logger.error(f"Error finding similar queries: {str(e)}")
            return []
    
    def get_user_documents(self, user_id: str, limit: int = 20, 
                           sort_by: str = "upload_date", 
                           sort_direction: int = -1) -> List[Document]:
        """שליפת כל המסמכים של משתמש מסוים."""
        try:
            docs = self.db.documents.find(
                {"user_id": user_id}
            ).sort(sort_by, sort_direction).limit(limit)
            
            return [Document.from_dict(doc) for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Error retrieving user documents: {str(e)}")
            return []
    
    def compare_documents(self, doc_id_1: str, doc_id_2: str) -> Dict[str, Any]:
        """השוואה בין שני מסמכים."""
        try:
            doc1 = self.retrieve_document(doc_id_1)
            doc2 = self.retrieve_document(doc_id_2)
            
            if not doc1 or not doc2:
                self.logger.warning("One or both documents not found")
                return {"error": "One or both documents not found"}
            
            comparison = {
                "documents": {
                    "doc1": {
                        "id": doc_id_1,
                        "filename": doc1.filename,
                        "document_type": doc1.document_type,
                        "upload_date": doc1.upload_date
                    },
                    "doc2": {
                        "id": doc_id_2,
                        "filename": doc2.filename,
                        "document_type": doc2.document_type,
                        "upload_date": doc2.upload_date
                    }
                },
                "financial_comparison": {}
            }
            
            # השוואת נתונים פיננסיים אם קיימים
            if doc1.financial_data and doc2.financial_data:
                # כאן יכנס קוד להשוואת נתונים פיננסיים ספציפיים
                # לדוגמה, השוואת תיק השקעות, תשואות, וכו'
                pass
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error comparing documents: {str(e)}")
            return {"error": str(e)}
