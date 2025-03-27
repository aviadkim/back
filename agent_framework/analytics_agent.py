# agent_framework/analytics_agent.py
from typing import Dict, Any, Optional
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .memory_agent import MemoryAgent


class AnalyticsAgent:
    """סוכן לניתוח מתקדם של נתונים פיננסיים."""

    def __init__(self, memory_agent: Optional[MemoryAgent] = None):
        self.logger = logging.getLogger(__name__)
        self.memory_agent = memory_agent or MemoryAgent()

    def analyze_portfolio_trends(
        self, user_id: str, time_period: int = 180
    ) -> Dict[str, Any]:
        """ניתוח מגמות בתיק השקעות לאורך זמן.

        Args:
            user_id: מזהה המשתמש
            time_period: תקופת הזמן בימים לניתוח (ברירת מחדל: 180 יום)

        Returns:
            מילון עם תוצאות הניתוח
        """
        try:
            # שליפת מסמכים רלוונטיים מתקופת הזמן המבוקשת
            since_date = datetime.now() - timedelta(days=time_period)

            # במערכת אמיתית, נשלוף את המסמכים ישירות עם שאילתת מסד נתונים
            docs = self.memory_agent.get_user_documents(user_id)
            docs = [doc for doc in docs if doc.upload_date >= since_date]

            if not docs:
                return {"message": "No documents found in the specified time period"}

            # איסוף נתונים פיננסיים
            portfolio_data = []
            for doc in docs:
                if doc.financial_data:
                    # שליפת התאריך מהמסמך
                    doc_date = doc.upload_date

                    # איסוף נתוני תיק ההשקעות
                    for table_id, table_info in doc.financial_data.items():
                        if isinstance(table_info, dict) and "dataframe" in table_info:
                            for row in table_info["dataframe"]:
                                row_data = dict(row)
                                row_data["date"] = doc_date
                                portfolio_data.append(row_data)

            if not portfolio_data:
                return {"message": "No financial data found in the documents"}

            # יצירת DataFrame לניתוח
            df = pd.DataFrame(portfolio_data)

            # חישוב מגמות ותובנות
            analysis = {
                "time_period": time_period,
                "document_count": len(docs),
                "date_range": {
                    "start": min(doc.upload_date for doc in docs),
                    "end": max(doc.upload_date for doc in docs),
                },
                "trends": {},
                "insights": [],
            }

            # דוגמה לניתוח - אם יש נתוני תשואה
            if "yield_percent" in df.columns:
                analysis["trends"]["yield"] = {
                    "mean": df["yield_percent"].mean(),
                    "trend": self._calculate_trend(df, "date", "yield_percent"),
                }

                # תובנות על תשואה
                if analysis["trends"]["yield"]["trend"] > 0.1:
                    analysis["insights"].append(
                        "תשואת התיק במגמת עלייה משמעותית בתקופה האחרונה"
                    )
                elif analysis["trends"]["yield"]["trend"] < -0.1:
                    analysis["insights"].append(
                        "תשואת התיק במגמת ירידה משמעותית בתקופה האחרונה"
                    )

            # ניתוח הרכב התיק
            if "security_type" in df.columns and "portfolio_weight" in df.columns:
                latest_doc = max(docs, key=lambda d: d.upload_date)
                latest_data = [
                    row
                    for table in latest_doc.financial_data.values()
                    for row in table.get("dataframe", [])
                ]

                if latest_data:
                    latest_df = pd.DataFrame(latest_data)
                    if (
                        "security_type" in latest_df.columns
                        and "portfolio_weight" in latest_df.columns
                    ):
                        composition = latest_df.groupby("security_type")[
                            "portfolio_weight"
                        ].sum()
                        analysis["portfolio_composition"] = composition.to_dict()

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing portfolio trends: {str(e)}")
            return {"error": str(e)}

    def detect_outliers(
        self,
        user_id: str,
        metric: str = "yield_percent",
        z_score_threshold: float = 2.0,
    ) -> Dict[str, Any]:
        """זיהוי חריגות בנתונים פיננסיים.

        Args:
            user_id: מזהה המשתמש
            metric: המדד לבדיקת חריגות
            z_score_threshold: סף ה-Z-score להגדרת חריגות

        Returns:
            מילון עם תוצאות הניתוח
        """
        try:
            # שליפת מסמכים
            docs = self.memory_agent.get_user_documents(user_id)

            if not docs:
                return {"message": "No documents found"}

            # איסוף נתונים פיננסיים
            financial_data = []
            for doc in docs:
                if doc.financial_data:
                    for table_id, table_info in doc.financial_data.items():
                        if isinstance(table_info, dict) and "dataframe" in table_info:
                            for row in table_info["dataframe"]:
                                if metric in row:
                                    financial_data.append(
                                        {
                                            "document_id": doc.id,
                                            "filename": doc.filename,
                                            "date": doc.upload_date,
                                            "value": row[metric],
                                            "security_name": row.get(
                                                "security_name", "Unknown"
                                            ),
                                            "security_type": row.get(
                                                "security_type", "Unknown"
                                            ),
                                        }
                                    )

            if not financial_data:
                return {"message": f"No data found for metric: {metric}"}

            # יצירת DataFrame לניתוח
            df = pd.DataFrame(financial_data)

            # חישוב Z-scores
            mean = df["value"].mean()
            std = df["value"].std() or 1  # במקרה שסטיית התקן היא 0
            df["z_score"] = (df["value"] - mean) / std

            # זיהוי חריגות
            outliers = df[abs(df["z_score"]) > z_score_threshold]

            result = {
                "metric": metric,
                "z_score_threshold": z_score_threshold,
                "mean": mean,
                "std": std,
                "total_items": len(df),
                "outliers_count": len(outliers),
                "outliers_percentage": (
                    (len(outliers) / len(df)) * 100 if len(df) > 0 else 0
                ),
                "outliers": [],
            }

            # מידע על החריגות
            for _, row in outliers.iterrows():
                result["outliers"].append(
                    {
                        "document_id": row["document_id"],
                        "document_name": row["filename"],
                        "date": row["date"],
                        "security_name": row["security_name"],
                        "security_type": row["security_type"],
                        "value": row["value"],
                        "z_score": row["z_score"],
                    }
                )

            return result

        except Exception as e:
            self.logger.error(f"Error detecting outliers: {str(e)}")
            return {"error": str(e)}

    def generate_insights(self, document_id: str) -> Dict[str, Any]:
        """הפקת תובנות אוטומטיות ממסמך פיננסי.

        Args:
            document_id: מזהה המסמך

        Returns:
            מילון עם תובנות מהמסמך
        """
        try:
            document = self.memory_agent.retrieve_document(document_id)

            if not document:
                return {"error": "Document not found"}

            if not document.financial_data:
                return {"message": "No financial data found in the document"}

            insights = {
                "document_id": document_id,
                "document_name": document.filename,
                "date": document.upload_date,
                "insights": [],
                "portfolio_summary": {},
                "top_performers": [],
                "bottom_performers": [],
            }

            # עיבוד הנתונים הפיננסיים
            financial_data = []
            for table_id, table_info in document.financial_data.items():
                if isinstance(table_info, dict) and "dataframe" in table_info:
                    financial_data.extend(table_info["dataframe"])

            if not financial_data:
                return {"message": "No financial data records found in the document"}

            # יצירת DataFrame לניתוח
            df = pd.DataFrame(financial_data)

            # סיכום תיק ההשקעות
            if "security_type" in df.columns and "portfolio_weight" in df.columns:
                composition = df.groupby("security_type")["portfolio_weight"].sum()
                insights["portfolio_summary"]["composition"] = composition.to_dict()

                # תובנה על הרכב התיק
                max_type = composition.idxmax()
                max_weight = composition.max()
                insights["insights"].append(
                    f"התיק מוטה בעיקר לכיוון {max_type} ({max_weight:.1f}%)"
                )

            # ניתוח ביצועים
            if "performance" in df.columns and "security_name" in df.columns:
                # מיון לפי ביצועים
                sorted_df = df.sort_values("performance", ascending=False)

                # חמשת המובילים
                top_5 = sorted_df.head(5)
                for _, row in top_5.iterrows():
                    insights["top_performers"].append(
                        {
                            "name": row["security_name"],
                            "type": row.get("security_type", "Unknown"),
                            "performance": row["performance"],
                            "weight": row.get("portfolio_weight", 0),
                        }
                    )

                # חמשת המפגרים
                bottom_5 = sorted_df.tail(5)
                for _, row in bottom_5.iterrows():
                    insights["bottom_performers"].append(
                        {
                            "name": row["security_name"],
                            "type": row.get("security_type", "Unknown"),
                            "performance": row["performance"],
                            "weight": row.get("portfolio_weight", 0),
                        }
                    )

                # תובנות על ביצועים
                if len(top_5) > 0 and len(bottom_5) > 0:
                    top_performer = top_5.iloc[0]
                    bottom_performer = bottom_5.iloc[0]

                    insights["insights"].append(
                        f"הנייר המוביל בביצועים: {top_performer['security_name']} "
                        f"({top_performer['performance']:.1f}%)"
                    )

                    insights["insights"].append(
                        f"הנייר המפגר בביצועים: {bottom_performer['security_name']} "
                        f"({bottom_performer['performance']:.1f}%)"
                    )

            # תובנות על תשואה
            if "yield_percent" in df.columns:
                avg_yield = df["yield_percent"].mean()
                insights["portfolio_summary"]["average_yield"] = avg_yield

                if avg_yield > 5:
                    insights["insights"].append(
                        f"תשואת התיק גבוהה יחסית ({avg_yield:.1f}%)"
                    )
                elif avg_yield < 2:
                    insights["insights"].append(
                        f"תשואת התיק נמוכה יחסית ({avg_yield:.1f}%)"
                    )

            return insights

        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return {"error": str(e)}

    def _calculate_trend(
        self, df: pd.DataFrame, date_col: str, value_col: str
    ) -> float:
        """חישוב מגמה באמצעות רגרסיה לינארית פשוטה."""
        try:
            # המרת תאריכים למספרים
            df = df.copy()
            if isinstance(df[date_col].iloc[0], (datetime, pd.Timestamp)):
                df["date_num"] = (df[date_col] - df[date_col].min()).dt.days
            else:
                df["date_num"] = list(range(len(df)))

            # חישוב שיפוע (מקדם הרגרסיה)
            if len(df) < 2:
                return 0

            x = df["date_num"].values
            y = df[value_col].values

            # בדיקה שיש מספיק ערכים תקינים
            valid_indices = ~np.isnan(y)
            if sum(valid_indices) < 2:
                return 0

            x = x[valid_indices]
            y = y[valid_indices]

            # חישוב מקדם הרגרסיה
            slope = np.polyfit(x, y, 1)[0]

            # נרמול השיפוע לפי טווח הערכים
            y_range = np.max(y) - np.min(y) if len(y) > 1 else 1
            x_range = np.max(x) - np.min(x) if len(x) > 1 else 1

            if y_range == 0 or x_range == 0:
                return 0

            # נרמול השיפוע כך שהוא יהיה בערך בין -1 ל-1
            normalized_slope = slope * x_range / y_range

            return normalized_slope

        except Exception as e:
            self.logger.error(f"Error calculating trend: {str(e)}")
            return 0
