import os
from langchain_huggingface import HuggingFaceHub
from flask import jsonify  # To return JSON responses

# Import singleton getters from other feature services
# Assuming they are structured correctly and accessible
# Adjust paths if necessary based on project structure/PYTHONPATH
try:
    from features.document_intake.services.document_classifier_service import get_classifier
    from features.summarization.services.summarization_service import get_summarizer
    # Import the new service getter for Phase 2
    from features.data_extraction.services import table_extraction_service
    # Import the new service getter for Phase 3
    from features.financial_insights.services import financial_analysis_service
    # Import the new service getter for Phase 4
    from features.compliance.services import compliance_service
except ImportError:
    # Provide dummy functions if imports fail, to allow basic structure testing
    # This should be resolved with proper project setup/PYTHONPATH
    print("Warning: Failed to import one or more feature services. Using dummy functions.")

    def get_classifier():
        return None

    def get_summarizer():
        return None

    # Dummy for extraction service
    class MockTableService:
        def handle_query(self, message, context):  # Add placeholder handler
            return jsonify({"response": f"Request handled by Mock Extraction Assistant. Message: {message}"})
    table_extraction_service = MockTableService()

    # Dummy for insights service
    class MockInsightsService:
        def handle_query(self, message, context):  # Add placeholder handler
            return jsonify({"response": f"Request handled by Mock Insights Assistant. Message: {message}"})
    financial_analysis_service = MockInsightsService()

    # Dummy for compliance service
    class MockComplianceService:
        def handle_query(self, message, context):  # Add placeholder handler
            return jsonify({"response": f"Request handled by Mock Compliance Assistant. Message: {message}"})
    compliance_service = MockComplianceService()


class RouterService:
    """
    Routes incoming Copilot requests to the appropriate specialized assistant service
    based on LLM classification of the user's message and context.
    """
    def __init__(self):
        """Initializes the RouterService with a HuggingFaceHub LLM for routing."""
        # Using Mistral 7B Instruct as specified for reasoning tasks
        self.routing_llm = HuggingFaceHub(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=os.environ.get("HUGGINGFACE_API_KEY"),
            task="text-generation"
        )
        # Get instances of the services this router will call
        self.classifier_service = get_classifier()
        self.summarizer_service = get_summarizer()
        self.extraction_service = table_extraction_service
        self.insights_service = financial_analysis_service
        # Instantiate the compliance service
        self.compliance_service = compliance_service  # Using the imported (or mock) service

    def determine_assistant_type(self, message, context):
        """
        Uses an LLM to determine the most appropriate assistant type for the request.

        Args:
            message (str): The user's message.
            context (dict): Additional context about the application state (e.g., current document).

        Returns:
            str: The determined assistant type ('intake', 'summarization', 'extraction', 'insights', 'compliance', 'general').
        """
        # Basic context analysis (can be expanded)
        context_summary = "No specific document context."
        if context and context.get('document_id'):
            context_summary = f"User is viewing document {context.get('document_id')}."
            if context.get('stage'):
                context_summary += f" Document stage: {context.get('stage')}."

        # Prompt for the routing LLM - Added 'compliance'
        prompt = f"""
        Determine the primary intent of the user's request and classify it into one of the following categories: 'intake', 'summarization', 'extraction', 'insights', 'compliance', or 'general'.

        'intake': Related to uploading, classifying, validating, or initial processing of documents.
        'summarization': Related to creating summaries of one or more documents, or comparing documents.
        'extraction': Related to extracting tables, specific data points (like numbers, dates, metrics), or calculating metrics from documents.
        'insights': Related to analyzing financial health, comparing performance, identifying trends, assessing risk, or asking complex questions about financial data.
        'compliance': Related to checking compliance, regulations, legal requirements, deadlines, or potential violations in documents.
        'general': Any other request, question, or conversation.

        Context: {context_summary}
        User Request: "{message}"

        Classification (return only one word: intake, summarization, extraction, insights, compliance, or general):
        """

        try:
            # Using invoke()
            result = self.routing_llm.invoke(prompt)
            determined_type = result.strip().lower()

            # Validate the output - Added 'compliance'
            if determined_type in ['intake', 'summarization', 'extraction', 'insights', 'compliance', 'general']:
                return determined_type
            else:
                # Fallback if LLM output is unexpected
                print(f"Warning: Unexpected routing LLM output: {result}. Falling back to 'general'.")
                return 'general'
        except Exception as e:
            print(f"Error during routing LLM call: {e}. Falling back to 'general'.")
            return 'general'

    def route_request(self, message, context):
        """
        Routes the request to the appropriate service based on determined type.

        Args:
            message (str): The user's message.
            context (dict): Additional context.

        Returns:
            Response: A Flask JSON response from the appropriate service or a general response.
        """
        assistant_type = self.determine_assistant_type(message, context)

        print(f"Routing request to: {assistant_type}")  # Logging for debugging

        # Route to the appropriate service handler (using placeholder handlers for now)

        if assistant_type == 'intake':
            if self.classifier_service:
                # Placeholder: Replace with actual call like self.classifier_service.handle_query(message, context)
                return jsonify({"response": f"Request routed to Intake Assistant (handler not fully implemented). Message: {message}"})
            else:
                return jsonify({"error": "Intake service not available"}), 500

        elif assistant_type == 'summarization':
            if self.summarizer_service:
                # Placeholder: Replace with actual call like self.summarizer_service.handle_query(message, context)
                return jsonify({"response": f"Request routed to Summarization Assistant (handler not fully implemented). Message: {message}"})
            else:
                return jsonify({"error": "Summarization service not available"}), 500

        elif assistant_type == 'extraction':
            if self.extraction_service:
                # Placeholder: Replace with actual call like self.extraction_service.handle_query(message, context)
                if hasattr(self.extraction_service, 'handle_query'):
                    return self.extraction_service.handle_query(message, context)
                else:
                    return jsonify({"response": f"Request routed to Extraction Assistant (handler not fully implemented). Message: {message}"})
            else:
                return jsonify({"error": "Extraction service not available"}), 500

        elif assistant_type == 'insights':
            if self.insights_service:
                # Placeholder: Replace with actual call like self.insights_service.handle_query(message, context)
                if hasattr(self.insights_service, 'handle_query'):
                    return self.insights_service.handle_query(message, context)
                else:
                    return jsonify({"response": f"Request routed to Insights Assistant (handler not fully implemented). Message: {message}"})
            else:
                return jsonify({"error": "Insights service not available"}), 500

        elif assistant_type == 'compliance':  # Added handler for compliance
            if self.compliance_service:
                # Placeholder: Replace with actual call like self.compliance_service.handle_query(message, context)
                if hasattr(self.compliance_service, 'handle_query'):
                    return self.compliance_service.handle_query(message, context)
                else:  # Fallback if mock/real service lacks handler
                    return jsonify({"response": f"Request routed to Compliance Assistant (handler not fully implemented). Message: {message}"})
            else:
                return jsonify({"error": "Compliance service not available"}), 500

        else:  # assistant_type == 'general'
            # Handle general queries - maybe use the routing LLM again or a default response
            # For now, a simple default response
            return jsonify({"response": f"This is a general response. You asked: {message}"})


# Singleton pattern for the router service
_router_service = None


def get_router_service():
    """
    Returns a singleton instance of the RouterService.

    Returns:
        RouterService: The singleton instance.
    """
    global _router_service
    if _router_service is None:
        _router_service = RouterService()
    return _router_service