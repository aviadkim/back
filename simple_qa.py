from simple_pdf_extractor import extract_pdf_text
import os
import sys
import json
import re

class SimpleQA:
    def __init__(self, pdf_path=None, extracted_text=None):
        """Initialize the QA system with either a PDF path or pre-extracted text"""
        self.document = None
        
        if extracted_text:
            self.document = extracted_text
        elif pdf_path:
            self.document = extract_pdf_text(pdf_path)
        
        # Prepare the document text
        if self.document:
            self.all_text = ""
            for page_num, page_data in self.document.items():
                self.all_text += page_data.get("text", "") + "\n\n"
    
    def ask(self, question):
        """Ask a question about the document"""
        if not self.document:
            return "No document loaded"
        
        question = question.lower()
        
        # Answer based on question type
        if re.search(r'how many pages', question):
            return f"The document has {len(self.document)} pages."
            
        elif "isin" in question:
            # Look for ISIN patterns
            isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
            matches = re.findall(isin_pattern, self.all_text)
            if matches:
                return f"I found these potential ISIN numbers: {', '.join(matches)}"
            else:
                return "I couldn't find any ISIN numbers in the document."
                
        elif "table" in question:
            # Simple table detection based on whitespace patterns
            potential_tables = []
            lines = self.all_text.split('\n')
            for i, line in enumerate(lines):
                if i < len(lines) - 3:  # Need at least 3 consecutive lines
                    if len(line.strip()) > 20 and '  ' in line:
                        # Check if next lines have similar spacing
                        if '  ' in lines[i+1] and '  ' in lines[i+2]:
                            # This might be a table
                            table_preview = line[:50] + "..."
                            potential_tables.append(table_preview)
            
            if potential_tables:
                return f"I found {len(potential_tables)} potential tables in the document. Here's a preview of one: {potential_tables[0]}"
            else:
                return "I couldn't detect any obvious tables in the text."
                
        else:
            # Split into paragraphs and find relevant ones
            paragraphs = self.all_text.split('\n\n')
            keywords = [w for w in question.split() if len(w) > 3]
            
            scored_paragraphs = []
            for para in paragraphs:
                if len(para.strip()) < 20:  # Skip short paragraphs
                    continue
                
                score = sum(1 for kw in keywords if kw in para.lower())
                if score > 0:
                    scored_paragraphs.append((para, score))
            
            scored_paragraphs.sort(key=lambda x: x[1], reverse=True)
            
            if scored_paragraphs:
                return f"Based on your question, this might be relevant:\n\n{scored_paragraphs[0][0]}"
            else:
                return "I couldn't find information related to your question."

def main():
    if len(sys.argv) < 3:
        print("Usage: python simple_qa.py <pdf_path> <question>")
        print("Example: python simple_qa.py test_documents/sample.pdf 'How many pages are in the document?'")
        return
    
    pdf_path = sys.argv[1]
    question = sys.argv[2]
    
    # Initialize QA system
    qa_system = SimpleQA(pdf_path=pdf_path)
    
    # Ask question
    print(f"Question: {question}")
    answer = qa_system.ask(question)
    print(f"Answer: {answer}")

if __name__ == "__main__":
    main()
