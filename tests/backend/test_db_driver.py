# tests/backend/test_db_driver.py
import pytest
# AsyncMock might be needed if we make db calls async later
from unittest.mock import patch, MagicMock, AsyncMock
import os

# Functions to test from db_driver
# We need to import db_driver itself to allow patching its module-level clients
from backend import db_driver
from backend.db_driver import (
    get_user_account_info_from_db,
    generate_embedding,
    query_knowledge_base,
    store_knowledge_base_article,
    save_interaction_summary,
    DBDriverError  # Import DBDriverError
)

# --- Fixtures (if any common setup needed) ---

# --- Tests for get_user_account_info_from_db ---


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
async def test_get_user_account_info_success(mock_supabase_client, mock_db_logger):
    """Test successfully retrieving user account information."""
    mock_user_id = "user_123"
    expected_data = {'user_id': mock_user_id,
                     'email': 'test@example.com', 'subscription_tier': 'premium'}

    # Configure the chain of mocks for supabase.table().select().eq().maybe_single().execute()
    mock_execute = MagicMock()
    mock_execute.data = expected_data
    mock_execute.error = None

    mock_maybe_single = MagicMock()
    mock_maybe_single.execute.return_value = mock_execute

    mock_eq = MagicMock()
    mock_eq.maybe_single.return_value = mock_maybe_single

    mock_select = MagicMock()
    mock_select.eq.return_value = mock_eq

    mock_table = MagicMock()
    mock_table.select.return_value = mock_select
    mock_supabase_client.table.return_value = mock_table

    result = await get_user_account_info_from_db(mock_user_id)

    assert result == expected_data
    mock_supabase_client.table.assert_called_once_with('user_profiles')
    mock_table.select.assert_called_once_with(
        'user_id, email, full_name, subscription_tier')
    mock_select.eq.assert_called_once_with('user_id', mock_user_id)
    mock_eq.maybe_single.assert_called_once()
    mock_maybe_single.execute.assert_called_once()
    mock_db_logger.info.assert_called_once_with(
        f"User account info found for user_id: {mock_user_id}")


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
async def test_get_user_account_info_not_found(mock_supabase_client, mock_db_logger):
    """Test user not found."""
    mock_user_id = "user_not_exist"
    mock_execute = MagicMock()
    mock_execute.data = None  # Simulate no data found
    mock_execute.error = None
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_execute

    result = await get_user_account_info_from_db(mock_user_id)
    assert result is None
    mock_db_logger.warning.assert_called_once_with(
        f"No user account info found for user_id: {mock_user_id}")


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
async def test_get_user_account_info_db_error(mock_supabase_client, mock_db_logger):
    """Test Supabase DB error should raise DBDriverError."""
    mock_user_id = "user_db_error"
    simulated_exception = Exception("Simulated DB Exception")

    # Simulate exception during execute:
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.side_effect = simulated_exception

    with pytest.raises(DBDriverError) as excinfo:
        await get_user_account_info_from_db(mock_user_id)

    assert f"Error fetching user account info for {mock_user_id} from Supabase: {simulated_exception}" in str(
        excinfo.value)
    # Check that the original error was logged before DBDriverError was raised
    mock_db_logger.error.assert_called_once_with(
        f"Error fetching user account info for {mock_user_id} from Supabase: {simulated_exception}")


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase', None)
async def test_get_user_account_info_supabase_not_initialized(mock_db_logger):
    """Test when Supabase client is None should raise DBDriverError."""
    with pytest.raises(DBDriverError) as excinfo:
        await get_user_account_info_from_db("any_user")

    assert "Supabase client not initialized. Cannot fetch user info." in str(
        excinfo.value)
    # Check that the error was logged before DBDriverError was raised
    mock_db_logger.error.assert_called_once_with(
        "Supabase client not initialized. Cannot fetch user info.")

# --- Tests for generate_embedding ---


