# Email Setup Instructions

## Quick Setup for Testing

1. **Open the configuration file**: `src/config/email.ts`

2. **Update the email addresses**:
   ```typescript
   export const EMAIL_CONFIG = {
     SENDER_EMAIL: 'your-email@gmail.com', // Replace with your actual email
     TEST_RECEIVER_EMAIL: 'test-receiver@gmail.com', // Replace with test email
     USE_TEST_MODE: true, // Set to false for production
   };
   ```

3. **For testing purposes**, you can use any email addresses since the system currently uses mock email sending.

## Features

### ✅ **Bigger Email Preview**
- Email preview dropdown is now much larger
- Shows the entire email without scrolling (min-height: 64, max-height: 96)
- Better layout with proper spacing and typography
- Shows both sender and receiver email addresses

### ✅ **Email Configuration**
- Centralized email configuration in `src/config/email.ts`
- Test mode allows using a test receiver email instead of actual lead emails
- Easy to switch between test and production modes

### ✅ **Test Mode Features**
- When `USE_TEST_MODE: true`, all emails are sent to your test receiver email
- Console logs show which email addresses are being used
- Clear indication when test mode is active

## How to Use

1. **Update your email addresses** in `src/config/email.ts`
2. **Click "Draft Email"** on any lead
3. **Review the email** in the larger preview dropdown
4. **Click "Send Email"** to send (currently mocked)
5. **Check console logs** to see the email details

## For Real Gmail Integration (Future)

To set up real Gmail integration, you'll need:

1. **Google Cloud Project** with Gmail API enabled
2. **OAuth2 credentials** (client_id and client_secret)
3. **credentials.json file** for OAuth2 flow
4. **Update the email service** to use real Gmail API calls

The current implementation is ready for this integration - just replace the mock functions with real API calls.

## Current Status

- ✅ **Bigger email preview dropdown**
- ✅ **Email configuration system**
- ✅ **Test mode for safe testing**
- ✅ **Mock email sending (ready for real integration)**
- ✅ **Console logging for debugging**

The email system is now ready for testing with your own email addresses!
