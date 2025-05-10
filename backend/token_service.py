import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, auth
# Assuming livekit-api or livekit-server-sdk is installed
from livekit.api import AccessToken, VideoGrants
from dotenv import load_dotenv

# Load environment variables from .env file
# Assuming .env file is in the same directory as this script (backend/)
# or in the project root if running uvicorn from project root and .env is there.
# More robustly: find the .env file relative to this script or project root.

# Determine the path to the .env file. Assumes it's in the same dir as this script (backend)
# If you run uvicorn from project root, it might look for .env in project root.
# This tries to be a bit more robust for development.
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    # If not found next to script, try project root (common for uvicorn from root)
    # This assumes token_service.py is in a 'backend' subdirectory of the project root.
    project_root_env_path = os.path.join(
        os.path.dirname(__file__), '..', '.env')
    if os.path.exists(project_root_env_path):
        env_path = project_root_env_path
    else:
        env_path = None  # Let load_dotenv search in CWD or raise error if critical

if env_path:
    print(f"Attempting to load .env from: {env_path}")
    load_dotenv(dotenv_path=env_path, override=True)
else:
    print("No .env file found at script location or project root, relying on CWD or environment.")
    # Default behavior: searches CWD, then parent dirs, or uses existing env vars.
    load_dotenv(override=True)

# --- Firebase Admin SDK Initialization ---
FIREBASE_ADMIN_SDK_PATH = os.getenv('FIREBASE_ADMIN_SDK_CREDENTIALS_PATH')
if not FIREBASE_ADMIN_SDK_PATH:
    print("Warning: FIREBASE_ADMIN_SDK_CREDENTIALS_PATH not found in .env. Firebase Admin SDK might not initialize correctly for local development.")
    # Attempt to initialize with default credentials if path is not provided (e.g., for cloud environments)
    try:
        firebase_admin.initialize_app()
        print("Firebase Admin SDK initialized with default credentials.")
    except Exception as e:
        print(
            f"Failed to initialize Firebase Admin SDK with default credentials: {e}")
else:
    try:
        cred = credentials.Certificate(FIREBASE_ADMIN_SDK_PATH)
        firebase_admin.initialize_app(cred)
        print(
            f"Firebase Admin SDK initialized using {FIREBASE_ADMIN_SDK_PATH}")
    except Exception as e:
        print(
            f"Error initializing Firebase Admin SDK with service account key from {FIREBASE_ADMIN_SDK_PATH}: {e}")
        # Depending on policy, you might want to raise an exception here to prevent startup

# --- FastAPI App Initialization ---
app = FastAPI()

# --- CORS Middleware Configuration ---
# Adjust origins as needed for production
origins = [
    "*",  # Allows all origins for development. Restrict this in production!
    # e.g., "http://localhost:5173" for your Vite frontend
    # "https://your-frontend-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Request/Response ---


class TokenRequest(BaseModel):
    firebase_id_token: str
    room_name: str  # The room the user wants to join


class TokenResponse(BaseModel):
    livekit_token: str
    user_id: str


# --- Environment Variables for LiveKit ---
LIVEKIT_API_KEY = os.getenv('LIVEKIT_API_KEY')
LIVEKIT_API_SECRET = os.getenv('LIVEKIT_API_SECRET')

if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
    print("Error: LIVEKIT_API_KEY or LIVEKIT_API_SECRET not found in .env. LiveKit token generation will fail.")
    # Consider raising an exception here to prevent startup if these are critical

# --- Helper function to verify Firebase token (dependency) ---


async def verify_firebase_token(token_request: TokenRequest) -> dict:
    try:
        decoded_token = auth.verify_id_token(token_request.firebase_id_token)
        return decoded_token
    except firebase_admin.auth.InvalidIdTokenError as e:
        print(f"Invalid Firebase ID token: {e}")
        raise HTTPException(
            status_code=401, detail="Invalid Firebase ID token")
    except Exception as e:
        print(f"Error verifying Firebase ID token: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error verifying Firebase ID token: {e}")

# --- API Endpoint ---


@app.post("/generate-livekit-token", response_model=TokenResponse)
async def generate_livekit_token_endpoint(token_request: TokenRequest, decoded_firebase_token: dict = Depends(verify_firebase_token)):
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise HTTPException(
            status_code=500, detail="LiveKit API key/secret not configured on server.")

    firebase_uid = decoded_firebase_token.get('uid')
    participant_name = decoded_firebase_token.get(
        'name') or firebase_uid  # Use name if available, else UID

    if not firebase_uid:
        raise HTTPException(
            status_code=400, detail="UID not found in Firebase token.")

    try:
        # 1. Create VideoGrants object
        video_grants_obj = VideoGrants(
            room_join=True,
            room=token_request.room_name,
            can_publish=True,
            can_subscribe=True,
            # can_publish_data=True, # If data channels are used and supported by your VideoGrants constructor
        )

        # 2. Build the AccessToken using the builder pattern
        token_builder = AccessToken(api_key=LIVEKIT_API_KEY,
                                    api_secret=LIVEKIT_API_SECRET)

        jwt_string = token_builder.with_identity(firebase_uid) \
                                  .with_name(participant_name) \
                                  .with_grants(video_grants_obj) \
                                  .to_jwt()

        print(
            f"Generated LiveKit token for user {firebase_uid} for room {token_request.room_name}")
        return TokenResponse(livekit_token=jwt_string, user_id=firebase_uid)

    except Exception as e:
        print(f"Error generating LiveKit token: {e}")
        raise HTTPException(
            status_code=500, detail=f"Could not generate LiveKit token: {e}")

# --- To run this app (save as token_service.py and run in terminal): ---
# uvicorn backend.token_service:app --reload --port 8080
# Ensure your .env file is in the root directory or where `load_dotenv()` can find it.
# The path for uvicorn assumes your terminal is in the project root.

if __name__ == "__main__":
    import uvicorn
    # This is for direct execution (python backend/token_service.py),
    # but `uvicorn backend.token_service:app --reload` is preferred for development.
    # Port 8000 is a common default for FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)
