// Simple email service for testing
// This is a basic implementation for sending test emails

interface EmailConfig {
  senderEmail: string;
  testReceiverEmail: string;
  useTestMode: boolean;
}

interface EmailContent {
  subject: string;
  body: string;
  to: string;
  from: string;
}

class SimpleEmailService {
  private config: EmailConfig;

  constructor(config: EmailConfig) {
    this.config = config;
  }

  /**
   * Send a test email using a simple approach
   * For now, this will simulate sending but provide detailed logs
   */
  async sendTestEmail(content: EmailContent): Promise<{ success: boolean; message: string }> {
    console.log('📧 Sending test email...');
    console.log('📧 From:', content.from);
    console.log('📧 To:', content.to);
    console.log('📧 Subject:', content.subject);
    console.log('📧 Body:', content.body);

    try {
      // Simulate email sending delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // For testing purposes, we'll create a detailed log
      const emailDetails = {
        timestamp: new Date().toISOString(),
        from: content.from,
        to: content.to,
        subject: content.subject,
        body: content.body,
        status: 'sent',
        testMode: this.config.useTestMode
      };

      console.log('✅ Email details logged:', emailDetails);

      // In a real implementation, you would send the email here
      // For now, we'll just log the details
      
      return {
        success: true,
        message: `Test email logged successfully to ${content.to}${this.config.useTestMode ? ' (Test Mode)' : ''}`
      };

    } catch (error) {
      console.error('❌ Email sending failed:', error);
      return {
        success: false,
        message: `Failed to send email: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Create email content from lead data
   */
  createEmailContent(lead: any): EmailContent {
    const subject = `Partnership Opportunity - ${lead.name}`;
    const body = `Hi there,

I hope this email finds you well. I came across ${lead.name} and was impressed by your ${lead.category || 'business'}${lead.website ? ` and website (${lead.website})` : ''}.

${lead.website_review ? `I noticed that ${lead.website_review.toLowerCase()}` : 'I believe there are some great opportunities to enhance your online presence.'}

I'd love to discuss how our AI-powered website optimization and SEO services could help ${lead.name} attract more customers and grow your business. We specialize in:

• Modern website design and development
• Search engine optimization (SEO)
• Performance optimization
• Mobile-responsive design

Would you be interested in a brief 15-minute call to explore how we could help ${lead.name} reach more customers online?

Best regards,
Your Sales Team

P.S. I'd be happy to provide a free website analysis to show you specific opportunities for improvement.`;

    const recipientEmail = this.config.useTestMode 
      ? this.config.testReceiverEmail 
      : lead.emails[0];

    return {
      subject,
      body,
      to: recipientEmail,
      from: this.config.senderEmail
    };
  }
}

export { SimpleEmailService, type EmailConfig, type EmailContent };
