# tests/backend/test_api.py
import pytest
from unittest.mock import MagicMock, patch

# Import the actual functions from backend.api
from backend.api import get_user_account_info, answer_from_company_kb, summarize_interaction_for_next_session
from backend.db_driver import DBDriverError  # Import DBDriverError

# Mock a RunContext


@pytest.fixture
def mock_run_context():
    ctx = MagicMock()
    ctx.userdata = {}  # Start with empty userdata, can be populated in specific tests
    # Logger will be patched directly in each test, so no need to mock it on ctx here.

    # Mock participant and identity as it's used in placeholder logic in api.py
    ctx.participant = MagicMock()
    ctx.participant.identity = "test_participant_id"
    return ctx

# --- Tests for get_user_account_info ---


@pytest.mark.asyncio
@patch('backend.api.logger')  # Patch the logger in the api module
# To mock the call to db_driver
@patch('backend.api.db_driver.get_user_account_info_from_db')
async def test_get_user_account_info_success(mock_get_user_from_db, mock_api_logger, mock_run_context):
    """Test successfully retrieving and formatting user account information via db_driver."""
    test_user_id = "user_exists_123"
    mock_run_context.participant.identity = test_user_id

    db_return_data = {
        'user_id': test_user_id,
        'email': 'real_user@example.com',
        'full_name': 'Real User',
        'subscription_tier': 'Gold Tier'
    }
    mock_get_user_from_db.return_value = db_return_data

    expected_response_string = (
        f"Okay, I found these details for user {test_user_id}:\n"
        f"Name: Real User\n"
        f"Email: real_user@example.com\n"
        f"Subscription: Gold Tier"
    )

    actual_response = await get_user_account_info(mock_run_context)

    mock_get_user_from_db.assert_called_once_with(test_user_id)
    assert actual_response == expected_response_string
    mock_api_logger.info.assert_any_call(
        f"Attempting to get user account info for participant: {test_user_id}")
    # We might also log the successful retrieval in api.py, if so, add assertion here.


@pytest.mark.asyncio
@patch('backend.api.logger')
@patch('backend.api.db_driver.get_user_account_info_from_db')
async def test_get_user_account_info_user_not_found_in_db(mock_get_user_from_db, mock_api_logger, mock_run_context):
    """Test when db_driver returns None (user not found)."""
    test_user_id = "user_not_found_404"
    mock_run_context.participant.identity = test_user_id
    mock_get_user_from_db.return_value = None  # Simulate db_driver finding no user

    expected_response_string = f"I couldn't find any account details for user ID: {test_user_id}. Please ensure the ID is correct or if you need to register."

    actual_response = await get_user_account_info(mock_run_context)

    mock_get_user_from_db.assert_called_once_with(test_user_id)
    assert actual_response == expected_response_string
    mock_api_logger.info.assert_any_call(
        f"Attempting to get user account info for participant: {test_user_id}")
    mock_api_logger.warning.assert_any_call(
        f"No account details found in DB for user ID: {test_user_id}")  # Assuming api.py logs this


@pytest.mark.asyncio
@patch('backend.api.logger')
@patch('backend.api.db_driver.get_user_account_info_from_db')
async def test_get_user_account_info_db_driver_exception(mock_get_user_from_db, mock_api_logger, mock_run_context):
    """Test when db_driver.get_user_account_info_from_db raises a DBDriverError."""
    test_user_id = "user_db_exception_500"
    mock_run_context.participant.identity = test_user_id

    # Simulate db_driver raising DBDriverError
    simulated_error_message = "Simulated DB driver error"
    mock_get_user_from_db.side_effect = DBDriverError(simulated_error_message)

    expected_response_string = f"Sorry, I encountered an issue trying to retrieve account details for user ID: {test_user_id}. Please try again later."

    actual_response = await get_user_account_info(mock_run_context)

    mock_get_user_from_db.assert_called_once_with(test_user_id)
    assert actual_response == expected_response_string
    mock_api_logger.info.assert_any_call(
        f"Attempting to get user account info for participant: {test_user_id}")
    # Assert the new error log message from api.py's except block
    mock_api_logger.error.assert_any_call(
        f"Failed to retrieve account details for {test_user_id} from DB driver. Error: {simulated_error_message}")


# --- Tests for answer_from_company_kb ---


