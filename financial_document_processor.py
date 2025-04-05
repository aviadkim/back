from langchain_mistralai import ChatMistralAI
from langchain_community.document_loaders import PyPDFLoader # Updated import
from langchain_text_splitters import RecursiveCharacterTextSplitter # Updated import
from langchain.chains import create_extraction_chain # Keep for now, consider LCEL later
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import numpy as np # Added for sentiment aggregation
from project_organized.features.financial_analysis.sentiment_analyzer import SentimentAnalyzer # Added import
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

        # Initialize Sentiment Analyzer
        try:
            self.sentiment_analyzer = SentimentAnalyzer()
            if not self.sentiment_analyzer.model:
                 print("Warning: Sentiment Analyzer model failed to load. Sentiment analysis will be skipped.")
                 self.sentiment_analyzer = None # Ensure it's None if loading failed
        except Exception as e:
            print(f"Warning: Failed to initialize SentimentAnalyzer: {e}. Sentiment analysis will be skipped.")
            self.sentiment_analyzer = None
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
        instruments = self._extract_financial_instruments(all_text)

        # Analyze overall document sentiment using raw text
        sentiment_result = None
        if self.sentiment_analyzer:
             # Use the raw text from the document before combining with tables
             raw_text_content = "\n".join([page_data['text'] for page_num, page_data in document.items()])
             sentiment_result = self._analyze_document_sentiment(raw_text_content)

        return {
            "instruments": instruments,
            "sentiment": sentiment_result
        }
    
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

    def _analyze_document_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyzes the overall sentiment of the document text chunk by chunk.

        Args:
            text: The raw text content of the document.

        Returns:
            A dictionary with the dominant sentiment label and average score,
            or None if analysis cannot be performed.
            Example: {'dominant_label': 'neutral', 'average_score': 0.65, 'label_distribution': {'positive': 2, 'negative': 1, 'neutral': 5}}
        """
        if not self.sentiment_analyzer or not text:
            return None

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, # Use smaller chunks for sentiment analysis
            chunk_overlap=50
        )
        chunks = text_splitter.split_text(text)

        sentiments = []
        for chunk in chunks:
            result = self.sentiment_analyzer.analyze_sentiment(chunk)
            if result:
                sentiments.append(result)

        if not sentiments:
            return None

        # Aggregate results
        label_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        label_scores = {'positive': [], 'negative': [], 'neutral': []}

        for sentiment in sentiments:
            label = sentiment['label']
            score = sentiment['score']
            if label in label_counts:
                label_counts[label] += 1
                label_scores[label].append(score)

        # Find dominant label
        dominant_label = max(label_counts, key=label_counts.get)

        # Calculate average score for the dominant label
        avg_score = np.mean(label_scores[dominant_label]) if label_scores[dominant_label] else 0.0

        return {
            "dominant_label": dominant_label,
            "average_score": float(avg_score), # Ensure float for JSON serialization
            "label_distribution": label_counts
        }


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
        analysis_results = processor.process_document(sample_pdf)
        instruments = analysis_results.get("instruments", [])
        sentiment = analysis_results.get("sentiment")

        print(f"Extracted {len(instruments)} financial instruments:")
        for instrument in instruments:
             # Ensure attributes exist before printing
             name = getattr(instrument, 'name', 'N/A')
             itype = getattr(instrument, 'type', 'N/A')
             value = getattr(instrument, 'value', 'N/A')
             currency = getattr(instrument, 'currency', 'N/A')
             print(f" - {name} ({itype}): {value} {currency}")

        if sentiment:
            print("\nDocument Sentiment Analysis:")
            print(f"  Dominant Label: {sentiment.get('dominant_label', 'N/A')}")
            print(f"  Average Score: {sentiment.get('average_score', 'N/A'):.4f}")
            print(f"  Label Distribution: {sentiment.get('label_distribution', {})}")
        else:
            print("\nSentiment analysis was skipped or failed.")
    else:
        print(f"Sample PDF not found: {sample_pdf}")
