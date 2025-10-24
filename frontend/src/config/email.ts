// Email Configuration for Testing
// Update these values with your actual email credentials

export const EMAIL_CONFIG = {
  // Your Gmail email address (sender)
  SENDER_EMAIL: 'rahulksanghvi21@gmail.com', // Replace with your actual email
  
  // Test receiver email address (for testing purposes)
  TEST_RECEIVER_EMAIL: 'hackohi00@gmail.com', // Replace with test email
  
  // Enable/disable test mode (true = use test receiver, false = use actual lead emails)
  USE_TEST_MODE: true, // Set to false for production
  
  // Gmail API Configuration (for future use with real Gmail API)
  GMAIL_CLIENT_ID: 'your-gmail-client-id',
  GMAIL_CLIENT_SECRET: 'your-gmail-client-secret',
};

// Instructions for setting up email credentials:

/*
🚨 CURRENT STATUS: The system is using LOGGING MODE for testing
   - Emails are logged to console with full details
   - No actual emails are sent yet
   - This is safe for testing and development

📧 TO ENABLE REAL EMAIL SENDING:

Option 1: Use the existing Gmail Agent (Recommended)
1. Set up Gmail API credentials:
   - Go to Google Cloud Console
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth2 credentials
   - Download credentials.json
   - Place it in HackOHIO/leads/app/agents/ directory

2. Update the email agent configuration:
   - Update the Google API key in HackOHIO/leads/app/agents/email_agent.py
   - Run the email agent to set up OAuth2 tokens

3. Create an API endpoint to call the email agent from the frontend

Option 2: Use a simple SMTP service (Quick setup)
1. Use services like SendGrid, Mailgun, or Gmail SMTP
2. Update the emailService.ts to use real SMTP sending
3. Add SMTP credentials to this config file

🔧 FOR NOW: The system will log detailed email information to the console
   - Check browser console to see email details
   - All email content is logged for verification
   - Safe for testing without sending real emails
*/
