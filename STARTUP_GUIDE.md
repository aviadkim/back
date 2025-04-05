# Application Startup Guide

This guide explains how to start the backend application.

## Prerequisites

1.  **Python Dependencies:** Ensure all Python dependencies are installed correctly. If starting fresh or encountering issues, run the following commands in the `back-repo` directory:
    ```bash
    pip install numpy==1.26.4 pandas==1.5.3
    pip install langchain==0.3.21 langchain-community==0.3.20 langchain-openai==0.3.11 boto3
    pip install sentence-transformers
    pip install -r requirements.txt --no-deps
    pip install --upgrade pymongo[srv] certifi
    ```
    *(Note: `requirements.txt` lists `numpy==1.26.4`, which seems more compatible than the version originally in `install_deps.sh`)*

2.  **Environment Variables:** Create or ensure the `back-repo/.env` file exists. It must contain:
    *   Required API keys (e.g., `OPENROUTER_API_KEY`, `GEMINI_API_KEY`).
    *   The correct `MONGODB_URI` for your MongoDB Atlas cluster. Example format (ensure `/admin` or your specific database is included before the options):
        `MONGODB_URI=mongodb+srv://<user>:<password>@<cluster_address>/admin?retryWrites=true&w=majority&appName=<AppName>`

3.  **MongoDB Connection:** The application **requires** a successful connection to MongoDB Atlas. If you encounter SSL handshake errors (`[SSL: TLSV1_ALERT_INTERNAL_ERROR]`), you must resolve them. This typically involves:
    *   Checking/updating system CA certificates.
    *   Ensuring firewalls/network configurations allow outgoing connections to `*.mongodb.net` on port 27017.
    *   Verifying your current IP address is added to the MongoDB Atlas project's IP Access List.

4.  **Frontend Build:** The backend serves a React frontend. Build it by running these commands inside the `back-repo/frontend` directory:
    ```bash
    npm install
    npm run build
    ```
    The build output should be in `back-repo/frontend/build`.

## Running the Backend

1.  Navigate to the `back-repo` directory in your terminal.
2.  Choose **one** of the following application entry points:
    *   **Option A (Structured App):** `python project_organized/app.py`
        *   This uses the more modular structure in the `project_organized` directory.
        *   Likely the intended primary application.
    *   **Option B (Root App):** `python app.py`
        *   A simpler version located in the root directory.
        *   Check if this is the one currently configured to run (e.g., in `Procfile` or deployment scripts if applicable).
3.  The application will start, usually on `http://127.0.0.1:5001` (or a nearby port like 5002-5005 if the default is busy).
4.  Monitor the terminal output for the exact address and check for any startup errors, especially database connection problems.