#!/usr/bin/env python3
"""
סקריפט להשוואת ביצועים בין הגרסה הקודמת לגרסה המשופרת
מודד מדדי דיוק, יעילות וזמן ריצה על מדגם קבצים
"""

import os
import sys
import time
import json
import argparse
import cv2
import numpy as np
from pathlib import Path
import subprocess
import matplotlib.pyplot as plt
from tabulate import tabulate
import pandas as pd

# ייבוא הסקריפטים הישנים והחדשים
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.process_document import process_document  # הגרסה הישנה
from scripts.improved_table_extraction import extract_tables_hybrid
from scripts.improved_securities_extraction import extract_securities_hybrid

# קבצי מבחן מתויגים ידנית - רשימה לדוגמה של קבצים שיש להם תיוג ידני
BENCHMARK_FILES = {
    "test_documents/2. Messos 28.02.2025.pdf": {
        "expected_tables": 3,      # מספר הטבלאות שאמורות להיות מזוהות
        "expected_securities": 4,  # מספר ניירות הערך שאמורים להיות מזוהים
        "ground_truth_securities": [
            "IL0011726384",        # דוגמאות למספרי ISIN שאמורים להיות מזוהים
            "US5949181045"
        ]
    }
    # ניתן להוסיף קבצי מבחן נוספים כאן
}

def evaluate_table_extraction(img_path, ground_truth=None):
    """
    הערכת דיוק זיהוי טבלאות
    משווה בין הגרסה הישנה לגרסה החדשה
    
    Args:
        img_path: נתיב לתמונה
        ground_truth: מספר הטבלאות האמיתי (אם ידוע)
        
    Returns:
        תוצאות ההערכה כמילון
    """
    results = {
        "old_version": {"tables": 0, "time": 0},
        "new_version": {"tables": 0, "time": 0}
    }
    
    # טעינת התמונה
    img = cv2.imread(img_path)
    if img is None:
        print(f"שגיאה: לא ניתן לטעון את התמונה מהנתיב {img_path}")
        return results
    
    # בדיקת הגרסה הישנה
    start_time = time.time()
    try:
        old_result = process_document(img_path, extract_tables=True, extract_securities=False)
        old_tables = len(old_result.get("tables", []))
    except Exception as e:
        print(f"שגיאה בהרצת הגרסה הישנה: {str(e)}")
        old_tables = 0
    old_time = time.time() - start_time
    
    # בדיקת הגרסה החדשה
    start_time = time.time()
    try:
        new_tables = extract_tables_hybrid(img)
        new_tables_count = len(new_tables)
    except Exception as e:
        print(f"שגיאה בהרצת הגרסה החדשה: {str(e)}")
        new_tables_count = 0
    new_time = time.time() - start_time
    
    # תוצאות
    results["old_version"]["tables"] = old_tables
    results["old_version"]["time"] = old_time
    results["new_version"]["tables"] = new_tables_count
    results["new_version"]["time"] = new_time
    
    # חישוב דיוק אם יש אמת מידה (ground truth)
    if ground_truth is not None:
        results["old_version"]["accuracy"] = old_tables / ground_truth if ground_truth > 0 else 0
        results["new_version"]["accuracy"] = new_tables_count / ground_truth if ground_truth > 0 else 0
    
    return results

