# back-repo/agents/financial/report_comparison_agent.py
import asyncio
from typing import Dict, Any

# Assuming BaseAgent is located here, adjust if necessary
from ..base.base_agent import BaseAgent

class ReportComparisonAgent(BaseAgent):
    """
    Agent responsible for comparing two reports (represented as dictionaries).
    """
    async def process(self, task: Dict[str, Any]) -> Any:
        """
        Compares two reports (dictionaries) and identifies differences.

        Args:
            task: A dictionary containing the task details.
                  Expected keys:
                  - 'report1': The first report dictionary.
                  - 'report2': The second report dictionary.

        Returns:
            A dictionary detailing the differences found between the reports.
            Returns None if 'report1' or 'report2' are missing or not dictionaries.
        """
        report1 = task.get('report1')
        report2 = task.get('report2')

        if not isinstance(report1, dict) or not isinstance(report2, dict):
            # TODO: Implement proper logging
            print("Error: 'report1' and 'report2' (dictionaries) not found or invalid in task for ReportComparisonAgent.")
            return None

        print(f"ReportComparisonAgent comparing two reports.") # Placeholder

        try:
            # Adapt the synchronous comparison logic.
            await asyncio.sleep(0.01) # Simulate minimal processing time

            differences = {}
            all_keys = set(report1.keys()) | set(report2.keys())

            for key in all_keys:
                val1 = report1.get(key)
                val2 = report2.get(key)

                if val1 != val2:
                    differences[key] = {
                        'report1_value': val1,
                        'report2_value': val2
                    }
                    if key not in report1:
                         differences[key]['status'] = 'Added in report2'
                    elif key not in report2:
                         differences[key]['status'] = 'Removed in report2'
                    else:
                         differences[key]['status'] = 'Value changed'


            print(f"ReportComparisonAgent comparison completed. Found {len(differences)} differences.") # Placeholder
            return differences

        except Exception as e:
            # TODO: Implement proper logging
            print(f"Error comparing reports: {e}")
            return None