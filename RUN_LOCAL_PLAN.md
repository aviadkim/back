# How to Run the Financial Document Processor Locally

This plan outlines the steps to set up and run the application on your local machine.

## Prerequisites

1.  **MongoDB:** Ensure a MongoDB server instance is installed and running.
2.  **Redis:** Ensure a Redis server instance is installed and running (on the default port 6379).
3.  **Python & Pip:** A working Python environment with `pip`.
4.  **Node.js & npm:** A working Node.js environment with `npm`.
5.  **Git:** Git must be installed to have cloned the repository.

## Setup Steps

**Note:** All commands should be run from the `back-repo` directory (`c:/Users/Aviad/Desktop/back/back-repo`) unless otherwise specified.

1.  **Configure Environment Variables:**
    *   Run the setup script. It will prompt you for your OpenRouter API key:
        ```bash
        ./setup_env.sh
        ```
    *   **Important:** Manually edit the `.env` file created by the script. Find the `MONGODB_URI` line and replace the placeholder value with the correct connection string for your local or remote MongoDB instance (e.g., `MONGODB_URI=mongodb://localhost:27017/findoc_db`). Add any other necessary API keys (Paddle, Mistral, etc.) if required for the features you intend to use.

2.  **Create Required Directories:**
    ```bash
    mkdir uploads extractions financial_data
    ```

3.  **Install Dependencies:**
    *   Install Python dependencies:
        ```bash
        ./install_deps.sh
        ```
    *   Install Node.js dependencies:
        ```bash
        npm install
        ```

4.  **Build Frontend (Real Build):**
    *   Navigate into the frontend directory:
        ```bash
        cd frontend
        ```
    *   Run the build command:
        ```bash
        npm run build
        ```
    *   Return to the `back-repo` directory:
        ```bash
        cd ..
        ```
    *   *(This assumes the frontend source code is located in `back-repo/frontend/src` and the `package.json` in `back-repo/frontend` is configured correctly for a React build).*

5.  **Start Celery Worker:**
    *   Open a **new, separate terminal window**.
    *   Navigate to the `back-repo` directory:
        ```bash
        cd c:/Users/Aviad/Desktop/back/back-repo
        ```
    *   Start the worker:
        ```bash
        celery -A celery_worker.celery_app worker --loglevel=info
        ```
    *   Keep this terminal open; it runs the background task processor.

6.  **Start Backend Server:**
    *   In your **original terminal window**.
    *   Navigate to the application code directory:
        ```bash
        cd project_organized
        ```
    *   Run the Flask application:
        ```bash
        python app.py
        ```
    *   The server should now be running, likely accessible at `http://localhost:5000` (or the port specified by the `PORT` environment variable, if set).

## Diagram of Running Components

```mermaid
graph TD
    subgraph Terminal 1 (Backend)
        A[cd back-repo/project_organized] --> B(python app.py);
    end

    subgraph Terminal 2 (Celery)
        C[cd back-repo] --> D(celery -A celery_worker.celery_app worker);
    end

    subgraph Background Services
        E(MongoDB Server);
        F(Redis Server);
    end

    B -- Connects to --> E;
    B -- Connects to --> F;
    D -- Connects to --> F;

    G(User Browser) -- HTTP Request --> B;