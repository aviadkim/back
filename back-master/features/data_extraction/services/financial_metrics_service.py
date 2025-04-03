import pandas as pd
import re


# Helper function to clean and convert potential numeric strings
def _clean_and_convert(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Remove currency symbols, commas, parentheses (for negatives)
        cleaned_value = re.sub(r'[$,()]', '', value).strip()
        # Handle potential percentage signs if needed, or assume they are not numeric columns
        if '%' in cleaned_value:
            return None  # Or handle percentages differently if required
        try:
            # Convert to float
            return float(cleaned_value)
        except ValueError:
            # Return None if conversion fails
            return None
    return None


def calculate_metrics(table_data):
    """
    Calculates basic financial metrics for a given table.
    Currently calculates totals for numeric columns.

    Args:
        table_data (dict): A dictionary representing the table, expected to have
                           'headers' (list) and 'rows' (list of dicts).

    Returns:
        dict: A dictionary containing calculated metrics (e.g., column totals).
              Returns an error message if input is invalid.
    """
    if not table_data or 'headers' not in table_data or 'rows' not in table_data:
        return {"error": "Invalid table data provided for metrics calculation."}

    headers = table_data['headers']
    rows = table_data['rows']

    if not rows:
        return {"column_totals": {}, "message": "Table has no rows to calculate totals."}

    # Use pandas DataFrame for easier calculation
    try:
        df = pd.DataFrame(rows)
        # Ensure DataFrame columns match headers if necessary, though DataFrame infer columns
    except Exception as e:
        return {"error": f"Failed to create DataFrame from table data: {e}"}

    column_totals = {}
    for header in headers:
        if header in df.columns:
            # Attempt to clean and convert the column to numeric
            numeric_series = df[header].apply(_clean_and_convert)

            # Check if the column contains any numeric values after cleaning
            if numeric_series.notna().any():
                # Calculate the sum, ignoring non-numeric values (NaNs)
                total = numeric_series.sum(skipna=True)
                column_totals[header] = total
            else:
                # Indicate if column was non-numeric or empty after cleaning
                column_totals[header] = "Non-numeric or empty"
        else:
            column_totals[header] = "Header not found in data"

    return {
        "table_id": table_data.get("id", "N/A"),
        "table_title": table_data.get("title", "N/A"),
        "metrics": {
            "column_totals": column_totals,
            "row_count": len(rows),
            "column_count": len(headers)
            # Add more metrics here later
        }
    }

# Note: This implementation assumes rows are dictionaries mapping headers to values.
# Adjustments might be needed if the table data structure is different.