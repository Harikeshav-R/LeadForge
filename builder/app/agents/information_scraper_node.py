from loguru import logger

from app.schemas import State, InformationScraperInput, InformationScraperOutput
from app.tools import information_scraper


def information_extractor_node(state: State) -> State:
    """
    Extracts content from a target website using an information scraper.

    This function takes the initial URL and scrape limit from the state,
    invokes the `information_scraper`, and updates the state with either
    the list of scraped pages or an error message if the scrape fails.

    Args:
        state: The current workflow state, containing `initial_website_url`
               and `initial_website_scrape_limit`.

    Returns:
        State: An updated copy of the state. If successful, `pages_scraped`
               is populated and `scrape_error` is None. If failed,
               `pages_scraped` is empty and `scrape_error` contains the
               error message.
    """
    website_url = state.initial_website_url
    logger.info(f"Starting information extraction for: {website_url}")

    try:
        # 1. Prepare the input for the scraper
        input_data = InformationScraperInput(
            url=website_url,
            limit=state.initial_website_scrape_limit,
        ).model_dump()

        logger.debug(f"Invoking information_scraper with input: {input_data}")

        # 2. Invoke the scraper
        scraped_information: InformationScraperOutput = information_scraper.invoke(input_data)

        page_count = len(scraped_information.pages)
        logger.info(f"Successfully scraped {page_count} pages from {website_url}.")

        # 3. Return the new state on success
        return state.model_copy(
            update={
                "pages_scraped": scraped_information.pages,
            }
        )

    except Exception as e:
        # 4. Handle any exception during the scraping process
        error_message = f"Failed to scrape website {website_url}: {e}"
        logger.error(error_message, exc_info=True)  # exc_info=True logs the stack trace

        # 5. Return the new state on failure
        return state.model_copy(
            update={
                "pages_scraped": [],  # Ensure pages list is empty on failure
            }
        )
