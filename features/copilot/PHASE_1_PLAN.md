# CopilotKit Specialized Assistants - Phase 1 Plan

**Goal:** Implement Phase 1 of the specialized AI assistant system, including the Document Intake and Document Summarization assistants, the LLM-based backend router, and the basic frontend hub structure. This phase lays the foundation for replacing parts of the `agent_framework` (specifically coordination and some NLP tasks).

**Phase 1 Plan:**

1.  **Backend - Setup Feature Slices:**
    *   Create directory structures:
        *   `features/document_intake/api/`, `features/document_intake/services/`, `features/document_intake/tests/`
        *   `features/summarization/api/`, `features/summarization/services/`, `features/summarization/tests/`
        *   `features/copilot_router/api/`, `features/copilot_router/services/`, `features/copilot_router/tests/`

2.  **Backend - Implement Services:**
    *   **`features/document_intake/services/document_classifier_service.py`**: Implement `DocumentClassifier` class using `HuggingFaceHub` with `repo_id="facebook/bart-large-mnli"` (as per spec code) for `classify` and `validate_document` methods. Include `get_classifier()` function.
    *   **`features/summarization/services/summarization_service.py`**: Implement `Summarizer` class using `HuggingFaceHub` with `repo_id="facebook/bart-large-cnn"` (as per spec code) for `generate_summary` and `compare_documents` methods. Include `get_summarizer()` function.
    *   **`features/copilot_router/services/router_service.py`**: Implement a `RouterService` class.
        *   Include a method `determine_assistant_type(message, context)` that uses an LLM (e.g., `HuggingFaceHub` with `mistralai/Mistral-7B-Instruct-v0.2`) to classify the request and return 'intake', 'summarization', or 'general'.
        *   Include a method `route_request(message, context)` that calls `determine_assistant_type` and then forwards the request data to the appropriate service (Intake or Summarization for Phase 1) or handles it generally.

3.  **Backend - Implement API Routes:**
    *   **`features/document_intake/api/intake_routes.py`**: Define `intake_routes` Blueprint with `/api/documents/classify` (POST) and `/api/documents/<document_id>/validate` (GET) endpoints, calling the `document_classifier_service`.
    *   **`features/summarization/api/summarization_routes.py`**: Define `summarization_routes` Blueprint with `/api/documents/<document_id>/summary` (GET) and `/api/documents/compare-summary` (GET) endpoints, calling the `summarization_service`.
    *   **`features/copilot_router/api/router_routes.py`**: Define `router_routes` Blueprint with `/api/copilot/route` (POST) endpoint, calling the `router_service.route_request` method. This will be the main entry point for CopilotKit frontend calls.

4.  **Backend - Register Blueprints & Dependencies:**
    *   **`app.py`**: Import and register the `intake_routes`, `summarization_routes`, and `router_routes` Blueprints.
    *   **`requirements.txt`**: Add/ensure `copilotkit-backend`, `langchain`, `langchain-huggingface`, `huggingface-hub`, `transformers`, `flask`.

5.  **Frontend - Setup Components:**
    *   Create corresponding directories if they don't exist (e.g., `frontend/src/features/document_intake/components/`).
    *   **`frontend/src/features/document_intake/components/DocumentUploadAssistant.jsx`**: Implement based on the specification, defining `classifyDocument` and `validateDocument` actions using `useCopilotAction`. Ensure it includes `<CopilotChatbox />`.
    *   **`frontend/src/features/summarization/components/SummarizationAssistant.jsx`**: Implement based on the specification, defining `generateExecutiveSummary` and `compareDocuments` actions using `useCopilotAction`. Ensure it includes `<CopilotChatbox />`.
    *   **`frontend/src/components/FinancialDocumentAssistantHub.jsx`**: Implement a basic version for Phase 1. It should:
        *   Include state for `activeAssistant` (defaulting to 'intake').
        *   Conditionally render `DocumentUploadAssistant` or `SummarizationAssistant` based on `activeAssistant`.
        *   Include a basic `AssistantSelector` component.
        *   Include a placeholder `DocumentContextPanel`.
    *   **`frontend/src/components/AssistantSelector.jsx`**: Simple component to switch between 'intake' and 'summarization' for Phase 1.
    *   **`frontend/src/components/DocumentContextPanel.jsx`**: Placeholder component for now.

