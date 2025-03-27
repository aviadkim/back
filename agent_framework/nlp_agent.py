from typing import Dict, Any  # Removed unused List
import re
import logging


class NaturalLanguageQueryAgent:
    """סוכן שמעבד שאילתות בשפה טבעית וממיר אותן לשאילתות מובנות."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # הגדרת תבניות עבור סוגי שאילתות שונות
        self.patterns = {
            "show_all": r"(?:הצג|הראה|מצא|show)\s+(?:את כל|כל|כל|me|all)\s+(.+)",
            "filter_by": r"(?:עם|בעלי|where|having|with)\s+(.+?)\s+(גדול מ|קטן מ|שווה ל|מכיל|greater than|less than|equal to|contains|above|below|=|>|<)\s+(.+?)\s+(?:ו|,|and|$)",
            "sort_by": r"(?:מיין|סדר|sort|order)\s+(?:לפי|by)\s+(.+?)\s+(בסדר עולה|בסדר יורד|עולה|יורד|ascending|descending|asc|desc)",
            "group_by": r"(?:קבץ|group)\s+(?:לפי|by)\s+(.+)",
            "isin": r"(?:isin|ISIN)[:\s]*([A-Z0-9]{12})",
            "date": r"(?:ב|בתאריך|from|before|after|in)\s+(\d{4}(?:-\d{2})?(?:-\d{2})?)",
            "percentage": r"(\d+(?:\.\d+)?)\s*%",
        }

        # הגדרת מיפויים למונחים פיננסיים
        self.financial_terms = {
            # מונחים באנגלית
            "bonds": "security_type",
            "stocks": "security_type",
            "etf": "security_type",
            "funds": "security_type",
            "yield": "yield_percent",
            "maturity": "maturity_date",
            "isin": "isin_number",
            "price": "current_price",
            "value": "total_value",
            "weight": "portfolio_weight",
            "performance": "performance",
            "return": "total_return",
            "profit": "profit",
            "loss": "loss",
            "dividend": "dividend_yield",
            "sector": "sector",
            "currency": "currency",
            "rating": "credit_rating",
            "type": "security_type",
            # מונחים בעברית
            "אג״ח": "security_type",
            "אגח": "security_type",
            "מניות": "security_type",
            "קרנות": "security_type",
            "תשואה": "yield_percent",
            "פדיון": "maturity_date",
            "מחיר": "current_price",
            "ערך": "total_value",
            "משקל": "portfolio_weight",
            "ביצועים": "performance",
            "תשואה כוללת": "total_return",
            "רווח": "profit",
            "הפסד": "loss",
            "דיבידנד": "dividend_yield",
            "סקטור": "sector",
            "מטבע": "currency",
            "דירוג": "credit_rating",
            "סוג": "security_type",
        }

    def process_query(self, query_text: str) -> Dict[str, Any]:
        """עיבוד שאילתה בשפה טבעית לשאילתה מובנית.

        Args:
            query_text: שאילתה בשפה טבעית מהמשתמש

        Returns:
            מילון המכיל פרמטרים מובנים של השאילתה
        """
        query_text = query_text.lower()
        structured_query = {
            "filters": [],
            "columns": [],
            "sort_by": {},
            "group_by": None,
        }

        try:
            # חילוץ עמודות להצגה
            show_match = re.search(self.patterns["show_all"], query_text)
            if show_match:
                entities = show_match.group(1)
                for term, field in self.financial_terms.items():
                    if term in entities and field not in structured_query["columns"]:
                        structured_query["columns"].append(field)

            # אם לא צוינו עמודות ספציפיות, השתמש בכל העמודות הזמינות
            if not structured_query["columns"]:
                structured_query["columns"] = list(set(self.financial_terms.values()))

            # חילוץ מספרי ISIN
            isin_matches = re.finditer(self.patterns["isin"], query_text, re.IGNORECASE)
            for match in isin_matches:
                isin = match.group(1)
                structured_query["filters"].append(
                    {"field": "isin_number", "operator": "=", "value": isin}
                )

            # חילוץ מסננים
            filter_matches = re.finditer(self.patterns["filter_by"], query_text)
            for match in filter_matches:
                field_text = match.group(1)
                operator_text = match.group(2)
                value_text = match.group(3)

                # מיפוי לשם שדה
                field = None
                for term, field_name in self.financial_terms.items():
                    if term in field_text:
                        field = field_name
                        break

                if field:
                    # מיפוי אופרטור
                    operator_map = {
                        "גדול מ": ">",
                        "greater than": ">",
                        "above": ">",
                        ">": ">",
                        "קטן מ": "<",
                        "less than": "<",
                        "below": "<",
                        "<": "<",
                        "שווה ל": "=",
                        "equal to": "=",
                        "=": "=",
                    }
                    operator = operator_map.get(operator_text, "=")

                    # עיבוד ערך
                    try:
                        # ניסיון להמרה למספר אם אפשר
                        value = float(value_text)
                    except ValueError:
                        # בדיקה אם זה אחוז
                        pct_match = re.search(r"(\d+(?:\.\d+)?)\s*%", value_text)
                        if pct_match:
                            value = float(pct_match.group(1))
                        else:
                            value = value_text

                    structured_query["filters"].append(
                        {"field": field, "operator": operator, "value": value}
                    )

            # חילוץ מסנני תאריכים
            date_matches = re.finditer(self.patterns["date"], query_text)
            for match in date_matches:
                date_value = match.group(1)

                # קביעה אם זה עבור תאריכי פדיון
                if "פדיון" in query_text or "maturity" in query_text:
                    field = "maturity_date"

                    # קביעת אופרטור בהתבסס על מילת היחס
                    prefix = query_text[
                        max(0, match.start() - 10):match.start()   # Removed space before :
                    ].strip()
                    if "before" in prefix or "לפני" in prefix:
                        operator = "<"
                    elif "after" in prefix or "אחרי" in prefix:
                        operator = ">"
                    else:
                        # ברירת מחדל ל-contains עבור שאילתות מסוג "ב-2025"
                        operator = "contains"

                    structured_query["filters"].append(
                        {"field": field, "operator": operator, "value": date_value}
                    )

            # חילוץ מיון
            sort_match = re.search(self.patterns["sort_by"], query_text)
            if sort_match:
                sort_field_text = sort_match.group(1)
                direction = (
                    "desc"
                    if any(
                        term in sort_match.group(2)
                        for term in ["desc", "יורד", "בסדר יורד"]
                    )
                    else "asc"
                )

                # מיפוי לשם שדה
                for term, field_name in self.financial_terms.items():
                    if term in sort_field_text:
                        structured_query["sort_by"] = {
                            "field": field_name,
                            "direction": direction,
                        }
                        break

            # חילוץ קיבוץ
            group_match = re.search(self.patterns["group_by"], query_text)
            if group_match:
                group_field_text = group_match.group(1)

                # מיפוי לשם שדה
                for term, field_name in self.financial_terms.items():
                    if term in group_field_text:
                        structured_query["group_by"] = field_name
                        break

            # טיפול במקרים מיוחדים
            if "bond" in query_text or "אגח" in query_text or "אג״ח" in query_text:
                structured_query["filters"].append(
                    {"field": "security_type", "operator": "=", "value": "bond"}
                )

            if "stock" in query_text or "מניות" in query_text or "מניה" in query_text:
                structured_query["filters"].append(
                    {"field": "security_type", "operator": "=", "value": "stock"}
                )

            self.logger.info(f"עיבוד שאילתה למבנה: {structured_query}")
            return structured_query

        except Exception as e:
            self.logger.error(f"שגיאה בעיבוד שאילתה בשפה טבעית: {str(e)}")
            # החזרת שאילתה בסיסית אם העיבוד נכשל
            return {
                "columns": list(set(self.financial_terms.values())),
                "filters": [],
                "sort_by": {},
                "group_by": None,
            }
