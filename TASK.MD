# TASK.MD - Insta-Voice-Assistant (LiveKit MVP)

## Project Goal: Real-time AI Voice Assistant for SaaS Customer Support (RAG, Custom Frontend, Basic Auth)

**Date Started (LiveKit MVP):** 2025-05-06

---

## Phase 1: MVP Setup & Core Functionality

### 1.1. Environment & Project Setup

- [x] Initialize Git repository. (Completed)
- [x] Update `PLANNING.MD` with MVP architecture (Completed).
- [x] Set up Python virtual environment (`backend/ai/`). (Completed)
- [x] Update `backend/requirements.txt`: (Completed)
  - `livekit-agents[openai,silero]~=1.0.19`
  - `python-dotenv`
  - `openai` (full library for embeddings)
  - `supabase` (corrected from supabase-py)
  - `PyJWT`
  - `firebase-admin`
  - `pytest`, `pytest-asyncio` (for testing)
- [x] Create/update `frontend/package.json` (or equivalent for chosen framework). (Completed)
  - `livekit-client`
  - `firebase` (for Firebase Web SDK)
- [x] Create/update `.env.example` (for backend) & frontend environment example. (Completed)
- [x] Populate `backend/.env` (OpenAI, Supabase URL & Key - Completed for current needs).
- [x] Populate frontend environment variables (Firebase Web SDK config). (Completed)

### 1.2. Authentication & Frontend Shell

- [x] Set up Firebase project. (Completed by user)
- [x] Enable Firebase Authentication (e.g., Google Sign-In and/or Email/Password). (Completed by user)
- [x] **Frontend**: Create basic frontend shell (e.g., React app). (Completed)
  - [x] Implement login page/component using Firebase Web SDK. (Completed)
  - [x] After login, store Firebase ID token. (Completed)
- [x] **Backend Helper (LiveKit Token Service - `backend/token_service.py`)**: (Completed)
  - [x] Accepts Firebase ID token from frontend. (Completed)
  - [x] Verifies Firebase ID token (using `firebase-admin`). (Completed)
  - [x] Generates a LiveKit access token (compatible with `livekit-api==1.0.2`). (Completed)
  - [x] Returns LiveKit token to frontend. (Completed & Tested via curl)
- **Frontend**: Use the LiveKit token to connect to a room. (PENDING - Frontend task)
- **Test**: User can log in, get LiveKit token from `token_service.py`, and (conceptually) connect. (Backend part tested, full test pending frontend integration)

### 1.3. LiveKit Agent Core (`backend/main.py` or `backend/agent_entry.py` - TBD)

- [ ] Use `AgentSession` and `Agent`.
- [ ] Configure `openai.realtime.RealtimeModel`.
- [ ] Configure `openai.TTS` for `session.say()`.
- [ ] Configure `silero.VAD`.
- [ ] `WELCOME_MESSAGE` via `session.say()`.
- [x] Update `backend/prompts.py` with `INSTRUCTIONS` for SaaS support. (Completed)
- [ ] Agent entrypoint should access `ctx.room.name` and `ctx.participant.identity`.
- [ ] Store `user_id` from `ctx.participant.identity` into `ctx.userdata`.

### 1.4. Supabase Setup (User Data & KB)

- [x] Create Supabase project. (Completed)
- [x] **Table: `user_profiles`** (SQL script created & run).
- [x] **Table: `knowledge_articles`** (SQL script created & run, uses `pgvector`).
- [x] **Table: `interaction_summaries`** (SQL script created & run).
- [x] Enable `pgvector` extension. (Completed)
- [x] Create SQL function `match_knowledge_articles` for vector search. (SQL script created & run)
- [x] Populate `knowledge_articles` with 4 sample SaaS FAQ chunks using backend/populate_kb.py script. (Completed)
- [ ] (Optional) Create a Supabase function/trigger for `user_profiles` creation on new Firebase user.

### 1.5. Database Driver (`backend/db_driver.py`)

- [x] Initialize Supabase client. (Completed & basic test in `test_embedding.py`)
- [x] `get_user_account_info_from_db(user_id: str) -> dict | None` (Implemented).
- [x] `save_interaction_summary(user_id: str, session_id: str, summary: str) -> bool` (Implemented).
- [x] `query_knowledge_base(query_text: str, top_k: int, ...) -> list[dict] | None` (Implemented).
- [x] `generate_embedding(text: str) -> list[float]` (Implemented using OpenAI, tested via `test_embedding.py`).
- [x] `store_knowledge_base_article(...)` (Implemented).

### 1.6. Tool Implementation (`backend/api.py`)

- [x] Tool: `get_user_account_info` (Implemented & integrated with db_driver).
- [x] Tool: `answer_from_company_kb` (Implemented & integrated with db_driver).
- [x] Tool: `summarize_interaction_for_next_session` (Implemented & integrated with db_driver).
- [ ] Update `fn_calling_context` in agent core file.

### 1.7. Initial Prompt Engineering (`backend/prompts.py`)

- [x] Craft `INSTRUCTIONS` for SaaS support agent. (Completed - Same as 1.3)

### 1.8. Unit & Integration Testing (Moved earlier as per TDD)

- [x] Unit tests for `backend/db_driver.py` (Comprehensive tests created and passing).
  - [x] DBDriverError exception handling implemented and tested.
- [x] Unit tests for `backend/api.py`:
  - [x] Initial tests for placeholder logic created.
  - [x] Tests for `get_user_account_info` (mocking `db_driver`) implemented and passing.
  - [x] Tests for `answer_from_company_kb` (mocking `db_driver`) implemented and passing.
  - [x] Tests for `summarize_interaction_for_next_session` (mocking `db_driver`) implemented and passing.
- [ ] Integration tests for API & DB interaction.
- [ ] End-to-end MVP test (as originally listed in 1.8).

### 1.9. Frontend LiveKit Integration & MVP Test (Original 1.8)

- **Frontend**:
  - Implement UI for connecting to LiveKit room using token.
  - Basic UI to show connection status, send/receive audio.
  - (Optional) Display transcript or agent messages.
- **End-to-end Test** (Original)

---

## Phase 2: Enhancements (Post-MVP)

- [ ] More sophisticated RAG, frontend UI/UX improvements.

---

## Discovered During Work

- Need to ensure consistent casing in log messages (e.g., "Supabase" vs "SupABASE"). (Addressed)
- Clarified Python import paths for test scripts (`test_embedding.py`). (Addressed)
- Importance of `.gitignore` for `.env` and virtual environments. (Addressed)
- `pytest-asyncio` is required for `async def` tests.

---
