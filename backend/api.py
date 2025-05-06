from __future__ import annotations

import logging
from typing import Annotated

from livekit.agents import function_tool, RunContext
# We'll need to import from db_driver.py later
# from . import db_driver

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
    logger.info(
        f"Attempting to get user account info for participant: {ctx.participant.identity}")

    # TODO:
    # 1. Determine user_id from ctx (e.g., participant identity, metadata, or a lookup via Firebase token)
    # 2. Call db_driver.get_user_from_db(user_id)
    # 3. Format and return the user's account information as a string.
    # 4. Handle cases where the user is not found or a database error occurs.

    # Example placeholder response
    user_id = ctx.participant.identity  # Placeholder, might need more robust mapping

    # Simulate DB call - replace with actual db_driver call
    if user_id == "test_user_found":
        return f"User {user_id}: Email: test@example.com, Subscription: Premium. (Mocked)"
    elif user_id == "test_user_not_found":
        return f"I couldn't find an account associated with the ID: {user_id}. (Mocked)"
    else:
        # In a real scenario, you might want to return a more generic "I couldn't retrieve the info."
        # and log the detailed error.
        logger.error(
            f"Simulated DB error or unexpected user_id for get_user_account_info: {user_id}")
        return f"Sorry, I encountered an issue trying to retrieve account details for {user_id}. (Mocked)"


@function_tool()
async def answer_from_company_kb(
    ctx: RunContext,
    query: Annotated[str, "The user's question to search for in the company knowledge base."],
) -> str:
    """Searches the company knowledge base (KB) for an answer to the user's query.
    Use this tool for general questions about the company, its products, FAQs, or how-to guides.
    """
    logger.info(f"Answering from KB. Query: {query}")

    # TODO:
    # 1. Call db_driver.query_knowledge_base(query) which will handle embedding the query
    #    and searching the vector DB (Supabase with pgvector).
    # 2. Format the retrieved information into a coherent answer.
    # 3. Handle cases where no relevant information is found or a database error occurs.

    # Example placeholder response
    if "password" in query.lower():
        return "To reset your password, go to the login page and click 'Forgot Password'. (Mocked from KB)"
    elif "feature x" in query.lower():
        return "Feature X allows you to do amazing things with our product! (Mocked from KB)"
    else:
        return "I couldn't find specific information about that in our knowledge base right now. Is there anything else I can help with? (Mocked)"


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

    # TODO:
    # 1. Determine user_id from ctx (as in get_user_account_info).
    # 2. Call db_driver.save_interaction_summary(user_id, interaction_summary).
    # 3. Handle potential database errors.

    # Example placeholder response
    user_id = ctx.participant.identity  # Placeholder

    # Simulate DB call
    if user_id and interaction_summary:
        logger.info(
            f"Successfully saved summary for user {user_id}: '{interaction_summary}' (Mocked)")
        return "Okay, I've made a note of that for next time."
    else:
        logger.error(
            f"Failed to save summary for user {user_id}. Summary provided: '{interaction_summary}' (Mocked)")
        return "I tried to save a note, but there was an issue. (Mocked)"

# We might add more tools later, e.g., for creating support tickets, etc.
