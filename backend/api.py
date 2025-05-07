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
    user_id = ctx.participant.identity  # Get user_id for logging
    logger.info(
        f"Attempting to answer from KB. User: {user_id}, Query: '{query}'")

    try:
        articles = await db_driver.query_knowledge_base(query)

        if not articles:  # Handles None or empty list
            logger.warning(
                f"No KB articles found for query: '{query}'. User: {user_id}")
            return "I couldn't find specific information about that in our knowledge base. Could you try rephrasing, or is there something else I can help with?"

        if len(articles) == 1:
            article = articles[0]
            # Ensure title and content exist, providing defaults if not (though db should ideally guarantee them)
            title = article.get('title', 'N/A')
            content = article.get('content', 'No content available.')
            response = (
                "I found this in our knowledge base:\n\n"
                f"Title: {title}\n"
                f"Content: {content}"
            )
            logger.info(
                f"Successfully found 1 article for query: '{query}'. User: {user_id}")
            return response
        else:
            formatted_articles = []
            for article in articles:
                title = article.get('title', 'N/A')
                content = article.get('content', 'No content available.')
                formatted_articles.append(
                    f"Title: {title}\nContent: {content}")

            # Corrected response construction for multiple articles
            response_header = "Here's what I found in our knowledge base related to your query:\n\n"
            articles_string = "\n\n---\n\n".join(formatted_articles)
            response = response_header + articles_string

            logger.info(
                f"Successfully found {len(articles)} articles for query: '{query}'. User: {user_id}")
            return response

    except DBDriverError as e:
        logger.error(
            f"Database error during KB query for User: {user_id}, Query: '{query}'. Error: {e}")
        return "Sorry, I encountered an issue trying to search our knowledge base. Please try again later."

    # Fallback, though logic above should cover all path defined by tests
    # return "I was unable to process your request to the knowledge base at this time."


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
    user_id = ctx.participant.identity
    # Assuming room SID is a good unique identifier for the session.
    # If not, this might need to be adjusted based on how sessions are tracked.
    session_id = ctx.room.sid if ctx.room else "unknown_session"

    logger.info(
        f"Attempting to save interaction summary for User: {user_id}, Session: {session_id}. Summary: '{interaction_summary}'")

    try:
        success = await db_driver.save_interaction_summary(
            user_id=user_id,
            session_id=session_id,
            summary_text=interaction_summary
        )

        if success:
            logger.info(
                f"Successfully saved interaction summary for User: {user_id}, Session: {session_id}")
            return "Okay, I've made a note of that for next time."
        else:
            logger.warning(
                f"Failed to save interaction summary to DB (db_driver returned False) for User: {user_id}, Session: {session_id}")
            return "I tried to save a note of our conversation, but there was an issue. Please try again later if it's important."

    except DBDriverError as e:
        logger.error(
            f"Database error while saving interaction summary for User: {user_id}, Session: {session_id}. Error: {e}")
        return "Sorry, I encountered a system issue while trying to save our conversation summary. Please try again later."

    # Fallback, though the logic above should cover all paths defined by the tests.
    # return "An unexpected error occurred while trying to save the summary."

# We might add more tools later, e.g., for creating support tickets, etc.
