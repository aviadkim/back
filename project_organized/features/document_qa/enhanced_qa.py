"""Enhanced question answering system for financial documents."""
import os
import re
import json
import logging
from typing import Dict, Any, Optional, List
import pandas as pd
from ...shared.ai.service import AIService

logger = logging.getLogger(__name__)

class EnhancedDocumentQA:
    """Advanced document Q&A system with specialized processing for financial documents"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.extraction_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'extractions'))
        self.qa_results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'qa_results'))
        os.makedirs(self.qa_results_dir, exist_ok=True)
        
        # Define prompt templates for different question types
        self.prompt_templates = {
            'financial': """You are a financial document analysis expert. 
Answer the following question based ONLY on the provided document content.
Be precise, direct, and extract exact figures when available.

Document content:
{content}

Question: {question}

Answer:""",
            'general': """Answer the following question based ONLY on the provided document content.
If the content doesn't contain information to answer the question, clearly state that.

Document content:
{content}

Question: {question}

Answer:"""
        }
    
    def answer_question(self, document_id: str, question: str) -> Dict[str, Any]:
        """Answer a question about a specific document
        
        Args:
            document_id: The document ID
            question: The question to answer
            
        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Processing question about document {document_id}: {question}")
        
        # Get document content
        document_content = self._get_document_content(document_id)
        if not document_content:
            return {"answer": "Sorry, I couldn't find the document content.", "success": False}
        
        # Determine question type for appropriate prompting
        question_category = self._categorize_question(question)
        
        # Create prompt based on question type
        prompt_template = self.prompt_templates.get(question_category, self.prompt_templates['general'])
        prompt = prompt_template.format(content=document_content, question=question)
        
        # Use AI service to answer
        try:
            answer = self.ai_service.generate_response(prompt)
            
            # Save Q&A for later reference
            self._save_qa_result(document_id, question, answer)
            
            return {
                "answer": answer,
                "success": True,
                "document_id": document_id,
                "question": question,
                "category": question_category
            }
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": f"I encountered an error trying to answer your question. Please try again. Error: {str(e)}",
                "success": False
            }
    
    def generate_table(self, document_id: str, table_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a custom table based on document content
        
        Args:
            document_id: The document ID
            table_spec: Dictionary with table specifications:
                - columns: List of columns to include
                - filters: Dictionary of filters to apply
                - sort_by: Column to sort by
                - sort_order: Sort direction ('asc' or 'desc')
                
        Returns:
            Dictionary with table data
        """
        # Get document content
        document_content = self._get_document_content(document_id)
        if not document_content:
            return {"error": "Document content not found", "success": False}
        
        # First approach: Use AI to extract table data
        try:
            # Create a prompt for the AI to extract table data
            columns_str = ", ".join(table_spec.get('columns', []))
            filters_str = ""
            for k, v in table_spec.get('filters', {}).items():
                filters_str += f"{k} = {v}, "
            
            prompt = f"""Extract a table from the document with these columns: {columns_str}.
{f'Apply these filters: {filters_str}' if filters_str else ''}
Format your response as JSON with an array of objects for rows.
Each object should have these keys: {columns_str}.
Only extract data that is actually present in the document.
If you can't find data for some columns, include only those you can find.

Document content:
{document_content[:10000]}  # Use only first 10K chars to avoid token limits
"""
            
            response = self.ai_service.generate_response(prompt)
            
            # Try to parse AI response as JSON
            try:
                # Find JSON part in the response
                json_match = re.search(r'