import os
# Use the specific HuggingFace integration package
from langchain_huggingface import HuggingFaceHub


class Summarizer:
    """
    Service for generating summaries of financial documents.
    Uses a Hugging Face model optimized for summarization.
    """
    def __init__(self):
        """Initializes the Summarizer with a HuggingFaceHub LLM."""
        self.llm = HuggingFaceHub(
            repo_id="facebook/bart-large-cnn",  # Model specified for summarization
            huggingfacehub_api_token=os.environ.get("HUGGINGFACE_API_KEY"),
            task="summarization"  # Specify task for better results
        )

    def generate_summary(self, document, format_type='narrative', max_length=250):
        """
        Generates a summary for a single document.

        Args:
            document (dict): Dictionary representing the document, expected to have 'content' and 'type'.
            format_type (str, optional): The desired format ('narrative', 'bullet-points', 'key-metrics'). Defaults to 'narrative'.
            max_length (int, optional): Approximate maximum length of the summary in words. Defaults to 250.

        Returns:
            dict: A dictionary containing the summary and metadata.
        """
        document_text = document.get('content', '')
        document_type = document.get('type', 'Unknown')
        document_id = document.get('id', 'Unknown')

        if not document_text:
            return {
                "document_id": document_id,
                "document_type": document_type,
                "summary_format": format_type,
                "summary_text": "Error: Document content is empty.",
                "word_count": 4
            }

        # Bart-large-cnn generally works best with just the text to summarize.
        # Adding complex instructions might confuse it. We'll keep it simple.
        # The prompt structure from the spec might be better suited for instruction-tuned models.
        # We also need to consider the model's max input length.
        # LangChain's HuggingFaceHub might handle truncation, but let's be explicit.
        max_input_length = 1024  # Typical limit for BART models
        input_text = document_text[:max_input_length]

        # Adjusting prompt for a summarization model
        prompt = f"Summarize the following financial document text:\n\n{input_text}"

        # Using invoke()
        summary_text = self.llm.invoke(prompt)

        # Post-processing for length (approximate)
        words = summary_text.split()
        if len(words) > max_length:
            summary_text = ' '.join(words[:max_length]) + '...'

        return {
            "document_id": document_id,
            "document_type": document_type,
            "summary_format": format_type,  # Keep track of requested format
            "summary_text": summary_text.strip(),
            "word_count": len(summary_text.strip().split())
        }

    def compare_documents(self, documents):
        """
        Generates a comparative summary for multiple documents.

        Args:
            documents (list): A list of document dictionaries.

        Returns:
            dict: A dictionary containing the comparison summary or an error.
        """
        if not documents or len(documents) < 2:
            return {"error": "At least two valid documents are required for comparison"}

        # Prepare document information for the prompt
        document_info = []
        doc_ids = []
        doc_titles = []
        max_input_length_per_doc = 1500 // len(documents)  # Distribute input budget

        for doc in documents:
            doc_id = doc.get('id', 'Unknown')
            doc_type = doc.get('type', 'Unknown')
            doc_title = doc.get('title', f'Document {doc_id}')
            doc_content = doc.get('content', '')[:max_input_length_per_doc]

            doc_ids.append(doc_id)
            doc_titles.append(doc_title)

            document_info.append(f"""
            --- Document: {doc_title} (ID: {doc_id}, Type: {doc_type}) ---
            Content excerpt:
            {doc_content}
            """)

        # Using a more capable model for comparison might be better, but sticking to spec for now.
        # The prompt needs to guide the summarization model towards comparison.
        prompt = f"""
        Compare and contrast the following financial documents:

        {''.join(document_info)}

        Provide a summary that highlights:
        1. Key similarities between the documents.
        2. Important differences or discrepancies.
        3. Notable trends or patterns across documents (if applicable).
        4. Overall insights from comparing these documents.

        Focus on the most significant financial information.
        """

        # Using invoke()
        comparison_text = self.llm.invoke(prompt)

        return {
            "document_ids": doc_ids,
            "document_titles": doc_titles,
            "comparison_text": comparison_text.strip(),
            "word_count": len(comparison_text.strip().split())
        }


# Singleton pattern for the summarizer service
_summarizer = None


def get_summarizer():
    """
    Returns a singleton instance of the Summarizer.

    Returns:
        Summarizer: The singleton instance.
    """
    global _summarizer
    if _summarizer is None:
        _summarizer = Summarizer()
    return _summarizer