import os
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_community.tools.gmail.create_draft import GmailCreateDraft
from langchain_community.tools.gmail.send_message import GmailSendMessage
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials
from langchain_core.tools import StructuredTool
from fastapi.middleware.cors import CORSMiddleware


# ============= EMAIL AGENT SETUP =============

# Load environment variables from .env.dev file in the HackOHIO root directory
from dotenv import load_dotenv
import pathlib

# Load from the .env.dev file in the HackOHIO root directory
env_path = pathlib.Path(__file__).parent.parent.parent.parent / ".env.dev"
load_dotenv(env_path)

# Get GEMINI_API_KEY from environment variable (this is the Google API key for Gemini)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required. Please set it in your .env.dev file.")

# Set the environment variable for the Gemini model
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Define the required scopes for Gmail operations
SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send"
]

# Get credentials with the correct scopes
# Use absolute paths to avoid path issues
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
token_path = os.path.join(current_dir, "token.json")
credentials_path = os.path.join(current_dir, "credentials.json")

credentials = get_gmail_credentials(
    token_file=token_path,
    scopes=SCOPES,
    client_secrets_file=credentials_path,
)

# Build the Gmail API service
api_resource = build_resource_service(credentials=credentials)

# Initialize base Gmail tools
gmail_draft = GmailCreateDraft(api_resource=api_resource)
gmail_send = GmailSendMessage(api_resource=api_resource)


# Wrap tools with proper schemas for Gemini
def create_draft_wrapper(message: str, to: str, subject: str, cc: Optional[str] = None,
                         bcc: Optional[str] = None) -> str:
    """Create draft in Gmail."""
    return gmail_draft.invoke({
        "message": message,
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
        "cc": [cc] if cc and isinstance(cc, str) else (cc or []),
        "bcc": [bcc] if bcc and isinstance(bcc, str) else (bcc or []),
    })


def send_message_wrapper(message: str, to: str, subject: str, cc: Optional[str] = None,
                         bcc: Optional[str] = None) -> str:
    """Send email."""
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

# --- DATA SCHEMAS ---
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


# --- AGENT FUNCTION ---
def run_agent_step(instruction: str, existing_messages: list = [], verbose: bool = False):
    """
    Runs the agent for one step of the conversation.
    """
    try:
        events = agent_executor.stream(
            {"messages": existing_messages + [("user", instruction)]},
            stream_mode="values",
        )

        all_messages = []
        for event in events:
            if verbose:
                event["messages"][-1].pretty_print()
            all_messages = event["messages"]

        return all_messages

    except Exception as e:
        print(f"Error during agent execution: {str(e)}")
        return existing_messages


# ============= FASTAPI SETUP =============

