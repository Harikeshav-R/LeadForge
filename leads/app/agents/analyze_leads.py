from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableParallel, RunnableLambda

from app.core.config import Config
from app.schemas import ContactScraperInput, ContactScraperOutput, VisualAnalysisInput, VisualAnalysisOutput
from app.schemas.lead import Lead
from app.schemas.state import State
from app.tools import contact_scraper, visual_analysis

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


def get_contact_info(lead: Lead) -> ContactScraperOutput:
    return contact_scraper.invoke(
        ContactScraperInput(
            url=lead.website
        ).model_dump()
    )


def get_visual_analysis(lead: Lead) -> tuple[VisualAnalysisOutput, str]:
    visual_analysis_result: VisualAnalysisOutput | str = visual_analysis.invoke(
        VisualAnalysisInput(
            url=lead.website
        ).model_dump()
    )

    if isinstance(visual_analysis_result, str):
        return VisualAnalysisOutput([]), ""

    gemini_client = init_chat_model(
        "gemini-2.5-flash",
        model_provider="google_genai",
        api_key=Config.GEMINI_API_KEY
    )

    messages = [
        SystemMessage(
            content=VISUAL_ANALYSIS_SYSTEM_PROMPT
        ),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": f"Here are your screenshots:"
                }
            ]
        )
    ]

    messages[1].content.extend(
        [
            {
                "type": "image_url",
                "image_url": screenshot.image
            }
            for screenshot in visual_analysis_result.root
        ]
    )

    response = gemini_client.invoke(messages)
    return visual_analysis_result, response.text


def analyze_lead(lead: Lead) -> Lead:
    parallel_runner = RunnableParallel(
        contacts_scraper=get_contact_info,
        visual_analysis=get_visual_analysis
    )

    result = parallel_runner.invoke(lead)

    analyzed_lead = lead.model_copy(
        update={
            "emails": result.get("contacts_scraper").emails,
            "phone_numbers": result.get("contacts_scraper").phone_numbers,
            "social_media": result.get("contacts_scraper").social_media,

            "screenshots": result.get("visual_analysis")[0].root,
            "website_review": result.get("visual_analysis")[1]
        }
    )

    return analyzed_lead


def analyze_leads_node(state: State) -> State:
    runnable = RunnableLambda(analyze_lead)
    batch_results = runnable.batch(state.leads)

    return state.model_copy(
        update={
            "leads": batch_results
        }
    )
