"""
Excel exporter module for financial document data
Requires pandas package: pip install pandas
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional

# We'll conditionally import pandas to avoid errors if it's not installed
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("Pandas not available. Excel export functionality will be limited.")

class ExcelExporter:
    """Export financial data to Excel format"""
    
    def __init__(self, export_dir: str = 'exports'):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        
        if not PANDAS_AVAILABLE:
            logging.warning("Pandas package is not installed. Please install it: pip install pandas")
    
    def export_financial_data(self, 
                               data: List[Dict[str, Any]], 
                               filename: str, 
                               document_id: Optional[str] = None) -> Optional[str]:
        """Export financial data to Excel file
        
        Args:
            data: List of dictionaries containing financial data
            filename: Output filename
            document_id: Optional document ID to include in filename
            
        Returns:
            Path to the created Excel file or None if export failed
        """
        if not PANDAS_AVAILABLE:
            logging.error("Cannot export to Excel: pandas package is not installed")
            return None
        
        try:
            # Create a pandas DataFrame from the data
            df = pd.DataFrame(data)
            
            # Add document ID to filename if provided
            if document_id:
                base_name, ext = os.path.splitext(filename)
                output_path = os.path.join(self.export_dir, f"{base_name}_{document_id}{ext}")
            else:
                output_path = os.path.join(self.export_dir, filename)
            
            # Export to Excel
            df.to_excel(output_path, index=False)
            
            logging.info(f"Financial data exported to {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Error exporting financial data to Excel: {str(e)}")
            return None
            
    def export_analysis_results(self, 
                                analysis: Dict[str, Any], 
                                filename: str,
                                document_id: Optional[str] = None) -> Optional[str]:
        """Export analysis results to Excel with multiple sheets
        
        Args:
            analysis: Dictionary containing analysis data
            filename: Output filename
            document_id: Optional document ID to include in filename
            
        Returns:
            Path to the created Excel file or None if export failed
        """
        if not PANDAS_AVAILABLE:
            logging.error("Cannot export to Excel: pandas package is not installed")
            return None
            
        try:
            # Add document ID to filename if provided
            if document_id:
                base_name, ext = os.path.splitext(filename)
                output_path = os.path.join(self.export_dir, f"{base_name}_{document_id}{ext}")
            else:
                output_path = os.path.join(self.export_dir, filename)
            
            # Create Excel writer
            with pd.ExcelWriter(output_path) as writer:
                # Summary sheet
                summary_data = {
                    'Metric': ['Total Value', 'Security Count'],
                    'Value': [analysis.get('total_value', 'N/A'), analysis.get('security_count', 'N/A')]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Asset allocation sheet
                if 'asset_allocation' in analysis:
                    allocation_data = []
                    for asset_type, data in analysis['asset_allocation'].items():
                        allocation_data.append({
                            'Asset Type': asset_type,
                            'Value': data.get('value'),
                            'Percentage': data.get('percentage')
                        })
                    pd.DataFrame(allocation_data).to_excel(writer, sheet_name='Asset Allocation', index=False)
                
                # Top holdings sheet
                if 'top_holdings' in analysis and analysis['top_holdings']:
                    pd.DataFrame(analysis['top_holdings']).to_excel(writer, sheet_name='Top Holdings', index=False)
            
            logging.info(f"Analysis results exported to {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Error exporting analysis results to Excel: {str(e)}")
            return None