def evaluate_securities_extraction(img_path, ground_truth=None, ground_truth_securities=None):
    """
    הערכת דיוק זיהוי ניירות ערך
    משווה בין הגרסה הישנה לגרסה החדשה
    
    Args:
        img_path: נתיב לתמונה
        ground_truth: מספר ניירות הערך האמיתי (אם ידוע)
        ground_truth_securities: רשימת מספרי ISIN אמיתיים (אם ידוע)
        
    Returns:
        תוצאות ההערכה כמילון
    """
    results = {
        "old_version": {"securities": 0, "time": 0, "isin_found": []},
        "new_version": {"securities": 0, "time": 0, "isin_found": []}
    }
    
    # טעינת התמונה
    img = cv2.imread(img_path)
    if img is None:
        print(f"שגיאה: לא ניתן לטעון את התמונה מהנתיב {img_path}")
        return results
    
    # בדיקת הגרסה הישנה
    start_time = time.time()
    try:
        old_result = process_document(img_path, extract_tables=False, extract_securities=True)
        old_securities = old_result.get("securities", [])
        old_securities_count = len(old_securities)
        old_isins = [s.get("isin") for s in old_securities if s.get("isin")]
    except Exception as e:
        print(f"שגיאה בהרצת הגרסה הישנה: {str(e)}")
        old_securities_count = 0
        old_isins = []
    old_time = time.time() - start_time
    
    # בדיקת הגרסה החדשה
    start_time = time.time()
    try:
        new_securities = extract_securities_hybrid(img=img)
        new_securities_count = len(new_securities)
        new_isins = [s.get("isin") for s in new_securities if s.get("isin")]
    except Exception as e:
        print(f"שגיאה בהרצת הגרסה החדשה: {str(e)}")
        new_securities_count = 0
        new_isins = []
    new_time = time.time() - start_time
    
    # תוצאות
    results["old_version"]["securities"] = old_securities_count
    results["old_version"]["time"] = old_time
    results["old_version"]["isin_found"] = old_isins
    
    results["new_version"]["securities"] = new_securities_count
    results["new_version"]["time"] = new_time
    results["new_version"]["isin_found"] = new_isins
    
    # חישוב דיוק אם יש אמת מידה (ground truth)
    if ground_truth is not None:
        results["old_version"]["count_accuracy"] = old_securities_count / ground_truth if ground_truth > 0 else 0
        results["new_version"]["count_accuracy"] = new_securities_count / ground_truth if ground_truth > 0 else 0
    
    # חישוב דיוק זיהוי ISIN
    if ground_truth_securities is not None and len(ground_truth_securities) > 0:
        old_precision = sum(1 for isin in old_isins if isin in ground_truth_securities) / len(old_isins) if old_isins else 0
        old_recall = sum(1 for isin in ground_truth_securities if isin in old_isins) / len(ground_truth_securities)
        old_f1 = 2 * (old_precision * old_recall) / (old_precision + old_recall) if (old_precision + old_recall) > 0 else 0
        
        new_precision = sum(1 for isin in new_isins if isin in ground_truth_securities) / len(new_isins) if new_isins else 0
        new_recall = sum(1 for isin in ground_truth_securities if isin in new_isins) / len(ground_truth_securities)
        new_f1 = 2 * (new_precision * new_recall) / (new_precision + new_recall) if (new_precision + new_recall) > 0 else 0
        
        results["old_version"]["precision"] = old_precision
        results["old_version"]["recall"] = old_recall
        results["old_version"]["f1"] = old_f1
        
        results["new_version"]["precision"] = new_precision
        results["new_version"]["recall"] = new_recall
        results["new_version"]["f1"] = new_f1
    
    return results

