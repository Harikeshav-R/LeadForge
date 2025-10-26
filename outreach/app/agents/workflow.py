from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.draft_email_node import draft_email_node
from app.agents.save_intermediate_state_node import save_intermediate_state_node
from app.agents.send_mail_node import send_mail_node
from app.agents.start_phone_call_node import start_phone_call_node
from app.schemas.state import State


def create_compiled_state_graph() -> CompiledStateGraph:
    workflow = StateGraph(State)
    workflow.add_node("draft_email_node", draft_email_node)
    workflow.add_node("send_mail_node", send_mail_node)
    workflow.add_node("save_intermediate_state_node", save_intermediate_state_node)
    workflow.add_node("start_phone_call_node", start_phone_call_node)

    workflow.set_entry_point("draft_email_node")
    workflow.add_edge("draft_email_node", "send_mail_node")
    workflow.add_edge("send_mail_node", "save_intermediate_state_node")
    workflow.add_edge("save_intermediate_state_node", "start_phone_call_node")
    workflow.set_finish_point("start_phone_call_node")

    app = workflow.compile()

    return app


if __name__ == "__main__":
    initial_state = State(
        client_name="The Yard Milkshake Bar",
        client_email="r.harikeshav@gmail.com",
        client_phone_number="+15138489642",
        sender_name="Hari",
        sender_title="Lead Developer",
        website_critique="""Here's a detailed analysis of the provided screenshots:\n\n### 1. First Impression & Visual Appeal\n\nThe website presents a strong, dark aesthetic with a black background and predominantly white text. While this can convey a sense of modern sophistication, its execution here feels somewhat inconsistent and hinders overall appeal.\n\n*   **Modernity:** The dark theme attempts a modern look, but the typography choices detract from it. The script fonts used for \"Columbus, Ohio\" and \"October Specials\" feel dated and, more critically, are extremely difficult to read against the black background, especially due to their thin strokes and low contrast. This immediately undermines a modern feel.\n*   **Trustworthiness:** The design struggles to build immediate trust. The cluttered navigation on desktop, the generic \"Sign up to receive our specials\" banner at the top, and the poor readability of key information (like the specials descriptions) make the site feel less professional and polished than a modern brand would aim for. The images of the milkshakes are vibrant and appealing, but their presentation within the overall layout is static and doesn't elevate the design. The logo itself is well-designed and fits the brand, but it's not enough to carry the entire visual experience.\n\n### 2. Navigation & Usability\n\nThe navigation and overall usability are major weaknesses of this design, creating a frustrating experience for users.\n\n*   **Desktop Navigation Overload:** The primary navigation bar on desktop is excessively crowded with too many top-level items (\"LOCATIONS & MENUS,\" \"SHOP,\" \"OUR STORY,\" \"FRANCHISING OPPORTUNITY,\" \"THE SCOOP,\" \"CONTACT US,\" \"E-GIFT CARDS,\" \"NEWSLETTER,\" \"ALLERGIES AND NUTRITION,\" \"SCHEDULE DELIVERY OR PICKUP\"). This creates severe cognitive overload and makes it difficult for users to quickly identify and locate specific information. Many of these items could be logically grouped under fewer, broader categories (e.g., \"About Us,\" \"Order\"). The length of \"ALLERGIES AND NUTRITION\" and \"SCHEDULE DELIVERY OR PICKUP\" further exacerbates the clutter.\n*   **Mobile Navigation:** While a hamburger menu correctly appears on mobile and tablet, the sheer number of navigation items means that opening the menu will present a long, scrolling list, replicating the desktop's clutter problem on a smaller screen.\n*   **Readability Issues:** Beyond the main navigation, readability is a persistent problem. The script fonts, particularly for \"Columbus, Ohio\" and \"October Specials,\" are decorative but impractical for conveying information. The white text on a black background, while a stylistic choice, becomes challenging to read in smaller font sizes and for longer descriptions, causing eye strain. The descriptions for the \"October Specials\" are particularly egregious in their lack of legibility.\n*   **Redundant Calls-to-Action:** The presence of a \"NUTRITION\" button directly below the location information, while \"ALLERGIES AND NUTRITION\" is already in the main navigation, creates redundancy and confusion. The \"MENU\" text is clickable but lacks the visual affordance of a button, making it less discoverable as a primary action.\n*   **Intrusive Top Banner:** The \"Sign up to receive our specials of the month!\" banner at the very top is generic, uses an unappealing font, and takes up significant screen real estate, especially on mobile devices where it pushes down critical content. Its dismiss button is small and lacks clear contrast.\n*   **Lack of Visual Hierarchy:** Within the hero section, the address, \"MENU\" link, and the three action buttons (\"DIRECTIONS,\" \"NUTRITION,\" \"CONTACT\") are given similar visual weight. There's no clear prioritization of the most important action a user might want to take (e.g., viewing the menu or getting directions).\n\n### 3. Responsiveness\n\nThe site attempts responsiveness by adapting the layout, but significant issues arise, particularly with content readability and hierarchy on smaller screens.\n\n*   **Hamburger Menu Implementation:** The hamburger menu correctly appears on tablet and mobile views, which is a standard and expected responsive behavior.\n*   **Main Content Scaling:** The main content block featuring the milkshakes, location, and primary calls-to-action scales reasonably well, with the buttons stacking vertically on mobile. However, the \"MENU\" text remains a simple text link without adapting to a more prominent button style, which would be more usable on touch devices.\n*   **\"October Specials\" Breakdown:** This section suffers significantly on smaller screens. The individual specials, which are already hard to read on desktop due to font choice, become almost completely illegible on tablet and mobile. The images shrink, and the text descriptions are crammed into narrow columns, making them impossible to decipher without extreme effort. This indicates a lack of thoughtful content adaptation for different screen sizes.\n*   **Top Banner Intrusion:** The \"Sign up...\" banner, already problematic on desktop, becomes even more intrusive on mobile, consuming a disproportionate amount of the initial viewport and pushing down the main, more valuable content.\n\n### 4. Suggestions for Improvement\n\n1.  **Revamp Typography and Enhance Readability:** Replace decorative script fonts used for \"Columbus, Ohio\" and \"October Specials\" with legible, brand-appropriate sans-serif or serif fonts. Ensure all text, especially smaller descriptions and navigation items, has sufficient contrast against the black background. Consider using a slightly off-white or light gray for body text instead of pure white to reduce eye strain on a dark background. This will drastically improve the user's ability to consume information quickly and comfortably.\n2.  **Streamline Navigation and Information Architecture:** Consolidate the overly extensive navigation menu. Group related items under logical, fewer top-level categories (e.g., \"About Us\" for \"Our Story,\" \"The Scoop,\" \"Franchising Opportunity\"; \"Locations & Ordering\" for \"Locations & Menus\" and \"Schedule Delivery or Pickup\"). Eliminate redundant links (e.g., remove the standalone \"NUTRITION\" button if \"ALLERGIES AND NUTRITION\" is in the main nav). This will reduce cognitive load, make the site easier to navigate on all devices, and provide a clearer path to key information.\n3.  **Optimize Mobile Content Presentation and Call-to-Actions:** Redesign the \"October Specials\" section for mobile views, employing a more user-friendly layout such as a horizontal carousel, accordion, or distinct cards with larger images and readable text descriptions. Ensure the \"MENU\" link is presented as a prominent, touch-friendly button. Finally, redesign the \"Sign up to receive specials\" banner to be less intrusive on mobile, perhaps as a fixed footer, a smaller, dismissible notification bar, or a pop-up triggered after a short delay.""",
        demo_url="https://www.yardmilkshakebar.com",
        web_agency_name="LeadForge",
        web_agency_logo="https://media.wired.com/photos/5926ffe47034dc5f91bed4e8/google-logo.jpg",
    )

    final_state = State(**create_compiled_state_graph().invoke(initial_state))

    print(final_state.model_dump_json(indent=2))
