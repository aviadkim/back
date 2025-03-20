#!/usr/bin/env python3
# scripts/analyze_all_documents.py
import os
import sys
import argparse
import json
import pandas as pd
import sqlite3
from pathlib import Path
from tabulate import tabulate
import matplotlib.pyplot as plt
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='ניתוח כל המסמכים במערכת')
    parser.add_argument('--db-path', default='./data/financial_docs.sqlite', help='נתיב למסד הנתונים')
    parser.add_argument('--output', default='./analysis_report.xlsx', help='נתיב לשמירת דוח ניתוח')
    parser.add_argument('--storage-path', default='./storage', help='נתיב לתיקיית אחסון')
    parser.add_argument('--model-path', default='./models', help='נתיב לתיקיית מודלים')
    args = parser.parse_args()
    
    # התחברות למסד הנתונים
    try:
        conn = sqlite3.connect(args.db_path)
        print(f"מתחבר למסד נתונים: {args.db_path}")
    except Exception as e:
        print(f"שגיאה בהתחברות למסד הנתונים: {str(e)}")
        sys.exit(1)
    
    # שליפת נתוני מסמכים
    try:
        documents_df = pd.read_sql("SELECT * FROM Documents", conn)
        tables_df = pd.read_sql("SELECT * FROM Tables", conn)
        items_df = pd.read_sql("SELECT * FROM FinancialItems", conn)
        
        print(f"נמצאו {len(documents_df)} מסמכים, {len(tables_df)} טבלאות, {len(items_df)} פריטים פיננסיים")
    except Exception as e:
        print(f"שגיאה בשליפת נתונים: {str(e)}")
        sys.exit(1)
    
    # יצירת דוח ניתוח
    report = {}
    
    # סטטיסטיקות כלליות
    report['general_stats'] = {
        'total_documents': len(documents_df),
        'completed_documents': len(documents_df[documents_df['processingStatus'] == 'completed']),
        'failed_documents': len(documents_df[documents_df['processingStatus'] == 'failed']),
        'total_tables': len(tables_df),
        'total_financial_items': len(items_df),
        'avg_tables_per_document': len(tables_df) / len(documents_df) if len(documents_df) > 0 else 0,
        'avg_items_per_document': len(items_df) / len(documents_df) if len(documents_df) > 0 else 0,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # סטטיסטיקות לפי סוג מסמך
    doc_types = documents_df['documentType'].fillna('Unknown').value_counts().to_dict()
    report['document_types'] = doc_types
    
    # סטטיסטיקות לפי סוג פריט פיננסי
    item_types = items_df['itemType'].value_counts().to_dict()
    report['item_types'] = item_types
    
    # חילוץ מספרי ISIN
    isin_items = items_df[items_df['itemType'] == 'ISIN']
    
    # סטטיסטיקות לפי מספרי ISIN
    if not isin_items.empty:
        isin_counts = isin_items['itemValue'].value_counts().to_dict()
        report['isin_counts'] = isin_counts
    
    # הדפסת דוח בסיסי
    print("\n==== דוח ניתוח מסמכים ====")
    print(f"סה״כ מסמכים: {report['general_stats']['total_documents']}")
    print(f"מסמכים שעובדו בהצלחה: {report['general_stats']['completed_documents']}")
    print(f"מסמכים שנכשלו בעיבוד: {report['general_stats']['failed_documents']}")
    print(f"סה״כ טבלאות: {report['general_stats']['total_tables']}")
    print(f"סה״כ פריטים פיננסיים: {report['general_stats']['total_financial_items']}")
    
    # הדפסת התפלגות סוגי מסמכים
    print("\nסוגי מסמכים:")
    doc_types_data = sorted(doc_types.items(), key=lambda x: x[1], reverse=True)
    print(tabulate(doc_types_data, headers=['סוג מסמך', 'כמות']))
    
    # הדפסת התפלגות סוגי פריטים
    print("\nסוגי פריטים פיננסיים:")
    item_types_data = sorted(item_types.items(), key=lambda x: x[1], reverse=True)
    print(tabulate(item_types_data, headers=['סוג פריט', 'כמות']))
    
    # שמירת הדוח לקובץ Excel
    try:
        with pd.ExcelWriter(args.output) as writer:
            # גליון סטטיסטיקות כלליות
            general_stats_df = pd.DataFrame([report['general_stats']])
            general_stats_df.to_excel(writer, sheet_name='General Stats', index=False)
            
            # גליון מסמכים
            documents_df.to_excel(writer, sheet_name='Documents', index=False)
            
            # גליון טבלאות
            tables_df.to_excel(writer, sheet_name='Tables', index=False)
            
            # גליון פריטים פיננסיים
            items_df.to_excel(writer, sheet_name='Financial Items', index=False)
            
            # גליון התפלגות סוגי מסמכים
            doc_types_df = pd.DataFrame(doc_types_data, columns=['Document Type', 'Count'])
            doc_types_df.to_excel(writer, sheet_name='Document Types', index=False)
            
            # גליון התפלגות סוגי פריטים
            item_types_df = pd.DataFrame(item_types_data, columns=['Item Type', 'Count'])
            item_types_df.to_excel(writer, sheet_name='Item Types', index=False)
            
            # גליון מספרי ISIN
            if 'isin_counts' in report:
                isin_data = sorted(report['isin_counts'].items(), key=lambda x: x[1], reverse=True)
                isin_df = pd.DataFrame(isin_data, columns=['ISIN', 'Count'])
                isin_df.to_excel(writer, sheet_name='ISIN Numbers', index=False)
        
        print(f"\nדוח ניתוח נשמר בהצלחה: {args.output}")
    except Exception as e:
        print(f"שגיאה בשמירת דוח ניתוח: {str(e)}")
    
    # ניתוק ממסד הנתונים
    conn.close()

if __name__ == "__main__":
    main() 