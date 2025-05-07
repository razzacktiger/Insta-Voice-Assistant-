from __future__ import annotations

import logging
from typing import Annotated

from livekit.agents import function_tool, RunContext
# We'll need to import from db_driver.py later
# from . import db_driver
from . import db_driver  # Import db_driver
from .db_driver import DBDriverError  # Import DBDriverError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Placeholder for user identification, this will need to be refined
# based on how authentication and LiveKit participant identity are linked.
# For now, we assume a user_id can be made available to the tool,
# or we might derive it from ctx.room.name or participant metadata.


@function_tool()
async def get_user_account_info(
    ctx: RunContext,
    # user_id: Annotated[str, "The unique identifier for the user whose account info is being requested."],
) -> str:
    """Retrieves account information for a given user.
    This tool should be used when a user asks about their specific account details
    like subscription tier, email address, or other stored profile information.

    The user's identity will be implicitly determined from the session.
    """
    user_id = ctx.participant.identity
    logger.info(
        f"Attempting to get user account info for participant: {user_id}")

    try:
        # Call db_driver to get user account information
        account_info = await db_driver.get_user_account_info_from_db(user_id)

        if account_info:
            # Format the success string as expected by the tests
            response = f"Okay, I found these details for user {user_id}:\nName: {account_info.get('full_name', 'N/A')}\nEmail: {account_info.get('email', 'N/A')}\nSubscription: {account_info.get('subscription_tier', 'N/A')}"
            logger.info(
                f"Successfully retrieved account details for user {user_id}.")
            return response
        else:
            # Handle cases where the user is not found (db_driver returned None)
            warning_message = f"No account details found in DB for user ID: {user_id}"
            logger.warning(warning_message)
            return f"I couldn't find any account details for user ID: {user_id}. Please ensure the ID is correct or if you need to register."
    except DBDriverError as e:
        # This case handles when db_driver explicitly raised an error (e.g. client not init, db connection issue)
        error_message = f"Failed to retrieve account details for {user_id} from DB driver. Error: {e}"
        # This matches the logger.error assertion in the test
        logger.error(error_message)
        # Return the user-facing message expected by test_get_user_account_info_db_driver_exception
        return f"Sorry, I encountered an issue trying to retrieve account details for user ID: {user_id}. Please try again later."


@function_tool()
async def answer_from_company_kb(
    ctx: RunContext,
    query: Annotated[str, "The user's question to search for in the company knowledge base."],
) -> str:
    """Searches the company knowledge base (KB) for an answer to the user's query.
    Use this tool for general questions about the company, its products, FAQs, or how-to guides.
    """
    logger.info(f"Answering from KB. Query: {query}")
    raise NotImplementedError("answer_from_company_kb is not yet implemented")

    # TODO:
    # 1. Call db_driver.query_knowledge_base(query) which will handle embedding the query
    #    and searching the vector DB (Supabase with pgvector).
    # 2. Format the retrieved information into a coherent answer.
    # 3. Handle cases where no relevant information is found or a database error occurs.

    # Example placeholder response
    # if "password" in query.lower():
    #     return "To reset your password, go to the login page and click 'Forgot Password'. (Mocked from KB)"
    # elif "feature x" in query.lower():
    #     return "Feature X allows you to do amazing things with our product! (Mocked from KB)"
    # else:
    #     return "I couldn't find specific information about that in our knowledge base right now. Is there anything else I can help with? (Mocked)"


@function_tool()
async def summarize_interaction_for_next_session(
    ctx: RunContext,
    interaction_summary: Annotated[str,
                                   "A brief summary of the key points and outcomes of the current interaction."]
) -> str:
    """Saves a summary of the current interaction for future reference.
    The LLM should call this tool when an interaction has reached a resolution
    or a significant milestone, providing a concise summary.
    """
    logger.info(f"Summarizing interaction: {interaction_summary}")
    raise NotImplementedError(
        "summarize_interaction_for_next_session is not yet implemented")

    # TODO:
    # 1. Determine user_id from ctx (as in get_user_account_info).
    # 2. Call db_driver.save_interaction_summary(user_id, interaction_summary).
    # 3. Handle potential database errors.

    # Example placeholder response
    # user_id = ctx.participant.identity  # Placeholder

    # Simulate DB call
    # if user_id and interaction_summary:
    #     logger.info(
    #         f"Successfully saved summary for user {user_id}: '{interaction_summary}' (Mocked)")
    #     return "Okay, I've made a note of that for next time."
    # else:
    #     logger.error(
    #         f"Failed to save summary for user {user_id}. Summary provided: '{interaction_summary}' (Mocked)")
    #     return "I tried to save a note, but there was an issue. (Mocked)"

# We might add more tools later, e.g., for creating support tickets, etc.
