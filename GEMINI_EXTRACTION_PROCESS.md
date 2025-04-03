# Gemini Financial Data Extraction Process

This document outlines the successful process used to extract structured financial instrument data from PDF documents using Google Gemini, as implemented in `gemini_financial_processor.py`.

## 1. PDF Text Extraction

*   **Library:** PyMuPDF (`fitz`) is used for robust text extraction from PDF files.
*   **Process:**
    *   The PDF is opened using `fitz.open(pdf_path)`.
    *   The script iterates through each `page` in `doc.pages()`.
    *   For each page, `page.get_text("text")` is called to extract plain text content.
    *   Error handling is included for potential issues during page processing or decryption (though basic password handling might need enhancement for complex cases).
    *   Extracted text from all pages is combined into a single string, separated by page markers (`--- PAGE X TEXT ---`).

## 2. Structured Data Extraction with Gemini

*   **Model:** Google Gemini (`gemini-1.5-flash` or a similar capable model) is used for its ability to understand context and return structured JSON.
*   **API Key:** The Gemini API key is configured using `genai.configure(api_key=...)`, fetched from `config.py` / `.env`.
*   **Prompting:**
    *   A detailed prompt instructs Gemini to analyze the combined text.
    *   The prompt specifies the exact desired JSON output format: a list of objects, each containing fields like `isin`, `name`, `type`, `value`, `currency`, and `percentage_in_portfolio`.
    *   It explicitly requests *only* the JSON list as output, without introductory text or markdown formatting.
    *   The input text is truncated (e.g., `text[:30000]`) to stay within potential API limits, although this limit might need adjustment based on the specific Gemini model used.
*   **API Call:**
    *   The `generate_content` method of the Gemini model is called.
    *   Crucially, `generation_config` is set with `response_mime_type="application/json"` to ensure Gemini returns clean JSON.
*   **Response Handling:**
    *   The response text is parsed using `json.loads()`.
    *   Error handling checks for blocked prompts, unexpected finish reasons, empty responses, and JSON decoding errors.
    *   The parsed JSON list is validated against the Pydantic `FinancialInstrument` model to ensure data integrity. Items failing validation are logged and skipped.

## 3. Key Success Factors

*   **PyMuPDF:** Provides more reliable text extraction from various PDF structures compared to some other libraries.
*   **Gemini Model:** Capable of understanding the financial context and extracting the requested fields accurately.
*   **Clear Prompting:** Explicitly defining the desired JSON structure and requesting *only* JSON output.
*   **`response_mime_type="application/json"`:** This configuration significantly improves the reliability of getting clean JSON output directly from the API.
*   **Pydantic Validation:** Ensures the extracted data conforms to the expected schema before further processing or storage.