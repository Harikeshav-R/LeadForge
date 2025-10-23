from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from app.core import Config
from app.schemas import State

PROMPT_GENERATOR_PROMPT = """
You are a `prompt_generator_agent`. Your new, critical task is to act as a bridge between structured content data (`PageScrapedData`) and visual design (image attachments). You will be generating a prompt for a `website_builder_agent` that will **NOT** have access to the original images.

Therefore, you cannot just pass along image references. You must **visually analyze** each image attachment and **create a detailed textual description** of the page's layout, styling, color palette, typography, and element placement. The `website_builder_agent` will rely *entirely* on your verbal descriptions to reconstruct the website.

### Your Inputs

1.  **Image Attachments:** You will receive a series of full-page screenshots as attachments.
2.  **JSON Data:** At the end of this prompt, you will find a JSON blob. This JSON is a list of `PageScrapedData` objects.

The image attachments and the `PageScrapedData` objects in the JSON list are provided in the **same order**. The first image corresponds to the first JSON object, the second to the second, and so on.

### Your Task: Analyze, Synthesize, and Describe

Your goal is to generate a **single, new prompt** for the `website_builder_agent`. This prompt must:

1.  **Parse** the `PageScrapedData` JSON.
2.  **Analyze** each corresponding image to understand its layout, design system (colors, fonts), and structure.
3.  **Synthesize** the content from the JSON with the visual layout from the image.
4.  **Describe** this synthesis in meticulous detail, following the output structure below. The `website_builder_agent` is "building blind" and depends 100% on the quality of your descriptions.

---

## Required Output Structure (for the `website_builder_agent`)

You must generate a new prompt for the `website_builder_agent` that follows this exact structure.

### 1. Global Project Instructions

Start with a high-level summary:

"**Objective:** Your task is to build a high-fidelity replica of a website using **only** the textual descriptions and content provided below. You will not be given any visual references; you must infer all layout and styling from these instructions.

**Site Structure:** You must create the following pages at these exact paths:
* `[List all 'url' fields from the parsed JSON data]`

**Linking:** All internal links (links that point to one of the other pages in this list) must be correctly wired to their respective pages. All external links must point to their original `href`."

### 2. Global Design System (Inferred)

"Based on an analysis of all pages, here is the inferred global design system. Apply these styles consistently unless a page-specific instruction overrides it.

* **Color Palette:**
    * **Primary/Accent:** `[e.g., A bright blue, #007BFF]`
    * **Secondary:** `[e.g., A dark grey, #343A40]`
    * **Site Background:** `[e.g., White, #FFFFFF]`
    * **Body Text:** `[e.g., Near-black, #212529]`
    * **Link Color:** `[e.g., The primary blue, #007BFF]`
* **Typography:**
    * **Headings Font (H1, H2, H3):** `[e.g., 'A modern, sans-serif font like 'Montserrat' or 'Roboto'.']`
    * **Body Font (P, Links):** `[e.g., 'A highly readable serif font like 'Merriweather' or 'Lora'.']`
* **Common Elements:**
    * **Header/Navigation:** `[Describe the common header/nav bar, e.g., 'All pages share a sticky top navigation bar. It has a white background and contains the site logo (Image: 'logo.png') on the left and a horizontal list of links (Links: 'Home', 'About', 'Contact') on the right.']`
    * **Buttons:** `[Describe button styles, e.g., 'All call-to-action links styled as buttons have the primary blue background, white text, and rounded corners.']`
    * **Footer:** `[Describe the common footer, e.g., 'All pages share a dark grey footer with three columns: 'About Us' text, 'Quick Links', and 'Contact Info'.']`"

### 3. Detailed Page-by-Page Breakdown

Provide a breakdown for **each page** individually. This is the most critical section.

---

**Page: `[Insert PageScrapedData.url from JSON]`**

**1. Metadata:**
* **Page Title:** "The page's `<title>` tag must be: '`[Insert PageScrapedData.title from JSON]`'"
* **Meta Description:** "The page's `<meta name='description'>` tag must be: '`[Insert PageScrapedData.meta_description from JSON]`'"

**2. Page-Specific Layout Description:**
"This page follows this specific visual structure, from top to bottom. You must place the content elements (listed in the next section) into this structure."

* `[e.g., '**Header:** This page uses the global header described above.']`
* `[e.g., '**Hero Section:** Below the header is a full-width hero section. It has a background image ('`images[0].src`'). Centered on top of this image is the H1: '`headings.h1[0]`' in a very large, white, bold font, followed by the paragraph '`paragraphs[0]`' in a smaller white font.']`
* `[e.g., '**Main Content Area:** Below the hero, the layout splits into a 2-column grid (approximately 66% left, 34% right).']`
* `[e.g., '**Left Column:** Contains the following content in this exact order:']`
    1.  `[e.g., 'The H2: '`headings.h2[0]`'.']`
    2.  `[e.g., 'The paragraph: '`paragraphs[1]`'.']`
    3.  `[e.g., 'The image: '`images[1].src`', which is full-width to this column.']`
    4.  `[e.g., 'The H3: '`headings.h3[0]`'.']`
    5.  `[e.g., 'The paragraphs: '`paragraphs[2]`' and '`paragraphs[3]`'.']`
* `[e.g., '**Right Sidebar:** Contains a container with a light grey background. It includes:']`
    1.  `[e.g., 'The H3: '`headings.h3[1]`'.']`
    2.  `[e.g., 'A vertical list of links: '`links[4]`', '`links[5]`', and '`links[6]`'.']`
* `[e.g., '**Footer:** This page uses the global footer described above.']`

**3. Content Element Reference:**
"Here is the complete list of content for this page. Use the layout description above to place them."

* **Headings:**
    * H1: `[List all h1 text from JSON]`
    * H2: `[List all h2 text from JSON]`
    * H3: `[List all h3 text from JSON]`
    * (etc. for H4, H5, H6)
* **Paragraphs:**
    * `[List all paragraph text from JSON]`
* **Images:**
    * `[List all images with 'src' and 'alt' from JSON]`
* **Links:**
    * `[List all links with 'text' and 'href' from JSON]`

---
"""


