// Email Agent API Configuration
export const EMAIL_CONFIG = {
    // Email Agent API URL (standalone service on port 8000)
    EMAIL_AGENT_API_URL: 'http://localhost:8000',

    // Outreach Service API URL (runs on port 8004)
    OUTREACH_API_URL: import.meta.env.VITE_OUTREACH_API_URL || 'http://localhost:8004',

    // Your Gmail email address (for display purposes)
    SENDER_EMAIL: 'hackohi00@gmail.com',

    // Default email settings
    DEFAULT_GOAL: 'to sell them my new AI-powered website optimization and SEO service',
    DEFAULT_MAX_WORDS: 150,

    // Sender information for outreach service
    SENDER_NAME: 'LeadForge Team',
    SENDER_TITLE: 'Business Development Manager',
    WEB_AGENCY_NAME: 'LeadForge',
    WEB_AGENCY_LOGO: 'https://via.placeholder.com/150', // Replace with your actual logo URL
};

// Instructions for using the Gmail Email Agent:

/*
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
- Test carefully before sending to real leads
*/
