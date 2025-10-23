import os
import json
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from pydantic import BaseModel, EmailStr, ValidationError
from langchain_community.tools.gmail.create_draft import GmailCreateDraft
from langchain_community.tools.gmail.send_message import GmailSendMessage
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials
from langchain_core.tools import StructuredTool
from typing import Optional, List

# Set up your API keys
os.environ["GOOGLE_API_KEY"] = "AIzaSyAoVyLl5tgqH0lqdy3zFfUfrQf6NARwYZI"

# Define the required scopes for Gmail operations
SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send"
]

# Get credentials with the correct scopes
credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=SCOPES,
    client_secrets_file="credentials.json",
)

# Build the Gmail API service
api_resource = build_resource_service(credentials=credentials)

# Initialize base Gmail tools
gmail_draft = GmailCreateDraft(api_resource=api_resource)
gmail_send = GmailSendMessage(api_resource=api_resource)


# Wrap tools with proper schemas for Gemini
def create_draft_wrapper(message: str, to: str, subject: str, cc: Optional[str] = None,
                         bcc: Optional[str] = None) -> str:
    """Create a draft email in Gmail."""
    return gmail_draft.invoke({
        "message": message,
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
        "cc": [cc] if cc and isinstance(cc, str) else (cc or []),
        "bcc": [bcc] if bcc and isinstance(bcc, str) else (bcc or []),
    })


def send_message_wrapper(message: str, to: str, subject: str, cc: Optional[str] = None,
                         bcc: Optional[str] = None) -> str:
    """Send an email via Gmail."""
    return gmail_send.invoke({
        "message": message,
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
        "cc": [cc] if cc and isinstance(cc, str) else (cc or []),
        "bcc": [bcc] if bcc and isinstance(bcc, str) else (bcc or []),
    })


# Create structured tools
tools = [
    StructuredTool.from_function(
        func=create_draft_wrapper,
        name="create_gmail_draft",
        description="Create a draft email in Gmail"
    ),
    StructuredTool.from_function(
        func=send_message_wrapper,
        name="send_gmail_message",
        description="Send an email via Gmail"
    ),
]

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# Create the agent
agent_executor = create_agent(llm, tools)


# --- 1. DEFINE DATA SCHEMAS ---
class Screenshot(BaseModel):
    device: str
    image: str


class Lead(BaseModel):
    place_id: str
    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = 0
    total_ratings: Optional[int] = 0
    category: Optional[str] = None
    price_level: Optional[int] = None
    is_open: Optional[bool] = None
    lat: Optional[float] = 0
    lng: Optional[float] = 0
    emails: List[EmailStr] = []
    phone_numbers: List[str] = []
    social_media: List[str] = []
    screenshots: List[Screenshot] = []
    website_review: Optional[str] = None
    id: str
    state_id: str


class LeadReport(BaseModel):
    city: str
    business_type: str
    radius: int
    min_rating: float
    max_results: int
    messages: List[str]
    leads: List[Lead]


# --- 2. YOUR AGENT FUNCTION (MODIFIED) ---
def run_agent_step(instruction: str, existing_messages: list = [], verbose: bool = True):
    """
    Runs the agent for one step of the conversation.

    Args:
        instruction: The new user prompt for the agent.
        existing_messages: The list of messages from previous steps (the conversation history).
        verbose: Whether to print the agent's process.

    Returns:
        A list of all messages in the new conversation state.
    """
    try:
        # Pass the full history to the agent so it has context
        events = agent_executor.stream(
            {"messages": existing_messages + [("user", instruction)]},
            stream_mode="values",
        )

        all_messages = []
        for event in events:
            if verbose:
                # We'll turn this off for the draft step to keep the console clean
                event["messages"][-1].pretty_print()
            all_messages = event["messages"]  # Get the full list of messages

        return all_messages  # Return the complete history

    except Exception as e:
        print(f"Error during agent execution: {str(e)}")
        return existing_messages  # Return old history on error


