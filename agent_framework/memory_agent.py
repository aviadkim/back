"""
סוכן זיכרון (Memory Agent)
אחראי על שמירה, אחזור, והשוואה של מידע לאורך זמן.
"""
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import os
import json
from bson import ObjectId

from models.document_models import Document, MemoryEntry, DocumentAnalytics

class MemoryAgent:
    """
    סוכן הזיכרון אחראי על:
    - שמירת מידע מעובד לצורך שימוש עתידי
    - אחזור מידע היסטורי
    - השוואה בין מסמכים
    - ניהול התראות ותובנות
    """
    
    def __init__(self, db_connector=None):
        """
        אתחול סוכן הזיכרון
        
        Args:
            db_connector: מחבר למסד הנתונים
        """
        self.logger = logging.getLogger(__name__)
        self.db_connector = db_connector
        
    def store_document_data(self, document_id: str, data: Dict[str, Any]) -> bool:
        """
        שמירת מידע מעובד עבור מסמך במסד הנתונים
        
        Args:
            document_id (str): מזהה המסמך
            data (Dict): מידע מעובד מהמסמך
            
        Returns:
            bool: האם השמירה בוצעה בהצלחה
        """
        try:
            # בדיקה האם המסמך כבר קיים
            if self.db_connector:
                self.db_connector.update_document(document_id, {
                    'extracted_text': data.get('document_content', {}),
                    'tables': data.get('tables', {}),
                    'financial_data': data.get('financial_data', {}),
                    'processing_status': 'completed',
                    'last_updated': datetime.now()
                })
                self.logger.info(f"מידע עבור מסמך {document_id} נשמר במסד הנתונים")
                return True
            else:
                # גיבוי לקבצי JSON אם אין חיבור למסד נתונים
                self._store_in_json(document_id, data)
                return True
                
        except Exception as e:
            self.logger.error(f"שגיאה בשמירת מידע עבור מסמך {document_id}: {str(e)}")
            return False
            
    def _store_in_json(self, document_id: str, data: Dict[str, Any]) -> None:
        """
        שמירת נתונים בקובץ JSON כגיבוי
        
        Args:
            document_id (str): מזהה המסמך
            data (Dict): המידע לשמירה
        """
        try:
            os.makedirs('data/memory', exist_ok=True)
            file_path = f'data/memory/{document_id}.json'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"מידע עבור מסמך {document_id} נשמר בקובץ {file_path}")
        except Exception as e:
            self.logger.error(f"שגיאה בשמירת קובץ JSON: {str(e)}")
            
    def retrieve_document_data(self, document_id: str) -> Dict[str, Any]:
        """
        שליפת מידע מעובד עבור מסמך ממסד הנתונים
        
        Args:
            document_id (str): מזהה המסמך
            
        Returns:
            Dict: המידע המעובד או מילון ריק אם לא נמצא
        """
        try:
            if self.db_connector:
                document = self.db_connector.get_document(document_id)
                if document:
                    self.logger.info(f"מידע עבור מסמך {document_id} נשלף ממסד הנתונים")
                    return {
                        'document_content': document.get('extracted_text', {}),
                        'tables': document.get('tables', {}),
                        'financial_data': document.get('financial_data', {}),
                        'document_type': document.get('document_type', 'unknown')
                    }
            else:
                # ניסיון לטעון מקובץ JSON
                return self._load_from_json(document_id)
                
            return {}
            
        except Exception as e:
            self.logger.error(f"שגיאה בשליפת מידע עבור מסמך {document_id}: {str(e)}")
            return {}
            
    def _load_from_json(self, document_id: str) -> Dict[str, Any]:
        """
        טעינת נתונים מקובץ JSON
        
        Args:
            document_id (str): מזהה המסמך
            
        Returns:
            Dict: המידע שנטען או מילון ריק אם לא נמצא
        """
        try:
            file_path = f'data/memory/{document_id}.json'
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.logger.info(f"מידע עבור מסמך {document_id} נטען מקובץ {file_path}")
                return data
            else:
                self.logger.warning(f"לא נמצא קובץ JSON עבור מסמך {document_id}")
                return {}
        except Exception as e:
            self.logger.error(f"שגיאה בטעינת קובץ JSON: {str(e)}")
            return {}
            
    def compare_documents(self, doc_id_1: str, doc_id_2: str) -> Dict[str, Any]:
        """
        השוואה בין שני מסמכים
        
        Args:
            doc_id_1 (str): מזהה המסמך הראשון
            doc_id_2 (str): מזהה המסמך השני
            
        Returns:
            Dict: תוצאות ההשוואה
        """
        try:
            doc1_data = self.retrieve_document_data(doc_id_1)
            doc2_data = self.retrieve_document_data(doc_id_2)
            
            if not doc1_data or not doc2_data:
                return {'error': 'אחד או יותר מהמסמכים לא נמצא'}
                
            # השוואה של נתונים פיננסיים
            comparison = {
                'document_ids': [doc_id_1, doc_id_2],
                'financial_comparison': self._compare_financial_data(
                    doc1_data.get('financial_data', {}),
                    doc2_data.get('financial_data', {})
                ),
                'tables_comparison': self._compare_tables(
                    doc1_data.get('tables', {}),
                    doc2_data.get('tables', {})
                )
            }
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"שגיאה בהשוואת מסמכים: {str(e)}")
            return {'error': str(e)}
            
    def _compare_financial_data(self, data1: Dict, data2: Dict) -> Dict[str, Any]:
        """
        השוואת נתונים פיננסיים בין שני מסמכים
        
        Args:
            data1 (Dict): נתונים פיננסיים מהמסמך הראשון
            data2 (Dict): נתונים פיננסיים מהמסמך השני
            
        Returns:
            Dict: תוצאות ההשוואה הפיננסית
        """
        comparison = {
            'differences': {},
            'changes': {},
            'insights': []
        }
        
        # אם אין מספיק נתונים להשוואה
        if not data1 or not data2:
            return comparison
            
        # השוואת מדדים פיננסיים מרכזיים
        for table_id, table_data1 in data1.items():
            if table_id in data2:
                table_data2 = data2[table_id]
                
                # בדיקה אם יש ניתוח לטבלה
                if 'analysis' in table_data1 and 'analysis' in table_data2:
                    analysis1 = table_data1['analysis']
                    analysis2 = table_data2['analysis']
                    
                    # השוואת ערכים מספריים
                    for key in analysis1:
                        if key in analysis2 and isinstance(analysis1[key], (int, float)) and isinstance(analysis2[key], (int, float)):
                            difference = analysis2[key] - analysis1[key]
                            percent_change = difference / analysis1[key] * 100 if analysis1[key] != 0 else float('inf')
                            
                            comparison['differences'][f"{table_id}.{key}"] = difference
                            comparison['changes'][f"{table_id}.{key}"] = {
                                'difference': difference,
                                'percent_change': percent_change,
                                'old_value': analysis1[key],
                                'new_value': analysis2[key]
                            }
                            
                            # זיהוי שינויים משמעותיים
                            if abs(percent_change) > 10:
                                direction = "עלייה" if difference > 0 else "ירידה"
                                comparison['insights'].append(
                                    f"נמצאה {direction} של {abs(percent_change):.2f}% ב-{key} בטבלה {table_id}"
                                )
        
        return comparison
        
    def _compare_tables(self, tables1: Dict, tables2: Dict) -> Dict[str, Any]:
        """
        השוואת טבלאות בין שני מסמכים
        
        Args:
            tables1 (Dict): טבלאות מהמסמך הראשון
            tables2 (Dict): טבלאות מהמסמך השני
            
        Returns:
            Dict: תוצאות ההשוואה
        """
        # יישום בסיסי - בהמשך ניתן להרחיב
        comparison = {
            'tables_found_in_both': [],
            'tables_only_in_first': [],
            'tables_only_in_second': [],
            'structure_changes': {}
        }
        
        # השוואת מבנה הטבלאות
        for page_num, page_tables1 in tables1.items():
            if page_num in tables2:
                for table in page_tables1:
                    table_id = f"page_{page_num}_table_{table.get('id', '')}"
                    # חיפוש הטבלה המקבילה
                    matching_table = None
                    for t2 in tables2.get(page_num, []):
                        if t2.get('id', '') == table.get('id', ''):
                            matching_table = t2
                            break
                    
                    if matching_table:
                        comparison['tables_found_in_both'].append(table_id)
                        # בדיקת שינויים במבנה
                        if len(table.get('data', [])) != len(matching_table.get('data', [])):
                            comparison['structure_changes'][table_id] = {
                                'rows_first': len(table.get('data', [])),
                                'rows_second': len(matching_table.get('data', []))
                            }
                    else:
                        comparison['tables_only_in_first'].append(table_id)
                        
        # טבלאות שקיימות רק במסמך השני
        for page_num, page_tables2 in tables2.items():
            for table in page_tables2:
                table_id = f"page_{page_num}_table_{table.get('id', '')}"
                found = False
                if page_num in tables1:
                    for t1 in tables1.get(page_num, []):
                        if t1.get('id', '') == table.get('id', ''):
                            found = True
                            break
                
                if not found:
                    comparison['tables_only_in_second'].append(table_id)
        
        return comparison
        
    def find_similar_documents(self, query_text: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        מציאת מסמכים דומים לשאילתה
        
        Args:
            query_text (str): טקסט השאילתה
            user_id (str, optional): מזהה המשתמש לסינון תוצאות
            
        Returns:
            List[Dict]: רשימת מסמכים דומים
        """
        if not self.db_connector:
            self.logger.error("אין חיבור למסד נתונים לביצוע חיפוש")
            return []
            
        try:
            # לוגיקת חיפוש בסיסית - בהמשך ניתן לשדרג לחיפוש סמנטי
            keywords = query_text.lower().split()
            results = []
            
            # חיפוש בכל המסמכים
            documents = self.db_connector.find_documents(user_id)
            
            for doc in documents:
                score = 0
                doc_text = json.dumps(doc.get('extracted_text', {}), ensure_ascii=False).lower()
                
                # בדיקת מספר מילות מפתח שמופיעות במסמך
                for keyword in keywords:
                    if keyword in doc_text:
                        score += 1
                
                if score > 0:
                    results.append({
                        'document_id': doc.get('_id'),
                        'filename': doc.get('filename', ''),
                        'relevance_score': score / len(keywords),
                        'upload_date': doc.get('upload_date')
                    })
            
            # מיון לפי רלוונטיות
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return results[:10]  # החזרת 10 התוצאות הטובות ביותר
            
        except Exception as e:
            self.logger.error(f"שגיאה בחיפוש מסמכים דומים: {str(e)}")
            return []
            
    def store_insight(self, document_id: str, insight_text: str, metadata: Dict[str, Any] = None) -> str:
        """
        שמירת תובנה לגבי מסמך
        
        Args:
            document_id (str): מזהה המסמך
            insight_text (str): טקסט התובנה
            metadata (Dict, optional): מידע נוסף על התובנה
            
        Returns:
            str: מזהה התובנה שנשמרה או ריק אם נכשל
        """
        try:
            if self.db_connector:
                insight_id = str(ObjectId())
                insight = {
                    '_id': insight_id,
                    'document_id': document_id,
                    'entry_type': 'insight',
                    'content': insight_text,
                    'metadata': metadata or {},
                    'creation_date': datetime.now(),
                    'last_accessed': datetime.now(),
                    'access_count': 0
                }
                
                self.db_connector.create_memory_entry(insight)
                self.logger.info(f"תובנה חדשה נשמרה עבור מסמך {document_id}")
                return insight_id
            else:
                # כתיבה לקובץ במקרה שאין מסד נתונים
                self._store_insight_in_json(document_id, insight_text, metadata)
                return f"local_{document_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
        except Exception as e:
            self.logger.error(f"שגיאה בשמירת תובנה: {str(e)}")
            return ""
            
    def _store_insight_in_json(self, document_id: str, insight_text: str, metadata: Dict[str, Any] = None) -> None:
        """
        שמירת תובנה בקובץ JSON
        
        Args:
            document_id (str): מזהה המסמך
            insight_text (str): טקסט התובנה
            metadata (Dict, optional): מידע נוסף על התובנה
        """
        try:
            os.makedirs('data/insights', exist_ok=True)
            file_path = f'data/insights/{document_id}_insights.json'
            
            # קריאת נתונים קיימים אם יש
            insights = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    insights = json.load(f)
            
            # הוספת התובנה החדשה
            insights.append({
                'id': f"local_{document_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'document_id': document_id,
                'content': insight_text,
                'metadata': metadata or {},
                'creation_date': datetime.now().isoformat(),
                'access_count': 0
            })
            
            # שמירת הקובץ המעודכן
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(insights, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"תובנה נשמרה בקובץ JSON עבור מסמך {document_id}")
        except Exception as e:
            self.logger.error(f"שגיאה בשמירת תובנה לקובץ JSON: {str(e)}")
            
    def get_document_insights(self, document_id: str) -> List[Dict[str, Any]]:
        """
        שליפת תובנות עבור מסמך
        
        Args:
            document_id (str): מזהה המסמך
            
        Returns:
            List[Dict]: רשימת תובנות
        """
        try:
            if self.db_connector:
                entries = self.db_connector.get_memory_entries_by_document(document_id, entry_type='insight')
                # עדכון מונה הגישות
                for entry in entries:
                    self.db_connector.update_memory_entry_access(entry.get('_id'))
                
                return entries
            else:
                # שליפה מקובץ JSON
                return self._get_insights_from_json(document_id)
                
        except Exception as e:
            self.logger.error(f"שגיאה בשליפת תובנות: {str(e)}")
            return []
            
    def _get_insights_from_json(self, document_id: str) -> List[Dict[str, Any]]:
        """
        שליפת תובנות מקובץ JSON
        
        Args:
            document_id (str): מזהה המסמך
            
        Returns:
            List[Dict]: רשימת תובנות
        """
        try:
            file_path = f'data/insights/{document_id}_insights.json'
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    insights = json.load(f)
                
                # עדכון מונה הגישות
                for insight in insights:
                    insight['access_count'] = insight.get('access_count', 0) + 1
                
                # שמירת הקובץ המעודכן
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(insights, f, ensure_ascii=False, indent=2)
                
                return insights
            else:
                return []
        except Exception as e:
            self.logger.error(f"שגיאה בשליפת תובנות מקובץ JSON: {str(e)}")
            return []
    
    def detect_anomalies(self, document_id: str, thresholds: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """
        זיהוי אנומליות וחריגות במסמך
        
        Args:
            document_id (str): מזהה המסמך
            thresholds (Dict, optional): ספי ערכים לזיהוי חריגות
            
        Returns:
            List[Dict]: רשימת אנומליות שזוהו
        """
        try:
            document_data = self.retrieve_document_data(document_id)
            if not document_data or not document_data.get('financial_data'):
                return []
            
            # ערכי ברירת מחדל לספים אם לא סופקו
            default_thresholds = {
                'balance_change_percent': 15.0,  # שינוי של יותר מ-15% במאזן
                'ratio_change_percent': 10.0,    # שינוי של יותר מ-10% ביחסים פיננסיים
                'outlier_std_dev': 2.0,          # חריגה של יותר מ-2 סטיות תקן
            }
            
            if thresholds:
                default_thresholds.update(thresholds)
            
            thresholds = default_thresholds
            anomalies = []
            
            financial_data = document_data.get('financial_data', {})
            
            # ניתוח הנתונים הפיננסיים
            for table_id, table_data in financial_data.items():
                if 'analysis' in table_data:
                    analysis = table_data['analysis']
                    table_type = table_data.get('table_type', 'unknown')
                    
                    # בדיקת יחסים פיננסיים לפי סוג הטבלה
                    if table_type == 'balance_sheet':
                        # בדיקת יחס נזילות
                        if 'current_ratio' in analysis and analysis['current_ratio'] < 1.0:
                            anomalies.append({
                                'type': 'financial_ratio',
                                'name': 'current_ratio',
                                'value': analysis['current_ratio'],
                                'expected': '≥ 1.0',
                                'severity': 'high' if analysis['current_ratio'] < 0.8 else 'medium',
                                'message': f"יחס נזילות נמוך מאוד: {analysis['current_ratio']:.2f}",
                                'table_id': table_id
                            })
                    
                    elif table_type == 'income_statement':
                        # בדיקת רווחיות
                        if 'profit_margin' in analysis and analysis['profit_margin'] < 0:
                            anomalies.append({
                                'type': 'financial_ratio',
                                'name': 'profit_margin',
                                'value': analysis['profit_margin'],
                                'expected': '≥ 0',
                                'severity': 'high',
                                'message': f"הפסד נקי: {analysis['profit_margin']:.2f}%",
                                'table_id': table_id
                            })
            
            # שמירת האנומליות שזוהו
            for anomaly in anomalies:
                self.store_insight(
                    document_id,
                    anomaly['message'],
                    {'anomaly_data': anomaly}
                )
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"שגיאה בזיהוי אנומליות: {str(e)}")
            return []
            
    def generate_report_summary(self, document_id: str) -> Dict[str, Any]:
        """
        יצירת סיכום למסמך
        
        Args:
            document_id (str): מזהה המסמך
            
        Returns:
            Dict: סיכום המסמך
        """
        try:
            document_data = self.retrieve_document_data(document_id)
            if not document_data:
                return {'error': 'המסמך לא נמצא'}
            
            # איסוף נתונים מרכזיים
            financial_data = document_data.get('financial_data', {})
            tables_count = len(document_data.get('tables', {}))
            
            # ניתוח נתונים פיננסיים מרכזיים
            key_metrics = {}
            insights = []
            
            for table_id, table_data in financial_data.items():
                if 'analysis' in table_data:
                    table_type = table_data.get('table_type', 'unknown')
                    analysis = table_data['analysis']
                    
                    # איסוף מדדים לפי סוג הטבלה
                    if table_type == 'balance_sheet':
                        key_metrics['total_assets'] = analysis.get('total_assets')
                        key_metrics['total_liabilities'] = analysis.get('total_liabilities')
                        key_metrics['equity'] = analysis.get('equity')
                        
                        if 'current_ratio' in analysis:
                            key_metrics['current_ratio'] = analysis['current_ratio']
                            if analysis['current_ratio'] < 1.0:
                                insights.append("יחס נזילות מתחת ל-1, מצביע על קשיי נזילות אפשריים")
                            elif analysis['current_ratio'] > 3.0:
                                insights.append("יחס נזילות גבוה מעל 3, ייתכן שהחברה אינה משתמשת ביעילות בנכסיה")
                    
                    elif table_type == 'income_statement':
                        key_metrics['revenue'] = analysis.get('revenue')
                        key_metrics['expenses'] = analysis.get('expenses')
                        key_metrics['net_income'] = analysis.get('net_income')
                        
                        if 'profit_margin' in analysis:
                            key_metrics['profit_margin'] = analysis['profit_margin']
                            if analysis['profit_margin'] < 0:
                                insights.append("החברה מראה הפסד בתקופה זו")
                            elif analysis['profit_margin'] > 20:
                                insights.append("רווחיות גבוהה במיוחד, מעל 20%")
            
            # זיהוי אנומליות
            anomalies = self.detect_anomalies(document_id)
            
            # יצירת הסיכום
            summary = {
                'document_id': document_id,
                'tables_count': tables_count,
                'key_metrics': key_metrics,
                'insights': insights,
                'anomalies_detected': len(anomalies),
                'generation_time': datetime.now().isoformat()
            }
            
            # שמירת הסיכום כתובנה
            self.store_insight(
                document_id,
                f"סיכום דוח: זוהו {len(insights)} תובנות ו-{len(anomalies)} חריגות",
                {'summary': summary}
            )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"שגיאה ביצירת סיכום דוח: {str(e)}")
            return {'error': str(e)}
