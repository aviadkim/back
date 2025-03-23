from typing import Dict, List, Any, Optional
import logging
import os

from pdf_processor.extraction.text_extractor import PDFTextExtractor
from pdf_processor.tables.table_extractor import TableExtractor
from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer
from .table_generator import CustomTableGenerator
from .nlp_agent import NaturalLanguageQueryAgent
from .memory_agent import MemoryAgent
from .analytics_agent import AnalyticsAgent
from models.document_models import Document, Query
from agents.base.base_agent import BaseAgent
from agents.financial.financial_agent import FinancialAgent

class AgentCoordinator:
    """מתאם הסוכנים שאחראי על תיאום פעולות בין סוכנים שונים במערכת."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents = {}
        self.context = {}  # הקשר משותף לסוכנים לחילופי מידע
        
        # אתחול הסוכנים הבסיסיים
        self._initialize_core_agents()
        
    def _initialize_core_agents(self):
        """אתחול סוכני הליבה של המערכת."""
        try:
            # יצירת רכיבי עיבוד ליבה
            text_extractor = PDFTextExtractor()
            table_extractor = TableExtractor()
            financial_analyzer = FinancialAnalyzer()
            financial_agent = FinancialAgent()
            table_generator = CustomTableGenerator(financial_analyzer)
            nlp_agent = NaturalLanguageQueryAgent()
            
            # אתחול סוכן הזיכרון
            memory_agent = MemoryAgent()
            self.register_agent('memory_agent', memory_agent)

            # אתחול סוכן האנליטיקה
            analytics_agent = AnalyticsAgent(memory_agent)
            self.register_agent('analytics_agent', analytics_agent)
            
            # רישום הסוכנים
            self.register_agent('extractor', text_extractor)
            self.register_agent('table_extractor', table_extractor)
            self.register_agent('financial_analyzer', financial_analyzer)
            self.register_agent('financial_agent', financial_agent)
            self.register_agent('table_generator', table_generator)
            self.register_agent('nlp_agent', nlp_agent)
            
            self.logger.info("הסוכנים העיקריים אותחלו בהצלחה")
        except Exception as e:
            self.logger.error(f"שגיאה באתחול הסוכנים העיקריים: {str(e)}")
            raise
        
    def register_agent(self, agent_name: str, agent_instance: Any) -> None:
        """רישום סוכן במתאם."""
        self.agents[agent_name] = agent_instance
        self.logger.info(f"נרשם סוכן: {agent_name}")
        
    def process_document(self, pdf_path: str) -> Dict[str, Any]:
        """עיבוד מסמך דרך צינור הסוכנים המלא."""
        results = {}
        
        try:
            # חילוץ טקסט וסיווג המסמך
            if 'extractor' in self.agents:
                self.logger.info("מפעיל סוכן חילוץ טקסט")
                document_content = self.agents['extractor'].extract_document(pdf_path)
                self.context['document_content'] = document_content
                results['document_content'] = document_content
            
            # חילוץ טבלאות
            if 'table_extractor' in self.agents:
                self.logger.info("מפעיל סוכן חילוץ טבלאות")
                tables = self.agents['table_extractor'].extract_tables(pdf_path)
                self.context['tables'] = tables
                results['tables'] = tables
            
            # ניתוח פיננסי
            if 'financial_analyzer' in self.agents and 'tables' in self.context:
                self.logger.info("מפעיל סוכן ניתוח פיננסי")
                financial_data = {}
                
                for page_num, page_tables in self.context['tables'].items():
                    for table in page_tables:
                        df = self.agents['table_extractor'].convert_to_dataframe(table)
                        if not df.empty:
                            # סיווג וניתוח הטבלה
                            table_type = self.agents['financial_analyzer'].classify_table(df)
                            analysis = self.agents['financial_analyzer'].analyze_financial_table(df, table_type)
                            
                            table_id = f"page_{page_num}_table_{table['id']}"
                            financial_data[table_id] = {
                                'table_type': table_type,
                                'analysis': analysis,
                                'dataframe': df.to_dict(orient='records')
                            }
                
                self.context['financial_data'] = financial_data
                results['financial_data'] = financial_data
                
                # עיבוד נוסף עם סוכן פיננסי ספציפי
                if 'financial_agent' in self.agents:
                    self.logger.info("מפעיל סוכן פיננסי לניתוח מתקדם")
                    advanced_analysis = self.agents['financial_agent'].analyze_financial_data(financial_data)
                    results['advanced_financial_analysis'] = advanced_analysis
            
            # שמירת המידע במסד הנתונים אם יש סוכן זיכרון
            if 'memory_agent' in self.agents:
                try:
                    # יצירת מודל מסמך
                    document = Document(
                        user_id=getattr(request, 'user_id', 'default_user'),  # בממשק אמיתי, יש להשתמש במזהה המשתמש האמיתי
                        filename=os.path.basename(pdf_path),
                        original_file_path=pdf_path,
                        processing_status="completed"
                    )
                    
                    # הוספת המידע המעובד
                    document.extracted_text = results.get('document_content', {})
                    document.tables = results.get('tables', {})
                    document.financial_data = results.get('financial_data', {})
                    
                    # שמירת המסמך
                    document_id = self.agents['memory_agent'].store_document(document)
                    
                    # עדכון המזהה בתוצאות
                    results['document_id'] = document_id
                    self.logger.info(f"Document stored in database with ID: {document_id}")
                except Exception as e:
                    self.logger.error(f"Error storing document in database: {str(e)}")
                    # ממשיכים גם אם יש שגיאה בשמירה
                
            self.logger.info("עיבוד המסמך הושלם בהצלחה")
            return results
            
        except Exception as e:
            self.logger.error(f"שגיאה בעיבוד המסמך: {str(e)}")
            raise
        
    def generate_custom_table(self, document_id: str, query_spec: Dict[str, Any]) -> Dict[str, Any]:
        """יצירת טבלה מותאמת אישית על סמך מפרט שאילתה."""
        try:
            # שליפת מידע מעובד עבור המסמך
            # במימוש אמיתי, זה יגיע ממסד נתונים
            if 'financial_data' not in self.context:
                self.logger.error("אין מידע פיננסי זמין ליצירת טבלה")
                return {"error": "אין מידע פיננסי זמין"}
            
            financial_data = self.context['financial_data']
            
            # שימוש בסוכן מחולל הטבלאות ליצירת הטבלה המותאמת אישית
            if 'table_generator' in self.agents:
                df = self.agents['table_generator'].generate_custom_table(financial_data, query_spec)
                
                if df.empty:
                    return {
                        "columns": [],
                        "rows": [],
                        "message": "לא נמצא מידע התואם את הקריטריונים שהוגדרו"
                    }
                
                return {
                    "columns": df.columns.tolist(),
                    "rows": df.to_dict(orient='records')
                }
            else:
                self.logger.error("סוכן מחולל הטבלאות אינו זמין")
                return {"error": "מחולל הטבלאות אינו זמין"}
                
        except Exception as e:
            self.logger.error(f"שגיאה ביצירת טבלה מותאמת אישית: {str(e)}")
            return {"error": str(e)}
    
    def process_natural_language_query(self, document_id: str, query_text: str) -> Dict[str, Any]:
        """עיבוד שאילתה בשפה טבעית ליצירת טבלה מותאמת אישית."""
        try:
            if 'nlp_agent' not in self.agents:
                self.logger.error("סוכן NLP לא זמין")
                return {"error": "עיבוד שפה טבעית לא זמין"}
            
            # המרת השאילתה בשפה טבעית לשאילתה מובנית
            structured_query = self.agents['nlp_agent'].process_query(query_text)
            
            # יצירת הטבלה בהתבסס על השאילתה המובנית
            table_result = self.generate_custom_table(document_id, structured_query)
            
            # הוספת השאילתה המפורשת לתשובה
            if 'error' not in table_result:
                table_result['query'] = structured_query
                
            return table_result
            
        except Exception as e:
            self.logger.error(f"שגיאה בעיבוד שאילתה בשפה טבעית: {str(e)}")
            return {"error": str(e)}
            
    def analyze_portfolio_trends(self, user_id: str, time_period: int = 180) -> Dict[str, Any]:
        """ניתוח מגמות בתיק השקעות לאורך זמן."""
        try:
            if 'analytics_agent' not in self.agents:
                self.logger.error("Analytics agent not available")
                return {"error": "Analytics not available"}
            
            return self.agents['analytics_agent'].analyze_portfolio_trends(user_id, time_period)
        except Exception as e:
            self.logger.error(f"Error analyzing portfolio trends: {str(e)}")
            return {"error": str(e)}
    
    def generate_document_insights(self, document_id: str) -> Dict[str, Any]:
        """הפקת תובנות ממסמך פיננסי."""
        try:
            if 'analytics_agent' not in self.agents:
                self.logger.error("Analytics agent not available")
                return {"error": "Analytics not available"}
            
            return self.agents['analytics_agent'].generate_insights(document_id)
        except Exception as e:
            self.logger.error(f"Error generating document insights: {str(e)}")
            return {"error": str(e)}
    
    def find_similar_documents(self, text_query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """חיפוש מסמכים דומים לפי שאילתת טקסט."""
        try:
            if 'memory_agent' not in self.agents:
                self.logger.error("Memory agent not available")
                return {"error": "Document search not available"}
            
            documents = self.agents['memory_agent'].find_similar_documents(text_query, user_id)
            
            return {
                "query": text_query,
                "results_count": len(documents),
                "documents": [
                    {
                        "id": doc.id,
                        "filename": doc.filename,
                        "upload_date": doc.upload_date,
                        "document_type": doc.document_type
                    } for doc in documents
                ]
            }
        except Exception as e:
            self.logger.error(f"Error finding similar documents: {str(e)}")
            return {"error": str(e)}
    
    def detect_outliers(self, user_id: str, metric: str = 'yield_percent') -> Dict[str, Any]:
        """זיהוי חריגות בנתונים פיננסיים."""
        try:
            if 'analytics_agent' not in self.agents:
                self.logger.error("Analytics agent not available")
                return {"error": "Analytics not available"}
            
            return self.agents['analytics_agent'].detect_outliers(user_id, metric)
        except Exception as e:
            self.logger.error(f"Error detecting outliers: {str(e)}")
            return {"error": str(e)}
    
    def remember_query(self, user_id: str, query_text: str, 
                        structured_query: Dict[str, Any], 
                        results: Dict[str, Any],
                        document_ids: List[str] = None) -> str:
        """שמירת שאילתה בשפה טבעית והתוצאות שלה לצורך למידה."""
        try:
            if 'memory_agent' not in self.agents:
                self.logger.error("Memory agent not available")
                return None
            
            query = Query(
                user_id=user_id,
                query_text=query_text,
                structured_query=structured_query,
                results=results,
                document_ids=document_ids or []
            )
            
            query_id = self.agents['memory_agent'].store_query(query)
            self.logger.info(f"Query stored in database with ID: {query_id}")
            
            return query_id
        except Exception as e:
            self.logger.error(f"Error storing query: {str(e)}")
            return None