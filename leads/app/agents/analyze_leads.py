from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableParallel, RunnableLambda
from loguru import logger

from app.core import Config
from app.schemas import (
    ContactScraperInput, ContactScraperOutput,
    VisualAnalysisInput, VisualAnalysisOutput
)
from app.schemas.lead import Lead
from app.schemas.state import State
from app.tools import contact_scraper, visual_analysis

# --- Constants and Configuration ---

# System prompt for the Gemini model to guide its UI/UX analysis.
VISUAL_ANALYSIS_SYSTEM_PROMPT = \
    """
    You are a world-class UI/UX design critic. You will be provided with screenshots of a website.
    Based on the screenshots, provide a detailed analysis covering the following points:
    1.  **First Impression & Visual Appeal:** Is the design modern and trustworthy?
    2.  **Navigation & Usability:** How easy is it for users to find what they need?
    3.  **Responsiveness:** How well does the site adapt between desktop, tablet, and mobile views?
    4.  **Suggestions for Improvement:** Provide a bulleted list of 3 actionable recommendations.

    Your final output should be a detailed, well-structured markdown report.
    Be as critical as you can be about your analysis. Find any and all flaws and errors possible.
    Do not reference the prompt, or mention any affirmations to the prompt, or any other irrelevant information.
    Just output the analysis.
    """


# --- Helper Functions for Lead Analysis ---

def get_contact_info(lead: Lead) -> ContactScraperOutput:
    """
    Scrapes a lead's website to extract contact information.

    Invokes the `contact_scraper` tool to find emails, phone numbers,
    and social media links on the provided website URL.

    Args:
        lead: The lead object containing the website URL to scrape.

    Returns:
        A `ContactScraperOutput` object containing the scraped information.
        Returns an empty object if scraping fails or the URL is invalid.
    """
    if not lead.website:
        logger.warning(f"Lead {lead.name} has no website URL. Skipping contact scraping.")
        return ContactScraperOutput(emails=[], phone_numbers=[], social_media=[])

    logger.info(f"Scraping contact info for {lead.name} from {lead.website}")
    try:
        # Prepare and invoke the contact scraper tool.
        scraper_input = ContactScraperInput(url=lead.website).model_dump()
        result = contact_scraper.invoke(scraper_input)
        logger.debug(f"Successfully scraped contact info for {lead.name}.")
        return result
    except Exception:
        # Log any exception during the scraping process and return a default
        # empty object to prevent downstream errors.
        logger.exception(f"Failed to scrape contact info for {lead.name}.")
        return ContactScraperOutput(emails=[], phone_numbers=[], social_media=[])


def get_visual_analysis(lead: Lead) -> tuple[VisualAnalysisOutput, str]:
    """
    Performs a visual analysis of a lead's website.

    This function first uses the `visual_analysis` tool to capture screenshots
    of the website. It then sends these screenshots to a Gemini model for a
    detailed UI/UX review based on the `VISUAL_ANALYSIS_SYSTEM_PROMPT`.

    Args:
        lead: The lead object containing the website URL to analyze.

    Returns:
        A tuple containing:
        - A `VisualAnalysisOutput` object with screenshot data.
        - A string with the markdown-formatted UI/UX review from the LLM.
        Returns empty objects `(VisualAnalysisOutput([]), "")` if analysis fails.
    """
    if not lead.website:
        logger.warning(f"Lead '{lead.name}' has no website URL. Skipping visual analysis.")
        return VisualAnalysisOutput(root=[]), ""

    logger.info(f"Performing visual analysis for {lead.name} at {lead.name}")

    try:
        # Step 1: Capture screenshots of the website.
        analysis_input = VisualAnalysisInput(url=lead.website).model_dump()
        visual_analysis_result: VisualAnalysisOutput | str = visual_analysis.invoke(analysis_input)

        # Handle cases where the tool returns an error string instead of data.
        if isinstance(visual_analysis_result, str) or not visual_analysis_result.root:
            logger.error(f"Visual analysis tool failed for {lead.name}. Reason: {visual_analysis_result}")
            return VisualAnalysisOutput(root=[]), ""

        # Step 2: Initialize the Gemini client for the review.
        gemini_client = init_chat_model(
            "gemini-2.5-flash",
            model_provider="google_genai",
            api_key=Config.GEMINI_API_KEY
        )

        # Step 3: Construct the prompt with the system message and screenshots.
        messages = [
            SystemMessage(content=VISUAL_ANALYSIS_SYSTEM_PROMPT),
            HumanMessage(
                content=[{"type": "text", "text": "Here are your screenshots:"}]
                        + [
                            {"type": "image_url", "image_url": screenshot.image}
                            for screenshot in visual_analysis_result.root
                        ]
            ),
        ]

        # Step 4: Invoke the Gemini model to get the UI/UX review.
        response = gemini_client.invoke(messages)
        logger.info(f"Successfully generated website review for {lead.name}")
        return visual_analysis_result, response.text

    except Exception:
        # Log any exceptions during the process and return empty results.
        logger.exception(f"An error occurred during visual analysis for {lead.name}.")
        return VisualAnalysisOutput(root=[]), ""