@patch('backend.db_driver.logger')
@patch('backend.db_driver.openai_client')
def test_generate_embedding_success(mock_openai_client, mock_db_logger):
    """Test successful embedding generation."""
    test_text = "Hello world"
    expected_embedding = [0.1, 0.2, 0.3]

    mock_embedding_data = MagicMock()
    mock_embedding_data.embedding = expected_embedding
    mock_response = MagicMock()
    # OpenAI API returns a list of embedding objects
    mock_response.data = [mock_embedding_data]
    mock_openai_client.embeddings.create.return_value = mock_response

    result = generate_embedding(test_text)

    assert result == expected_embedding
    mock_openai_client.embeddings.create.assert_called_once_with(
        input=test_text.replace("\x00", ""),
        model="text-embedding-3-small"
    )
    mock_db_logger.info.assert_called_once_with(
        f"Successfully generated embedding for text: {test_text[:50]}...")


@patch('backend.db_driver.logger')
@patch('backend.db_driver.openai_client')
def test_generate_embedding_empty_text(mock_openai_client, mock_db_logger):
    """Test with empty input text."""
    result = generate_embedding("")
    assert result is None
    mock_openai_client.embeddings.create.assert_not_called()
    mock_db_logger.warning.assert_called_once_with(
        "generate_embedding received empty or invalid text.")


@patch('backend.db_driver.logger')
@patch('backend.db_driver.openai_client')
def test_generate_embedding_openai_error(mock_openai_client, mock_db_logger):
    """Test OpenAI API error."""
    mock_openai_client.embeddings.create.side_effect = Exception(
        "Simulated OpenAI API Error")
    result = generate_embedding("some text")
    assert result is None
    mock_db_logger.error.assert_called_once_with(
        "OpenAI API error during embedding generation: Simulated OpenAI API Error")


@patch('backend.db_driver.logger')
@patch('backend.db_driver.openai_client', None)
def test_generate_embedding_openai_not_initialized(mock_db_logger):
    """Test when OpenAI client is None."""
    result = generate_embedding("some text")
    assert result is None
    mock_db_logger.error.assert_called_once_with(
        "OpenAI client not initialized. Cannot generate embedding.")

# --- Tests for query_knowledge_base ---


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
# Mock our own generate_embedding
@patch('backend.db_driver.generate_embedding')
async def test_query_knowledge_base_success(mock_generate_embedding, mock_supabase_client, mock_db_logger):
    """Test successful KB query."""
    query_text = "What is AI?"
    mock_embedding = [0.1] * 1536
    mock_generate_embedding.return_value = mock_embedding

    expected_articles = [
        {'id': 'article1', 'title': 'AI Intro', 'content': '...'}]
    mock_execute = MagicMock()
    mock_execute.data = expected_articles
    mock_supabase_client.rpc.return_value.execute.return_value = mock_execute

    result = await query_knowledge_base(query_text, top_k=1)

    assert result == expected_articles
    mock_generate_embedding.assert_called_once_with(query_text)
    mock_supabase_client.rpc.assert_called_once_with(
        'match_knowledge_articles',
        params={'query_embedding': mock_embedding,
                'match_count': 1, 'match_threshold': 0.7}
    )
    mock_db_logger.info.assert_called_once_with(
        f"Found {len(expected_articles)} relevant articles for query: {query_text[:50]}...")


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
@patch('backend.db_driver.generate_embedding')
async def test_query_knowledge_base_no_articles_found(mock_generate_embedding, mock_supabase_client, mock_db_logger):
    """Test when no articles are found by Supabase RPC."""
    query_text = "Unknown topic"
    mock_embedding = [0.3] * 1536
    mock_generate_embedding.return_value = mock_embedding

    mock_execute = MagicMock()
    mock_execute.data = []  # Simulate RPC returning empty list
    mock_supabase_client.rpc.return_value.execute.return_value = mock_execute

    result = await query_knowledge_base(query_text)

    assert result is None  # Function returns None if no data
    mock_generate_embedding.assert_called_once_with(query_text)
    mock_supabase_client.rpc.assert_called_once()
    mock_db_logger.info.assert_called_with(
        f"No relevant articles found for query: {query_text[:50]}...")


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
# Keep supabase patched to avoid None client issues if generate_embedding was not patched
@patch('backend.db_driver.supabase')
@patch('backend.db_driver.generate_embedding')
async def test_query_knowledge_base_embedding_fails(mock_generate_embedding, mock_supabase_client, mock_db_logger):
    """Test when generate_embedding returns None."""
    query_text = "A query that will fail embedding"
    mock_generate_embedding.return_value = None

    result = await query_knowledge_base(query_text)

    assert result is None
    mock_generate_embedding.assert_called_once_with(query_text)
    # RPC should not be called if embedding fails
    mock_supabase_client.rpc.assert_not_called()
    mock_db_logger.error.assert_called_once_with(
        "Failed to generate embedding for KB query.")


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
@patch('backend.db_driver.generate_embedding')
async def test_query_knowledge_base_supabase_rpc_error(mock_generate_embedding, mock_supabase_client, mock_db_logger):
    """Test when Supabase RPC call raises an exception."""
    query_text = "Query leading to RPC error"
    mock_embedding = [0.4] * 1536
    mock_generate_embedding.return_value = mock_embedding
    error_message = "Simulated RPC error"

    mock_supabase_client.rpc.return_value.execute.side_effect = Exception(
        error_message)

    result = await query_knowledge_base(query_text)

    assert result is None
    mock_generate_embedding.assert_called_once_with(query_text)
    mock_supabase_client.rpc.assert_called_once()
    logged_error_message = mock_db_logger.error.call_args[0][0]
    assert f"Error querying knowledge base from Supabase: {error_message}" in logged_error_message


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase', None)
@patch('backend.db_driver.generate_embedding')
async def test_query_knowledge_base_supabase_not_initialized(mock_generate_embedding, mock_db_logger):
    """Test query_knowledge_base when Supabase client is None."""
    query_text = "Any query"

    result = await query_knowledge_base(query_text)

    assert result is None
    mock_generate_embedding.assert_not_called()  # If supabase check is first
    mock_db_logger.error.assert_called_once_with(
        "Supabase client not initialized. Cannot query KB.")  # Expect title case

