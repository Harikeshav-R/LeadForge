# Outreach Email Integration - Implementation Summary

## ✅ What Was Completed

Successfully integrated the outreach email agent (port 8004) into the frontend, enabling one-click AI-powered email generation and sending.

## 📝 Files Modified

### 1. **`frontend/src/config/email.ts`**
- Added `OUTREACH_API_URL` configuration (http://localhost:8004)
- Updated sender email to `hackohi00@gmail.com`
- Added sender details (name, title, agency info) for outreach workflow
- Updated documentation comments

### 2. **`frontend/src/services/api.ts`**
- Added `EmailApiService.sendEmailViaOutreach()` method
- Maps Lead data to outreach State schema
- Handles workflow execution and response parsing
- Includes comprehensive error handling and timeout management

### 3. **`frontend/src/components/LeadsTable.tsx`**
- Added `handleSendViaOutreach()` function
- Added "Send Email" button (primary action)
- Updated "Draft Email" button (secondary action)
- Enhanced loading states to distinguish between drafting and sending
- Displays appropriate messages during AI generation and email sending

## 🎯 How To Use

### Quick Start

1. **Ensure `.env.dev` has Gmail credentials:**
   ```bash
   SENDER_EMAIL_ADDRESS=hackohi00@gmail.com
   SENDER_EMAIL_PASSWORD=your_16_digit_app_password
   GEMINI_API_KEY=your_gemini_key
   ```

2. **Start the outreach service:**
   ```bash
   docker-compose -f docker-compose.dev.yml up outreach
   ```

3. **In the UI:**
   - Search for leads
   - Customize email goal (optional)
   - Click **"Send Email"** to generate and send immediately
   - Or click **"Draft"** to review before sending

## 🔄 User Flow

```
┌─────────────────────┐
│  Search for Leads   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  View Leads Table   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Customize Goal      │
│   (Optional)        │
└──────────┬──────────┘
           │
      ┌────┴────┐
      │         │
      ▼         ▼
  ┌──────┐  ┌────────┐
  │Draft │  │  Send  │
  └───┬──┘  │ Email  │
      │     └───┬────┘
      │         │
      ▼         │
  ┌──────┐     │
  │Review│     │
  └───┬──┘     │
      │         │
      ▼         ▼
  ┌─────────────────┐
  │ Email Sent via  │
  │ hackohi00@...   │
  └─────────────────┘
```

## 🛠️ Technical Details

### API Call Flow

1. User clicks "Send Email"
2. `handleSendViaOutreach(lead)` is called
3. Constructs State object:
   ```typescript
   {
     client_name: lead.name,
     client_email: lead.emails[0],
     sender_name: "LeadForge Team",
     sender_title: "Business Development Manager",
     website_critique: lead.website_review || generated,
     demo_url: lead.deployed_website_url || lead.website,
     web_agency_name: "LeadForge",
     web_agency_logo: "https://via.placeholder.com/150"
   }
   ```
4. POST to `http://localhost:8004/workflow/create-workflow`
5. Workflow executes:
   - Gemini generates personalized email
   - Sends via Gmail SMTP
6. Returns `{ success: bool, emailContent: {...} }`
7. UI updates with success/error message

### Error Handling

- **Connection errors**: "Cannot connect to outreach service..."
- **Timeout**: After 2 minutes with helpful message
- **SMTP errors**: Detailed Gmail authentication errors
- **No email**: Disabled button with tooltip
- **General errors**: User-friendly messages with retry option

## 📋 Required Environment Variables

Your `.env.dev` file should include:

```bash
# Gmail (REQUIRED for sending)
SENDER_EMAIL_ADDRESS=hackohi00@gmail.com
SENDER_EMAIL_PASSWORD=<16-digit app password>

# AI (REQUIRED for email generation)
GEMINI_API_KEY=<your key>
MODEL_NAME=gemini-2.0-flash-exp
MODEL_PROVIDER=google_genai

# Database (REQUIRED)
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_OUTREACH_DB=outreach_db

# Debug (REQUIRED for CORS)
DEBUG=true
```

## 🧪 Testing Checklist

- [ ] Outreach service starts without errors
- [ ] Frontend connects to http://localhost:8004
- [ ] "Send Email" button appears for leads with emails
- [ ] Button shows loading state during sending
- [ ] Success message appears when email sent
- [ ] Email received at lead's inbox
- [ ] Email sent from hackohi00@gmail.com
- [ ] Error handling works for missing credentials
- [ ] Timeout handling works (can test by stopping service mid-request)
- [ ] Draft button still works independently

## 📚 Documentation

- **Detailed Guide**: See `OUTREACH_INTEGRATION_GUIDE.md`
- **API Docs**: http://localhost:8004/docs (when service is running)
- **Email Config**: `frontend/src/config/email.ts`

## 🎉 Next Steps

1. **Get Gmail App Password** (if not already done)
2. **Update `.env.dev`** with credentials
3. **Start services** and test the flow
4. **Customize email templates** if needed (edit `outreach/app/agents/draft_email_node.py`)
5. **Monitor Gmail limits** (500 emails/day for regular accounts)

## 💡 Tips

- **Test with yourself first**: Use your own email as the lead to test
- **Check browser console**: Detailed logs show the entire flow
- **Monitor Docker logs**: `docker logs -f outreach_dev`
- **Gmail sent folder**: Verify emails are being sent
- **Customize goals**: Different pitches for different lead types

---

**Integration completed successfully! 🚀**

The "Send Email" button now uses the outreach workflow to generate and send emails via `hackohi00@gmail.com`.

