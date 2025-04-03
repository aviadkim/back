"""
Test script for the table generator functionality

This script tests the table generator's ability to create custom tables
from financial data based on specifications.
"""

import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_table_generator():
    """Test the table generator functionality"""
    logger.info("=== Testing Table Generator ===")
    
    try:
        # Import the table generator
        from agent_framework.table_generator import CustomTableGenerator
        logger.info("✅ Successfully imported CustomTableGenerator")
        
        # Initialize the table generator
        table_generator = CustomTableGenerator()
        logger.info("✅ Initialized CustomTableGenerator")
        
        # Sample financial data
        logger.info("\nCreating sample financial data...")
        financial_data = [
            {"security_type": "bond", "name": "US Treasury 10Y", "yield_percent": 4.2, "maturity_date": "2033-05-15", "currency": "USD", "credit_rating": "AAA"},
            {"security_type": "bond", "name": "Corporate Bond A", "yield_percent": 5.3, "maturity_date": "2028-10-20", "currency": "USD", "credit_rating": "BBB+"},
            {"security_type": "bond", "name": "Corporate Bond B", "yield_percent": 6.1, "maturity_date": "2029-03-15", "currency": "USD", "credit_rating": "BB"},
            {"security_type": "bond", "name": "Government Bond C", "yield_percent": 3.8, "maturity_date": "2030-11-30", "currency": "EUR", "credit_rating": "AA-"},
            {"security_type": "stock", "name": "Tech Company X", "dividend_yield": 1.2, "sector": "Technology", "currency": "USD"},
            {"security_type": "stock", "name": "Bank Y", "dividend_yield": 3.5, "sector": "Financials", "currency": "EUR"},
            {"security_type": "etf", "name": "S&P 500 ETF", "expense_ratio": 0.04, "category": "Equity", "currency": "USD"}
        ]
        logger.info(f"✅ Created {len(financial_data)} sample financial data entries")
        
        # Test 1: Basic table with filters
        logger.info("\nTest 1: Creating a basic table with filters")
        basic_spec = {
            "columns": ["name", "yield_percent", "maturity_date", "currency", "credit_rating"],
            "filters": [
                {"field": "security_type", "operator": "=", "value": "bond"},
                {"field": "yield_percent", "operator": ">", "value": 5.0},
                {"field": "currency", "operator": "=", "value": "USD"}
            ],
            "sort_by": {"field": "yield_percent", "direction": "desc"}
        }
        
        basic_table = table_generator.generate_custom_table(financial_data, basic_spec)
        
        # Verify the results
        logger.info(f"✅ Generated table with {basic_table.get('count', 0)} rows")
        logger.info(f"Headers: {basic_table.get('headers', [])}")
        for row in basic_table.get('rows', []):
            logger.info(f"Row: {row}")
        
        # Test 2: Group by currency
        logger.info("\nTest 2: Creating a table grouped by currency")
        group_spec = {
            "columns": ["currency", "security_type", "yield_percent"],
            "group_by": "currency"
        }
        
        group_table = table_generator.generate_custom_table(financial_data, group_spec)
        
        # Verify the results
        logger.info(f"✅ Generated grouped table with {group_table.get('count', 0)} rows")
        logger.info(f"Headers: {group_table.get('headers', [])}")
        for row in group_table.get('rows', []):
            logger.info(f"Row: {row}")
        
        # Test 3: Minimal specification
        logger.info("\nTest 3: Creating a table with minimal specification")
        minimal_spec = {
            "columns": ["name", "security_type", "currency"]
        }
        
        minimal_table = table_generator.generate_custom_table(financial_data, minimal_spec)
        
        # Verify the results
        logger.info(f"✅ Generated minimal table with {minimal_table.get('count', 0)} rows")
        logger.info(f"Headers: {minimal_table.get('headers', [])}")
        logger.info(f"First row (sample): {minimal_table.get('rows', [])[0] if minimal_table.get('rows') else 'No rows'}")
        
        # Test 4: Error handling with invalid specification
        logger.info("\nTest 4: Testing error handling with invalid specification")
        invalid_spec = {
            "columns": ["invalid_column"],
            "filters": [{"field": "nonexistent", "operator": "=", "value": "test"}]
        }
        
        try:
            invalid_table = table_generator.generate_custom_table(financial_data, invalid_spec)
            logger.info("Table generator handled invalid specification gracefully")
            logger.info(f"Result: {invalid_table}")
        except Exception as e:
            logger.error(f"Error handling invalid specification: {str(e)}")
        
        logger.info("\n=== Table Generator Tests Completed Successfully ===")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in table generator test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    test_table_generator()
