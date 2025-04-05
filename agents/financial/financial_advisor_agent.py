# back-repo/agents/financial/financial_advisor_agent.py
import asyncio
from typing import Dict, Any

# Assuming BaseAgent is located here, adjust if necessary
from ..base.base_agent import BaseAgent

class FinancialAdvisorAgent(BaseAgent):
    """
    Agent responsible for providing basic financial advice based on income and expenses.
    """
    async def process(self, task: Dict[str, Any]) -> Any:
        """
        Provides financial advice based on income and expenses.

        Args:
            task: A dictionary containing the task details.
                  Expected keys:
                  - 'income': The total income amount (numeric).
                  - 'expenses': The total expenses amount (numeric).

        Returns:
            A dictionary containing financial advice or status.
            Returns None if 'income' or 'expenses' are missing or invalid.
        """
        income = task.get('income')
        expenses = task.get('expenses')

        # Basic validation
        if income is None or expenses is None or not isinstance(income, (int, float)) or not isinstance(expenses, (int, float)):
            # TODO: Implement proper logging
            print("Error: 'income' and 'expenses' (numeric) not found or invalid in task for FinancialAdvisorAgent.")
            return None

        print(f"FinancialAdvisorAgent processing income={income}, expenses={expenses}") # Placeholder

        try:
            # Adapt the synchronous example code logic.
            # This logic is simple and doesn't require async operations itself.
            await asyncio.sleep(0.01) # Simulate minimal processing time

            savings = income - expenses
            advice = {}

            if savings > 0:
                advice['status'] = "Surplus"
                advice['message'] = f"You have a surplus of {savings}. Consider saving or investing."
                advice['savings_rate'] = (savings / income) * 100 if income > 0 else 0
            elif savings < 0:
                advice['status'] = "Deficit"
                advice['message'] = f"You have a deficit of {abs(savings)}. Review your expenses."
                advice['savings_rate'] = (savings / income) * 100 if income > 0 else 0 # Will be negative
            else:
                advice['status'] = "Balanced"
                advice['message'] = "Your income equals your expenses. Aim to build savings."
                advice['savings_rate'] = 0

            print(f"FinancialAdvisorAgent completed.") # Placeholder
            return advice

        except Exception as e:
            # TODO: Implement proper logging
            print(f"Error processing financial advice for income={income}, expenses={expenses}: {e}")
            return None