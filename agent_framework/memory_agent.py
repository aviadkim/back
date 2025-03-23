from typing import List, Dict, Optional, Union
import os
import pickle
import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

class MemoryAgent:
    """
    סוכן לניהול זיכרון ואחסון מסמכים
    מאפשר אחסון מסמכים, יצירת וקטורים, ושליפת מידע רלוונטי
    """
    
    def __init__(self, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        אתחול סוכן הזיכרון
        
        Args:
            embedding_model_name: מודל אמבדינג מקומי מ-HuggingFace
        """
        self.documents = {}  # מילון לאחסון מסמכים גולמיים
        self.vector_store = None  # מאגר וקטורים
        
        # יצירת ספריית אחסון לאמבדינגים
        os.makedirs("data/embeddings", exist_ok=True)
        
        # אתחול מודל אמבדינג (מקומי ללא צורך ב-API key)
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        
        # יצירת מפצל טקסט
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # טעינת מאגר הוקטורים אם קיים
        self._load_vector_store()
    
    def add_document(self, document_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """
        הוספת מסמך למאגר ויצירת אמבדינגים
        
        Args:
            document_id: מזהה ייחודי למסמך
            content: תוכן המסמך
            metadata: מטה-דאטה נוסף על המסמך (אופציונלי)
            
        Returns:
            bool: האם הפעולה הצליחה
        """
        try:
            # שמירת המסמך המקורי
            if metadata is None:
                metadata = {}
            
            self.documents[document_id] = {
                "content": content,
                "metadata": metadata
            }
            
            # יצירת חלקי טקסט ומטה-דאטה
            splits = self.text_splitter.split_text(content)
            metadatas = [{"document_id": document_id, **metadata} for _ in splits]
            
            # הוספה למאגר הוקטורים
            if self.vector_store is None:
                # יצירת מאגר חדש אם לא קיים
                self.vector_store = FAISS.from_texts(splits, self.embeddings, metadatas=metadatas)
            else:
                # הוספה למאגר קיים
                self.vector_store.add_texts(splits, metadatas=metadatas)
            
            # שמירת המאגר המעודכן
            self._save_vector_store()
            
            return True
        except Exception as e:
            print(f"שגיאה בהוספת מסמך: {e}")
            return False
    
    def get_relevant_context(self, query: str, document_ids: Optional[List[str]] = None, k: int = 5) -> str:
        """
        שליפת מידע רלוונטי מהמסמכים בהתאם לשאילתה
        
        Args:
            query: שאילתת חיפוש
            document_ids: רשימת מזהי מסמכים להגבלת החיפוש (אופציונלי)
            k: מספר תוצאות לשליפה
            
        Returns:
            str: הקשר רלוונטי מהמסמכים
        """
        if self.vector_store is None:
            return "אין מידע זמין."
        
        # יצירת פילטר להגבלת חיפוש למסמכים ספציפיים
        filter_dict = None
        if document_ids:
            filter_dict = {"document_id": {"$in": document_ids}}
        
        # חיפוש במאגר הוקטורים
        relevant_docs = self.vector_store.similarity_search(
            query, k=k, filter=filter_dict
        )
        
        # חיבור התוצאות למחרוזת אחת
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        return context
    
    def clear_memory(self) -> bool:
        """
        מחיקת כל המידע מהזיכרון
        
        Returns:
            bool: האם הפעולה הצליחה
        """
        try:
            self.documents = {}
            self.vector_store = None
            
            # מחיקת קבצים מקומיים
            if os.path.exists("data/embeddings/vector_store.pkl"):
                os.remove("data/embeddings/vector_store.pkl")
            
            return True
        except Exception as e:
            print(f"שגיאה במחיקת זיכרון: {e}")
            return False
    
    def _save_vector_store(self) -> None:
        """שמירת מאגר הוקטורים לקובץ"""
        if self.vector_store:
            with open("data/embeddings/vector_store.pkl", "wb") as f:
                pickle.dump(self.vector_store, f)
    
    def _load_vector_store(self) -> None:
        """טעינת מאגר הוקטורים מקובץ"""
        if os.path.exists("data/embeddings/vector_store.pkl"):
            try:
                with open("data/embeddings/vector_store.pkl", "rb") as f:
                    self.vector_store = pickle.load(f)
            except Exception as e:
                print(f"שגיאה בטעינת מאגר וקטורים: {e}")
                self.vector_store = None
