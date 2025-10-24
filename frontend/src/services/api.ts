import type { 
  Lead, 
  WorkflowResponse, 
  SearchRequest,
  BuilderRequest,
  BuilderWorkflowResponse,
  DeployerRequest,
  DeployerResponse,
  EmailDraftResponse,
  BuildAndDeployResponse
} from '../types';
import { EMAIL_CONFIG } from '../config/email';
import { SimpleEmailService } from './emailService';

const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_LEADS_API_URL || 'http://localhost:8001',
  ENDPOINTS: {
    WORKFLOW: '/workflow/create-workflow',
    HEALTH: '/docs',
  },
  DEFAULT_SETTINGS: {
    RADIUS: 25000,
    MIN_RATING: 0.0,
    MAX_RESULTS: 2,
  }
};

const BUILDER_API_CONFIG = {
  BASE_URL: import.meta.env.VITE_BUILDER_API_URL || 'http://localhost:8002',
  ENDPOINTS: {
    WORKFLOW: '/workflow/create-workflow',
    HEALTH: '/docs',
  },
  DEFAULT_SETTINGS: {
    SCRAPE_LIMIT: 5,
  }
};

const DEPLOYER_API_CONFIG = {
  BASE_URL: import.meta.env.VITE_DEPLOYER_API_URL || 'http://localhost:8003',
  ENDPOINTS: {
    DEPLOY: '/deploy/',
    HEALTH: '/docs',
  }
};

// Email API config - currently using mock implementation
// const EMAIL_API_CONFIG = {
//   BASE_URL: import.meta.env.VITE_EMAIL_API_URL || 'http://localhost:8001',
//   ENDPOINTS: {
//     DRAFT: '/email/draft',
//     HEALTH: '/docs',
//   }
// };
class ApiErrorHandler {
  static async parseError(response: Response): Promise<string> {
    try {
      const errorData = await response.json();
      
      if (errorData.detail) {
        return this.formatErrorDetail(errorData.detail);
      }
      
      if (errorData.message) {
        return `API Error: ${errorData.message}`;
      }
      
      return `HTTP Error: ${response.status} - ${response.statusText}`;
    } catch (parseError) {
      return `HTTP Error: ${response.status} - ${response.statusText}`;
    }
  }

  private static formatErrorDetail(detail: unknown): string {
    if (typeof detail === 'string') {
      return `API Error: ${detail}`;
    }
    
    if (Array.isArray(detail)) {
      const errors = detail.map((err: unknown) => {
        if (typeof err === 'string') return err;
        if (err && typeof err === 'object') {
          const errorObj = err as Record<string, unknown>;
          return errorObj.msg || errorObj.message || JSON.stringify(err);
        }
        return JSON.stringify(err);
      }).join(', ');
      return `Validation Error: ${errors}`;
    }
    
    return `API Error: ${JSON.stringify(detail)}`;
  }
}

/**
 * Utility class for parsing search queries
 */
class QueryParser {
  private static readonly CITY_PATTERNS = [
    /in\s+([^,\n]+?)(?:\s|$)/i,
    /near\s+([^,\n]+?)(?:\s|$)/i,
    /at\s+([^,\n]+?)(?:\s|$)/i,
    /around\s+([^,\n]+?)(?:\s|$)/i,
    /located\s+in\s+([^,\n]+?)(?:\s|$)/i
  ];

  static parse(query: string): { city: string; businessType: string } {
    if (!query?.trim()) {
      throw new Error('Search query cannot be empty');
    }

    const trimmedQuery = query.trim();
    let city = 'Columbus'; // Default city for testing
    let businessType = trimmedQuery;

    // Try to extract city from query
    for (const pattern of this.CITY_PATTERNS) {
      const match = trimmedQuery.match(pattern);
      if (match) {
        city = this.cleanCityName(match[1]);
        businessType = trimmedQuery.replace(pattern, '').trim();
        break;
      }
    }

    // Clean up business type
    businessType = businessType
      .replace(/^(in|near|at|around|located in)\s+/i, '')
      .trim();

    return { city, businessType };
  }

  private static cleanCityName(city: string): string {
    return city.trim().replace(/[^\w\s-]/g, '');
  }
}

/**
 * Main API service for lead generation
 */
