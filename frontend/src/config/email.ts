// Email Agent API Configuration
export const EMAIL_CONFIG = {
  // Email Agent API URL (standalone service on port 8000)
  EMAIL_AGENT_API_URL: 'http://localhost:8000',
  
  // Your Gmail email address (for display purposes)
  SENDER_EMAIL: 'rahulksanghvi21@gmail.com',
  
  // Default email settings
  DEFAULT_GOAL: 'to sell them my new AI-powered website optimization and SEO service',
  DEFAULT_MAX_WORDS: 150,
};

// Instructions for using the Gmail Email Agent:

/*
📧 GMAIL EMAIL AGENT INTEGRATION

The system now uses the real Gmail Email Agent API running on port 8000.

🚀 TO START THE EMAIL AGENT:
1. Navigate to: cd HackOHIO/leads/app/agents/
2. Run: python email_agent.py
3. The agent will start on http://localhost:8000

📋 FEATURES:
- AI-powered personalized email generation using Gemini
- Real Gmail draft creation via Gmail API
- Real email sending via Gmail
- Customizable email goals/pitch
- Lead intelligence integration (website reviews, business info)

🔧 REQUIREMENTS:
- Gmail OAuth credentials are already set up (token.json, credentials.json)
- Google API key is configured in email_agent.py
- Email agent service must be running on port 8000

⚠️ IMPORTANT:
- Drafts will be created in your actual Gmail drafts folder
- Sent emails will be sent from your Gmail account
- Test carefully before sending to real leads
*/
