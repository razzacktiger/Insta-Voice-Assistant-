# Insta-Voice-Assistant-

Here I use various technologies to create a customer voice assistant assisted with tools.

---

## Full Project Setup Guide

This guide explains how to set up and run the entire Insta-Voice-Assistant project, including the frontend, backend services (token generation and LiveKit agent), Supabase database, and how to run tests.

### 1. Prerequisites

- **Git:** For cloning the repository.
- **Python:** Version 3.10 or higher (project uses 3.11 recommended).
- **Node.js and npm/yarn:** For the frontend (e.g., Node.js >= 18, check `frontend/frontend/package.json` for specifics).
- **Firebase Project:**
  - A Firebase project is required.
  - Enable **Firebase Authentication** (e.g., Email/Password and/or Google Sign-In).
  - Download your **Service Account Key JSON file** (Firebase Console > Project Settings > Service Accounts > Generate new private key).
- **Supabase Project:**
  - A Supabase project is required.
  - Note your Supabase Project URL and `service_role` key (or `anon` key depending on `db_driver.py` needs, but `service_role` is common for backend admin tasks like KB population).
- **LiveKit Account/Server:**
  - A LiveKit Cloud account (e.g., `wss://your-project.livekit.cloud`) or a self-hosted LiveKit server.
  - You\'ll need your LiveKit API Key and API Secret.
- **OpenAI Account:**
  - An OpenAI API Key is needed for STT, LLM, TTS, and embedding generation.

### 2. Initial Clone & Environment Configuration

1.  **Clone the Repository:**

    ```bash
    git clone <your-repository-url>
    cd Insta-Voice-Assistant-
    ```

2.  **Backend Environment Variables (`backend/.env`):**

    - Navigate to the `backend/` directory.
    - Create a file named `.env` (you can copy `backend/.env.example` if it exists).
    - Add the following, replacing placeholders with your actual credentials:

      ```env
      # Firebase Admin SDK (absolute or relative path from backend/ to your downloaded JSON key)
      FIREBASE_ADMIN_SDK_CREDENTIALS_PATH="path/to/your/firebase-service-account-key.json"

      # LiveKit Credentials & URL
      LIVEKIT_API_KEY="YOUR_LIVEKIT_API_KEY"
      LIVEKIT_API_SECRET="YOUR_LIVEKIT_API_SECRET"
      LIVEKIT_URL="wss://your-livekit-server-url.livekit.cloud"

      # OpenAI API Key
      OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

      # Supabase Credentials
      SUPABASE_URL="YOUR_SUPABASE_PROJECT_URL" # e.g., https://xyz.supabase.co
      SUPABASE_KEY="YOUR_SUPABASE_SERVICE_ROLE_KEY" # For admin tasks like KB population
      ```

    - **Important:**
      - Ensure `FIREBASE_ADMIN_SDK_CREDENTIALS_PATH` points correctly to your Firebase service account JSON file.
      - Add the service account JSON file itself (e.g., `firebase-service-account-key.json`) to your main `.gitignore` file to prevent committing it.

3.  **Frontend Environment Variables (`frontend /frontend/.env`):**

    - Navigate to the `frontend /frontend/` directory.
    - Create a file named `.env` (or `.env.local` depending on your frontend framework, e.g., Vite uses `.env`).
    - Add your Firebase web app configuration (from Firebase Console > Project Settings > Your apps > Web app > SDK setup & config):

      ```env
      # Example for Vite (React) - adjust prefixes if needed for other frameworks
      VITE_FIREBASE_API_KEY="YOUR_FIREBASE_WEB_API_KEY"
      VITE_FIREBASE_AUTH_DOMAIN="YOUR_PROJECT_ID.firebaseapp.com"
      VITE_FIREBASE_PROJECT_ID="YOUR_PROJECT_ID"
      VITE_FIREBASE_STORAGE_BUCKET="YOUR_PROJECT_ID.appspot.com"
      VITE_FIREBASE_MESSAGING_SENDER_ID="YOUR_MESSAGING_SENDER_ID"
      VITE_FIREBASE_APP_ID="YOUR_WEB_APP_ID"

      # URL for the backend token service
      VITE_TOKEN_SERVICE_URL="http://localhost:8000" # Or whatever port you run token_service on
      ```

