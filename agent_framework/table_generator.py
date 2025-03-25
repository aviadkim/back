"""
Table generator module for creating custom tables based on financial data

This module provides functionality to generate structured tables from financial data
based on user queries and specifications.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class CustomTableGenerator:
    """
    Class to generate custom tables based on financial data
    """
    
    def __init__(self):
        """Initialize the table generator"""
        self.logger = logging.getLogger(__name__)
    
    def generate_custom_table(self, data: List[Dict[str, Any]], spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a custom table based on financial data and a specification

        Args:
            data: List of data dictionaries (usually financial data points)
            spec: A specification for the table including columns, filters, etc.
            
        Returns:
            A structured table in dictionary format
        """
        try:
            # Extract table components from spec
            columns = spec.get('columns', [])
            filters = spec.get('filters', [])
            sort_by = spec.get('sort_by', {})
            group_by = spec.get('group_by')
            
            # Apply filters to data
            filtered_data = self._apply_filters(data, filters)
            
            # Group data if needed
            if group_by:
                result_data = self._group_data(filtered_data, group_by, columns)
            else:
                # Select only the specified columns
                result_data = self._select_columns(filtered_data, columns)
            
            # Sort the results
            if sort_by:
                result_data = self._sort_data(result_data, sort_by)
            
            # Construct the table
            headers = columns if columns else (list(result_data[0].keys()) if result_data else [])
            rows = []
            
            for item in result_data:
                row = [str(item.get(col, '')) for col in headers]
                rows.append(row)
            
            return {
                'headers': headers,
                'rows': rows,
                'count': len(rows),
                'filters_applied': len(filters),
                'metadata': {
                    'sort_by': sort_by.get('field') if sort_by else None,
                    'sort_direction': sort_by.get('direction') if sort_by else None,
                    'grouped_by': group_by
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating custom table: {str(e)}")
            # Return a minimal structure in case of error
            return {
                'headers': [],
                'rows': [],
                'count': 0,
                'error': str(e)
            }
    
    def _apply_filters(self, data: List[Dict[str, Any]], filters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply filters to the data"""
        if not filters:
            return data
        
        filtered_data = data.copy()
        
        for filter_spec in filters:
            field = filter_spec.get('field')
            operator = filter_spec.get('operator')
            value = filter_spec.get('value')
            
            if not field or not operator:
                continue
            
            filtered_data = [
                item for item in filtered_data 
                if self._matches_filter(item.get(field), operator, value)
            ]
        
        return filtered_data
    
    def _matches_filter(self, item_value: Any, operator: str, filter_value: Any) -> bool:
        """Check if a value matches a filter condition"""
        if item_value is None:
            return False
        
        if operator == '=':
            return item_value == filter_value
        elif operator == '>':
            return item_value > filter_value
        elif operator == '<':
            return item_value < filter_value
        elif operator == 'contains':
            return str(filter_value).lower() in str(item_value).lower()
        
        return False
    
    def _select_columns(self, data: List[Dict[str, Any]], columns: List[str]) -> List[Dict[str, Any]]:
        """Select only the specified columns from the data"""
        if not columns:
            return data
        
        result = []
        for item in data:
            filtered_item = {col: item.get(col) for col in columns}
            result.append(filtered_item)
        
        return result
    
    def _sort_data(self, data: List[Dict[str, Any]], sort_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sort the data based on a field and direction"""
        field = sort_spec.get('field')
        direction = sort_spec.get('direction', 'asc')
        
        if not field:
            return data
        
        reverse = direction.lower() == 'desc'
        
        # Try to handle different types appropriately
        def get_sort_key(item):
            value = item.get(field)
            if value is None:
                return '' if reverse else float('inf')
            return value
        
        return sorted(data, key=get_sort_key, reverse=reverse)
    
    def _group_data(self, data: List[Dict[str, Any]], group_by: str, metrics: List[str]) -> List[Dict[str, Any]]:
        """Group the data by a field and calculate aggregates for metrics"""
        if not group_by or not data:
            return data
        
        groups = {}
        for item in data:
            key = item.get(group_by)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        
        result = []
        for key, items in groups.items():
            grouped_item = {group_by: key}
            
            for metric in metrics:
                if metric == group_by:
                    continue
                
                # Calculate different aggregates based on data type
                values = [item.get(metric) for item in items if item.get(metric) is not None]
                
                if values:
                    # Try numeric operations first
                    try:
                        grouped_item[f"sum_{metric}"] = sum(values)
                        grouped_item[f"avg_{metric}"] = sum(values) / len(values)
                        grouped_item[f"count_{metric}"] = len(values)
                    except (TypeError, ValueError):
                        # For non-numeric data, just count occurrences
                        grouped_item[f"count_{metric}"] = len(values)
                
            result.append(grouped_item)
        
        return result
