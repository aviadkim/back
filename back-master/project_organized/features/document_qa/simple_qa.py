"""Simple question answering system for documents."""
import re

class SimpleQA:
    """Simple question answering system that provides basic responses"""
    
    def answer(self, question, document_content):
        """Answer a general question about a document
        
        Args:
            question: The question to answer
            document_content: The document content as text
            
        Returns:
            Answer string
        """
        question = question.lower().strip()
        
        # Check for page count questions
        if re.search(r'how many pages|page count', question):
            return self._get_page_count(document_content)
            
        # Check for document type questions
        if re.search(r'what (kind|type) of document|document type', question):
            return self._get_document_type(document_content)
            
        # Check for date questions
        if re.search(r'what date|when|date of', question):
            return self._find_date(document_content)
            
        # Simple full text search
        return self._search_document(question, document_content)
    
    def _get_page_count(self, document_content):
        """Extract page count information from document"""
        # Look for explicit page count in the content
        match = re.search(r'page\s*(\d+)\s*of\s*(\d+)', document_content, re.IGNORECASE)
        if match:
            return f"This document has {match.group(2)} pages."
            
        # Estimate based on document content size
        words = len(document_content.split())
        estimated_pages = max(1, words // 500)  # Rough estimate: ~500 words per page
        return f"This document appears to be approximately {estimated_pages} pages long."
    
    def _get_document_type(self, document_content):
        """Try to determine the document type"""
        content = document_content.lower()
        
        if 'invoice' in content or 'bill' in content:
            return "This appears to be an invoice or bill."
        elif 'report' in content:
            if 'financial' in content:
                return "This appears to be a financial report."
            elif 'annual' in content:
                return "This appears to be an annual report."
            else:
                return "This appears to be some type of report."
        elif 'agreement' in content or 'contract' in content:
            return "This appears to be a contract or agreement."
        elif 'portfolio' in content and ('valuation' in content or 'statement' in content):
            return "This appears to be a portfolio valuation statement."
        else:
            return "I can't determine the exact document type from the content."
    
    def _find_date(self, document_content):
        """Try to find a date in the document"""
        # Look for dates in various formats
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY or DD-MM-YYYY
            r'\d{1,2}\.\d{1,2}\.\d{2,4}',  # MM.DD.YYYY or DD.MM.YYYY
            r'[A-Za-z]{3,9} \d{1,2},? \d{4}',  # Month DD, YYYY
            r'\d{1,2} [A-Za-z]{3,9},? \d{4}'   # DD Month YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, document_content)
            if match:
                return f"I found this date in the document: {match.group(0)}"
                
        return "I couldn't find a clear date in this document."
    
    def _search_document(self, question, document_content):
        """Search for relevant information in the document"""
        # Extract keywords from question
        keywords = self._extract_keywords(question)
        
        # Look for sentences containing keywords
        sentences = re.split(r'(?<=[.!?])\s+', document_content)
        relevant_sentences = []
        
        for sentence in sentences:
            for keyword in keywords:
                if keyword in sentence.lower():
                    relevant_sentences.append(sentence)
                    break
                    
        if relevant_sentences:
            if len(relevant_sentences) > 2:
                return f"I found relevant information: {'. '.join(relevant_sentences[:2])}..."
            else:
                return f"I found relevant information: {'. '.join(relevant_sentences)}"
        else:
            return "I couldn't find specific information related to your question in this document."
    
    def _extract_keywords(self, question):
        """Extract keywords from the question"""
        # Remove common stop words
        stop_words = ['what', 'where', 'when', 'who', 'how', 'is', 'are', 'a', 'an', 'the', 
                     'this', 'that', 'in', 'on', 'at', 'to', 'for', 'with', 'about', 'document']
        
        words = question.lower().split()
        return [word for word in words if word not in stop_words and len(word) > 3]