@pytest.mark.asyncio
@patch('backend.api.logger')
@patch('backend.api.db_driver.query_knowledge_base')
async def test_answer_from_company_kb_found_password(mock_query_knowledge_base, mock_api_logger, mock_run_context):
    """Test successfully finding and returning a single answer from the KB."""
    user_query = "How do I reset my password?"
    mock_run_context.participant.identity = "test_user_kb_search"

    kb_article = {
        'title': 'Password Reset Procedure',
        'content': 'To reset your password, please visit the account recovery page and follow the instructions.',
        # 'similarity_score': 0.9 # db_driver might return this, api layer might not use it directly in response
    }
    # db_driver.query_knowledge_base returns a list
    mock_query_knowledge_base.return_value = [kb_article]

    expected_response = (
        "I found this in our knowledge base:\n\n"
        f"Title: {kb_article['title']}\n"
        f"Content: {kb_article['content']}"
    )

    actual_response = await answer_from_company_kb(mock_run_context, user_query)

    mock_api_logger.info.assert_any_call(
        f"Attempting to answer from KB. User: test_user_kb_search, Query: '{user_query}'")
    mock_query_knowledge_base.assert_called_once_with(user_query)
    assert actual_response == expected_response
    # We could also add a log for successful retrieval if desired
    # mock_api_logger.info.assert_any_call(f"Successfully found 1 article(s) for query: '{user_query}'")


@pytest.mark.asyncio
@patch('backend.api.logger')
@patch('backend.api.db_driver.query_knowledge_base')
async def test_answer_from_company_kb_found_multiple_articles(mock_query_knowledge_base, mock_api_logger, mock_run_context):
    """Test successfully finding and returning multiple articles from the KB."""
    user_query = "Tell me about feature x"
    mock_run_context.participant.identity = "test_user_multi_article"

    kb_articles = [
        {
            'title': 'Feature X Overview',
            'content': 'Feature X is a revolutionary new tool that helps you achieve your goals.'
        },
        {
            'title': 'Getting Started with Feature X',
            'content': 'To start using Feature X, navigate to the dashboard and click the Feature X button.'
        }
    ]
    mock_query_knowledge_base.return_value = kb_articles

    expected_response = (
        "Here's what I found in our knowledge base related to your query:\n\n"
        f"Title: {kb_articles[0]['title']}\nContent: {kb_articles[0]['content']}\n\n"
        "---\n\n"
        f"Title: {kb_articles[1]['title']}\nContent: {kb_articles[1]['content']}"
    )

    actual_response = await answer_from_company_kb(mock_run_context, user_query)

    mock_api_logger.info.assert_any_call(
        f"Attempting to answer from KB. User: test_user_multi_article, Query: '{user_query}'")
    mock_query_knowledge_base.assert_called_once_with(user_query)
    assert actual_response == expected_response
    # mock_api_logger.info.assert_any_call(f"Successfully found {len(kb_articles)} article(s) for query: '{user_query}'")


@pytest.mark.asyncio
@patch('backend.api.logger')
@patch('backend.api.db_driver.query_knowledge_base')
async def test_answer_from_company_kb_not_found(mock_query_knowledge_base, mock_api_logger, mock_run_context):
    """Test handling when no relevant information is found in the KB."""
    user_query = "What is the meaning of plumbus?"
    mock_run_context.participant.identity = "test_user_kb_not_found"

    mock_query_knowledge_base.return_value = None  # Simulate no articles found

    expected_response = "I couldn't find specific information about that in our knowledge base. Could you try rephrasing, or is there something else I can help with?"

    actual_response = await answer_from_company_kb(mock_run_context, user_query)

    mock_api_logger.info.assert_any_call(
        f"Attempting to answer from KB. User: test_user_kb_not_found, Query: '{user_query}'")
    mock_query_knowledge_base.assert_called_once_with(user_query)
    assert actual_response == expected_response
    mock_api_logger.warning.assert_any_call(
        f"No KB articles found for query: '{user_query}'. User: test_user_kb_not_found")


@pytest.mark.asyncio
@patch('backend.api.logger')
@patch('backend.api.db_driver.query_knowledge_base')
async def test_answer_from_company_kb_db_error(mock_query_knowledge_base, mock_api_logger, mock_run_context):
    """Test handling for a DBDriverError during KB lookup."""
    user_query = "Tell me about product Y with a DB error."
    mock_run_context.participant.identity = "test_user_kb_db_error"
    simulated_db_error_message = "Simulated DB error during KB query"

    mock_query_knowledge_base.side_effect = DBDriverError(
        simulated_db_error_message)

    expected_response = "Sorry, I encountered an issue trying to search our knowledge base. Please try again later."

    actual_response = await answer_from_company_kb(mock_run_context, user_query)

    mock_api_logger.info.assert_any_call(
        f"Attempting to answer from KB. User: test_user_kb_db_error, Query: '{user_query}'")
    mock_query_knowledge_base.assert_called_once_with(user_query)
    assert actual_response == expected_response
    mock_api_logger.error.assert_any_call(
        f"Database error during KB query for User: test_user_kb_db_error, Query: '{user_query}'. Error: {simulated_db_error_message}")