# --- Tests for store_knowledge_base_article ---


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
@patch('backend.db_driver.generate_embedding')
async def test_store_knowledge_base_article_success(mock_generate_embedding, mock_supabase_client, mock_db_logger):
    """Test successful article storage."""
    title = "New Article"
    content = "This is the content."
    mock_embedding = [0.2] * 1536
    mock_generate_embedding.return_value = mock_embedding

    mock_execute = MagicMock()
    # Simulate successful insert returning data
    mock_execute.data = [{'id': 'new_id'}]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_execute

    result = await store_knowledge_base_article(title, content)

    assert result is True
    mock_generate_embedding.assert_called_once_with(content)
    mock_supabase_client.table.assert_called_once_with('knowledge_articles')
    mock_supabase_client.table.return_value.insert.assert_called_once_with(
        {'title': title, 'content': content, 'embedding': mock_embedding}
    )
    mock_db_logger.info.assert_called_once_with(
        f"Successfully stored KB article: {title}")


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
@patch('backend.db_driver.generate_embedding')
async def test_store_knowledge_base_article_embedding_fails(mock_generate_embedding, mock_supabase_client, mock_db_logger):
    """Test when generate_embedding returns None for store_knowledge_base_article."""
    title = "Article with failed embedding"
    content = "Some content"
    mock_generate_embedding.return_value = None

    result = await store_knowledge_base_article(title, content)

    assert result is False
    mock_generate_embedding.assert_called_once_with(content)
    # Supabase table insert should not be called
    mock_supabase_client.table.assert_not_called()
    mock_db_logger.error.assert_called_once_with(
        f"Failed to generate embedding for KB article: {title}")


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
@patch('backend.db_driver.generate_embedding')
async def test_store_knowledge_base_article_supabase_error(mock_generate_embedding, mock_supabase_client, mock_db_logger):
    """Test Supabase error during article storage."""
    title = "Article causing DB error"
    content = "Content here"
    mock_embedding = [0.5] * 1536
    mock_generate_embedding.return_value = mock_embedding
    error_message = "Simulated Supabase Insert Error"

    mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception(
        error_message)

    result = await store_knowledge_base_article(title, content)

    assert result is False
    mock_generate_embedding.assert_called_once_with(content)
    mock_supabase_client.table.assert_called_once_with('knowledge_articles')
    logged_error_message = mock_db_logger.error.call_args[0][0]
    assert f"Error storing KB article '{title}' to Supabase: {error_message}" in logged_error_message


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
@patch('backend.db_driver.generate_embedding')
async def test_store_knowledge_base_article_insert_fails_no_data(mock_generate_embedding, mock_supabase_client, mock_db_logger):
    """Test when Supabase insert returns no data (simulating a failure)."""
    title = "Article insert no data"
    content = "Content for no data"
    mock_embedding = [0.6] * 1536
    mock_generate_embedding.return_value = mock_embedding

    mock_response_object = MagicMock()  # This is what execute() returns
    mock_response_object.data = None  # No data indicates failure or nothing inserted
    mock_response_object.error = None  # No explicit error object
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response_object

    result = await store_knowledge_base_article(title, content)

    assert result is False
    mock_generate_embedding.assert_called_once_with(content)
    mock_supabase_client.table.assert_called_once_with('knowledge_articles')
    # The actual response object is logged, so checking parts of the string is safer
    logged_error_message = mock_db_logger.error.call_args[0][0]
    assert f"Failed to store KB article '{title}'" in logged_error_message
    # Check that the response part is logged
    assert "Response: " in logged_error_message


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase', None)
# Still mock to prevent execution
@patch('backend.db_driver.generate_embedding')
async def test_store_knowledge_base_article_supabase_not_initialized(mock_generate_embedding, mock_db_logger):
    """Test store_knowledge_base_article when Supabase client is None."""
    title = "Any Title"
    content = "Any Content"

    result = await store_knowledge_base_article(title, content)

    assert result is False
    # In store_knowledge_base_article, supabase is checked before generate_embedding
    mock_generate_embedding.assert_not_called()
    mock_db_logger.error.assert_called_once_with(
        "Supabase client not initialized. Cannot store KB article.")


