import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import logging
from openai import OpenAI  # Import OpenAI

load_dotenv()  # Load environment variables from .env

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Custom Exception for DB Driver issues


class DBDriverError(Exception):
    pass


# Initialize Supabase client
SUPABASE_URL: Optional[str] = os.environ.get("SUPABASE_URL")
# Use service role key for backend operations
SUPABASE_KEY: Optional[str] = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Supabase URL or Key not found in environment variables.")
    # You might want to raise an exception here or handle it gracefully
    # depending on how critical the DB connection is at startup.
    supabase: Optional[Client] = None
else:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase = None

# Initialize OpenAI client (synchronous)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in environment variables.")
    openai_client: Optional[OpenAI] = None
else:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)  # Synchronous client
        logger.info("OpenAI client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        openai_client = None

# --- User Account Functions ---


async def get_user_account_info_from_db(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves user account information from the 'users' table in Supabase.
    Assumes user_id is the primary key or a unique identifier in your 'users' table.
    Raises DBDriverError if the Supabase client is not initialized or if there's a database exception.
    Returns None if the user is not found.
    """
    if not supabase:
        err_msg = "Supabase client not initialized. Cannot fetch user info."
        logger.error(err_msg)
        raise DBDriverError(err_msg)
    try:
        # This is a synchronous call in supabase-py v2 when using the default client
        response = supabase.table('user_profiles').select(
            'user_id, email, full_name, subscription_tier'
        ).eq('user_id', user_id).maybe_single().execute()

        if response.data:
            logger.info(f"User account info found for user_id: {user_id}")
            return response.data
        else:
            logger.warning(
                f"No user account info found for user_id: {user_id}")
            return None
    except Exception as e:
        err_msg = f"Error fetching user account info for {user_id} from Supabase: {e}"
        logger.error(err_msg)
        raise DBDriverError(err_msg)

# --- Knowledge Base (RAG) Functions ---


# Changed to synchronous
def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generates an embedding for the given text using OpenAI.
    """
    if not openai_client:
        logger.error(
            "OpenAI client not initialized. Cannot generate embedding.")
        return None
    if not text or not isinstance(text, str) or not text.strip():
        logger.warning("generate_embedding received empty or invalid text.")
        return None
    try:
        processed_text = text.replace("\x00", "")
        response = openai_client.embeddings.create(  # Removed await, using synchronous client
            input=processed_text,
            model="text-embedding-3-small"
        )
        logger.info(
            f"Successfully generated embedding for text: {processed_text[:50]}...")
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI API error during embedding generation: {e}")
        return None


async def query_knowledge_base(query_text: str, top_k: int = 3) -> Optional[List[Dict[str, Any]]]:
    """
    Queries the knowledge base for articles relevant to the query_text.
    1. Generates an embedding for the query_text.
    2. Uses Supabase pgvector to find similar articles.
    """
    if not supabase:
        logger.error("Supabase client not initialized. Cannot query KB.")
        return None

    query_embedding = generate_embedding(query_text)
    if not query_embedding:
        logger.error("Failed to generate embedding for KB query.")
        return None

    try:
        # TODO: Define your actual function name in Supabase for vector search
        # This usually involves an RPC call to a custom SQL function.
        # Example: 'match_documents(query_embedding vector, match_threshold float, match_count int)'
        response = supabase.rpc(
            'match_knowledge_articles',
            params={'query_embedding': query_embedding, 'match_count': top_k,
                    'match_threshold': 0.7}  # Adjust threshold
        ).execute()

        if response.data:
            logger.info(
                f"Found {len(response.data)} relevant articles for query: {query_text[:50]}...")
            return response.data
        else:
            logger.info(
                f"No relevant articles found for query: {query_text[:50]}...")
            return None
    except Exception as e:
        logger.error(f"Error querying knowledge base from Supabase: {e}")
        return None


async def store_knowledge_base_article(title: str, content: str, metadata: Optional[Dict] = None) -> bool:
    """
    Generates embedding for content and stores the article in Supabase.
    This is a utility function you might call separately to populate your KB.
    """
    if not supabase:
        logger.error(
            "Supabase client not initialized. Cannot store KB article.")
        return False

    # Call synchronous function directly
    embedding = generate_embedding(content)
    if not embedding:
        logger.error(f"Failed to generate embedding for KB article: {title}")
        return False

    try:
        # TODO: Define your 'knowledge_articles' table name and columns
        article_data = {'title': title,
                        'content': content, 'embedding': embedding}
        if metadata:
            article_data.update(metadata)

        response = supabase.table('knowledge_articles').insert(
            article_data).execute()
        # Check if insert was successful (supabase-py v2 might return list of inserted records)
        if response.data:
            logger.info(f"Successfully stored KB article: {title}")
            return True
        else:  # supabase-py v2 might have error info in response.error
            # Corrected quote escaping
            logger.error(
                f"Failed to store KB article '{title}'. Response: {response}")
            return False
    except Exception as e:
        # Corrected quote escaping
        logger.error(f"Error storing KB article '{title}' to Supabase: {e}")
        return False

# --- Interaction Summary Functions ---


async def save_interaction_summary(user_id: str, session_id: str, summary_text: str) -> bool:
    """
    Saves an interaction summary to the 'interaction_summaries' table.
    """
    if not supabase:
        logger.error("Supabase client not initialized. Cannot save summary.")
        return False
    try:
        # This is a synchronous call in supabase-py v2 when using the default client
        response = supabase.table('interaction_summaries').insert({
            'user_id': user_id,
            'session_id': session_id,  # Good to link to a specific LiveKit session if possible
            'summary': summary_text,
            # 'timestamp': datetime.utcnow() # Handled by Supabase `now()` or `created_at`
        }).execute()

        if response.data:
            logger.info(
                f"Interaction summary saved for user_id: {user_id}, session_id: {session_id}")
            return True
        else:
            logger.error(
                f"Failed to save interaction summary for user_id {user_id}. Response: {response}")
            return False
    except Exception as e:
        logger.error(
            f"Error saving interaction summary for {user_id} to Supabase: {e}")
        return False