def analyze_lead(lead: Lead) -> Lead:
    """
    Analyzes a single lead by running contact scraping and visual analysis in parallel.

    Args:
        lead: The lead object to be analyzed.

    Returns:
        An updated lead object with the analysis results populated.
    """
    logger.info(f"Starting parallel analysis for lead: {lead.name}")
    try:
        # Define the parallel tasks for scraping contacts and performing visual analysis.
        parallel_runner = RunnableParallel(
            contacts_scraper=get_contact_info,
            visual_analysis=get_visual_analysis
        )

        # Execute the tasks in parallel for the given lead.
        result = parallel_runner.invoke(lead)

        # Safely extract results from the parallel execution.
        contacts_data: ContactScraperOutput = result.get("contacts_scraper",
                                                         ContactScraperOutput(emails=[], phone_numbers=[],
                                                                              social_media=[]))
        visual_data: tuple[VisualAnalysisOutput, str] = result.get("visual_analysis",
                                                                   (VisualAnalysisOutput(root=[]), ""))

        # Update the lead object with the new information.
        analyzed_lead = lead.model_copy(
            update={
                "emails": contacts_data.emails,
                "phone_numbers": contacts_data.phone_numbers,
                "social_media": contacts_data.social_media,
                "screenshots": visual_data[0].root,
                "website_review": visual_data[1]
            }
        )
        logger.info(f"Successfully analyzed lead: {lead.name}")
        return analyzed_lead

    except Exception:
        logger.exception(f"Failed to analyze lead '{lead.name}'. Returning original lead.")
        return lead.model_copy()


# --- Main Node Function ---

def analyze_leads_node(state: State) -> State:
    """
    Analyzes a batch of leads from the state using a parallel processing pipeline.

    This node takes a list of leads from the current state, runs the `analyze_lead`
    function on each of them in a batch, and updates the state with the
    enriched lead information.

    Args:
        state: The current application state containing the list of leads.

    Returns:
        An updated state object with the analyzed leads.
    """
    if not state.leads:
        logger.warning("No leads to analyze. Skipping analysis node.")
        return state.model_copy()

    logger.info("Starting analysis for a batch of %d leads.", len(state.leads))
    try:
        # Create a runnable lambda to apply the `analyze_lead` function.
        runnable = RunnableLambda(analyze_lead)

        # Execute the analysis for all leads in the state in a batch.
        # The `.batch()` method efficiently processes the list.
        batch_results: list[Lead] = runnable.batch(state.leads)
        logger.info("Finished batch analysis of leads.")

        # Return a new state object with the updated leads list.
        return state.model_copy(update={"leads": batch_results})
    except Exception:
        logger.exception("A critical error occurred during the batch lead analysis.")
        # Return the original state to prevent data loss.
        return state.model_copy()
