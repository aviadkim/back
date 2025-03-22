from pdf_processor.tables.table_extractor import TableExtractor
import pandas as pd

def test_table_extraction():
    extractor = TableExtractor()
    tables = extractor.extract_tables("test_documents/your_financial_doc.pdf")
    
    for page_num, page_tables in tables.items():
        print(f"Page {page_num}: {len(page_tables)} tables found")
        for i, table in enumerate(page_tables):
            print(f"  Table {i}: {table['row_count']} rows, {table['col_count']} columns")
            df = extractor.convert_to_dataframe(table)
            print(df.head())
            print("\n")

if __name__ == "__main__":
    test_table_extraction()
