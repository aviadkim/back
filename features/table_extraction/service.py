"""
Services for Table Extraction Feature
"""

import logging
import json
import io
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory table storage (in a real app, this would be in a database)
document_tables = {}

# Sample table data for testing
sample_asset_allocation = {
    "id": "sample_document_table_1",
    "name": "חלוקת נכסים",
    "page": 1,
    "header": ["סוג נכס", "אחוז מהתיק", "שווי (₪)"],
    "rows": [
        ["מניות", "45%", "450,000"],
        ["אג\"ח ממשלתי", "30%", "300,000"],
        ["אג\"ח קונצרני", "15%", "150,000"],
        ["מזומן", "10%", "100,000"]
    ]
}

sample_currency_allocation = {
    "id": "sample_document_table_2",
    "name": "התפלגות מטבעית",
    "page": 2,
    "header": ["מטבע", "אחוז מהתיק", "שווי (₪)"],
    "rows": [
        ["שקל (₪)", "60%", "600,000"],
        ["דולר ($)", "25%", "250,000"],
        ["אירו (€)", "10%", "100,000"],
        ["אחר", "5%", "50,000"]
    ]
}

# Initialize with sample data
document_tables["sample_document"] = {
    "1": [sample_asset_allocation],
    "2": [sample_currency_allocation]
}

def get_document_tables(document_id, page=None):
    """
    Get tables from a document
    
    Args:
        document_id: Document ID
        page: Optional page number
        
    Returns:
        list: Tables in the document or on the specified page
    """
    logger.info(f"Getting tables for document {document_id}{' on page ' + str(page) if page else ''}")
    
    # Create sample tables if we don't have any for this document
    if document_id not in document_tables:
        document_tables[document_id] = {
            "1": [{
                "id": f"{document_id}_table_1",
                "name": "חלוקת נכסים",
                "page": 1,
                "header": ["סוג נכס", "אחוז מהתיק", "שווי (₪)"],
                "rows": [
                    ["מניות", "45%", "450,000"],
                    ["אג\"ח ממשלתי", "30%", "300,000"],
                    ["אג\"ח קונצרני", "15%", "150,000"],
                    ["מזומן", "10%", "100,000"]
                ]
            }],
            "2": [{
                "id": f"{document_id}_table_2",
                "name": "התפלגות מטבעית",
                "page": 2,
                "header": ["מטבע", "אחוז מהתיק", "שווי (₪)"],
                "rows": [
                    ["שקל (₪)", "60%", "600,000"],
                    ["דולר ($)", "25%", "250,000"],
                    ["אירו (€)", "10%", "100,000"],
                    ["אחר", "5%", "50,000"]
                ]
            }]
        }
    
    # If page is specified, return tables from that page only
    if page:
        page_str = str(page)
        return document_tables[document_id].get(page_str, [])
    
    # Otherwise return all tables as a flattened list
    tables = []
    for page_tables in document_tables[document_id].values():
        tables.extend(page_tables)
    
    return tables

def get_table_by_id(table_id):
    """
    Get a specific table by ID
    
    Args:
        table_id: Table ID
        
    Returns:
        dict: Table data or None if not found
    """
    logger.info(f"Getting table by ID: {table_id}")
    
    # Search through all documents and pages
    for doc_tables in document_tables.values():
        for page_tables in doc_tables.values():
            for table in page_tables:
                if table["id"] == table_id:
                    return table
    
    return None

def generate_table_view(document_id, table_ids, view_format="default", options=None):
    """
    Generate a specialized view of tables
    
    Args:
        document_id: Document ID
        table_ids: List of table IDs to include
        view_format: Format of the view (default, summary, comparison)
        options: Additional options
        
    Returns:
        dict: The generated view
    """
    logger.info(f"Generating {view_format} table view for document {document_id}")
    options = options or {}
    
    # Get the requested tables
    tables = []
    for table_id in table_ids:
        table = get_table_by_id(table_id)
        if table:
            tables.append(table)
    
    # Generate the requested view
    if view_format == "summary":
        return generate_summary_view(tables, options)
    elif view_format == "comparison":
        return generate_comparison_view(tables, options)
    else:
        # Default view
        return {
            "id": f"view_{document_id}_{int(datetime.now().timestamp())}",
            "name": options.get("name", "מבט משולב"),
            "type": "default",
            "tables": tables,
            "created_at": datetime.now().isoformat()
        }