# --- Tests for save_interaction_summary ---

@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
async def test_save_interaction_summary_success(mock_supabase_client, mock_db_logger):
    """Test successful summary saving."""
    user_id = "user1"
    session_id = "session1"
    summary_text = "User asked about X."

    mock_execute = MagicMock()
    mock_execute.data = [{'id': 'summary_id'}]  # Simulate successful insert
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_execute

    result = await save_interaction_summary(user_id, session_id, summary_text)

    assert result is True
    mock_supabase_client.table.assert_called_once_with('interaction_summaries')
    mock_supabase_client.table.return_value.insert.assert_called_once_with({
        'user_id': user_id,
        'session_id': session_id,
        'summary': summary_text,
    })
    mock_db_logger.info.assert_called_once_with(
        f"Interaction summary saved for user_id: {user_id}, session_id: {session_id}")


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
async def test_save_interaction_summary_supabase_error(mock_supabase_client, mock_db_logger):
    """Test Supabase error during summary saving."""
    user_id = "user_err"
    session_id = "session_err"
    summary_text = "Summary causing error."
    error_message = "Simulated DB Insert Error for summary"

    mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception(
        error_message)

    result = await save_interaction_summary(user_id, session_id, summary_text)

    assert result is False
    mock_supabase_client.table.assert_called_once_with('interaction_summaries')
    logged_error_message = mock_db_logger.error.call_args[0][0]
    assert f"Error saving interaction summary for {user_id} to Supabase: {error_message}" in logged_error_message


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase')
async def test_save_interaction_summary_insert_fails_no_data(mock_supabase_client, mock_db_logger):
    """Test when Supabase insert returns no data for summary (simulating failure)."""
    user_id = "user_nodata"
    session_id = "session_nodata"
    summary_text = "Summary with no data response."

    mock_response_object = MagicMock()
    mock_response_object.data = None
    mock_response_object.error = None
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response_object

    result = await save_interaction_summary(user_id, session_id, summary_text)

    assert result is False
    mock_supabase_client.table.assert_called_once_with('interaction_summaries')
    logged_error_message = mock_db_logger.error.call_args[0][0]
    assert f"Failed to save interaction summary for user_id {user_id}" in logged_error_message
    assert "Response: " in logged_error_message


@pytest.mark.asyncio
@patch('backend.db_driver.logger')
@patch('backend.db_driver.supabase', None)
async def test_save_interaction_summary_supabase_not_initialized(mock_db_logger):
    """Test save_interaction_summary when Supabase client is None."""
    user_id = "any_user"
    session_id = "any_session"
    summary_text = "Any summary"

    result = await save_interaction_summary(user_id, session_id, summary_text)

    assert result is False
    mock_db_logger.error.assert_called_once_with(
        "Supabase client not initialized. Cannot save summary.")
