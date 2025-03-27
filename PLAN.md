# Project Stabilization and Enhancement Plan

This plan outlines the steps taken and the proposed path forward for stabilizing the financial document analysis application and preparing it for future enhancements.

**Architectural Decision:** We will proceed with the current **hybrid architecture** for now, prioritizing environment fixes and core feature delivery over immediate large-scale refactoring towards a pure Vertical Slice model.

## Phase 1: Stabilization & Configuration (Completed)

*   **Dependencies:**
    *   Pinned versions in `requirements.txt`.
    *   Added necessary development/testing tools (`flake8`, `black`, `pytest`, `safety`).
    *   Added core functionality dependencies (`sentence-transformers`, `torch`).
    *   Resolved dependency conflicts.
*   **Deployment:**
    *   Reviewed and updated Elastic Beanstalk configuration (`.ebextensions/`, `Dockerfile`, `.github/workflows/`) to use Docker, MongoDB, and fetch secrets from SSM.
*   **Persistence:**
    *   Implemented MongoDB persistence for chat history (`shared/database.py`).
    *   Refactored chat routes (`routes/langchain_routes.py`) to use database persistence.
    *   Confirmed document/embedding persistence in `MemoryAgent`.
*   **Refactoring:**
    *   Updated `utils/pdf_processor.py` to use `pypdf`.
    *   Fixed Langchain v0.1.x compatibility issues in `agent_framework/coordinator.py` (specifically `get_openai_callback` usage).
*   **Linting:**
    *   Ran `black` formatter on `agent_framework`.
    *   Fixed critical `flake8` errors.
    *   Configured `.flake8` to ignore less critical stylistic issues (E501, W503, W291) for now.
*   **Security:**
    *   Updated vulnerable packages based on `safety` report.
    *   Created `.safety.yml` policy file to ignore remaining, reviewed vulnerabilities.
*   **LLM Config:**
    *   Reviewed and confirmed LLM selection logic in `AgentCoordinator`.

## Phase 2: Testing & Verification (Currently Blocked)

*   **Blocker Resolution (Requires External Action):** The following environment issues must be resolved before testing can proceed effectively:
    1.  **PyTorch `OSError`:** The installed PyTorch CPU wheels are incompatible with the Codespace environment's C library, preventing imports. Needs investigation to find a compatible wheel/version or fix the environment.
    2.  **Docker Not Found:** The `docker` and `docker compose` commands are unavailable, preventing the local MongoDB service (needed for tests) from starting. Docker needs to be installed/configured correctly in the environment.
*   **Testing (Post-Blocker):** Once the environment is fixed:
    1.  Run the initial PDF processor test (`tests/test_pdf_processor.py`).
    2.  Write and run comprehensive tests for:
        *   `utils/pdf_processor.py` (including OCR fallback with appropriate sample files).
        *   Database interactions in `shared/database.py` (chat history, document storage).
        *   `agent_framework/memory_agent.py` (add/forget documents, context retrieval via vector search).
        *   `agent_framework/coordinator.py` (mocking LLM calls, testing logic flow).
        *   Service layers and background tasks (if applicable, structure needs review).
        *   Chatbot conversational flows (`routes/langchain_routes.py`).
    3.  Run tests with coverage (`pytest --cov`) and analyze the report to improve test coverage.
    4.  Re-enable and ensure `quick_check.sh` (including `flake8` and `safety`) passes cleanly.

## Phase 3: Enhancements (Future)

*   **LLM Refinement:** Further refine system prompts and potentially explore LCEL instead of `LLMChain` in `AgentCoordinator`.
*   **Advanced Features:** Implement features like document comparison, enhanced table generation, Excel export, UI improvements, etc.
*   **Architecture Documentation:** Update `docs/vertical_slice_architecture.md` to accurately reflect the hybrid approach being used, or revisit refactoring later.

## Diagram

```mermaid
graph TD
    subgraph Phase 1 (Done)
        A[Stabilization, Config, Persistence, Security]
    end
    subgraph Phase 2 (Blocked)
        B(Fix Environment: PyTorch & Docker) -- External Action --> C{Testing & Verification};
        C --> D[Verify Vector Search];
        C --> E[Write/Run Tests];
    end
    subgraph Phase 3 (Future)
        F[Refine LLM/Prompts] --> G[Advanced Features];
        G --> H[Update Arch Docs];
    end
    A --> B;
    E --> F;