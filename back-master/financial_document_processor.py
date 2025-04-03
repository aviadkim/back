from langchain_mistralai import ChatMistralAI
from langchain_community.document_loaders import PyPDFLoader # Updated import
from langchain_text_splitters import RecursiveCharacterTextSplitter # Updated import
from langchain.chains import create_extraction_chain # Keep for now, consider LCEL later
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional
import os

class FinancialInstrument(BaseModel):
    """מודל נתונים למכשיר פיננסי שחולץ ממסמך."""
    isin: str = Field(description="ISIN code of the financial instrument")
    name: str = Field(description="Name of the financial instrument")
    type: Optional[str] = Field(description="Instrument type (stock, bond, ETF, etc.)")
    value: Optional[float] = Field(description="Current value of the instrument")
    currency: Optional[str] = Field(description="Currency of the instrument")
    percentage_in_portfolio: Optional[float] = Field(description="Percentage value in portfolio")

class FinancialDocumentProcessor:
    """מעבד מסמכים פיננסיים באמצעות LangChain ו-Mistral AI."""
    
    def __init__(self, mistral_api_key=None):
        self.mistral_api_key = mistral_api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.mistral_api_key:
            raise ValueError("Mistral API key is required. Pass it directly or set MISTRAL_API_KEY environment variable.")
            
        self.llm = ChatMistralAI(
            model="mistral-small",  # Free tier model
            mistral_api_key=self.mistral_api_key
        )
        
    def process_document(self, pdf_path):
        """עיבוד מסמך PDF והוצאת מידע פיננסי מובנה."""
        # Load document using your existing PDF extractor
        from pdf_processor.extraction.text_extractor import PDFTextExtractor
        extractor = PDFTextExtractor()
        document = extractor.extract_document(pdf_path)
        
        # Extract tables using your existing table extractor
        from pdf_processor.tables.table_extractor import TableExtractor
        table_extractor = TableExtractor()
        tables = table_extractor.extract_tables(pdf_path)
        
        # Combine document text and tables into a single context
        all_text = self._combine_document_and_tables(document, tables)
        
        # Process with LLM to extract structured financial data
        results = self._extract_financial_instruments(all_text)
        
        return results
    
    def _combine_document_and_tables(self, document, tables):
        """שילוב טקסט המסמך והטבלאות לפורמט אחיד."""
        content = []
        
        # Add full document text with page numbers
        for page_num, page_data in document.items():
            content.append(f"--- PAGE {page_num+1} TEXT ---\n{page_data['text']}\n")
        
        # Add tables with structure preserved
        for page_num, page_tables in tables.items():
            for i, table in enumerate(page_tables):
                content.append(f"--- PAGE {page_num+1} TABLE {i+1} ---\n")
                for row in table.get("data", []):
                    content.append(" | ".join(str(cell) for cell in row))
        
        return "\n".join(content)
    
    def _extract_financial_instruments(self, text):
        """חילוץ מכשירים פיננסיים מטקסט המסמך באמצעות מודל שפה גדול."""
        # Split the text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(text)
        
        # Create extraction chain
        extraction_chain = create_extraction_chain(FinancialInstrument, self.llm)
        
        # Process each chunk
        all_instruments = []
        for chunk in chunks:
            # Add special instructions for Hebrew content if needed
            prompt = (
                "Extract all financial instruments from this document chunk. "
                "Pay special attention to ISIN codes, which are 12-character alphanumeric identifiers. "
                "The document may contain text in Hebrew and English.\n\n"
                f"{chunk}"
            )
            
            result = extraction_chain.run(prompt)
            all_instruments.extend(result)
        
        # Remove duplicates based on ISIN
        unique_instruments = {}
        for instrument in all_instruments:
            if instrument.isin not in unique_instruments:
                unique_instruments[instrument.isin] = instrument
        
        return list(unique_instruments.values())


# Example usage
if __name__ == "__main__":
    # This code will run only if the script is executed directly
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    processor = FinancialDocumentProcessor()
    
    # Test with a sample PDF
    sample_pdf = "path/to/sample.pdf"
    if os.path.exists(sample_pdf):
        results = processor.process_document(sample_pdf)
        print(f"Extracted {len(results)} financial instruments:")
        for instrument in results:
            print(f" - {instrument.name} ({instrument.type}): {instrument.value} {instrument.currency}")
    else:
        print(f"Sample PDF not found: {sample_pdf}")