def prompt_generator_node(state: State) -> State:
    """
    Generates a new prompt by sending scraped text and screenshots to Gemini.

    This node initializes a chat model, constructs a multi-modal message
    containing system instructions, scraped text data, and page screenshots,
    and then invokes the model to generate a new prompt.

    Args:
        state: The current workflow state, containing `pages_scraped`
               and `pages_screenshots`.

    Returns:
        State: An updated copy of the state. If successful, `prompt` is
               populated and `prompt_error` is None. If failed, `prompt`
               is None and `prompt_error` contains the error message.
    """
    logger.info("Starting prompt generation node...")

    try:
        # 1. Initialize the chat client
        logger.debug("Initializing chat model...")
        gemini_client = init_chat_model(
            model=Config.MODEL_NAME,
            model_provider=Config.MODEL_PROVIDER,
            api_key=Config.GEMINI_API_KEY
        )
        logger.info(f"Chat model '{Config.MODEL_NAME}' initialized.")

        # 2. Construct the multi-modal messages
        logger.debug("Constructing messages for Gemini...")

        # Prepare text content
        scraped_text = state.model_dump().get('pages_scraped', [])
        text_content = {
            "type": "text",
            "text": f"Here is the JSON data of the scraped website: {scraped_text}"
        }

        # Prepare image content
        image_content = [
            {
                "type": "image_url",
                "image_url": page.screenshot
            }
            for page in state.pages_screenshots
        ]

        messages = [
            SystemMessage(content=PROMPT_GENERATOR_PROMPT),
            HumanMessage(content=[text_content] + image_content),
        ]

        logger.info(f"Constructed messages with 1 text block and {len(image_content)} images.")

        # 3. Invoke the Gemini client
        logger.debug("Invoking Gemini client...")
        response = gemini_client.invoke(messages)

        if not response or not hasattr(response, 'text'):
            raise ValueError("Invalid or empty response from Gemini client.")

        logger.info("Successfully received and validated response from Gemini.")
        logger.debug(f"Generated prompt (truncated): {response.text[:100]}...")

        # 4. Return the new state on success
        return state.model_copy(
            update={
                "prompt": response.text,
            }
        )

    except Exception as e:
        # 5. Handle any exception during the process
        error_message = f"Failed during prompt generation: {e}"
        logger.error(error_message, exc_info=True)  # exc_info=True logs the stack trace

        # 6. Return the new state on failure
        return state.model_copy(
            update={
                "prompt": None,  # Ensure prompt is empty on failure
            }
        )
