import pandas as pd
import os
import json
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDataExporter:
    """Export financial data to Excel"""
    
    def __init__(self, output_dir='excel_exports'):
        """Initialize the exporter
        
        Args:
            output_dir: Directory to save Excel files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_document_data(self, document_id, financial_dir='financial_data', extraction_dir='extractions'):
        """Export all data for a document to Excel
        
        Args:
            document_id: The document ID
            financial_dir: Directory containing financial data
            extraction_dir: Directory containing document extractions
            
        Returns:
            Path to the generated Excel file
        """
        logger.info(f"Exporting data for document: {document_id}")
        
        # Load document data
        document_data = self._load_document_data(document_id, financial_dir, extraction_dir)
        if not document_data:
            logger.error(f"Could not load data for document: {document_id}")
            return None
        
        # Create Excel writer
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_path = os.path.join(self.output_dir, f"{document_id}_export_{timestamp}.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            # Export document summary
            self._export_summary(writer, document_data)
            
            # Export securities
            self._export_securities(writer, document_data)
            
            # Export allocations
            self._export_allocations(writer, document_data)
            
            # Export extracted tables
            self._export_tables(writer, document_data)
            
            # Format the workbook
            self._format_workbook(writer)
        
        logger.info(f"Data exported to: {excel_path}")
        return excel_path
    
    def export_custom_table(self, document_id, columns, financial_dir='financial_data'):
        """Export a custom table for a document
        
        Args:
            document_id: The document ID
            columns: List of column names to include
            financial_dir: Directory containing financial data
            
        Returns:
            Path to the generated Excel file
        """
        logger.info(f"Exporting custom table for document: {document_id}")
        
        # Load financial data
        financial_path = os.path.join(financial_dir, f"{document_id}_financial.json")
        if not os.path.exists(financial_path):
            logger.error(f"Financial data not found: {financial_path}")
            return None
        
        try:
            with open(financial_path, 'r', encoding='utf-8') as f:
                financial_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading financial data: {e}")
            return None
        
        # Create the custom table data
        securities = financial_data.get('securities', [])
        
        rows = []
        for security in securities:
            row = {}
            
            # Add requested columns
            for column in columns:
                if column.lower() == 'isin':
                    row['ISIN'] = security.get('isin', '')
                
                elif column.lower() == 'name':
                    row['Security Name'] = security.get('name', '')
                
                elif column.lower() == 'currency':
                    currencies = security.get('currency', [])
                    row['Currency'] = currencies[0] if currencies else ''
                
                elif column.lower() == 'quantity':
                    quantities = security.get('quantities', [])
                    row['Quantity'] = quantities[0].get('value', '') if quantities else ''
                
                elif column.lower() == 'price':
                    prices = security.get('prices', [])
                    row['Price'] = prices[0].get('value', '') if prices else ''
                
                elif column.lower() == 'value':
                    quantities = security.get('quantities', [])
                    prices = security.get('prices', [])
                    
                    quantity = quantities[0].get('value', '0') if quantities else '0'
                    price = prices[0].get('value', '0') if prices else '0'
                    
                    try:
                        # Clean numeric strings
                        quantity_clean = re.sub(r'[^\d.]', '', quantity)
                        price_clean = re.sub(r'[^\d.]', '', price)
                        
                        quantity_val = float(quantity_clean) if quantity_clean else 0
                        price_val = float(price_clean) if price_clean else 0
                        
                        row['Value'] = quantity_val * price_val
                    except (ValueError, TypeError):
                        row['Value'] = ''
            
            rows.append(row)
        
        # Create DataFrame
        if rows:
            df = pd.DataFrame(rows)
            
            # Export to Excel
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            excel_path = os.path.join(self.output_dir, f"{document_id}_custom_table_{timestamp}.xlsx")
            
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Custom Table', index=False)
                
                # Format the workbook
                workbook = writer.book
                worksheet = writer.sheets['Custom Table']
                
                # Add header format
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'border': 1,
                    'bg_color': '#D6E0F5'
                })
                
                # Apply header format
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Set column widths
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).apply(len).max(), len(str(col))) + 2
                    worksheet.set_column(i, i, max_len)
            
            logger.info(f"Custom table exported to: {excel_path}")
            return excel_path
        else:
            logger.error("No data found for custom table")
            return None
    
    def _load_document_data(self, document_id, financial_dir, extraction_dir):
        """Load document and financial data"""
        data = {
            'document_id': document_id,
            'extraction': None,
            'financial': None
        }
        
        # Load extraction data
        extraction_path = os.path.join(extraction_dir, f"{document_id}_extraction.json")
        if os.path.exists(extraction_path):
            try:
                with open(extraction_path, 'r', encoding='utf-8') as f:
                    data['extraction'] = json.load(f)
                logger.info(f"Loaded extraction data: {extraction_path}")
            except Exception as e:
                logger.error(f"Error loading extraction data: {e}")
        else:
            logger.warning(f"Extraction file not found: {extraction_path}")
        
        # Load financial data
        financial_path = os.path.join(financial_dir, f"{document_id}_financial.json")
        if os.path.exists(financial_path):
            try:
                with open(financial_path, 'r', encoding='utf-8') as f:
                    data['financial'] = json.load(f)
                logger.info(f"Loaded financial data: {financial_path}")
            except Exception as e:
                logger.error(f"Error loading financial data: {e}")
        else:
            logger.warning(f"Financial data file not found: {financial_path}")
        
        # Check if we have any data
        if not data['extraction'] and not data['financial']:
            return None
        
        return data
    
    def _export_summary(self, writer, document_data):
        """Export document summary sheet"""
        extraction = document_data.get('extraction')
        financial = document_data.get('financial')
        
        summary_data = []
        
        # Add document metadata
        if extraction:
            summary_data.append(['Document ID', document_data['document_id']])
            summary_data.append(['Filename', extraction.get('filename', 'Unknown')])
            summary_data.append(['Page Count', extraction.get('page_count', 0)])
            summary_data.append(['Language', extraction.get('language', 'Unknown')])
            summary_data.append(['', ''])
        
        # Add financial summary
        if financial:
            summary = financial.get('summary', {})
            
            # Client and account info
            client_name = summary.get('client_name', {}).get('value', 'Unknown')
            account_number = summary.get('account_number', {}).get('value', 'Unknown')
            
            if client_name != 'Unknown':
                summary_data.append(['Client Name', client_name])
            
            if account_number != 'Unknown':
                summary_data.append(['Account Number', account_number])
            
            # Valuation date
            valuation_date = summary.get('valuation_date', {}).get('value', 'Unknown')
            if valuation_date != 'Unknown':
                summary_data.append(['Valuation Date', valuation_date])
            
            # Portfolio value
            portfolio_value = summary.get('total_portfolio_value', {})
            if portfolio_value:
                value = portfolio_value.get('value', 'Unknown')
                currency = portfolio_value.get('currency', '')
                summary_data.append(['Total Portfolio Value', f"{currency}{value}"])
            
            summary_data.append(['', ''])
            
            # Statistics
            isins_count = len(financial.get('isins', []))
            securities_count = len(financial.get('securities', []))
            tables_count = len(financial.get('tables', []))
            
            summary_data.append(['ISIN Count', isins_count])
            summary_data.append(['Securities Count', securities_count])
            summary_data.append(['Detected Tables', tables_count])
        
        # Create DataFrame and export
        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='Summary', header=False, index=False)
        
        # Format the summary sheet
        workbook = writer.book
        worksheet = writer.sheets['Summary']
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'bg_color': '#D6E0F5'
        })
        
        # Apply formatting
        for row_num in range(len(summary_data)):
            worksheet.write(row_num, 0, summary_data[row_num][0], header_format)
        
        # Set column widths
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 1, 40)
    
    def _export_securities(self, writer, document_data):
        """Export securities sheet"""
        financial = document_data.get('financial')
        
        if not financial or 'securities' not in financial:
            return
        
        securities = financial['securities']
        
        # Prepare data for DataFrame
        rows = []
        for security in securities:
            row = {
                'ISIN': security.get('isin', ''),
                'Security Name': security.get('name', '')
            }
            
            # Add currency
            currencies = security.get('currency', [])
            row['Currency'] = currencies[0] if currencies else ''
            
            # Add quantity
            quantities = security.get('quantities', [])
            row['Quantity'] = quantities[0].get('value', '') if quantities else ''
            
            # Add price
            prices = security.get('prices', [])
            row['Price'] = prices[0].get('value', '') if prices else ''
            
            # Calculate value if possible
            if prices and quantities:
                try:
                    quantity = quantities[0].get('value', '0')
                    price = prices[0].get('value', '0')
                    
                    # Clean numeric strings
                    quantity_clean = re.sub(r'[^\d.]', '', quantity)
                    price_clean = re.sub(r'[^\d.]', '', price)
                    
                    quantity_val = float(quantity_clean) if quantity_clean else 0
                    price_val = float(price_clean) if price_clean else 0
                    
                    row['Value'] = quantity_val * price_val
                except (ValueError, TypeError):
                    row['Value'] = ''
            else:
                row['Value'] = ''
            
            rows.append(row)
        
        # Create DataFrame
        if rows:
            df = pd.DataFrame(rows)
            
            # Export to Excel
            df.to_excel(writer, sheet_name='Securities', index=False)
            
            # Format the sheet
            workbook = writer.book
            worksheet = writer.sheets['Securities']
            
            # Add header format
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'border': 1,
                'bg_color': '#D6E0F5'
            })
            
            # Apply header format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Set column widths
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).apply(len).max(), len(str(col))) + 2
                worksheet.set_column(i, i, max_len)
    
    def _export_allocations(self, writer, document_data):
        """Export allocations sheet"""
        financial = document_data.get('financial')
        
        if not financial or 'metrics' not in financial:
            return
        
        metrics = financial['metrics']
        
        # Check if we have allocation data
        asset_allocation = metrics.get('asset_allocation', [])
        currency_allocation = metrics.get('currency_allocation', [])
        
        if not asset_allocation and not currency_allocation:
            return
        
        # Create asset allocation DataFrame
        if asset_allocation:
            asset_rows = []
            for item in asset_allocation:
                asset_rows.append({
                    'Asset Class': item.get('category', ''),
                    'Percentage': item.get('percentage', '')
                })
            
            asset_df = pd.DataFrame(asset_rows)
            
            # Export to Excel
            asset_df.to_excel(writer, sheet_name='Asset Allocation', index=False)
            
            # Format the sheet
            workbook = writer.book
            worksheet = writer.sheets['Asset Allocation']
            
            # Add header format
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'border': 1,
                'bg_color': '#D6E0F5'
            })
            
            # Apply header format
            for col_num, value in enumerate(asset_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Set column widths
            worksheet.set_column(0, 0, 25)
            worksheet.set_column(1, 1, 15)
        
        # Create currency allocation DataFrame
        if currency_allocation:
            currency_rows = []
            for item in currency_allocation:
                currency_rows.append({
                    'Currency': item.get('category', ''),
                    'Percentage': item.get('percentage', '')
                })
            
            currency_df = pd.DataFrame(currency_rows)
            
            # Export to Excel
            currency_df.to_excel(writer, sheet_name='Currency Allocation', index=False)
            
            # Format the sheet
            workbook = writer.book
            worksheet = writer.sheets['Currency Allocation']
            
            # Add header format
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'border': 1,
                'bg_color': '#D6E0F5'
            })
            
            # Apply header format
            for col_num, value in enumerate(currency_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Set column widths
            worksheet.set_column(0, 0, 25)
            worksheet.set_column(1, 1, 15)
    
    def _export_tables(self, writer, document_data):
        """Export extracted tables"""
        financial = document_data.get('financial')
        
        if not financial or 'tables' not in financial:
            return
        
        tables = financial['tables']
        
        for i, table in enumerate(tables):
            # Skip tables without enough data
            if not table.get('headers') or not table.get('rows'):
                continue
            
            headers = table['headers']
            rows = table['rows']
            
            # Create DataFrame
            table_data = []
            for row in rows:
                # Make sure row has the same length as headers
                if len(row) < len(headers):
                    row.extend([''] * (len(headers) - len(row)))
                elif len(row) > len(headers):
                    row = row[:len(headers)]
                
                table_data.append(row)
            
            df = pd.DataFrame(table_data, columns=headers)
            
            # Export to Excel
            sheet_name = f'Table {i+1}'
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Format the sheet
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Add header format
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'border': 1,
                'bg_color': '#D6E0F5'
            })
            
            # Apply header format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Set column widths
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).apply(len).max(), len(str(col))) + 2
                worksheet.set_column(i, i, max_len)
    
    def _format_workbook(self, writer):
        """Apply additional formatting to the workbook"""
        workbook = writer.book
        
        # Add formats
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})
        percentage_format = workbook.add_format({'num_format': '0.00%'})
        
        # Apply formats to specific columns in all sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            
            # Apply date format to date columns
            for col_idx, col_name in enumerate(writer.sheets[sheet_name].table.keys()):
                if 'date' in col_name.lower():
                    try:
                        worksheet.set_column(col_idx, col_idx, None, date_format)
                    except:
                        pass
            
            # Apply currency format to value/price columns
            for col_idx, col_name in enumerate(writer.sheets[sheet_name].table.keys()):
                if col_name.lower() in ['value', 'price', 'amount']:
                    try:
                        worksheet.set_column(col_idx, col_idx, None, currency_format)
                    except:
                        pass
            
            # Apply percentage format to percentage columns
            for col_idx, col_name in enumerate(writer.sheets[sheet_name].table.keys()):
                if 'percentage' in col_name.lower() or col_name.lower() == 'pct':
                    try:
                        worksheet.set_column(col_idx, col_idx, None, percentage_format)
                    except:
                        pass

# Usage example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python excel_exporter.py <document_id> [custom_columns]")
        sys.exit(1)
    
    document_id = sys.argv[1]
    exporter = FinancialDataExporter()
    
    if len(sys.argv) > 2:
        # Custom table export
        columns = sys.argv[2].split(',')
        output_path = exporter.export_custom_table(document_id, columns)
    else:
        # Full document export
        output_path = exporter.export_document_data(document_id)
    
    if output_path:
        print(f"Data exported to: {output_path}")
    else:
        print("Export failed")