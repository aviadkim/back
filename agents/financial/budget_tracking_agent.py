# back-repo/agents/financial/budget_tracking_agent.py
import asyncio
from typing import Dict, Any, List

# Assuming BaseAgent is located here, adjust if necessary
from ..base.base_agent import BaseAgent

class BudgetTrackingAgent(BaseAgent):
    """
    Agent responsible for tracking income and expenses from a list of transactions.
    """
    async def process(self, task: Dict[str, Any]) -> Any:
        """
        Calculates total income and expenses from a list of transactions.

        Args:
            task: A dictionary containing the task details.
                  Expected keys:
                  - 'transactions': A list of dictionaries, where each dictionary
                                    represents a transaction and should ideally have
                                    'type' ('income' or 'expense') and 'amount' keys.
                                    Example: [{'type': 'income', 'amount': 100}, {'type': 'expense', 'amount': 50}]

        Returns:
            A dictionary summarizing total income, total expenses, and net balance.
            Returns None if 'transactions' is missing or invalid.
        """
        transactions = task.get('transactions')
        if not transactions or not isinstance(transactions, list):
            # TODO: Implement proper logging
            print("Error: 'transactions' (list) not found or invalid in task for BudgetTrackingAgent.")
            return None

        print(f"BudgetTrackingAgent processing {len(transactions)} transactions.") # Placeholder

        try:
            # Adapt the synchronous example logic. Simple calculation, no real async needed.
            await asyncio.sleep(0.01) # Simulate minimal processing time

            total_income = 0.0
            total_expenses = 0.0

            for tx in transactions:
                if not isinstance(tx, dict) or 'type' not in tx or 'amount' not in tx:
                    print(f"Warning: Skipping invalid transaction format: {tx}")
                    continue

                amount = tx.get('amount', 0.0)
                if not isinstance(amount, (int, float)):
                     print(f"Warning: Skipping transaction with non-numeric amount: {tx}")
                     continue

                if tx.get('type') == 'income':
                    total_income += amount
                elif tx.get('type') == 'expense':
                    total_expenses += amount
                else:
                    print(f"Warning: Skipping transaction with unknown type: {tx}")

            net_balance = total_income - total_expenses

            summary = {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_balance": net_balance,
                "transaction_count": len(transactions)
            }

            print(f"BudgetTrackingAgent completed.") # Placeholder
            return summary

        except Exception as e:
            # TODO: Implement proper logging
            print(f"Error processing budget tracking for transactions: {e}")
            return None