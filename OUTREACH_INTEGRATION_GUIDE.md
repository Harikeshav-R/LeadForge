# Outreach Email Agent Integration Guide

## Overview

The frontend is now integrated with the outreach email service, allowing you to generate and send emails directly from the UI using AI-powered email generation and Gmail SMTP.

## What Was Implemented

### 1. **Frontend Configuration** (`frontend/src/config/email.ts`)
- Added `OUTREACH_API_URL` pointing to `http://localhost:8004`
- Updated sender email to `hackohi00@gmail.com`
- Added sender information (name, title, agency name, logo) for the outreach workflow

### 2. **API Service** (`frontend/src/services/api.ts`)
- Added `EmailApiService.sendEmailViaOutreach()` method
- Automatically maps Lead data to outreach State schema
- Handles workflow execution and email sending
- Provides detailed error messages and timeout handling

### 3. **UI Components** (`frontend/src/components/LeadsTable.tsx`)
- Added "Send Email" button that uses the outreach workflow
- Added "Draft" button for reviewing emails before sending (existing flow)
- Shows loading states during email generation and sending
- Displays success/error messages
- Allows customization of email goal/pitch per lead

## How It Works

### User Flow

1. **Search for leads** using the campaign form
2. For each lead, you can customize the **email goal** (optional)
3. Click one of two buttons:
   - **"Draft"** - Generate email draft for review before sending (port 8000 service)
   - **"Send Email"** - Generate and send immediately via outreach workflow (port 8004)

### Outreach Workflow Process

When you click "Send Email":

1. Frontend calls `EmailApiService.sendEmailViaOutreach(lead, goal, customFields)`
2. API constructs the State object:
   ```typescript
   {
     client_name: "Business Name",
     client_email: "contact@business.com",
     sender_name: "LeadForge Team",
     sender_title: "Business Development Manager",
     website_critique: "AI-generated or lead's website review",
     demo_url: "Deployed website URL or lead's website",
     web_agency_name: "LeadForge",
     web_agency_logo: "Logo URL"
   }
   ```
3. POST request to `http://localhost:8004/workflow/create-workflow`
4. Outreach service workflow:
   - **draft_email_node**: Gemini AI generates personalized email
   - **send_mail_node**: Sends via Gmail SMTP
5. Frontend receives response with `email_sent: true/false`
6. UI updates to show success or error

## Setup Instructions

### 1. Configure Environment Variables

Create or update `.env.dev` in the project root:

```bash
# Gmail Credentials for Outreach Service
SENDER_EMAIL_ADDRESS=hackohi00@gmail.com
SENDER_EMAIL_PASSWORD=your_16_digit_app_password_here

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.0-flash-exp
MODEL_PROVIDER=google_genai

# Database Configuration
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_OUTREACH_DB=outreach_db

# Debug Mode (enables CORS)
DEBUG=true
```

### 2. Start the Outreach Service

#### Option A: Using Docker Compose (Recommended)
```bash
cd LeadForge
docker-compose -f docker-compose.dev.yml up outreach
```

#### Option B: Standalone
```bash
cd LeadForge/outreach
uv run uvicorn app:app --host 0.0.0.0 --port 8004 --reload
```

### 3. Verify Service is Running

Check the API docs at: http://localhost:8004/docs

### 4. Start the Frontend

