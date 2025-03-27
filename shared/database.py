import os
import logging
from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# הגדרת לוגר
logger = logging.getLogger(__name__)

# SQLAlchemy Base class for models
Base = declarative_base()

# MongoDB connection
def get_mongo_client() -> Optional[MongoClient]:
    """
    יצירת חיבור ל-MongoDB
    
    Returns:
        MongoClient: לקוח MongoDB, או None אם הייתה שגיאה
    """
    mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/financial_documents')
    
    try:
        client = MongoClient(mongo_uri)
        # בדיקת החיבור
        client.admin.command('ping')
        logger.info("MongoDB connection successful")
        return client
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return None

def get_mongo_db(db_name: Optional[str] = None):
    """
    קבלת אובייקט DB מה-MongoDB
    
    Args:
        db_name: שם מסד הנתונים (אופציונלי)
        
    Returns:
        MongoDB database or None
    """
    client = get_mongo_client()
    if not client:
        return None
    
    # אם לא ניתן שם מסד נתונים, משתמש בברירת מחדל
    if not db_name:
        # מחלץ את שם מסד הנתונים מה-URI
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/financial_documents')
        db_name = mongo_uri.split('/')[-1]
        if not db_name or '?' in db_name:  # אם אין שם או יש פרמטרים נוספים
            db_name = 'financial_documents'  # ברירת מחדל
    
    return client[db_name]

# SQLAlchemy engine and session
def init_sqlalchemy_db(app=None):
    """
    אתחול SQLAlchemy עם אפליקציית Flask (אופציונלי)
    
    Args:
        app: אפליקציית Flask (אופציונלי)
        
    Returns:
        tuple: (engine, session)
    """
    # בחירת מנגנון מסד הנתונים
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///financial_documents.db')
    
    # יצירת מנוע SQLAlchemy
    engine = create_engine(db_uri, echo=False)
    
    # יצירת פעולת session בהיקף האפליקציה
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    
    # אם ניתנה אפליקציית Flask, מאתחל באמצעותה
    if app:
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            Session.remove()
    
    # יצירת כל הטבלאות
    Base.metadata.create_all(engine)
    
    return engine, Session

# Database access class
class Database:
    """
    מחלקה לגישה למסד הנתונים
    """
    def __init__(self, use_mongo: bool = True):
        """
        אתחול גישה למסד הנתונים
        
        Args:
            use_mongo: האם להשתמש ב-MongoDB (אחרת SQLAlchemy)
        """
        self.use_mongo = use_mongo
        
        if use_mongo:
            self.client = get_mongo_client()
            if self.client:
                self.db = get_mongo_db()
            else:
                self.db = None
        else:
            self.engine, self.Session = init_sqlalchemy_db()
    
    def get_collection(self, collection_name: str):
        """
        קבלת קולקציית MongoDB
        
        Args:
            collection_name: שם הקולקציה
            
        Returns:
            Collection or None
        """
        if not self.use_mongo or not self.db:
            return None
        
        return self.db[collection_name]
    
    def get_session(self):
        """
        קבלת סשן SQLAlchemy
        
        Returns:
            Session or None
        """
        if self.use_mongo:
            return None
        
        return self.Session()
    
    def store_document(self, collection: str, document: Dict[str, Any]) -> str:
        """
        שמירת מסמך במסד הנתונים
        
        Args:
            collection: שם הקולקציה
            document: המסמך לשמירה
            
        Returns:
            str: מזהה המסמך שנשמר
        """
        if self.use_mongo and self.db:
            result = self.db[collection].insert_one(document)
            return str(result.inserted_id)
        else:
            logger.error("Database connection not available")
            return ""
    
    def find_document(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        חיפוש מסמך במסד הנתונים
        
        Args:
            collection: שם הקולקציה
            query: שאילתת החיפוש
            
        Returns:
            Dict or None: המסמך שנמצא או None
        """
        if self.use_mongo and self.db:
            return self.db[collection].find_one(query)
        else:
            logger.error("Database connection not available")
            return None
    
    def update_document(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """
        עדכון מסמך במסד הנתונים
        
        Args:
            collection: שם הקולקציה
            query: שאילתת החיפוש
            update: עדכון המסמך
            
        Returns:
            bool: האם העדכון הצליח
        """
        if self.use_mongo and self.db:
            result = self.db[collection].update_one(query, {"$set": update})
            return result.modified_count > 0
        else:
            logger.error("Database connection not available")
            return False
    
    def delete_document(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        מחיקת מסמך ממסד הנתונים
        
        Args:
            collection: שם הקולקציה
            query: שאילתת החיפוש
            
        Returns:
            bool: האם המחיקה הצליחה
        """
        if self.use_mongo and self.db:
            result = self.db[collection].delete_one(query)
            return result.deleted_count > 0
        else:
            logger.error("Database connection not available")
            return False

# יצירת מופע ברירת מחדל (singleton)
db = Database()