def run_benchmark():
    """
    הרצת הבנצ'מרק על כל קבצי המבחן
    והצגת התוצאות
    """
    results = {
        "tables": {},
        "securities": {}
    }
    
    print("\n" + "="*60)
    print("בודק ביצועים ומשווה בין הגרסאות")
    print("="*60)
    
    # בדיקה אם קיימים קבצי מבחן
    if not BENCHMARK_FILES:
        print("שגיאה: לא הוגדרו קבצי מבחן. יש להגדיר קבצי מבחן ב-BENCHMARK_FILES.")
        sys.exit(1)
    
    # עיבוד כל קובץ מבחן
    for file_path, ground_truth in BENCHMARK_FILES.items():
        file_name = os.path.basename(file_path)
        print(f"\nבודק קובץ: {file_name}")
        
        # וידוא שהקובץ קיים
        if not os.path.exists(file_path):
            print(f"שגיאה: הקובץ {file_path} לא נמצא.")
            continue
        
        # המרה ל-PNG אם צריך
        if file_path.lower().endswith('.pdf'):
            # המרה לתמונה באמצעות הסקריפט הקיים
            print("ממיר PDF לתמונה...")
            try:
                result = subprocess.run(
                    [sys.executable, "scripts/analyze_bank_statement.py", file_path, "--output_dir", "benchmark_temp", "--no-analyze"],
                    capture_output=True, text=True, check=True
                )
                # מציאת קובץ התמונה שנוצר
                images = list(Path("benchmark_temp").glob(f"{os.path.splitext(file_name)[0]}*.png"))
                if not images:
                    print("שגיאה: לא נוצרו תמונות מה-PDF.")
                    continue
                img_path = str(images[0])
            except Exception as e:
                print(f"שגיאה בהמרת ה-PDF: {str(e)}")
                continue
        else:
            img_path = file_path
        
        # בדיקת זיהוי טבלאות
        print("בודק זיהוי טבלאות...")
        tables_results = evaluate_table_extraction(
            img_path, 
            ground_truth=ground_truth.get("expected_tables")
        )
        results["tables"][file_name] = tables_results
        
        # בדיקת זיהוי ניירות ערך
        print("בודק זיהוי ניירות ערך...")
        securities_results = evaluate_securities_extraction(
            img_path, 
            ground_truth=ground_truth.get("expected_securities"),
            ground_truth_securities=ground_truth.get("ground_truth_securities")
        )
        results["securities"][file_name] = securities_results
    
    # ניתוח התוצאות המצטברות
    print("\n" + "="*60)
    print("סיכום תוצאות")
    print("="*60)
    
    # טבלאות סיכום
    table_data = []
    for file_name, data in results["tables"].items():
        old_version = data["old_version"]
        new_version = data["new_version"]
        
        speed_improvement = (old_version["time"] / new_version["time"]) if new_version["time"] > 0 else float('inf')
        
        row = [
            file_name,
            old_version["tables"],
            new_version["tables"],
            f"{old_version['time']:.2f}s",
            f"{new_version['time']:.2f}s",
            f"{speed_improvement:.2f}x"
        ]
        
        if "accuracy" in old_version and "accuracy" in new_version:
            row.extend([
                f"{old_version['accuracy']*100:.2f}%",
                f"{new_version['accuracy']*100:.2f}%"
            ])
        
        table_data.append(row)
    
    print("\nסיכום זיהוי טבלאות:")
    headers = ["קובץ", "טבלאות (ישן)", "טבלאות (חדש)", "זמן (ישן)", "זמן (חדש)", "שיפור מהירות"]
    if "accuracy" in next(iter(results["tables"].values()))["old_version"]:
        headers.extend(["דיוק (ישן)", "דיוק (חדש)"])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # סיכום זיהוי ניירות ערך
    securities_data = []
    for file_name, data in results["securities"].items():
        old_version = data["old_version"]
        new_version = data["new_version"]
        
        speed_improvement = (old_version["time"] / new_version["time"]) if new_version["time"] > 0 else float('inf')
        
        row = [
            file_name,
            old_version["securities"],
            new_version["securities"],
            f"{old_version['time']:.2f}s",
            f"{new_version['time']:.2f}s",
            f"{speed_improvement:.2f}x"
        ]
        
        if "f1" in old_version and "f1" in new_version:
            row.extend([
                f"{old_version['f1']*100:.2f}%",
                f"{new_version['f1']*100:.2f}%"
            ])
        
        securities_data.append(row)
    
    print("\nסיכום זיהוי ניירות ערך:")
    headers = ["קובץ", "ני\"ע (ישן)", "ני\"ע (חדש)", "זמן (ישן)", "זמן (חדש)", "שיפור מהירות"]
    if "f1" in next(iter(results["securities"].values()))["old_version"]:
        headers.extend(["F1 (ישן)", "F1 (חדש)"])
    
    print(tabulate(securities_data, headers=headers, tablefmt="grid"))
    
    # יצירת הויזואליזציה
    create_benchmark_charts(results, "benchmark_results.png")
    print(f"\nגרף השוואת ביצועים נשמר בקובץ: benchmark_results.png")
    
    # מסקנות
    print("\n" + "="*60)
    print("מסקנות")
    print("="*60)
    
    # חישוב ממוצעים
    avg_table_speedup = sum(
        data["old_version"]["time"] / data["new_version"]["time"] 
        for data in results["tables"].values() 
        if data["new_version"]["time"] > 0
    ) / len(results["tables"])
    
    avg_securities_speedup = sum(
        data["old_version"]["time"] / data["new_version"]["time"] 
        for data in results["securities"].values() 
        if data["new_version"]["time"] > 0
    ) / len(results["securities"])
    
    print(f"שיפור ממוצע במהירות זיהוי טבלאות: {avg_table_speedup:.2f}x")
    print(f"שיפור ממוצע במהירות זיהוי ניירות ערך: {avg_securities_speedup:.2f}x")
    
    # אם יש מידע על דיוק
    if all("accuracy" in data["old_version"] and "accuracy" in data["new_version"] for data in results["tables"].values()):
        avg_old_accuracy = sum(data["old_version"]["accuracy"] for data in results["tables"].values()) / len(results["tables"])
        avg_new_accuracy = sum(data["new_version"]["accuracy"] for data in results["tables"].values()) / len(results["tables"])
        accuracy_improvement = (avg_new_accuracy - avg_old_accuracy) / avg_old_accuracy if avg_old_accuracy > 0 else float('inf')
        
        print(f"שיפור ממוצע בדיוק זיהוי טבלאות: {accuracy_improvement*100:.2f}%")
    
    # אם יש מידע על דיוק ניירות ערך
    if all("f1" in data["old_version"] and "f1" in data["new_version"] for data in results["securities"].values()):
        avg_old_f1 = sum(data["old_version"]["f1"] for data in results["securities"].values()) / len(results["securities"])
        avg_new_f1 = sum(data["new_version"]["f1"] for data in results["securities"].values()) / len(results["securities"])
        f1_improvement = (avg_new_f1 - avg_old_f1) / avg_old_f1 if avg_old_f1 > 0 else float('inf')
        
        print(f"שיפור ממוצע במדד F1 לזיהוי ניירות ערך: {f1_improvement*100:.2f}%")
    
    return results