# --- Tests for summarize_interaction_for_next_session ---


@pytest.mark.asyncio
@patch('backend.api.logger')
@patch('backend.api.db_driver.save_interaction_summary')
async def test_summarize_interaction_success(mock_save_summary, mock_api_logger, mock_run_context):
    """Test successfully summarizing the interaction and saving it."""
    summary_content = "User asked about password reset and was given instructions."
    test_user_id = "user_summary_success"
    test_session_id = "session_abc123"

    mock_run_context.participant.identity = test_user_id
    mock_run_context.room = MagicMock()
    mock_run_context.room.sid = test_session_id

    mock_save_summary.return_value = True  # Simulate successful save

    expected_response = "Okay, I've made a note of that for next time."

    actual_response = await summarize_interaction_for_next_session(mock_run_context, summary_content)

    mock_api_logger.info.assert_any_call(
        f"Attempting to save interaction summary for User: {test_user_id}, Session: {test_session_id}. Summary: '{summary_content}'")
    mock_save_summary.assert_called_once_with(
        user_id=test_user_id, session_id=test_session_id, summary_text=summary_content)
    assert actual_response == expected_response
    mock_api_logger.info.assert_any_call(
        f"Successfully saved interaction summary for User: {test_user_id}, Session: {test_session_id}")


@pytest.mark.asyncio
@patch('backend.api.logger')
@patch('backend.api.db_driver.save_interaction_summary')
async def test_summarize_interaction_save_fails(mock_save_summary, mock_api_logger, mock_run_context):
    """Test handling for when saving the summary fails (db_driver returns False)."""
    summary_content = "User was unhappy with the resolution."
    test_user_id = "user_summary_fail_save"
    test_session_id = "session_def456"

    mock_run_context.participant.identity = test_user_id
    mock_run_context.room = MagicMock()
    mock_run_context.room.sid = test_session_id

    mock_save_summary.return_value = False  # Simulate save failure

    expected_response = "I tried to save a note of our conversation, but there was an issue. Please try again later if it's important."

    actual_response = await summarize_interaction_for_next_session(mock_run_context, summary_content)

    mock_api_logger.info.assert_any_call(
        f"Attempting to save interaction summary for User: {test_user_id}, Session: {test_session_id}. Summary: '{summary_content}'")
    mock_save_summary.assert_called_once_with(
        user_id=test_user_id, session_id=test_session_id, summary_text=summary_content)
    assert actual_response == expected_response
    mock_api_logger.warning.assert_any_call(
        f"Failed to save interaction summary to DB (db_driver returned False) for User: {test_user_id}, Session: {test_session_id}")


@pytest.mark.asyncio
@patch('backend.api.logger')
@patch('backend.api.db_driver.save_interaction_summary')
async def test_summarize_interaction_db_driver_error(mock_save_summary, mock_api_logger, mock_run_context):
    """Test handling for DBDriverError when trying to save the summary."""
    summary_content = "Critical interaction details."
    test_user_id = "user_summary_db_error"
    test_session_id = "session_ghi789"
    simulated_db_error_message = "Simulated DB error during summary save"

    mock_run_context.participant.identity = test_user_id
    mock_run_context.room = MagicMock()
    mock_run_context.room.sid = test_session_id

    mock_save_summary.side_effect = DBDriverError(simulated_db_error_message)

    expected_response = "Sorry, I encountered a system issue while trying to save our conversation summary. Please try again later."

    actual_response = await summarize_interaction_for_next_session(mock_run_context, summary_content)

    mock_api_logger.info.assert_any_call(
        f"Attempting to save interaction summary for User: {test_user_id}, Session: {test_session_id}. Summary: '{summary_content}'")
    mock_save_summary.assert_called_once_with(
        user_id=test_user_id, session_id=test_session_id, summary_text=summary_content)
    assert actual_response == expected_response
    mock_api_logger.error.assert_any_call(
        f"Database error while saving interaction summary for User: {test_user_id}, Session: {test_session_id}. Error: {simulated_db_error_message}")


# We'll also need a test for the Firebase token verification if we build that into a tool
# and tests for the Supabase DB driver functions.

# Example placeholder for db_driver tests (would be in tests/backend/test_db_driver.py)
# def test_connect_to_supabase():
# pass