# --- 3. YOUR NEW MAIN EXECUTION BLOCK (WITH CONFIRMATION) ---
if __name__ == "__main__":

    input_file = "lead_report.json"

    # 2. Define the GOAL of your email campaign.
    MY_GOAL = "to sell them my new AI-powered website optimization and SEO service."

    try:
        # 1. Open and read the JSON file
        with open(input_file, 'r') as f:
            data_dict = json.load(f)

        # 2. VALIDATE the entire report
        report = LeadReport(**data_dict)
        print(f"--- Successfully validated {input_file}. Found {len(report.leads)} leads. ---")

        if not report.leads:
            print("No leads found in the report. Exiting.")

        # 3. Loop through each lead
        for i, lead in enumerate(report.leads, 1):
            print(f"\n" + "=" * 70)
            print(f"Processing Lead {i}/{len(report.leads)}: {lead.name}")
            print("=" * 70)

            # 4. Check for an email
            if not lead.emails:
                print(f"SKIPPING '{lead.name}': No emails found.")
                continue

            contact_email = lead.emails[0]

            # 5. Build the "Intelligence Context"
            lead_context = f"""
            - Company Name: {lead.name}
            - Website: {lead.website}
            - Category: {lead.category}
            - Key Website Review Finding: "{lead.website_review}"
            """

            # 6. Create the "DRAFT-ONLY" prompt
            draft_instruction = f"""
            You are an expert B2B sales strategist.

            **Your Task:**
            Draft a hyper-personalized, professional, and respectful email.

            **CRITICAL:** Do NOT send it. Just return the draft.
            Wait for my approval before you do anything else.

            **Recipient:** {lead.name}
            **Your Primary Goal:** {MY_GOAL}
            **Full Intelligence Report on this lead:**
            {lead_context}

            **Drafting Instructions:**
            1.  Draft a short, compelling email (under 150 words).
            2.  Use the "Key Website Review Finding" as the *reason* for your outreach. This is the hook.
            3.  Clearly state your goal, but frame it as a benefit to *them*.
            4.  The tone must be professional and helpful.

            Respond *only* with the full text of the email draft.
            """

            # 7. --- STEP 1: GET THE DRAFT ---
            print("🤖 Generating draft...")
            # Start with an empty history []
            # 'verbose=False' keeps the console clean for this step
            message_history = run_agent_step(draft_instruction, [], verbose=False)

            # The draft is the last message from the AI
            draft_message = message_history[-1]
            draft_content = draft_message.content

            # 8. --- STEP 2: SHOW DRAFT TO USER FOR CONFIRMATION ---
            print("\n" + "--- DRAFT FOR YOUR REVIEW ---".center(70, "-"))
            print(draft_content)
            print("-" * 70)

            user_input = input("Approve this draft? (yes/y to send, no/n to skip): ").strip().lower()

            # 9. --- STEP 3: SEND THE EMAIL (OR SKIP) ---
            if user_input in ['yes', 'y']:
                print("\n--- 👍 Approving... Sending email... ---")

                # The prompt to send the email it just drafted
                send_instruction = f"That draft is perfect. Please send it to {contact_email} now."

                # Pass in the *entire previous history* so the agent has context
                # 'verbose=True' lets us see the agent's "send_email" tool call
                final_message_history = run_agent_step(send_instruction, message_history, verbose=True)

                print(f"--- ✅ Email sent to {lead.name} ---")

            else:
                print(f"--- 🚫 Skipping draft for {lead.name} ---")

            # Add a small pause to let you read the output
            time.sleep(2)

    except FileNotFoundError:
        print(f"Error: The input file '{input_file}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_file}'. Please check the file's formatting.")
    except ValidationError as e:
        print(f"--- ERROR: JSON DATA IS INVALID ---")
        print(f"Could not process '{input_file}' because the data is incomplete or badly formatted.\n")
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")