6.  **Frontend - Integrate Hub & CopilotKit:**
    *   **`frontend/`**: Run `npm install @copilotkit/react-core @copilotkit/react-ui`.
    *   **`frontend/src/App.jsx` (or `App.js`)**:
        *   Import `CopilotProvider`.
        *   Wrap the main application structure (or the part where the assistant should live) with `<CopilotProvider>`.
        *   Configure `apiUrl="/api/copilot/route"` (pointing to the new router endpoint).
        *   Implement `chatApiConfig.sendMessages` to POST to `/api/copilot/route`, sending the message and any relevant context.
        *   Render the `<FinancialDocumentAssistantHub />`.

7.  **Agent Framework Replacement Strategy:**
    *   This plan focuses on building the new Intake and Summarization assistants and the router.
    *   The actual *replacement* of `agent_framework/coordinator.py` and relevant parts of `agent_framework/nlp_agent.py` will be handled carefully. Initially, the new system will operate alongside the old one.
    *   A subsequent step/plan will involve analyzing dependencies and refactoring the code to fully transition away from the replaced agent framework components once the new assistants are tested and stable.

8.  **Configuration:**
    *   Ensure the `HUGGINGFACE_API_KEY` environment variable is accessible to the backend services.

9.  **Testing (Phase 1):**
    *   Unit tests for backend services (classification, summarization, routing logic).
    *   Integration tests for API endpoints.
    *   Manual frontend testing:
        *   Verify the Hub UI and assistant switching.
        *   Test Intake assistant actions (`classifyDocument`, `validateDocument`) via its chatbox.
        *   Test Summarization assistant actions (`generateExecutiveSummary`, `compareDocuments`) via its chatbox.
        *   Test the router by sending messages intended for different assistants to `/api/copilot/route`.

**Visual Overview (Phase 1 - Simplified):**

```mermaid
graph TD
    subgraph Frontend (React @ /frontend)
        F_App[App.jsx] -- wraps --> F_Hub[FinancialDocumentAssistantHub]
        F_App -- contains --> F_Provider[CopilotProvider apiUrl='/api/copilot/route']
        F_Hub -- contains --> F_Selector[AssistantSelector]
        F_Hub -- renders --> F_Intake[DocumentUploadAssistant]
        F_Hub -- renders --> F_Summarize[SummarizationAssistant]
        F_Intake -- uses --> F_IntakeChat[CopilotChatbox]
        F_Summarize -- uses --> F_SummarizeChat[CopilotChatbox]

        F_Provider -- configures --> F_SendMsgFn[sendMessages Function]
        F_Intake -- defines --> F_ActionClassify[useCopilotAction: classifyDocument]
        F_Intake -- defines --> F_ActionValidate[useCopilotAction: validateDocument]
        F_Summarize -- defines --> F_ActionGenSum[useCopilotAction: generateExecutiveSummary]
        F_Summarize -- defines --> F_ActionCompSum[useCopilotAction: compareDocuments]

        F_SendMsgFn -- calls --> B_RouterEP[/api/copilot/route]
        F_ActionClassify -- calls --> B_ClassifyEP[/api/documents/classify]
        F_ActionValidate -- calls --> B_ValidateEP[/api/documents/.../validate]
        F_ActionGenSum -- calls --> B_GenSumEP[/api/documents/.../summary]
        F_ActionCompSum -- calls --> B_CompSumEP[/api/documents/compare-summary]
    end

    subgraph Backend (Flask @ /)
        B_App[app.py] -- registers --> B_IntakeRoutes[features/document_intake/api/intake_routes.py]
        B_App -- registers --> B_SummarizeRoutes[features/summarization/api/summarization_routes.py]
        B_App -- registers --> B_RouterRoutes[features/copilot_router/api/router_routes.py]

        B_RouterRoutes -- defines --> B_RouterEP
        B_IntakeRoutes -- defines --> B_ClassifyEP & B_ValidateEP
        B_SummarizeRoutes -- defines --> B_GenSumEP & B_CompSumEP

        B_RouterEP -- uses --> B_RouterService[features/copilot_router/services/router_service.py]
        B_RouterService -- uses --> B_RouterLLM[LLM: Mistral 7B]
        B_RouterService -- routes to --> B_IntakeService[features/document_intake/services/document_classifier_service.py]
        B_RouterService -- routes to --> B_SummarizeService[features/summarization/services/summarization_service.py]

        B_IntakeService -- uses --> B_IntakeLLM[LLM: BART-MNLI]
        B_SummarizeService -- uses --> B_SummarizeLLM[LLM: BART-CNN]

        B_IntakeLLM & B_SummarizeLLM & B_RouterLLM -- needs --> ENV_Key[HUGGINGFACE_API_KEY]
    end

    User -- interacts --> F_Hub