```bash
cd LeadForge/frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

## Gmail App Password Setup

To send emails via Gmail SMTP, you need an **App Password**:

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification** (must be enabled)
3. Scroll to **App passwords**
4. Generate a new app password for "Mail"
5. Copy the 16-digit password
6. Add it to `.env.dev` as `SENDER_EMAIL_PASSWORD`

⚠️ **Important**: Regular Gmail passwords won't work. You must use an App Password.

## Testing the Integration

### Test Flow

1. Start the outreach service: `docker-compose -f docker-compose.dev.yml up outreach`
2. Start the frontend: `cd frontend && npm run dev`
3. Search for leads (e.g., "coffee shops in Columbus")
4. For a lead with an email address:
   - Optionally customize the email goal
   - Click "Send Email"
   - Wait for AI to generate and send (~10-30 seconds)
5. Check the lead's inbox for the email from `hackohi00@gmail.com`

### Verification

- Check browser console for detailed logs
- Check Docker logs: `docker logs outreach_dev`
- Verify email in recipient's inbox
- Check Gmail sent folder of `hackohi00@gmail.com`

## Troubleshooting

### "Cannot connect to the outreach service"

**Problem**: Frontend can't reach the outreach service.

**Solutions**:
- Verify service is running: `docker ps | grep outreach`
- Check port 8004 is not in use: `netstat -an | grep 8004`
- Check Docker logs: `docker logs outreach_dev`
- Ensure no firewall blocking localhost:8004

### "SMTP authentication failed"

**Problem**: Gmail credentials are incorrect or missing.

**Solutions**:
- Verify `SENDER_EMAIL_ADDRESS` in `.env.dev`
- Ensure `SENDER_EMAIL_PASSWORD` is a 16-digit App Password (not regular password)
- Check that 2-Step Verification is enabled on the Gmail account
- Regenerate App Password if needed

### "Email send timeout"

**Problem**: Workflow is taking too long (> 2 minutes).

**Solutions**:
- Check Gemini API key is valid (`GEMINI_API_KEY` in `.env.dev`)
- Verify network connection
- Check Docker container resources: `docker stats outreach_dev`
- Review logs for errors: `docker logs outreach_dev`

### "No email address available for this lead"

**Problem**: Lead doesn't have a valid email.

**Solutions**:
- This is expected for some leads
- Use the lead generation service to enrich contact data
- Manually add email if known

## API Reference

### `EmailApiService.sendEmailViaOutreach()`

**Parameters**:
- `lead: Lead` - The lead object from the leads table
- `goal: string` - Email goal/pitch (e.g., "to sell them my new AI-powered website optimization service")
- `customFields?: object` - Optional overrides:
  - `websiteCritique?: string` - Custom website critique
  - `demoUrl?: string` - Custom demo URL

**Returns**: `Promise<{ success: boolean; message?: string; emailContent?: any }>`

**Example**:
```typescript
const result = await EmailApiService.sendEmailViaOutreach(
  lead,
  "to offer a free website audit and redesign consultation",
  {
    websiteCritique: "Your website loads slowly and lacks mobile optimization",
    demoUrl: "https://demo.leadforge.com/sample"
  }
);

if (result.success) {
  console.log('Email sent!', result.emailContent);
} else {
  console.error('Failed:', result.message);
}
```

## Architecture

```
┌─────────────┐
│   Frontend  │
│ (Port 5173) │
└──────┬──────┘
       │
       │ POST /workflow/create-workflow
       │ { client_name, client_email, ... }
       ▼
┌─────────────────┐
│ Outreach Service│
│   (Port 8004)   │
├─────────────────┤
│ ┌─────────────┐ │
│ │ Draft Email │ │  ← Gemini AI
│ │    Node     │ │
│ └──────┬──────┘ │
│        │        │
│ ┌──────▼──────┐ │
│ │  Send Mail  │ │  → Gmail SMTP
│ │    Node     │ │    (hackohi00@gmail.com)
│ └─────────────┘ │
└─────────────────┘
```

## Next Steps

1. **Test thoroughly** with real leads before production use
2. **Monitor Gmail sending limits** (500 emails/day for regular accounts)
3. **Customize email templates** by modifying `draft_email_node.py` prompt
4. **Track email performance** (opens, replies) using Gmail API or external tools
5. **Add email tracking** by integrating with services like SendGrid or Mailgun

## Support

For issues or questions:
- Check the Docker logs: `docker logs outreach_dev`
- Review the API docs: http://localhost:8004/docs
- Test the workflow manually using the Swagger UI

## Related Files

- `LeadForge/frontend/src/config/email.ts` - Email configuration
- `LeadForge/frontend/src/services/api.ts` - API service methods
- `LeadForge/frontend/src/components/LeadsTable.tsx` - UI components
- `LeadForge/outreach/app/agents/workflow.py` - Workflow definition
- `LeadForge/outreach/app/agents/draft_email_node.py` - Email generation
- `LeadForge/outreach/app/tools/mail.py` - Gmail SMTP integration
- `LeadForge/docker-compose.dev.yml` - Docker configuration