app = FastAPI(title="Lead Email Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # during dev, allow all; later restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Request Models
class DraftEmailRequest(BaseModel):
    lead: Lead
    goal: str = "to sell them my new AI-powered website optimization and SEO service."
    max_words: int = 150


class SendEmailRequest(BaseModel):
    lead: Lead
    goal: str = "to sell them my new AI-powered website optimization and SEO service."
    max_words: int = 150


class BatchDraftRequest(BaseModel):
    leads: List[Lead]
    goal: str = "to sell them my new AI-powered website optimization and SEO service."
    max_words: int = 150


# API Endpoints
@app.get("/")
def root():
    """Root endpoint with API info"""
    return {
        "message": "Lead Email Agent API is running",
        "endpoints": {
            "/draft-email": "POST - Draft an email for a single lead",
            "/send-email": "POST - Draft and send email to a single lead",
            "/batch-draft": "POST - Draft emails for multiple leads",
            "/health": "GET - Health check",
            "/docs": "API documentation"
        }
    }


@app.post("/draft-email")
def draft_email_for_lead(request: DraftEmailRequest):
    """
    Draft a personalized email for a single lead.

    Returns the draft content for review.
    """
    try:
        lead = request.lead

        # Check for email with safe array access
        if not lead.emails or len(lead.emails) == 0:
            raise HTTPException(status_code=400, detail=f"No emails found for {lead.name}")
        
        # Safe array access with validation
        contact_email = lead.emails[0] if len(lead.emails) > 0 else None
        if not contact_email or not isinstance(contact_email, str) or not contact_email.strip():
            raise HTTPException(status_code=400, detail=f"Invalid email address for {lead.name}")

        # Build intelligence context
        lead_context = f"""
        - Company Name: {lead.name}
        - Website: {lead.website}
        - Category: {lead.category}
        - Key Website Review Finding: "{lead.website_review}"
        """

        # Create draft instruction
        draft_instruction = f"""
        You are an expert B2B sales strategist.

        **Your Task:**
        Draft a hyper-personalized, professional, and respectful email.

        **CRITICAL:** Do NOT send it. Just return the draft.

        **Recipient:** {lead.name}
        **Your Primary Goal:** {request.goal}
        **Full Intelligence Report on this lead:**
        {lead_context}

        **Drafting Instructions:**
        1. Draft a short, compelling email (under {request.max_words} words).
        2. Use the "Key Website Review Finding" as the *reason* for your outreach. This is the hook.
        3. Clearly state your goal, but frame it as a benefit to *them*.
        4. The tone must be professional and helpful.

        Respond *only* with the full text of the email draft.
        """

        # Generate draft
        message_history = run_agent_step(draft_instruction, [], verbose=False)
        
        # Safe access to message history
        if not message_history or len(message_history) == 0:
            raise HTTPException(status_code=500, detail="Agent failed to generate draft content")
        
        draft_content = message_history[-1].content if len(message_history) > 0 else ""
        
        if not draft_content:
            raise HTTPException(status_code=500, detail="Agent returned empty draft content")

        return {
            "success": True,
            "lead_name": lead.name,
            "contact_email": contact_email,
            "draft": draft_content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send-email")
def send_email_to_lead(request: SendEmailRequest):
    """
    Draft and immediately send an email to a single lead.

    Use with caution - this will actually send the email!
    """
    try:
        lead = request.lead

        # Check for email with safe array access
        if not lead.emails or len(lead.emails) == 0:
            raise HTTPException(status_code=400, detail=f"No emails found for {lead.name}")
        
        # Safe array access with validation
        contact_email = lead.emails[0] if len(lead.emails) > 0 else None
        if not contact_email or not isinstance(contact_email, str) or not contact_email.strip():
            raise HTTPException(status_code=400, detail=f"Invalid email address for {lead.name}")

        # Build intelligence context
        lead_context = f"""
        - Company Name: {lead.name}
        - Website: {lead.website}
        - Category: {lead.category}
        - Key Website Review Finding: "{lead.website_review}"
        """

        # Create draft instruction
        draft_instruction = f"""
        You are an expert B2B sales strategist.

        **Your Task:**
        Draft a hyper-personalized, professional, and respectful email.

        **Recipient:** {lead.name}
        **Your Primary Goal:** {request.goal}
        **Full Intelligence Report on this lead:**
        {lead_context}

        **Drafting Instructions:**
        1. Draft a short, compelling email (under {request.max_words} words).
        2. Use the "Key Website Review Finding" as the *reason* for your outreach.
        3. Clearly state your goal, but frame it as a benefit to *them*.
        4. The tone must be professional and helpful.

        Respond *only* with the full text of the email draft.
        """

        # Step 1: Generate draft
        message_history = run_agent_step(draft_instruction, [], verbose=False)
        
        # Safe access to message history
        if not message_history or len(message_history) == 0:
            raise HTTPException(status_code=500, detail="Agent failed to generate draft content")
        
        draft_content = message_history[-1].content if len(message_history) > 0 else ""
        
        if not draft_content:
            raise HTTPException(status_code=500, detail="Agent returned empty draft content")

        # Step 2: Send the email
        send_instruction = f"That draft is perfect. Please send it to {contact_email} now."
        final_history = run_agent_step(send_instruction, message_history, verbose=False)

        return {
            "success": True,
            "lead_name": lead.name,
            "contact_email": contact_email,
            "draft": draft_content,
            "sent": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-draft")
def batch_draft_emails(request: BatchDraftRequest):
    """
    Draft emails for multiple leads at once.

    Returns a list of drafts for review.
    """
    try:
        results = []

        for lead in request.leads:
            # Skip if no emails
            if not lead.emails:
                results.append({
                    "lead_name": lead.name,
                    "skipped": True,
                    "reason": "No emails found"
                })
                continue

            contact_email = lead.emails[0]

            # Build context
            lead_context = f"""
            - Company Name: {lead.name}
            - Website: {lead.website}
            - Category: {lead.category}
            - Key Website Review Finding: "{lead.website_review}"
            """

            # Draft instruction
            draft_instruction = f"""
            You are an expert B2B sales strategist.

            **Your Task:** Draft a hyper-personalized, professional email.

            **Recipient:** {lead.name}
            **Your Goal:** {request.goal}
            **Intelligence:** {lead_context}

            Draft a short email (under {request.max_words} words) using the website review as your hook.
            Respond only with the email text.
            """

            # Generate draft
            try:
                message_history = run_agent_step(draft_instruction, [], verbose=False)
                
                # Safe access to message history
                if not message_history or len(message_history) == 0:
                    results.append({
                        "lead_name": lead.name,
                        "contact_email": lead.emails[0] if lead.emails else "",
                        "success": False,
                        "error": "Agent failed to generate draft"
                    })
                    continue
                
                draft_content = message_history[-1].content if len(message_history) > 0 else ""
                
                if not draft_content:
                    results.append({
                        "lead_name": lead.name,
                        "contact_email": lead.emails[0] if lead.emails else "",
                        "success": False,
                        "error": "Agent returned empty content"
                    })
                    continue

                results.append({
                    "lead_name": lead.name,
                    "contact_email": contact_email,
                    "draft": draft_content,
                    "skipped": False
                })
            except Exception as e:
                results.append({
                    "lead_name": lead.name,
                    "skipped": True,
                    "reason": str(e)
                })

        return {
            "success": True,
            "total_leads": len(request.leads),
            "drafts_generated": len([r for r in results if not r.get("skipped")]),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Check if API is running"""
    return {"status": "healthy", "gmail_connected": True}


# Run the server http://127.0.0.1:8000/docs
if __name__ == "__main__":
    import uvicorn

    print("Starting Lead Email Agent API...")
    print("API will be available at: http://localhost:8000")
    print("Docs available at: http://localhost:8000/docs")
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

    ## rahul runs with this
    uvicorn.run(app, host="0.0.0.0", port=8000)