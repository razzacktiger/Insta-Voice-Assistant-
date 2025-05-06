# TASK.MD - Insta-Voice-Assistant (LiveKit MVP)

## Project Goal: Real-time AI Voice Assistant for SaaS Customer Support (RAG, Custom Frontend, Basic Auth)

**Date Started (LiveKit MVP):** 2025-05-06

---

## Phase 1: MVP Setup & Core Functionality

### 1.1. Environment & Project Setup

- [ ] Initialize Git repository.
- [x] Update `PLANNING.MD` with MVP architecture (Completed).
- [ ] Set up Python virtual environment (`backend/ai/`).
- [ ] Update `backend/requirements.txt`:
  - `livekit-agents[openai,silero]~=1.0.19` (confirm latest stable 1.0.x; other extras if explicitly needed)
  - `python-dotenv`
  - `openai` (full library for embeddings)
  - `supabase-py`
  - `PyJWT` (for potential token generation/validation if needed server-side for LiveKit)
  - `firebase-admin` (for backend validation of Firebase tokens if chosen route)
- [ ] Create/update `frontend/package.json` (or equivalent for chosen framework).
  - `livekit-client`
  - `firebase` (for Firebase Web SDK)
- [ ] Create/update `.env.example` (for backend) & frontend environment example.
- [ ] Populate `backend/.env` (OpenAI, LiveKit Cloud, Supabase URL & Key, Firebase service account details if needed).
- [ ] Populate frontend environment variables (Firebase Web SDK config).

### 1.2. Authentication & Frontend Shell

- [ ] Set up Firebase project.
- [ ] Enable Firebase Authentication (e.g., Google Sign-In and/or Email/Password).
- [ ] **Frontend**: Create basic frontend shell (e.g., React app).
  - Implement login page/component using Firebase Web SDK.
  - After login, store Firebase ID token.
- [ ] **Backend Helper (Optional but Recommended)**: Create a simple backend endpoint (e.g., in a minimal FastAPI/Flask app within `backend/` or a serverless function) that:
  - Accepts Firebase ID token from frontend.
  - Verifies Firebase ID token (using `firebase-admin`).
  - Generates a LiveKit access token with the Firebase UID as `identity` and grants `agent` capabilities if this user is an agent, or appropriate participant grants.
  - Returns LiveKit token to frontend.
- **Frontend**: Use the LiveKit token to connect to a room.
- **Test**: User can log in via frontend, frontend gets a LiveKit token and can (conceptually) connect.

### 1.3. LiveKit Agent Core (`backend/agent.py`)

- [ ] Use `AgentSession` and `Agent`.
- [ ] Configure `openai.realtime.RealtimeModel`.
- [ ] Configure `openai.TTS` for `session.say()`.
- [ ] Configure `silero.VAD`.
- [ ] `WELCOME_MESSAGE` via `session.say()`.
- [ ] Update `backend/prompts.py` with `INSTRUCTIONS` for SaaS support.
- [ ] Agent entrypoint (`entrypoint` in `JobContext`) should be able to access `ctx.room.name` and `ctx.participant.identity` (which will be Firebase UID).
- [ ] Store `user_id` (Firebase UID) from `ctx.participant.identity` into `ctx.userdata` for tools to use.

### 1.4. Supabase Setup (User Data & KB)

- [ ] Create Supabase project (if not done for auth testing).
- [ ] **Table: `user_profiles`**:
  - `user_id` (text, primary key - Firebase UID)
  - `name` (text, nullable)
  - `email` (text, nullable)
  - `subscription_tier` (text, nullable)
  - `last_interaction_summary` (text, nullable)
- [ ] **Table: `company_kb`** (for RAG):
  - `id` (UUID, primary key, default `uuid_generate_v4()`)
  - `content` (text)
  - `embedding` (vector, using `pgvector`)
- [ ] Enable `pgvector` extension.
- [ ] Populate `company_kb` with 2-3 sample SaaS FAQ chunks. Generate & store embeddings.
- [ ] (Optional) Create a Supabase function/trigger to create a `user_profiles` entry when a new Firebase user signs up if not handled by a backend tool.

### 1.5. Database Driver (`backend/db_driver.py`)

- [ ] Initialize Supabase client.
- [ ] `get_user_profile(user_id: str) -> dict | None`
- [ ] `update_user_interaction_summary(user_id: str, summary: str) -> bool`
- [ ] `find_relevant_kb_chunks(query_embedding: list[float], limit: int = 3) -> list[str]`
- [ ] `embed_text(text: str) -> list[float]` (using OpenAI API).

### 1.6. Tool Implementation (`backend/api.py`)

- [ ] Tool: `get_user_account_info` (uses `user_id` from `ctx.userdata`).
- [ ] Tool: `answer_from_company_kb` (uses `user_query` and RAG functions).
- [ ] Tool: `summarize_interaction_for_next_session`.
- [ ] Update `fn_calling_context` in `backend/agent.py`.

### 1.7. Initial Prompt Engineering (`backend/prompts.py`)

- [ ] Craft `INSTRUCTIONS` for SaaS support agent: explain capabilities (KB, profile), tool usage, summarization.

### 1.8. Frontend LiveKit Integration & MVP Test

- **Frontend**:
  - Implement UI for connecting to LiveKit room using token.
  - Basic UI to show connection status, send/receive audio.
  - (Optional) Display transcript or agent messages.
- **End-to-end Test**:
  - User logs in via frontend.
  - Frontend connects to LiveKit, agent joins.
  - Agent greets.
  - User asks for their profile info.
  - User asks a question answerable from `company_kb`.
  - Agent attempts to summarize at the end.

---

## Phase 2: Enhancements (Post-MVP)

- [ ] More sophisticated RAG, frontend UI/UX improvements.
- [ ] Unit/integration tests.

---

## Discovered During Work

- (Add items here)

---
