import re

def fix_analyze_portfolio():
    """Fix the portfolio analysis function in enhanced_financial_extractor.py"""
    # Read the file
    with open('enhanced_financial_extractor.py', 'r') as f:
        content = f.read()
    
    # Find the problematic function
    analyze_portfolio_pattern = r'def analyze_portfolio\(holdings_data\):.*?return results'
    analyze_portfolio_match = re.search(analyze_portfolio_pattern, content, re.DOTALL)
    
    if not analyze_portfolio_match:
        print("Could not find analyze_portfolio function")
        return False
    
    old_func = analyze_portfolio_match.group(0)
    
    # Replace with fixed function
    new_func = """def analyze_portfolio(holdings_data):
    \"\"\"Perform comprehensive portfolio analysis\"\"\"
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(holdings_data, orient='index')
    
    # Check if DataFrame is empty
    if df.empty:
        return {
            'total_value': 0,
            'security_count': 0,
            'asset_allocation': {},
            'currency_allocation': {},
            'top_holdings': [],
            'risk_metrics': {},
            'performance': {}
        }
    
    # Ensure numeric values
    numeric_columns = ['market_value', 'quantity', 'price', 'percentage']
    for col in numeric_columns:
        if col in df.columns:
            # Check if the column has any non-null values
            if df[col].notna().any():
                # Convert string percentages to floats
                if col == 'percentage':
                    # Handle percentage values with % symbol
                    df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce') / 100.0
                else:
                    # Handle numeric values with commas
                    df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Initialize results
    results = {
        'total_value': 0,
        'security_count': len(df),
        'asset_allocation': {},
        'currency_allocation': {},
        'top_holdings': [],
        'risk_metrics': {},
        'performance': {}
    }
    
    # Calculate total value
    if 'market_value' in df.columns and df['market_value'].notna().any():
        results['total_value'] = df['market_value'].sum()
    
    # Calculate asset allocation
    if 'security_type' in df.columns and df['security_type'].notna().any() and 'market_value' in df.columns:
        try:
            # Filter out rows with NaN values
            valid_rows = df[df['security_type'].notna() & df['market_value'].notna()]
            if not valid_rows.empty:
                asset_allocation = valid_rows.groupby('security_type')['market_value'].sum()
                asset_allocation_dict = asset_allocation.to_dict()
                
                # Calculate percentages
                for asset_type, value in asset_allocation_dict.items():
                    if asset_type and not pd.isna(asset_type):
                        results['asset_allocation'][asset_type] = {
                            'value': value,
                            'percentage': value / results['total_value'] * 100 if results['total_value'] else 0
                        }
        except Exception as e:
            print(f"Error calculating asset allocation: {e}")
    
    # Identify top holdings
    if 'market_value' in df.columns and df['market_value'].notna().any():
        try:
            # Filter valid rows and get top 10
            valid_rows = df[df['market_value'].notna()]
            if not valid_rows.empty:
                top_holdings = valid_rows.nlargest(10, 'market_value')
                
                for idx, row in top_holdings.iterrows():
                    holding_data = {
                        'isin': idx,
                        'market_value': row['market_value'],
                        'percentage': row['market_value'] / results['total_value'] * 100 if results['total_value'] else 0
                    }
                    
                    # Add name if available
                    if 'name' in row and not pd.isna(row['name']):
                        holding_data['name'] = row['name']
                    else:
                        holding_data['name'] = 'Unknown'
                    
                    results['top_holdings'].append(holding_data)
        except Exception as e:
            print(f"Error identifying top holdings: {e}")
    
    return results"""
    
    # Replace the function
    updated_content = content.replace(old_func, new_func)
    
    # Write back to file
    with open('enhanced_financial_extractor.py', 'w') as f:
        f.write(updated_content)
    
    print("Fixed analyze_portfolio function")
    return True

if __name__ == "__main__":
    fix_analyze_portfolio()
