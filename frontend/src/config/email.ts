// Email Agent API Configuration
export const EMAIL_CONFIG = {
  // Email Agent API URL (standalone service on port 8000)
  EMAIL_AGENT_API_URL: 'http://localhost:8000',
  
<<<<<<< HEAD
  // Outreach Service API URL (runs on port 8004)
  OUTREACH_API_URL: import.meta.env.VITE_OUTREACH_API_URL || 'http://localhost:8004',
  
  // Your Gmail email address (for display purposes)
  SENDER_EMAIL: 'hackohi00@gmail.com',
=======
  // Your Gmail email address (for display purposes)
  SENDER_EMAIL: 'rahulksanghvi21@gmail.com',
>>>>>>> main-holder
  
  // Default email settings
  DEFAULT_GOAL: 'to sell them my new AI-powered website optimization and SEO service',
  DEFAULT_MAX_WORDS: 150,
<<<<<<< HEAD
  
  // Sender information for outreach service
  SENDER_NAME: 'LeadForge Team',
  SENDER_TITLE: 'Business Development Manager',
  WEB_AGENCY_NAME: 'LeadForge',
  WEB_AGENCY_LOGO: 'https://via.placeholder.com/150', // Replace with your actual logo URL
=======
>>>>>>> main-holder
};

// Instructions for using the Gmail Email Agent:

/*
<<<<<<< HEAD
📧 EMAIL SERVICE INTEGRATION

This app supports two email services:

1️⃣ OUTREACH SERVICE (Port 8004) - RECOMMENDED
   - Drafts and sends emails in one workflow
   - Uses Gmail SMTP with credentials from .env.dev
   - Powered by Gemini AI for email generation
   - Automatically sends via hackohi00@gmail.com
   
   🚀 TO START:
   docker-compose -f docker-compose.dev.yml up outreach
   
   🔧 REQUIREMENTS:
   - Set SENDER_EMAIL_ADDRESS and SENDER_EMAIL_PASSWORD in .env.dev
   - Service runs on http://localhost:8004

2️⃣ EMAIL AGENT (Port 8000) - Legacy
   - Standalone Gmail API service
   - Requires OAuth credentials setup
   
⚠️ IMPORTANT:
- Emails will be sent from hackohi00@gmail.com (configured in .env.dev)
=======
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
>>>>>>> main-holder
- Test carefully before sending to real leads
*/
