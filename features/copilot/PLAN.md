# CopilotKit Integration Plan

**Goal:** Integrate CopilotKit to provide an in-app AI assistant for interacting with financial documents, using Mistral 7B via Hugging Face and enabling initial actions for table extraction and summarization.

**Plan:**

1.  **Backend - Create Copilot Feature Slice:**
    *   Create the directory structure: `features/copilot/api/`, `features/copilot/services/`, `features/copilot/tests/`.
    *   **`features/copilot/api/copilot_routes.py`**:
        *   Define a Flask Blueprint (`copilot_bp`).
        *   Implement the `/api/copilot/chat` endpoint:
            *   Accepts `message` and `document_id` POST data.
            *   Imports and uses `document_service.get_document_content(document_id)` (from `services/document_service.py`) to fetch context.
            *   Initializes `langchain_huggingface.HuggingFaceHub` with `repo_id="mistralai/Mistral-7B-Instruct-v0.2"` and reads the API key from the `HUGGINGFACE_API_KEY` environment variable.
            *   Constructs a prompt combining the document context and the user's message.
            *   Calls the LLM and returns the generated response in JSON format.
    *   **`app.py`**: Register the `copilot_bp` Blueprint.
    *   **`requirements.txt`**: Add `copilotkit-backend`, `langchain`, `langchain-huggingface`, `huggingface-hub`.

2.  **Backend - Create Action Endpoints:**
    *   To allow the frontend Copilot actions (`extractTables`, `summarizeDocument`) to trigger backend logic, we need corresponding API endpoints.
    *   **`features/copilot/api/copilot_routes.py` (Additions)**:
        *   Implement `/api/copilot/actions/extractTables`:
            *   Accepts `document_id` and `pageNumber`.
            *   Imports and calls the relevant function from `pdf_processor.tables.table_extractor`.
            *   Returns the extracted tables.
        *   Implement `/api/copilot/actions/summarizeDocument`:
            *   Accepts `document_id`.
            *   Imports and calls the relevant function (likely from `services.document_analyzer` or `pdf_processor.analysis.financial_analyzer`).
            *   Returns the summary.

3.  **Frontend - Integrate CopilotKit UI & Core:**
    *   **`frontend/`**: Run `npm install @copilotkit/react-core @copilotkit/react-ui`.
    *   **`frontend/src/App.js` (or `App.jsx`)**:
        *   Import `CopilotProvider`, `CopilotSidebar` from `@copilotkit/react-ui`.
        *   Wrap the main application structure with `<CopilotProvider>`.
        *   Configure `apiUrl="/api/copilot"` (relative path to backend).
        *   Implement `chatApiConfig.sendMessages`:
            *   Fetch from `/api/copilot/chat` (POST).
            *   Send `{ message: lastMessage.content, document_id: currentDocumentId }` (Need to ensure `currentDocumentId` is accessible here).
            *   Format the backend response into the required Copilot message structure.
        *   Add `<CopilotSidebar />` within the provider, likely at the top level of your app layout.
    *   **`frontend/src/components/DocumentViewer.jsx`**:
        *   Import `useCopilotAction` from `@copilotkit/react-core`.
        *   Define the `extractTables` action using `useCopilotAction`:
            *   `name: "extractTables"`
            *   `description: "Extract tables from a specific page of the financial document"`
            *   `parameters`: Define `pageNumber` parameter.
            *   `handler`: Fetch from `/api/copilot/actions/extractTables` (POST), passing `document.id` and `pageNumber`. Return the result.
        *   Define the `summarizeDocument` action using `useCopilotAction`:
            *   `name: "summarizeDocument"`
            *   `description: "Generate a summary of the financial document"`
            *   `handler`: Fetch from `/api/copilot/actions/summarizeDocument` (POST), passing `document.id`. Return the result.

4.  **Environment & Configuration:**
    *   Ensure the `HUGGINGFACE_API_KEY` environment variable is available to the backend process (e.g., via `.env` file, system environment).

5.  **Testing:**
    *   Add basic unit/integration tests for the new backend endpoints in `features/copilot/tests/`.
    *   Perform manual testing:
        *   Open a document.
        *   Use the Copilot chat interface to ask questions about the document.
        *   Trigger the `extractTables` action (e.g., "extract tables from page 3").
        *   Trigger the `summarizeDocument` action (e.g., "summarize this document").

**Visual Overview (Mermaid Diagram):**

```mermaid
graph TD
    subgraph Frontend (React @ /frontend)
        F_App[App.js] -- wraps --> F_ExistingApp[Existing App Components]
        F_App -- contains --> F_Provider[CopilotProvider apiUrl='/api/copilot']
        F_App -- contains --> F_Sidebar[CopilotSidebar]
        F_Provider -- configures --> F_SendMsgFn[sendMessages Function]
        F_Viewer[components/DocumentViewer.jsx] -- uses --> F_ActionExtract[useCopilotAction: extractTables]
        F_Viewer -- uses --> F_ActionSummarize[useCopilotAction: summarizeDocument]

        F_SendMsgFn -- calls --> B_ChatEP[/api/copilot/chat]
        F_ActionExtract -- calls --> B_ExtractEP[/api/copilot/actions/extractTables]
        F_ActionSummarize -- calls --> B_SummarizeEP[/api/copilot/actions/summarizeDocument]
    end

    subgraph Backend (Flask @ /)
        B_App[app.py] -- registers --> B_Routes[features/copilot/api/copilot_routes.py]
        B_Routes -- defines --> B_ChatEP
        B_Routes -- defines --> B_ExtractEP
        B_Routes -- defines --> B_SummarizeEP

        B_ChatEP -- uses --> B_DocService[services/document_service.py]
        B_ChatEP -- uses --> B_LLM[Langchain: HuggingFaceHub Mistral 7B]
        B_ExtractEP -- uses --> B_TableExtractor[pdf_processor/tables/table_extractor.py]
        B_SummarizeEP -- uses --> B_Analyzer[services/document_analyzer.py OR pdf_processor/analysis/financial_analyzer.py]

        B_LLM -- needs --> ENV_Key[HUGGINGFACE_API_KEY]
    end

    User -- interacts --> F_Sidebar