export class LeadsApiService {
  /**
   * Test if the API service is reachable
   */
  static async testConnection(): Promise<boolean> {
    try {
      console.log('🔗 Testing connection to:', `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.HEALTH}`);
      
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.HEALTH}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        // Add timeout to prevent hanging
        signal: AbortSignal.timeout(30000) // 30 second timeout for health check
      });
      
      console.log('🔗 Connection test response:', response.status, response.statusText);
      return response.ok;
    } catch (error) {
      console.error('❌ API connection test failed:', error);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          console.error('Connection timeout - backend may be slow or not responding');
        } else if (error.message.includes('fetch')) {
          console.error('Network error - backend may not be running or CORS issue');
        }
      }
      
      return false;
    }
  }

  /**
   * Search for leads using natural language query
   */
  static async searchLeads(searchQuery: string): Promise<Lead[]> {
    console.log('🔍 Starting lead search for:', searchQuery);

    try {
      // Parse the search query
      const parsedQuery = QueryParser.parse(searchQuery);
      console.log('📝 Parsed query:', parsedQuery);

      // Log timing for debugging
      const startTime = Date.now();

      // Prepare the search request
      const searchRequest: SearchRequest = {
        city: parsedQuery.city,
        business_type: parsedQuery.businessType,
        radius: API_CONFIG.DEFAULT_SETTINGS.RADIUS,
        min_rating: API_CONFIG.DEFAULT_SETTINGS.MIN_RATING,
        max_results: API_CONFIG.DEFAULT_SETTINGS.MAX_RESULTS,
        messages: [],
        leads: []
      };

      console.log('📤 Sending request:', searchRequest);

      // Make the API call
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.WORKFLOW}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(searchRequest),
        // Add timeout to prevent hanging - agents need more time
        signal: AbortSignal.timeout(120000) // 2 minute timeout for workflow processing
      });

      // Handle errors
      if (!response.ok) {
        const errorMessage = await ApiErrorHandler.parseError(response);
        throw new Error(errorMessage);
      }

      // Parse successful response
      const workflow: WorkflowResponse = await response.json();
      console.log('✅ Workflow completed:', workflow);

      const leads = workflow.final_state.leads || [];
      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;
      
      console.log(`🎯 Found ${leads.length} leads in ${duration}s`);

      return leads;

    } catch (error) {
      console.error('❌ Lead search failed:', error);
      
      // Provide more specific error messages for common issues
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Search timeout - The AI agents are taking longer than expected to process your request. This can happen when:\n\n• Searching for many businesses\n• Enriching contact information\n• Analyzing websites\n\nTry searching for a more specific business type or smaller location.');
        } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
          throw new Error('Cannot connect to the backend service. Please ensure:\n1. The leads service is running on port 8001\n2. Docker containers are started\n3. No firewall is blocking the connection');
        } else if (error.message.includes('CORS')) {
          throw new Error('CORS error - backend service may not be configured to accept requests from this domain');
        }
      }
      
      throw error;
    }
  }

  /**
   * Validate API connection and throw user-friendly error if not available
   */
  static async ensureConnection(): Promise<void> {
    const isConnected = await this.testConnection();
    if (!isConnected) {
      throw new Error(
        'Cannot connect to the leads service. Please check:\n\n' +
        '1. Backend service is running: docker-compose up leads\n' +
        '2. Service is accessible on port 8001\n' +
        '3. No firewall blocking localhost:8001\n' +
        '4. Docker containers are healthy\n\n' +
        'Try running: docker-compose ps to check service status'
      );
    }
  }

  /**
   * Run comprehensive diagnostics
   */
  static async runDiagnostics(): Promise<void> {
    console.log('🔍 Running API diagnostics...');
    
    // Test different endpoints
    const endpoints = [
      { name: 'Health Check', url: `${API_CONFIG.BASE_URL}/docs` },
      { name: 'API Root', url: `${API_CONFIG.BASE_URL}/` },
      { name: 'Workflow Endpoint', url: `${API_CONFIG.BASE_URL}/workflow/` }
    ];

    for (const endpoint of endpoints) {
      try {
        console.log(`Testing ${endpoint.name}: ${endpoint.url}`);
        const response = await fetch(endpoint.url, { 
          method: 'GET',
          signal: AbortSignal.timeout(5000)
        });
        console.log(`✅ ${endpoint.name}: ${response.status} ${response.statusText}`);
      } catch (error) {
        console.log(`❌ ${endpoint.name}: ${error}`);
      }
    }

    // Test CORS
    try {
      console.log('Testing CORS...');
      const response = await fetch(`${API_CONFIG.BASE_URL}/docs`, {
        method: 'OPTIONS',
        signal: AbortSignal.timeout(5000)
      });
      console.log(`✅ CORS: ${response.status}`);
    } catch (error) {
      console.log(`❌ CORS: ${error}`);
    }
  }
}

/**
 * API service for website building and deployment
 */
