import os
import re
from langchain_huggingface import HuggingFaceHub

# Import the placeholder service for getting structured data
try:
    from features.financial_insights.services import financial_data_service
except ImportError:
    print("Warning: Could not import financial_data_service. Using placeholder.")
    # Define a dummy function if import fails

    def get_financial_data(document_id):
        print(f"Warning: Using dummy get_financial_data for ID: {document_id}")
        # Return structure similar to the mock service
        if document_id == "doc1":
            return {
                "revenue": {"total": "$1,250,000"}, "expenses": {"total": "$875,000"},
                "assets": {"total": "$3,000,000", "current": "$950,000"},
                "liabilities": {"total": "$1,500,000", "current": "$600,000"}
            }
        return None
    financial_data_service = type('obj', (object,), {'get_financial_data': get_financial_data})()


# Helper function to clean and convert currency strings (similar to metrics service)
def _parse_currency(value_str):
    if isinstance(value_str, (int, float)):
        return float(value_str)
    if isinstance(value_str, str):
        cleaned_value = re.sub(r'[$,()]', '', value_str).strip()
        try:
            return float(cleaned_value)
        except ValueError:
            return 0.0  # Default to 0 if parsing fails
    return 0.0


class FinancialAnalyzer:
    """
    Service for analyzing financial data to provide insights and comparisons.
    Uses an LLM for generating qualitative assessments.
    """
    def __init__(self):
        """Initializes the FinancialAnalyzer with a HuggingFaceHub LLM."""
        # Use a model with strong reasoning capabilities as per spec
        self.llm = HuggingFaceHub(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=os.environ.get("HUGGINGFACE_API_KEY"),
            task="text-generation"
        )

    def analyze_health(self, financial_data):
        """
        Analyzes financial health based on provided structured data.

        Args:
            financial_data (dict): Structured financial data (revenue, expenses, assets, liabilities).

        Returns:
            dict: An assessment including calculated ratios and LLM-generated analysis.
        """
        if not financial_data:
            return {"error": "Financial data not provided for health analysis."}

        # Extract key metrics safely
        revenue = financial_data.get('revenue', {})
        expenses = financial_data.get('expenses', {})
        assets = financial_data.get('assets', {})
        liabilities = financial_data.get('liabilities', {})

        # Calculate financial ratios using helper functions
        current_ratio = self._calculate_current_ratio(assets, liabilities)
        profit_margin = self._calculate_profit_margin(revenue, expenses)
        debt_to_equity = self._calculate_debt_to_equity(assets, liabilities)

        # Generate health assessment using LLM
        prompt = f"""
        Analyze the financial health of a company with the following metrics:
        - Current Ratio: {current_ratio if current_ratio is not None else 'N/A'}
        - Profit Margin: {profit_margin if profit_margin is not None else 'N/A'}%
        - Debt to Equity Ratio: {debt_to_equity if debt_to_equity is not None else 'N/A'}

        Additional financial information:
        - Revenue: {revenue.get('total', 'N/A')}
        - Expenses: {expenses.get('total', 'N/A')}
        - Total Assets: {assets.get('total', 'N/A')}
        - Total Liabilities: {liabilities.get('total', 'N/A')}

        Provide a comprehensive assessment of the company's financial health,
        including strengths, weaknesses, and recommendations. Be concise and clear.
        """

        try:
            assessment = self.llm.invoke(prompt)
        except Exception as e:
            print(f"Error during LLM health assessment: {e}")
            assessment = "Error generating LLM assessment."

        return {
            "metrics": {
                "current_ratio": current_ratio,
                "profit_margin": f"{profit_margin}%" if profit_margin is not None else "N/A",
                "debt_to_equity": debt_to_equity
            },
            "assessment": assessment.strip(),
            "health_score": self._calculate_health_score(current_ratio, profit_margin, debt_to_equity)
        }

    def get_comparison_data(self, document, comparison_period):
        """
        Placeholder function to get comparison data (e.g., previous year, industry average).

        Args:
            document (dict): The current document's data (used potentially for context).
            comparison_period (str): The period to compare against ('previous-year', 'industry-average').

        Returns:
            dict: Mock comparison data.
        """
        print(f"Warning: Using mock comparison data for period: {comparison_period}")
        # In a real implementation, you would fetch this from your database based on document context and period
        if comparison_period == "previous-year":
            # Fetch previous year's data for the same entity (mock)
            return {
                "period": "2023",
                "revenue": {"total": "$1,050,000"},
                "expenses": {"total": "$750,000"},
                "net_income": "$300,000",  # Added for comparison prompt
                "assets": {"total": "$2,500,000", "current": "$800,000"},
                "liabilities": {"total": "$1,200,000", "current": "$500,000"}
            }
        elif comparison_period == "industry-average":
            # Fetch industry average data (mock)
            return {
                "period": "Industry Average 2024",
                "revenue": {"total": "$1,150,000"},
                "expenses": {"total": "$820,000"},
                "net_income": "$330,000",  # Added for comparison prompt
                "assets": {"total": "$2,600,000", "current": "$780,000"},
                "liabilities": {"total": "$1,300,000", "current": "$520,000"}
            }

        return {}  # Return empty if period is unknown

    def compare_performance(self, current_financial_data, comparison_data):
        """
        Compares financial performance between two periods using LLM.

        Args:
            current_financial_data (dict): Structured data for the current period.
            comparison_data (dict): Structured data for the comparison period.

        Returns:
            dict: Analysis results including LLM comparison and calculated changes.
        """
        if not current_financial_data or not comparison_data:
            return {"error": "Insufficient data for performance comparison."}

        # Prepare data for the prompt
        current_revenue = current_financial_data.get('revenue', {}).get('total', 'N/A')
        current_expenses = current_financial_data.get('expenses', {}).get('total', 'N/A')
        current_net_income = current_financial_data.get('net_income', 'N/A')  # Assumes net_income is available

        comp_revenue = comparison_data.get('revenue', {}).get('total', 'N/A')
        comp_expenses = comparison_data.get('expenses', {}).get('total', 'N/A')
        comp_net_income = comparison_data.get('net_income', 'N/A')  # Assumes net_income is available

        prompt = f"""
        Compare the financial performance of:

        Current Period:
        - Revenue: {current_revenue}
        - Expenses: {current_expenses}
        - Net Income: {current_net_income}

        Comparison Period ({comparison_data.get('period', 'N/A')}):
        - Revenue: {comp_revenue}
        - Expenses: {comp_expenses}
        - Net Income: {comp_net_income}

        Provide a detailed analysis of the performance comparison,
        highlighting significant changes, potential causes, and future implications.
        Be concise and focus on key differences.
        """

        try:
            analysis = self.llm.invoke(prompt)
        except Exception as e:
            print(f"Error during LLM performance comparison: {e}")
            analysis = "Error generating LLM comparison analysis."

        # Calculate percentage changes
        revenue_change = self._calculate_percentage_change(current_revenue, comp_revenue)
        expenses_change = self._calculate_percentage_change(current_expenses, comp_expenses)
        net_income_change = self._calculate_percentage_change(current_net_income, comp_net_income)

        return {
            "analysis": analysis.strip(),
            "changes": {
                "revenue": revenue_change,
                "expenses": expenses_change,
                "net_income": net_income_change
            }
        }

    # --- Helper methods for ratio calculations ---

    def _calculate_current_ratio(self, assets, liabilities):
        try:
            current_assets = _parse_currency(assets.get('current', '0'))
            current_liabilities = _parse_currency(liabilities.get('current', '0'))
            if current_liabilities == 0:
                return None
            return round(current_assets / current_liabilities, 2)
        except Exception:
            return None

    def _calculate_profit_margin(self, revenue, expenses):
        try:
            total_revenue = _parse_currency(revenue.get('total', '0'))
            total_expenses = _parse_currency(expenses.get('total', '0'))
            if total_revenue == 0:
                return None  # Avoid division by zero
            net_income = total_revenue - total_expenses
            return round((net_income / total_revenue) * 100, 2)
        except Exception:
            return None

    def _calculate_debt_to_equity(self, assets, liabilities):
        try:
            total_assets = _parse_currency(assets.get('total', '0'))
            total_liabilities = _parse_currency(liabilities.get('total', '0'))
            equity = total_assets - total_liabilities
            if equity == 0:
                return None
            return round(total_liabilities / equity, 2)
        except Exception:
            return None

    def _calculate_health_score(self, current_ratio, profit_margin, debt_to_equity):
        # A simplified scoring algorithm - needs refinement for real-world use
        score = 0
        count = 0

        # Score based on Current Ratio (Ideal typically 1.5-3)
        if current_ratio is not None:
            if 1.5 <= current_ratio <= 3:
                score += 33
            elif current_ratio > 1:
                score += 15
            count += 1

        # Score based on Profit Margin (Higher is better)
        if profit_margin is not None:
            score += max(0, min(34, profit_margin * 2))  # Cap at 34 points
            count += 1

        # Score based on Debt to Equity (Lower is generally better, depends on industry)
        if debt_to_equity is not None:
            score += max(0, min(33, 33 - (debt_to_equity * 15)))  # Cap at 33 points
            count += 1

        if count == 0:
            return 50  # Default score if no metrics calculable
        return round(score)

    def _calculate_percentage_change(self, current, previous):
        try:
            current_value = _parse_currency(current)
            previous_value = _parse_currency(previous)

            if previous_value == 0:
                # Handle zero division
                return "N/A" if current_value == 0 else "inf"

            # Use abs for denominator
            change = ((current_value - previous_value) / abs(previous_value)) * 100
            return f"{round(change, 2)}%"
        except Exception:
            return "N/A"


# Singleton instance


_analyzer = None


def get_analyzer():
    """
    Returns a singleton instance of the FinancialAnalyzer.

    Returns:
        FinancialAnalyzer: The singleton instance.
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = FinancialAnalyzer()
    return _analyzer