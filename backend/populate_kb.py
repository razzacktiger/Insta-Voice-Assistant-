import asyncio
import logging

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Relative import for db_driver assuming the script is run from the project root
# or the backend directory has been added to PYTHONPATH.
# If running from project root: python -m backend.populate_kb
try:
    from db_driver import store_knowledge_base_article, DBDriverError
except ImportError:
    logger.error("Failed to import from db_driver. Ensure you are running from the project root as 'python -m backend.populate_kb' or that backend module is in PYTHONPATH.")
    # As a fallback for local execution directly within backend/ for simplicity during dev,
    # though module execution is preferred.
    import sys
    import os
    # Add the parent directory (project root) to sys.path to allow for absolute-like imports from backend
    # This is a bit of a hack for direct script execution convenience.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from backend.db_driver import store_knowledge_base_article, DBDriverError


SAMPLE_ARTICLES = [
    {
        "title": "How to Reset Your Password",
        "content": "If you've forgotten your password, you can reset it by visiting our login page and clicking the 'Forgot Password' link. You will then receive an email with further instructions. Please check your spam folder if you don't see it within a few minutes."
    },
    {
        "title": "Understanding Your Subscription Tiers",
        "content": "We offer three subscription tiers: Basic, Premium, and Enterprise. The Basic tier is free and includes core features. The Premium tier adds advanced analytics and priority support. The Enterprise tier provides custom solutions and dedicated account management. You can find detailed feature comparisons on our pricing page."
    },
    {
        "title": "Integrating with Third-Party Services",
        "content": "Our platform supports integration with a variety of third-party services through our API and dedicated connectors. To integrate a service, go to the 'Integrations' section in your account settings. You will need API keys from the third-party service. Detailed guides for each supported integration are available in our help center."
    },
    {
        "title": "Troubleshooting Common Login Issues",
        "content": "If you're having trouble logging in, first ensure your email and password are correct. Check for typos and make sure your Caps Lock key is off. If you've recently reset your password, try using the new one. Clearing your browser cache and cookies can also resolve some login problems. If issues persist, contact support with the error message you are receiving."
    }
]


async def main():
    logger.info(
        f"Starting to populate knowledge base with {len(SAMPLE_ARTICLES)} articles...")
    successful_uploads = 0
    failed_uploads = 0

    for i, article_data in enumerate(SAMPLE_ARTICLES):
        title = article_data["title"]
        content = article_data["content"]
        logger.info(
            f"Processing article {i+1}/{len(SAMPLE_ARTICLES)}: '{title}'")
        try:
            # Metadata is optional, so we're not passing it here for simplicity
            success = await store_knowledge_base_article(title=title, content=content)
            if success:
                logger.info(f"Successfully stored article: '{title}'")
                successful_uploads += 1
            else:
                logger.warning(
                    f"Failed to store article (db_driver returned False): '{title}'")
                failed_uploads += 1
        except DBDriverError as e:
            logger.error(f"DBDriverError while storing article '{title}': {e}")
            failed_uploads += 1
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while storing article '{title}': {e}")
            failed_uploads += 1
        logger.info("---")  # Separator for readability

    logger.info("Knowledge base population complete.")
    logger.info(f"Successfully uploaded: {successful_uploads} articles.")
    logger.info(f"Failed to upload: {failed_uploads} articles.")

if __name__ == "__main__":
    # This script is intended to be run as a module from the project root, e.g.,
    # python -m backend.populate_kb
    # The try-except for imports at the top attempts to handle direct execution too, but it's less robust.
    asyncio.run(main())