export class BuilderApiService {
  /**
   * Test if the builder API service is reachable
   */
  static async testConnection(): Promise<boolean> {
    try {
      console.log('🔗 Testing builder connection to:', `${BUILDER_API_CONFIG.BASE_URL}${BUILDER_API_CONFIG.ENDPOINTS.HEALTH}`);
      
      const response = await fetch(`${BUILDER_API_CONFIG.BASE_URL}${BUILDER_API_CONFIG.ENDPOINTS.HEALTH}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(10000) // 10 second timeout for health check
      });
      
      console.log('🔗 Builder connection test response:', response.status, response.statusText);
      return response.ok;
    } catch (error) {
      console.error('❌ Builder API connection test failed:', error);
      return false;
    }
  }

  /**
   * Build a website from a URL or create a generic business website
   */
  static async buildWebsite(websiteUrl: string, businessName: string): Promise<string> {
    console.log('🏗️ Starting website build for:', businessName, 'from URL:', websiteUrl);

    try {
      const startTime = Date.now();

      // Prepare the build request
      const buildRequest: BuilderRequest = {
        initial_website_url: websiteUrl || `https://example.com`, // Fallback URL if none provided
        initial_website_scrape_limit: BUILDER_API_CONFIG.DEFAULT_SETTINGS.SCRAPE_LIMIT,
        prompt: websiteUrl ? undefined : `Create a professional business website for ${businessName}`,
      };

      console.log('📤 Sending build request:', buildRequest);

      // Make the API call to builder
      const response = await fetch(`${BUILDER_API_CONFIG.BASE_URL}${BUILDER_API_CONFIG.ENDPOINTS.WORKFLOW}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(buildRequest),
        signal: AbortSignal.timeout(180000) // 3 minute timeout for building
      });

      // Handle errors
      if (!response.ok) {
        const errorMessage = await ApiErrorHandler.parseError(response);
        throw new Error(errorMessage);
      }

      // Parse successful response
      const workflow: BuilderWorkflowResponse = await response.json();
      console.log('✅ Website build completed:', workflow);

      const websiteZip = workflow.final_state.final_website_zip;
      if (!websiteZip) {
        throw new Error('Website build completed but no zip file was generated');
      }

      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;
      console.log(`🎯 Website built in ${duration}s`);

      return websiteZip;

    } catch (error) {
      console.error('❌ Website build failed:', error);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Website build timeout - The AI agents are taking longer than expected to build your website. This can happen when:\n\n• Scraping complex websites\n• Processing many pages\n• Generating custom content\n\nPlease try again or use a simpler website URL.');
        } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
          throw new Error('Cannot connect to the builder service. Please ensure:\n1. The builder service is running on port 8002\n2. Docker containers are started\n3. No firewall is blocking the connection');
        }
      }
      
      throw error;
    }
  }

  /**
   * Build and deploy a website in one operation
   */
  static async buildAndDeployWebsite(websiteUrl: string, businessName: string): Promise<BuildAndDeployResponse> {
    console.log('🚀 Starting build and deploy for:', businessName);

    try {
      // Step 1: Build the website
      const websiteZip = await this.buildWebsite(websiteUrl, businessName);

      // Step 2: Deploy the website
      const deployedSite = await DeployerApiService.deployWebsite(businessName, websiteZip);

      return {
        websiteZip,
        deployedUrl: deployedSite.url,
        websiteId: deployedSite.id,
      };

    } catch (error) {
      console.error('❌ Build and deploy failed:', error);
      throw error;
    }
  }
}

/**
 * API service for website deployment
 */
export class DeployerApiService {
  /**
   * Test if the deployer API service is reachable
   */
  static async testConnection(): Promise<boolean> {
    try {
      console.log('🔗 Testing deployer connection to:', `${DEPLOYER_API_CONFIG.BASE_URL}${DEPLOYER_API_CONFIG.ENDPOINTS.HEALTH}`);
      
      const response = await fetch(`${DEPLOYER_API_CONFIG.BASE_URL}${DEPLOYER_API_CONFIG.ENDPOINTS.HEALTH}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(10000) // 10 second timeout for health check
      });
      
      console.log('🔗 Deployer connection test response:', response.status, response.statusText);
      return response.ok;
    } catch (error) {
      console.error('❌ Deployer API connection test failed:', error);
      return false;
    }
  }

  /**
   * Deploy a website from a base64-encoded zip file
   */
  static async deployWebsite(websiteName: string, zipBase64: string): Promise<DeployerResponse> {
    console.log('🚀 Starting website deployment for:', websiteName);

    try {
      const startTime = Date.now();

      // Prepare the deploy request
      const deployRequest: DeployerRequest = {
        name: websiteName,
        zip_base64: zipBase64,
      };

      console.log('📤 Sending deploy request for:', websiteName);

      // Make the API call to deployer
      const response = await fetch(`${DEPLOYER_API_CONFIG.BASE_URL}${DEPLOYER_API_CONFIG.ENDPOINTS.DEPLOY}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(deployRequest),
        signal: AbortSignal.timeout(60000) // 1 minute timeout for deployment
      });

      // Handle errors
      if (!response.ok) {
        const errorMessage = await ApiErrorHandler.parseError(response);
        throw new Error(errorMessage);
      }

      // Parse successful response
      const deployedSite: DeployerResponse = await response.json();
      console.log('✅ Website deployed:', deployedSite);

      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;
      console.log(`🎯 Website deployed in ${duration}s at: ${deployedSite.url}`);

      return deployedSite;

    } catch (error) {
      console.error('❌ Website deployment failed:', error);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Website deployment timeout - The deployment is taking longer than expected. Please try again.');
        } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
          throw new Error('Cannot connect to the deployer service. Please ensure:\n1. The deployer service is running on port 8003\n2. Docker containers are started\n3. No firewall is blocking the connection');
        }
      }
      
      throw error;
    }
  }
}

/**
 * API service for email draft creation
 */
export class EmailApiService {
  // Use configuration from config file
  private static readonly TEST_CONFIG = EMAIL_CONFIG;
  private static emailService = new SimpleEmailService({
    senderEmail: EMAIL_CONFIG.SENDER_EMAIL,
    testReceiverEmail: EMAIL_CONFIG.TEST_RECEIVER_EMAIL,
    useTestMode: EMAIL_CONFIG.USE_TEST_MODE
  });

  /**
   * Create a Gmail draft for a specific lead
   */
  static async createEmailDraft(lead: Lead, goal?: string): Promise<EmailDraftResponse> {
    console.log('📧 Creating email draft for:', lead.name);

    try {
      if (!lead.emails || lead.emails.length === 0) {
        throw new Error('No email address available for this lead');
      }

      const startTime = Date.now();

      console.log('📤 Creating email draft for:', lead.name, 'with goal:', goal || 'default sales goal');

      // For now, we'll simulate the email draft creation since the email agent
      // is a standalone script. In a real implementation, this would call
      // a proper API endpoint that wraps the email agent functionality.
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Generate a realistic email draft based on lead information
      const subject = `Partnership Opportunity - ${lead.name}`;
      const body = `Hi there,

I hope this email finds you well. I came across ${lead.name} and was impressed by your ${lead.category || 'business'} ${lead.website ? `and website (${lead.website})` : ''}.

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

      // Determine recipient email (use test email in test mode)
      const recipientEmail = this.TEST_CONFIG.USE_TEST_MODE 
        ? this.TEST_CONFIG.TEST_RECEIVER_EMAIL 
        : lead.emails[0];

      // Mock successful response with draft content
      const draftResponse: EmailDraftResponse = {
        success: true,
        draft_id: `draft_${Date.now()}_${lead.id}`,
        message: `Email draft created successfully for ${lead.name}`,
        draft_content: {
          subject,
          body,
          to: recipientEmail,
        },
      };

      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;
      console.log(`✅ Email draft created in ${duration}s for: ${lead.name}`);

      return draftResponse;

    } catch (error) {
      console.error('❌ Email draft creation failed:', error);
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  /**
   * Send an email using the simple email service
   */
  static async sendEmail(draftId: string, lead: Lead): Promise<{ success: boolean; message?: string; error?: string }> {
    console.log('📧 Sending email for:', lead.name, 'draft ID:', draftId);

    try {
      // Create email content
      const emailContent = this.emailService.createEmailContent(lead);
      
      // Send the email
      const result = await this.emailService.sendTestEmail(emailContent);

      if (result.success) {
        console.log(`✅ Email sent successfully from ${emailContent.from} to ${emailContent.to}`);
        console.log(`📧 Test Mode: ${this.TEST_CONFIG.USE_TEST_MODE ? 'Enabled' : 'Disabled'}`);
        
        return {
          success: true,
          message: result.message,
        };
      } else {
        return {
          success: false,
          error: result.message,
        };
      }

    } catch (error) {
      console.error('❌ Email send failed:', error);
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred while sending email',
      };
    }
  }
}

// Export the service as default for backward compatibility
export const leadsApi = {
  testConnection: LeadsApiService.testConnection,
  createWorkflow: LeadsApiService.searchLeads,
};