### 3. Supabase Database Setup

1.  **Log in to your Supabase project dashboard.**
2.  **SQL Editor Navigation:**
    - Navigate to the "SQL Editor" section from the sidebar.
3.  **Run SQL Scripts:**
    - Click "+ New query" for each script.
    - Open the SQL files located in the `database_setup/` directory of this project.
    - **Execute them in the following order:**
      1.  `01_extensions.sql` (This likely enables `pgvector` and any other required PostgreSQL extensions).
      2.  `02_tables.sql` (This should create `user_profiles`, `knowledge_articles`, `interaction_summaries`, etc.)
      3.  `03_functions.sql` (This should create functions like `match_knowledge_articles` for RAG).
    - Copy the content of each SQL file, paste it into the Supabase SQL Editor, and click "RUN". Verify each script executes successfully. Check the `TASK.MD` to ensure all expected tables/functions are created.

### 4. Backend Setup & Services

1.  **Navigate to the Backend Directory:**

    ```bash
    cd backend  # From project root
    ```

2.  **Create and Activate Python Virtual Environment:**

    ```bash
    python3 -m venv ai
    source ai/bin/activate
    ```

    _(On Windows, use `ai\Scripts\activate`)_

3.  **Install Python Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Populate Knowledge Base (Optional - if you have sample data):**

    - If there\'s a script like `backend/populate_kb.py`, you can run it to insert initial data into your `knowledge_articles` table.
    - Ensure your `backend/.env` is configured, especially `OPENAI_API_KEY` (for embeddings) and Supabase credentials.

    ```bash
    python populate_kb.py
    ```

5.  **Run the Backend Services:** You\'ll typically run these in separate terminal windows/tabs. Ensure the virtual environment (`ai`) is active in each.

    - **A. LiveKit Token Service (`token_service.py`):**

      - From the project root (`Insta-Voice-Assistant-/`):
        ```bash
        uvicorn backend.token_service:app --reload --port 8000
        ```
      - This service allows the frontend to get LiveKit tokens after Firebase login.

    - **B. LiveKit Agent (`main.py`):**
      - From the project root (`Insta-Voice-Assistant-/`):
        ```bash
        python backend/main.py
        ```
      - This is the AI voice assistant that will connect to LiveKit rooms.

### 5. Frontend Setup

1.  **Navigate to the Frontend Directory:**

    - From the project root (`Insta-Voice-Assistant-/`):
      ```bash
      cd "frontend /frontend" # Adjust if your path is different
      ```

2.  **Install Node.js Dependencies:**

    ```bash
    npm install  # or yarn install
    ```

3.  **Run the Frontend Development Server:**
    ```bash
    npm run dev # or yarn dev
    ```
    - The frontend app should typically run on `http://localhost:5173`. Check your terminal output for the exact URL.

### 6. Running Tests (Pytest)

1.  **Ensure Backend Setup is Done:**
    - Python virtual environment (`ai`) should be created and its dependencies installed.
2.  **Activate Virtual Environment:**
    - If not already active in your terminal, from the `backend/` directory: `source ai/bin/activate`
3.  **Navigate to Project Root:**
    - Your tests might be configured to run from the project root.
    ```bash
    cd .. # if you are in backend/
    ```
4.  **Run Pytest:**
    ```bash
    pytest
    ```
    or
    ```bash
    python -m pytest
    ```
    - This will discover and run tests (e.g., in the `tests/` directory or files named `test_*.py`).

### Workflow Overview

1.  Start the **Supabase** service (it\'s always running in the cloud). Ensure schema is set up.
2.  Start the **LiveKit Token Service** (`backend/token_service.py` via Uvicorn).
3.  Start the **LiveKit Agent** (`backend/main.py`).
4.  Start the **Frontend** development server.
5.  Open your browser to the frontend URL.
6.  Sign up/Log in using Firebase on the frontend.
7.  The frontend should then request a LiveKit token from your `token_service`.
8.  With the token, the frontend connects to a LiveKit room where the `agent` should be waiting or will join.

---
