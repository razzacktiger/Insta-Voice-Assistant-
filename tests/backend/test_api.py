# tests/backend/test_api.py
import pytest
from unittest.mock import MagicMock, patch

# Import the actual functions from backend.api
from backend.api import get_user_account_info, answer_from_company_kb, summarize_interaction_for_next_session

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
async def test_get_user_account_info_success(mock_logger, mock_run_context):
    """Test successfully retrieving user account information."""
    mock_run_context.participant.identity = "test_user_found"
    result = await get_user_account_info(mock_run_context)
    assert "Email: test@example.com" in result
    assert "Subscription: Premium" in result
    assert "(Mocked)" in result
    mock_logger.error.assert_not_called()
    mock_logger.info.assert_any_call(
        f"Attempting to get user account info for participant: {mock_run_context.participant.identity}"
    )


@pytest.mark.asyncio
@patch('backend.api.logger')
async def test_get_user_account_info_user_not_found(mock_logger, mock_run_context):
    """Test handling for a user not found in the database."""
    mock_run_context.participant.identity = "test_user_not_found"
    result = await get_user_account_info(mock_run_context)
    assert "couldn't find an account" in result.lower()
    assert "(Mocked)" in result
    mock_logger.error.assert_not_called()
    mock_logger.info.assert_any_call(
        f"Attempting to get user account info for participant: {mock_run_context.participant.identity}"
    )


@pytest.mark.asyncio
@patch('backend.api.logger')
async def test_get_user_account_info_db_error(mock_logger, mock_run_context):
    """Test handling for a database error during lookup."""
    test_identity = "some_other_id_causing_simulated_error"
    mock_run_context.participant.identity = test_identity
    result = await get_user_account_info(mock_run_context)
    assert "encountered an issue" in result.lower()
    assert "(Mocked)" in result
    mock_logger.info.assert_any_call(
        f"Attempting to get user account info for participant: {test_identity}")
    mock_logger.error.assert_called_once_with(
        f"Simulated DB error or unexpected user_id for get_user_account_info: {test_identity}"
    )

# --- Tests for answer_from_company_kb ---


@pytest.mark.asyncio
@patch('backend.api.logger')
async def test_answer_from_company_kb_found_password(mock_logger, mock_run_context):
    """Test successfully finding and returning an answer from the KB (password case)."""
    user_query = "How do I reset my password?"
    result = await answer_from_company_kb(mock_run_context, user_query)
    assert "reset your password" in result.lower()
    assert "(Mocked from KB)" in result
    mock_logger.info.assert_called_once_with(
        f"Answering from KB. Query: {user_query}")


@pytest.mark.asyncio
@patch('backend.api.logger')
async def test_answer_from_company_kb_found_feature_x(mock_logger, mock_run_context):
    """Test successfully finding and returning an answer from the KB (feature x case)."""
    user_query = "Tell me about feature x"
    result = await answer_from_company_kb(mock_run_context, user_query)
    assert "feature x allows you" in result.lower()
    assert "(Mocked from KB)" in result
    mock_logger.info.assert_called_once_with(
        f"Answering from KB. Query: {user_query}")


@pytest.mark.asyncio
@patch('backend.api.logger')
async def test_answer_from_company_kb_not_found(mock_logger, mock_run_context):
    """Test handling when no relevant information is found in the KB."""
    user_query = "What is the meaning of life?"
    result = await answer_from_company_kb(mock_run_context, user_query)
    assert "couldn't find specific information" in result.lower()
    assert "(Mocked)" in result
    mock_logger.info.assert_called_once_with(
        f"Answering from KB. Query: {user_query}")


@pytest.mark.asyncio
@patch('backend.api.logger')
async def test_answer_from_company_kb_db_error(mock_logger, mock_run_context):
    """Test handling for a database/RAG error during KB lookup."""
    user_query = "Tell me about product Y."
    result = await answer_from_company_kb(mock_run_context, user_query)
    assert "couldn't find specific information" in result.lower()
    mock_logger.info.assert_called_once_with(
        f"Answering from KB. Query: {user_query}")
    mock_logger.error.assert_not_called()
    pass

# --- Tests for summarize_interaction_for_next_session ---


@pytest.mark.asyncio
@patch('backend.api.logger')
async def test_summarize_interaction_success(mock_logger, mock_run_context):
    """Test successfully summarizing the interaction and saving it."""
    summary_content = "User asked about password reset and was given instructions."
    test_identity = "test_user_to_save_summary"
    mock_run_context.participant.identity = test_identity
    result = await summarize_interaction_for_next_session(mock_run_context, summary_content)
    assert "Okay, I've made a note of that for next time." in result
    mock_logger.info.assert_any_call(
        f"Summarizing interaction: {summary_content}")
    mock_logger.info.assert_any_call(
        f"Successfully saved summary for user {test_identity}: '{summary_content}' (Mocked)"
    )
    mock_logger.error.assert_not_called()


@pytest.mark.asyncio
@patch('backend.api.logger')
async def test_summarize_interaction_db_error(mock_logger, mock_run_context):
    """Test handling for a database error when trying to save the summary."""
    summary_content = ""
    test_identity = "test_user_summary_fail"
    mock_run_context.participant.identity = test_identity
    result = await summarize_interaction_for_next_session(mock_run_context, summary_content)
    assert "I tried to save a note, but there was an issue." in result
    mock_logger.info.assert_any_call(
        f"Summarizing interaction: {summary_content}")
    mock_logger.error.assert_called_once_with(
        f"Failed to save summary for user {test_identity}. Summary provided: '{summary_content}' (Mocked)"
    )

# We'll also need a test for the Firebase token verification if we build that into a tool
# and tests for the Supabase DB driver functions.

# Example placeholder for db_driver tests (would be in tests/backend/test_db_driver.py)
# def test_connect_to_supabase():
# pass
