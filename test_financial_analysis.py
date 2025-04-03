from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer
import pandas as pd

def test_financial_analysis():
    analyzer = FinancialAnalyzer()
    
    # Create test data (or load from a real financial table)
    data = {
        'Item': ['Revenue', 'Cost of Sales', 'Gross Profit', 'Operating Expenses', 'Net Income'],
        '2022': [1000000, 600000, 400000, 300000, 100000],
        '2023': [1200000, 700000, 500000, 350000, 150000]
    }
    df = pd.DataFrame(data)
    df = df.set_index('Item')
    
    # Analyze the data
    table_type = analyzer.classify_table(df)
    analysis = analyzer.analyze_financial_table(df, table_type)
    
    print(f"Table classified as: {table_type}")
    print("Analysis results:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_financial_analysis()
