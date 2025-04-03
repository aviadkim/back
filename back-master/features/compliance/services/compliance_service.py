import os
from langchain_huggingface import HuggingFaceHub

# Placeholder import - adjust based on actual project structure
try:
    from services import document_service  # Assuming a global/shared document service
except ImportError:
    print("Warning: document_service not found at services.document_service. Using placeholder.")

    class MockDocumentService:
        _mock_docs = {
            "doc1": {"id": "doc1", "content": "Document 1 content mentioning SEC filing deadline.", "type": "Financial Report"},
            "doc2": {"id": "doc2", "content": "Document 2 content with GDPR reference.", "type": "Policy"},
        }

        def get_document(self, document_id):
            print(f"Warning: Using mock document_service.get_document for ID: {document_id}")
            return self._mock_docs.get(document_id)

    document_service = MockDocumentService()


class ComplianceChecker:
    """
    Service for checking compliance issues and identifying regulatory requirements
    in financial documents using an LLM.
    """
    def __init__(self):
        """Initializes the ComplianceChecker with a HuggingFaceHub LLM."""
        # Use a model with strong understanding of legal/regulatory language
        self.llm = HuggingFaceHub(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=os.environ.get("HUGGINGFACE_API_KEY"),
            task="text-generation"
        )

    def check_compliance(self, document, jurisdictions):
        """
        Analyzes a document for compliance issues against specified jurisdictions.

        Args:
            document (dict): The document data (expected 'id', 'content', 'type').
            jurisdictions (list): A list of jurisdiction strings (e.g., ['US', 'EU']).

        Returns:
            dict: A dictionary containing the compliance analysis results.
        """
        document_text = document.get('content', '')
        document_type = document.get('type', 'Unknown')
        document_id = document.get('id', 'Unknown')

        if not document_text:
            return {"error": f"Document {document_id} content is empty."}

        # Generate compliance check prompt based on jurisdictions
        jurisdiction_prompts = [f"- {j.strip()}" for j in jurisdictions if j and j.strip()]
        jurisdictions_text = "\n".join(jurisdiction_prompts) if jurisdiction_prompts else "- Default jurisdiction (interpret broadly)"

        prompt = f"""
        Analyze the following {document_type} document for compliance with financial regulations
        in these jurisdictions:
        {jurisdictions_text}

        Document content excerpt (first 3000 chars):
        {document_text[:3000]}

        Identify any potential compliance issues, missing required disclosures,
        or regulatory requirements that may apply to this document based on the specified jurisdictions.

        Format your response with clear sections using markdown headers:
        ### Potential Compliance Issues
        [List issues found or state 'None identified']
        ### Missing Required Elements
        [List missing elements or state 'None identified']
        ### Applicable Regulatory Requirements
        [List requirements identified or state 'None identified']
        ### Recommendations
        [Provide actionable recommendations or state 'None']
        """

        try:
            analysis = self.llm.invoke(prompt)
        except Exception as e:
            print(f"Error during LLM compliance check for doc {document_id}: {e}")
            analysis = "Error generating LLM compliance analysis."

        return {
            "document_id": document_id,
            "document_type": document_type,
            "jurisdictions": jurisdictions,
            "compliance_analysis": analysis.strip(),
            "compliance_score": self._calculate_compliance_score(analysis)  # Score based on LLM output
        }

    def identify_requirements(self, document):
        """
        Identifies specific regulatory requirements mentioned within the document text.

        Args:
            document (dict): The document data (expected 'id', 'content', 'type').

        Returns:
            dict: A dictionary containing extracted requirements.
        """
        document_text = document.get('content', '')
        document_type = document.get('type', 'Unknown')
        document_id = document.get('id', 'Unknown')

        if not document_text:
            return {"error": f"Document {document_id} content is empty."}

        prompt = f"""
        Review the following {document_type} document and identify all specific regulatory requirements,
        deadlines, filing obligations, or compliance-related statements mentioned within the text.

        Document content excerpt (first 3000 chars):
        {document_text[:3000]}

        Extract each requirement clearly. If possible, include:
        - The requirement description
        - Relevant deadline (if mentioned)
        - Authority or regulator mentioned (if any)

        Format the output as a bulleted list. If no specific requirements are found, state 'No specific requirements identified'.
        """

        try:
            extraction = self.llm.invoke(prompt)
        except Exception as e:
            print(f"Error during LLM requirement identification for doc {document_id}: {e}")
            extraction = "Error generating LLM requirement extraction."

        # Enhanced parsing logic for better requirement extraction
        requirements = []
        extraction_lines = extraction.strip().split('\n')
        for line in extraction_lines:
            line = line.strip()
            # Skip empty lines and headers
            if not line or line.startswith('#') or line.lower().startswith('no specific'):
                continue
            
            # Clean bullet points and numbering
            if line.startswith(('-', '*', '•')) or (len(line) > 2 and line[0].isdigit() and line[1] in ['.', ')']):
                line = line[2:].strip()
            
            if line:  # Only add non-empty lines
                requirements.append(line)

        return {
            "document_id": document_id,
            "document_type": document_type,
            "extracted_requirements_text": extraction.strip(),  # Raw LLM output
            "extracted_requirements_list": requirements,  # Enhanced parsed list
            "requirement_count": len(requirements) if requirements else self._count_requirements_fallback(extraction)
        }

    def _calculate_compliance_score(self, analysis):
        """
        Calculates a simple heuristic score based on keywords in the analysis text.
        """
        lower_analysis = analysis.lower()
        score = 70  # Start neutral-positive

        # Penalties
        negative_terms = ["violation", "non-compliance", "missing required", "failure", "inadequate", "risk identified"]
        negative_count = sum(lower_analysis.count(term) for term in negative_terms)
        score -= negative_count * 10

        # Bonuses
        positive_terms = ["compliant", "meets requirements", "properly disclosed", "no issues identified"]
        positive_count = sum(lower_analysis.count(term) for term in positive_terms)
        score += positive_count * 5

        return max(0, min(100, score))  # Clamp score between 0 and 100

    def _count_requirements_fallback(self, extraction):
        """
        Fallback heuristic to count requirements if list parsing fails.
        Counts lines that seem like list items.
        """
        lines = extraction.strip().split('\n')
        count = 0
        for line in lines:
            line = line.strip()
            # Check if line looks like a list item (starts with bullet/number or is non-empty after stripping)
            if line and (line.startswith(('-', '*')) or (len(line) > 3 and line[0].isdigit() and line[1] == '.')):
                count += 1
        # Avoid zero count if there's text but no list items detected
        return max(1, count) if extraction and not extraction.lower().startswith('no specific') else 0


# Singleton instance
_checker = None


def get_checker():
    """
    Returns a singleton instance of the ComplianceChecker.

    Returns:
        ComplianceChecker: The singleton instance.
    """
    global _checker
    if _checker is None:
        _checker = ComplianceChecker()
    return _checker