def create_benchmark_charts(results, output_path):
    """
    יצירת גרפים להשוואה ויזואלית של תוצאות הבנצ'מרק
    
    Args:
        results: תוצאות הבנצ'מרק
        output_path: נתיב לשמירת הגרפים
    """
    # יצירת גרף משולב
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # הגדרות משותפות
    colors = {
        'old': '#007acc',
        'new': '#00cc66',
    }
    
    # 1. השוואת מספר טבלאות שזוהו
    file_names = list(results["tables"].keys())
    old_tables = [data["old_version"]["tables"] for data in results["tables"].values()]
    new_tables = [data["new_version"]["tables"] for data in results["tables"].values()]
    
    x = range(len(file_names))
    width = 0.35
    
    ax1.bar([i - width/2 for i in x], old_tables, width, label='גרסה ישנה', color=colors['old'])
    ax1.bar([i + width/2 for i in x], new_tables, width, label='גרסה חדשה', color=colors['new'])
    ax1.set_title('מספר טבלאות שזוהו')
    ax1.set_xlabel('קובץ')
    ax1.set_ylabel('מספר טבלאות')
    ax1.set_xticks(x)
    ax1.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in file_names], rotation=45)
    ax1.legend()
    
    # 2. השוואת זמני עיבוד טבלאות
    old_times = [data["old_version"]["time"] for data in results["tables"].values()]
    new_times = [data["new_version"]["time"] for data in results["tables"].values()]
    
    ax2.bar([i - width/2 for i in x], old_times, width, label='גרסה ישנה', color=colors['old'])
    ax2.bar([i + width/2 for i in x], new_times, width, label='גרסה חדשה', color=colors['new'])
    ax2.set_title('זמן עיבוד טבלאות (שניות)')
    ax2.set_xlabel('קובץ')
    ax2.set_ylabel('זמן (שניות)')
    ax2.set_xticks(x)
    ax2.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in file_names], rotation=45)
    ax2.legend()
    
    # 3. השוואת מספר ניירות ערך שזוהו
    file_names = list(results["securities"].keys())
    old_securities = [data["old_version"]["securities"] for data in results["securities"].values()]
    new_securities = [data["new_version"]["securities"] for data in results["securities"].values()]
    
    x = range(len(file_names))
    
    ax3.bar([i - width/2 for i in x], old_securities, width, label='גרסה ישנה', color=colors['old'])
    ax3.bar([i + width/2 for i in x], new_securities, width, label='גרסה חדשה', color=colors['new'])
    ax3.set_title('מספר ניירות ערך שזוהו')
    ax3.set_xlabel('קובץ')
    ax3.set_ylabel('מספר ניירות ערך')
    ax3.set_xticks(x)
    ax3.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in file_names], rotation=45)
    ax3.legend()
    
    # 4. השוואת זמני עיבוד ניירות ערך
    old_times = [data["old_version"]["time"] for data in results["securities"].values()]
    new_times = [data["new_version"]["time"] for data in results["securities"].values()]
    
    ax4.bar([i - width/2 for i in x], old_times, width, label='גרסה ישנה', color=colors['old'])
    ax4.bar([i + width/2 for i in x], new_times, width, label='גרסה חדשה', color=colors['new'])
    ax4.set_title('זמן עיבוד ניירות ערך (שניות)')
    ax4.set_xlabel('קובץ')
    ax4.set_ylabel('זמן (שניות)')
    ax4.set_xticks(x)
    ax4.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in file_names], rotation=45)
    ax4.legend()
    
    # כותרת ראשית
    fig.suptitle('השוואת ביצועים: גרסה ישנה מול גרסה חדשה', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # שמירת הגרף
    plt.savefig(output_path)

def main():
    parser = argparse.ArgumentParser(description='השוואת ביצועים בין הגרסה הקודמת לגרסה המשופרת')
    parser.add_argument('--visualize', '-v', action='store_true', help='הצג את הגרפים בסיום הבדיקה')
    args = parser.parse_args()
    
    # ניקוי תיקיית temp אם קיימת
    if os.path.exists("benchmark_temp"):
        import shutil
        shutil.rmtree("benchmark_temp")
    os.makedirs("benchmark_temp", exist_ok=True)
    
    # הרצת הבנצ'מרק
    results = run_benchmark()
    
    # הצגת הגרף אם צוין
    if args.visualize and os.path.exists("benchmark_results.png"):
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath('benchmark_results.png')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 