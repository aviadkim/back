from typing import Dict, List, Any, Optional
import pandas as pd
import re
import logging

class CustomTableGenerator:
    """סוכן שמייצר טבלאות מותאמות אישית לפי דרישות המשתמש."""
    
    def __init__(self, financial_analyzer=None):
        self.logger = logging.getLogger(__name__)
        self.financial_analyzer = financial_analyzer
        
    def generate_custom_table(self, financial_data: Dict[str, Any], query: Dict[str, Any]) -> pd.DataFrame:
        """יצירת טבלה מותאמת אישית על סמך מפרט שאילתה.
        
        Args:
            financial_data: מידע פיננסי שחולץ ממסמכים
            query: מפרט שאילתה עם מסננים, עמודות, וכו'
            
        Returns:
            DataFrame המכיל את הטבלה המותאמת אישית
        """
        # חילוץ כל הטבלאות לתוך DataFrames
        all_dataframes = []
        
        for table_id, table_info in financial_data.items():
            if 'dataframe' in table_info:
                # שימוש ב-dataframe המאוחסן אם זמין
                df = pd.DataFrame(table_info['dataframe'])
                if not df.empty:
                    # הוספת מקור וסוג_טבלה כעמודות מטא-נתונים
                    df['source_table'] = table_id
                    df['table_type'] = table_info.get('table_type', 'unknown')
                    all_dataframes.append(df)
            elif 'analysis' in table_info:
                # חילוץ נתונים לפורמט סטנדרטי
                df = self._extract_table_data(table_id, table_info)
                if not df.empty:
                    all_dataframes.append(df)
        
        # שילוב כל ה-DataFrames
        if not all_dataframes:
            self.logger.warning("לא נמצאו נתונים מתאימים לטבלה המותאמת אישית")
            return pd.DataFrame()
            
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # החלת מסננים
        if 'filters' in query and query['filters']:
            combined_df = self._apply_filters(combined_df, query['filters'])
        
        # בחירת עמודות
        if 'columns' in query and query['columns']:
            # כלול רק עמודות שקיימות ב-dataframe
            columns = [col for col in query['columns'] if col in combined_df.columns]
            if columns:
                # תמיד כלול source_table ו-table_type לייחוס
                if 'source_table' in combined_df.columns and 'source_table' not in columns:
                    columns.append('source_table')
                if 'table_type' in combined_df.columns and 'table_type' not in columns:
                    columns.append('table_type')
                    
                combined_df = combined_df[columns]
        
        # החלת קיבוץ
        if 'group_by' in query and query['group_by'] in combined_df.columns:
            group_cols = [query['group_by']]
            
            # טיפול באגרגציה
            if 'aggregate' in query and query['aggregate']:
                aggregations = query['aggregate']
                combined_df = combined_df.groupby(group_cols).agg(aggregations).reset_index()
            else:
                # אגרגציה ברירת מחדל היא סכום לעמודות מספריות
                numeric_cols = combined_df.select_dtypes(include=['number']).columns
                agg_dict = {col: 'sum' for col in numeric_cols if col not in group_cols}
                
                # השתמש בראשון עבור עמודות לא מספריות
                non_numeric_cols = combined_df.select_dtypes(exclude=['number']).columns
                for col in non_numeric_cols:
                    if col not in group_cols:
                        agg_dict[col] = 'first'
                        
                combined_df = combined_df.groupby(group_cols).agg(agg_dict).reset_index()
        
        # החלת מיון
        if 'sort_by' in query and query['sort_by'] and 'field' in query['sort_by']:
            sort_field = query['sort_by']['field']
            if sort_field in combined_df.columns:
                ascending = query['sort_by'].get('direction', 'asc') != 'desc'
                combined_df = combined_df.sort_values(sort_field, ascending=ascending)
        
        return combined_df
    
    def _extract_table_data(self, table_id: str, table_info: Dict[str, Any]) -> pd.DataFrame:
        """חילוץ נתונים מטבלה לתוך DataFrame סטנדרטי."""
        # המימוש תלוי במבנה הטבלה הספציפי
        # עבור טבלאות פיננסיות, נחלץ מדדים ויחסים מרכזיים
        
        df_data = []
        
        try:
            analysis = table_info.get('analysis', {})
            table_type = table_info.get('table_type', 'unknown')
            
            # לוגיקת חילוץ שונה בהתבסס על סוג הטבלה
            if table_type == 'income_statement':
                metrics = ['revenue', 'gross_profit', 'operating_income', 'net_income']
                time_periods = analysis.get('time_periods', [])
                
                for metric in metrics:
                    if metric in analysis:
                        metric_values = analysis[metric]
                        for i, value in enumerate(metric_values):
                            period = time_periods[i] if i < len(time_periods) else f"Period_{i+1}"
                            df_data.append({
                                'metric': metric,
                                'period': period,
                                'value': value,
                                'table_type': table_type,
                                'source_table': table_id
                            })
                            
            elif table_type == 'balance_sheet':
                metrics = ['total_assets', 'total_liabilities', 'equity', 'cash', 'debt']
                time_periods = analysis.get('time_periods', [])
                
                for metric in metrics:
                    if metric in analysis:
                        metric_values = analysis[metric]
                        for i, value in enumerate(metric_values):
                            period = time_periods[i] if i < len(time_periods) else f"Period_{i+1}"
                            df_data.append({
                                'metric': metric,
                                'period': period,
                                'value': value,
                                'table_type': table_type,
                                'source_table': table_id
                            })
                            
            elif table_type == 'ratios':
                for ratio_name, values in analysis.items():
                    if isinstance(values, list):
                        time_periods = analysis.get('time_periods', [])
                        for i, value in enumerate(values):
                            period = time_periods[i] if i < len(time_periods) else f"Period_{i+1}"
                            df_data.append({
                                'metric': ratio_name,
                                'period': period,
                                'value': value,
                                'table_type': table_type,
                                'source_table': table_id
                            })
            
            # עבור סוגי טבלאות לא ידועים, ננסה לחלץ כל מידע מספרי
            else:
                # קבלת סטטיסטיקות אם זמינות
                if 'statistics' in analysis:
                    for col_name, stats in analysis['statistics'].items():
                        for stat_name, value in stats.items():
                            df_data.append({
                                'column': col_name,
                                'statistic': stat_name,
                                'value': value,
                                'table_type': table_type,
                                'source_table': table_id
                            })
            
            return pd.DataFrame(df_data)
            
        except Exception as e:
            self.logger.error(f"שגיאה בחילוץ נתוני טבלה מ-{table_id}: {str(e)}")
            return pd.DataFrame()
        
    def _apply_filters(self, df: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
        """החלת מסננים על DataFrame."""
        filtered_df = df.copy()
        
        for filter_spec in filters:
            if 'field' in filter_spec and filter_spec['field'] in filtered_df.columns:
                field = filter_spec['field']
                operator = filter_spec.get('operator', '=')
                value = filter_spec.get('value')
                
                try:
                    if operator == '=' or operator == '==':
                        filtered_df = filtered_df[filtered_df[field] == value]
                    elif operator == '!=':
                        filtered_df = filtered_df[filtered_df[field] != value]
                    elif operator == '>':
                        filtered_df = filtered_df[filtered_df[field] > value]
                    elif operator == '>=':
                        filtered_df = filtered_df[filtered_df[field] >= value]
                    elif operator == '<':
                        filtered_df = filtered_df[filtered_df[field] < value]
                    elif operator == '<=':
                        filtered_df = filtered_df[filtered_df[field] <= value]
                    elif operator == 'contains':
                        filtered_df = filtered_df[filtered_df[field].astype(str).str.contains(str(value), na=False)]
                except Exception as e:
                    self.logger.warning(f"שגיאה בהחלת מסנן {filter_spec}: {str(e)}")
        
        return filtered_df