def generate_summary_view(tables, options=None):
    """
    Generate a summary view of tables
    
    Args:
        tables: List of tables
        options: Additional options
        
    Returns:
        dict: Summary view
    """
    options = options or {}
    metrics = []
    
    for table in tables:
        if table.get("header") and table.get("rows"):
            for row in table["rows"]:
                if len(row) >= 2:
                    metrics.append({
                        "category": table["name"],
                        "name": row[0],
                        "value": row[1],
                        "additional": ", ".join(row[2:]) if len(row) > 2 else ""
                    })
    
    return {
        "id": f"summary_{int(datetime.now().timestamp())}",
        "name": options.get("name", "תקציר נתונים"),
        "type": "summary",
        "metrics": metrics,
        "source_tables": [t["id"] for t in tables],
        "created_at": datetime.now().isoformat()
    }

def generate_comparison_view(tables, options=None):
    """
    Generate a comparison view of tables
    
    Args:
        tables: List of tables
        options: Additional options
        
    Returns:
        dict: Comparison view
    """
    options = options or {}
    
    # Need at least 2 tables for comparison
    if len(tables) < 2:
        return {
            "id": f"comparison_{int(datetime.now().timestamp())}",
            "name": "השוואה",
            "type": "comparison",
            "error": "נדרשות לפחות שתי טבלאות להשוואה",
            "created_at": datetime.now().isoformat()
        }
    
    # Extract categories from all tables
    categories = []
    for table in tables:
        if table.get("header") and table.get("rows"):
            for row in table["rows"]:
                if row and row[0] not in categories:
                    categories.append(row[0])
    
    # Build comparison data
    comparison_data = []
    for category in categories:
        category_data = {
            "category": category,
            "values": []
        }
        
        for table in tables:
            row = next((r for r in table.get("rows", []) if r and r[0] == category), None)
            
            if row:
                category_data["values"].append({
                    "table": table["name"],
                    "value": row[1] if len(row) > 1 else "N/A",
                    "additional": ", ".join(row[2:]) if len(row) > 2 else ""
                })
            else:
                category_data["values"].append({
                    "table": table["name"],
                    "value": "N/A",
                    "additional": ""
                })
        
        comparison_data.append(category_data)
    
    return {
        "id": f"comparison_{int(datetime.now().timestamp())}",
        "name": options.get("name", "השוואת נתונים"),
        "type": "comparison",
        "tables": [{"id": t["id"], "name": t["name"]} for t in tables],
        "categories": categories,
        "comparison_data": comparison_data,
        "created_at": datetime.now().isoformat()
    }

def export_table(document_id, table_id, export_format="csv"):
    """
    Export a table in various formats
    
    Args:
        document_id: Document ID
        table_id: Table ID
        export_format: Export format (csv, json, xlsx)
        
    Returns:
        str or BytesIO: Exported table data
    """
    logger.info(f"Exporting table {table_id} from document {document_id} in {export_format} format")
    
    table = get_table_by_id(table_id)
    if not table:
        raise ValueError(f"Table not found: {table_id}")
    
    if export_format == "json":
        return json.dumps(table, ensure_ascii=False, indent=2)
    
    elif export_format == "xlsx":
        # For a real implementation, you would use a library like openpyxl
        # For this demo, we'll just return a placeholder
        return io.BytesIO(b"XLSX export placeholder")
    
    else:  # Default to CSV
        csv_lines = []
        
        # Add header
        if table.get("header"):
            csv_lines.append(",".join([f'"{h}"' for h in table["header"]]))
        
        # Add rows
        if table.get("rows"):
            for row in table["rows"]:
                csv_lines.append(",".join([f'"{cell}"' for cell in row]))
        
        return "\n".join(csv_lines)
