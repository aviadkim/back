# Placeholder service to provide mock structured financial data for analysis.
# In a real application, this would fetch data extracted and structured
# from documents, likely stored in a database.

_mock_financial_data = {
    "doc1": {
        "revenue": {"total": "$1,250,000", "details": "..."},
        "expenses": {"total": "$875,000", "details": "..."},
        "assets": {"total": "$3,000,000", "current": "$950,000"},
        "liabilities": {"total": "$1,500,000", "current": "$600,000"},
        "net_income": "$375,000"  # Added for completeness
    },
    # Add more mock data for other document IDs if needed
    "doc2": {
        "revenue": {"total": "$0", "details": "N/A"},
        "expenses": {"total": "$5,000", "details": "Travel expenses"},
        "assets": {"total": "$10,000", "current": "$10,000"},
        "liabilities": {"total": "$2,000", "current": "$2,000"},
        "net_income": "-$5,000"
    }
}


def get_financial_data(document_id):
    """
    Placeholder function to retrieve mock structured financial data for a document ID.

    Args:
        document_id (str): The ID of the document.

    Returns:
        dict or None: The mock financial data if found, otherwise None.
    """
    print(f"Warning: Using mock financial_data_service.get_financial_data for ID: {document_id}")
    return _mock_financial_data.get(document_id)

# Note: This service is intentionally simple for Phase 3 development.


# It needs to be replaced with actual data retrieval logic later.