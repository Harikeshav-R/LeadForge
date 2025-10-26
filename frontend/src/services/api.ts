<<<<<<< HEAD
import type {
    BuildAndDeployResponse,
    BuilderRequest,
    BuilderWorkflowResponse,
    DeployerRequest,
    DeployerResponse,
    EmailContent,
    EmailDraftRequest,
    EmailDraftResponse,
    EmailSendRequest,
    EmailSendResponse,
    Lead,
    SearchRequest,
    WorkflowResponse
} from '../types';
import {EMAIL_CONFIG} from '../config/email';

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
=======
import type { 
  Lead, 
  WorkflowResponse, 
  SearchRequest,
  BuilderRequest,
  BuilderWorkflowResponse,
  DeployerRequest,
  DeployerResponse,
  EmailDraftRequest,
  EmailDraftResponse,
  EmailSendRequest,
  EmailSendResponse,
  BuildAndDeployResponse,
  EmailContent
} from '../types';
import { EMAIL_CONFIG } from '../config/email';

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
>>>>>>> main-holder
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
<<<<<<< HEAD
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
=======
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
>>>>>>> main-holder
}

/**
 * Utility class for parsing search queries
 */
class QueryParser {
<<<<<<< HEAD
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

        return {city, businessType};
    }

    private static cleanCityName(city: string): string {
        return city.trim().replace(/[^\w\s-]/g, '');
    }
=======
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
>>>>>>> main-holder
}

/**
 * Main API service for lead generation
 */
export class LeadsApiService {
<<<<<<< HEAD
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

            // HARDCODE: Insert cookie website at the top for demo
            const cookieLead: Lead = {
                id: 'demo-cookie-' + Date.now(),
                place_id: 'demo-place-id-cookie',
                state_id: '',
                name: 'Cookies 4 U',
                address: '67 West Oakland Avenue, Columbus, OH 43201',
                phone_number: '(440)3349257',
                phone_numbers: ['(440)3349257'],
                emails: ['rahulksanghvi21@gmail.com'], // Display email (shown on screen)
                social_media: [],
                screenshots: [],
                website: 'http://deployer:8003/demo-website/',
                rating: 3.7,
                total_ratings: 67,
                category: 'Cookie Shop',
                lat: 39.9612,
                lng: -82.9988,
                // deployed_website_url will be populated when website is deployed
                website_review: 'First Impression & Visual Appeal\n' +
                    'The first impression is overwhelmingly negative. The website appears to be from the early 1990s or, more likely, is broken and has failed to load its CSS stylesheet. It does not look modern, and more importantly, it does not look trustworthy. For a business selling food, trust is paramount, and this design actively erodes it.\n' +
                    '\n' +
                    'The site relies entirely on default browser-agent styles: a serif font (Times New Roman), standard blue/purple hyperlinks, and a stark white background. There is a complete absence of branding, color theory, or visual design.\n' +
                    '\n' +
                    'Branding: There is no logo, color palette, or custom typography to establish a brand identity for "Cookies 4 U."\n' +
                    '\n' +
                    'Imagery: A website selling cookies must feature high-quality, appetizing photos of the product. The lack of any images is a critical failure.\n' +
                    '\n' +
                    'Layout: The content is a single, left-aligned column of text. This "layout" is monotonous, difficult to scan, and looks unprofessional.\n' +
                    '\n' +
                    'Navigation & Usability\n' +
                    'The site\'s usability is extremely low, and its navigation is confusing.\n' +
                    '\n' +
                    'Navigation: The primary navigation at the top is an unstyled bulleted list. This is visually jarring and looks like an error. Furthermore, the links in this list ("Menu," "Hours," "Contact") appear to point to sections that are already on this same page, making the navigation redundant and confusing.\n' +
                    '\n' +
                    'Hierarchy: While a logical information structure exists (Menu > Why Us > Testimonials), there is no visual hierarchy to support it. The default heading styles provide very little differentiation, forcing the user to read the page like a document rather than scan it.\n' +
                    '\n' +
                    'Call to Action (CTA): The primary CTA, "Order inquiry," is a small, standard blue link that is easily lost. It lacks prominence, visual weight, and compelling copy (e.g., "Order Your Cookies Now").\n' +
                    '\n' +
                    'Trust Signals: The "Contact Us" section lists a generic email address (johnjohannes671@email.com). A professional business should use a domain-specific email (e.g., orders@cookies4u.com), as this generic address feels personal and suspicious.\n' +
                    '\n' +
                    'Responsiveness\n' +
                    'Only a desktop view was provided, but conclusions can be drawn from the fluid-width, unstyled layout.\n' +
                    '\n' +
                    'The site is "responsive by accident," not by design. The single column of text will simply reflow to fit any screen size. This is not a positive trait.\n' +
                    '\n' +
                    'On Wide Monitors: On wide screens, the text lines will become excessively long, severely damaging readability.\n' +
                    '\n' +
                    'On Mobile Devices: On a narrow mobile screen, the text will reflow, but the default font size will likely be too small, and the layout will feel cramped. A proper responsive design would adapt font sizes, spacing, and navigation (e.g., using a "hamburger" menu) for an optimal mobile experience. This site does none of that.\n' +
                    '\n' +
                    'Suggestions for Improvement\n' +
                    'Implement a Professional Design: The site must be built with a CSS stylesheet. This involves developing a simple brand identity (a logo, a warm and appetizing color palette) and using it to style the page. Replace the default serif font with a modern, readable sans-serif font for body text and headings.\n' +
                    '\n' +
                    'Create a Visual Hierarchy and Layout: Use a grid system to structure the content instead of a single column. Use intentional whitespace, background colors, and typography to visually separate sections (e.g., placing the Menu in a clear card or table structure, and setting Testimonials apart). High-quality photographs of the cookies are non-negotiable and must be added.\n' +
                    '\n' +
                    'Redesign the Navigation and CTA: The primary navigation should be a clean, horizontal bar at the top, and it should link to clear sections if this remains a one-page site. The "Order inquiry" link must be converted into a prominent, high-contrast button (a clear Call to Action) and placed "above the fold" to immediately capture the user\'s attention.'
            };

            // Insert at the beginning of the array
            leads.unshift(cookieLead);

            const endTime = Date.now();
            const duration = (endTime - startTime) / 1000;

            console.log(`🎯 Found ${leads.length} leads in ${duration}s`);
            console.log('🎯 Cookies 4 U hardcoded at top for demo');

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
            {name: 'Health Check', url: `${API_CONFIG.BASE_URL}/docs`},
            {name: 'API Root', url: `${API_CONFIG.BASE_URL}/`},
            {name: 'Workflow Endpoint', url: `${API_CONFIG.BASE_URL}/workflow/`}
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
=======
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
>>>>>>> main-holder
}

/**
 * API service for website building and deployment
 */
export class BuilderApiService {
<<<<<<< HEAD
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
                initial_website_url: websiteUrl || `http://localhost:8003/demo-website`, // Fallback URL if none provided
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
                // No timeout - allow long-running AI agent processes to complete
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
=======
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
>>>>>>> main-holder
}

/**
 * API service for website deployment
 */
export class DeployerApiService {
<<<<<<< HEAD
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
=======
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
>>>>>>> main-holder
}

/**
 * API service for Gmail Email Agent integration
 */
export class EmailApiService {
<<<<<<< HEAD
    /**
     * Test if the email agent API service is reachable
     */
    static async testConnection(): Promise<boolean> {
        try {
            console.log('🔗 Testing email agent connection to:', `${EMAIL_CONFIG.EMAIL_AGENT_API_URL}/health`);

            const response = await fetch(`${EMAIL_CONFIG.EMAIL_AGENT_API_URL}/health`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                signal: AbortSignal.timeout(10000) // 10 second timeout for health check
            });

            console.log('🔗 Email agent connection test response:', response.status, response.statusText);
            return response.ok;
        } catch (error) {
            console.error('❌ Email agent API connection test failed:', error);
            return false;
        }
    }

    /**
     * Create a Gmail draft for a specific lead using the email agent
     */
    static async createEmailDraft(lead: Lead, goal: string, maxWords: number = EMAIL_CONFIG.DEFAULT_MAX_WORDS): Promise<EmailDraftResponse> {
        console.log('📧 Creating Gmail draft for:', lead.name, 'with goal:', goal);

        try {
            if (!lead.emails || lead.emails.length === 0) {
                throw new Error('No email address available for this lead');
            }

            const startTime = Date.now();

            // Prepare the draft request
            const draftRequest: EmailDraftRequest = {
                lead,
                goal,
                max_words: maxWords,
            };

            console.log('📤 Sending draft request to email agent for:', lead.name);

            // Make the API call to email agent
            const response = await fetch(`${EMAIL_CONFIG.EMAIL_AGENT_API_URL}/draft-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify(draftRequest),
                signal: AbortSignal.timeout(60000) // 1 minute timeout for AI generation
            });

            // Handle errors
            if (!response.ok) {
                const errorMessage = await ApiErrorHandler.parseError(response);
                throw new Error(errorMessage);
            }

            // Parse successful response
            const draftResponse: EmailDraftResponse = await response.json();
            console.log('✅ Gmail draft created:', draftResponse);

            const endTime = Date.now();
            const duration = (endTime - startTime) / 1000;
            console.log(`🎯 Gmail draft created in ${duration}s for: ${lead.name}`);

            return draftResponse;

        } catch (error) {
            console.error('❌ Gmail draft creation failed:', error);

            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    throw new Error('Email draft creation timeout - The AI is taking longer than expected. Please try again.');
                } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
                    throw new Error('Cannot connect to the email agent service. Please ensure:\n1. The email agent is running on port 8000\n2. Run: cd HackOHIO/leads/app/agents && python email_agent.py\n3. Gmail OAuth credentials are set up');
                }
            }

            throw error;
        }
    }

    /**
     * Send an email using the email agent (drafts and sends in one call)
     */
    static async sendEmail(lead: Lead, goal: string, maxWords: number = EMAIL_CONFIG.DEFAULT_MAX_WORDS): Promise<EmailSendResponse> {
        console.log('📧 Sending email via Gmail for:', lead.name, 'with goal:', goal);

        try {
            if (!lead.emails || lead.emails.length === 0) {
                throw new Error('No email address available for this lead');
            }

            const startTime = Date.now();

            // Prepare the send request
            const sendRequest: EmailSendRequest = {
                lead,
                goal,
                max_words: maxWords,
            };

            console.log('📤 Sending email request to email agent for:', lead.name);

            // Make the API call to email agent
            const response = await fetch(`${EMAIL_CONFIG.EMAIL_AGENT_API_URL}/send-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify(sendRequest),
                signal: AbortSignal.timeout(60000) // 1 minute timeout for AI generation + sending
            });

            // Handle errors
            if (!response.ok) {
                const errorMessage = await ApiErrorHandler.parseError(response);
                throw new Error(errorMessage);
            }

            // Parse successful response
            const sendResponse: EmailSendResponse = await response.json();
            console.log('✅ Email sent via Gmail:', sendResponse);

            const endTime = Date.now();
            const duration = (endTime - startTime) / 1000;
            console.log(`🎯 Email sent in ${duration}s to: ${sendResponse.contact_email}`);

            return sendResponse;

        } catch (error) {
            console.error('❌ Email send failed:', error);

            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    throw new Error('Email send timeout - The operation is taking longer than expected. Please try again.');
                } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
                    throw new Error('Cannot connect to the email agent service. Please ensure:\n1. The email agent is running on port 8000\n2. Run: cd HackOHIO/leads/app/agents && python email_agent.py\n3. Gmail OAuth credentials are set up');
                }
            }

            throw error;
        }
    }

    /**
     * Send a custom email with user-edited content
     * This sends the exact content provided by the user (after editing)
     */
    static async sendCustomEmail(emailContent: EmailContent): Promise<void> {
        console.log('📧 Sending custom email with edited content:', {
            to: emailContent.to,
            subject: emailContent.subject,
            bodyPreview: emailContent.body.substring(0, 100) + '...',
        });

        try {
            if (!emailContent.to) {
                throw new Error('Recipient email address is required');
            }

            if (!emailContent.subject) {
                throw new Error('Email subject is required');
            }

            if (!emailContent.body) {
                throw new Error('Email body is required');
            }

            const startTime = Date.now();

            // Parse recipients from comma-separated strings
            const parseEmails = (value: string): string[] => {
                if (!value || typeof value !== 'string') return [];
                return value
                    .split(',')
                    .map(email => email.trim())
                    .filter(email => email.length > 0);
            };

            const toEmails = parseEmails(emailContent.to);

            // Ensure we have at least one valid recipient
            if (toEmails.length === 0) {
                throw new Error('At least one recipient email is required');
            }

            // Use the first email as the primary recipient (backend uses lead.emails[0])
            const primaryRecipient = toEmails[0];

            // Create a temporary lead object with the edited email
            // Use only the first email for the lead object (backend expects emails[0])
            const tempLead: Lead = {
                place_id: 'temp-' + Date.now(),
                id: 'temp-' + Date.now(),
                state_id: 'temp-state',
                name: 'Custom Email',
                emails: [primaryRecipient], // Single email string as required by backend
                phone_numbers: [],
                social_media: [],
                screenshots: [],
                address: '',
                website: '',
                rating: 0,
                total_ratings: 0,
                category: '',
                lat: 0,
                lng: 0,
            };

            // Create a custom goal that includes the exact content the user wants to send
            const customGoal = `Send an email with the following exact content:
=======
  /**
   * Test if the email agent API service is reachable
   */
  static async testConnection(): Promise<boolean> {
    try {
      console.log('🔗 Testing email agent connection to:', `${EMAIL_CONFIG.EMAIL_AGENT_API_URL}/health`);
      
      const response = await fetch(`${EMAIL_CONFIG.EMAIL_AGENT_API_URL}/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(10000) // 10 second timeout for health check
      });
      
      console.log('🔗 Email agent connection test response:', response.status, response.statusText);
      return response.ok;
    } catch (error) {
      console.error('❌ Email agent API connection test failed:', error);
      return false;
    }
  }

  /**
   * Create a Gmail draft for a specific lead using the email agent
   */
  static async createEmailDraft(lead: Lead, goal: string, maxWords: number = EMAIL_CONFIG.DEFAULT_MAX_WORDS): Promise<EmailDraftResponse> {
    console.log('📧 Creating Gmail draft for:', lead.name, 'with goal:', goal);

    try {
      if (!lead.emails || lead.emails.length === 0) {
        throw new Error('No email address available for this lead');
      }

      const startTime = Date.now();

      // Prepare the draft request
      const draftRequest: EmailDraftRequest = {
        lead,
        goal,
        max_words: maxWords,
      };

      console.log('📤 Sending draft request to email agent for:', lead.name);

      // Make the API call to email agent
      const response = await fetch(`${EMAIL_CONFIG.EMAIL_AGENT_API_URL}/draft-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(draftRequest),
        signal: AbortSignal.timeout(60000) // 1 minute timeout for AI generation
      });

      // Handle errors
      if (!response.ok) {
        const errorMessage = await ApiErrorHandler.parseError(response);
        throw new Error(errorMessage);
      }

      // Parse successful response
      const draftResponse: EmailDraftResponse = await response.json();
      console.log('✅ Gmail draft created:', draftResponse);

      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;
      console.log(`🎯 Gmail draft created in ${duration}s for: ${lead.name}`);

      return draftResponse;

    } catch (error) {
      console.error('❌ Gmail draft creation failed:', error);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Email draft creation timeout - The AI is taking longer than expected. Please try again.');
        } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
          throw new Error('Cannot connect to the email agent service. Please ensure:\n1. The email agent is running on port 8000\n2. Run: cd HackOHIO/leads/app/agents && python email_agent.py\n3. Gmail OAuth credentials are set up');
        }
      }
      
      throw error;
    }
  }

  /**
   * Send an email using the email agent (drafts and sends in one call)
   */
  static async sendEmail(lead: Lead, goal: string, maxWords: number = EMAIL_CONFIG.DEFAULT_MAX_WORDS): Promise<EmailSendResponse> {
    console.log('📧 Sending email via Gmail for:', lead.name, 'with goal:', goal);

    try {
      if (!lead.emails || lead.emails.length === 0) {
        throw new Error('No email address available for this lead');
      }

      const startTime = Date.now();

      // Prepare the send request
      const sendRequest: EmailSendRequest = {
        lead,
        goal,
        max_words: maxWords,
      };

      console.log('📤 Sending email request to email agent for:', lead.name);

      // Make the API call to email agent
      const response = await fetch(`${EMAIL_CONFIG.EMAIL_AGENT_API_URL}/send-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(sendRequest),
        signal: AbortSignal.timeout(60000) // 1 minute timeout for AI generation + sending
      });

      // Handle errors
      if (!response.ok) {
        const errorMessage = await ApiErrorHandler.parseError(response);
        throw new Error(errorMessage);
      }

      // Parse successful response
      const sendResponse: EmailSendResponse = await response.json();
      console.log('✅ Email sent via Gmail:', sendResponse);

      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;
      console.log(`🎯 Email sent in ${duration}s to: ${sendResponse.contact_email}`);

      return sendResponse;

    } catch (error) {
      console.error('❌ Email send failed:', error);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Email send timeout - The operation is taking longer than expected. Please try again.');
        } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
          throw new Error('Cannot connect to the email agent service. Please ensure:\n1. The email agent is running on port 8000\n2. Run: cd HackOHIO/leads/app/agents && python email_agent.py\n3. Gmail OAuth credentials are set up');
        }
      }
      
      throw error;
    }
  }

  /**
   * Send a custom email with user-edited content
   * This sends the exact content provided by the user (after editing)
   */
  static async sendCustomEmail(emailContent: EmailContent): Promise<void> {
    console.log('📧 Sending custom email with edited content:', {
      to: emailContent.to,
      subject: emailContent.subject,
      bodyPreview: emailContent.body.substring(0, 100) + '...',
    });

    try {
      if (!emailContent.to) {
        throw new Error('Recipient email address is required');
      }

      if (!emailContent.subject) {
        throw new Error('Email subject is required');
      }

      if (!emailContent.body) {
        throw new Error('Email body is required');
      }

      const startTime = Date.now();

      // Parse recipients from comma-separated strings
      const parseEmails = (value: string): string[] => {
        if (!value || typeof value !== 'string') return [];
        return value
          .split(',')
          .map(email => email.trim())
          .filter(email => email.length > 0);
      };

      const toEmails = parseEmails(emailContent.to);
      
      // Ensure we have at least one valid recipient
      if (toEmails.length === 0) {
        throw new Error('At least one recipient email is required');
      }

      // Use the first email as the primary recipient (backend uses lead.emails[0])
      const primaryRecipient = toEmails[0];

      // Create a temporary lead object with the edited email
      // Use only the first email for the lead object (backend expects emails[0])
      const tempLead: Lead = {
        place_id: 'temp-' + Date.now(),
        id: 'temp-' + Date.now(),
        state_id: 'temp-state',
        name: 'Custom Email',
        emails: [primaryRecipient], // Single email string as required by backend
        phone_numbers: [],
        social_media: [],
        screenshots: [],
        address: '',
        website: '',
        rating: 0,
        total_ratings: 0,
        category: '',
        lat: 0,
        lng: 0,
      };

      // Create a custom goal that includes the exact content the user wants to send
      const customGoal = `Send an email with the following exact content:
>>>>>>> main-holder
      
TO: ${primaryRecipient}
Subject: ${emailContent.subject}

${emailContent.body}

${emailContent.cc ? `CC: ${emailContent.cc}` : ''}
${emailContent.bcc ? `BCC: ${emailContent.bcc}` : ''}

IMPORTANT: Send this email to ${primaryRecipient}. Use this exact subject and body. Do not modify or regenerate the content.`;

<<<<<<< HEAD
            // Use the existing send-email endpoint with the custom goal
            const sendRequest: EmailSendRequest = {
                lead: tempLead,
                goal: customGoal,
                max_words: 10000, // Large number to avoid truncation
            };

            console.log('📤 Sending custom email request to email agent');
            console.log('📋 Request payload:', {
                lead: {
                    name: tempLead.name,
                    emails: tempLead.emails,
                    emailCount: tempLead.emails.length
                },
                goalPreview: customGoal.substring(0, 200) + '...',
                max_words: 10000
            });

            // Make the API call to email agent
            const response = await fetch(`${EMAIL_CONFIG.EMAIL_AGENT_API_URL}/send-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify(sendRequest),
                signal: AbortSignal.timeout(60000) // 1 minute timeout
            });

            // Handle errors
            if (!response.ok) {
                const errorMessage = await ApiErrorHandler.parseError(response);
                throw new Error(errorMessage);
            }

            // Parse successful response
            const sendResponse: EmailSendResponse = await response.json();
            console.log('✅ Custom email sent via Gmail:', sendResponse);

            const endTime = Date.now();
            const duration = (endTime - startTime) / 1000;
            console.log(`🎯 Custom email sent in ${duration}s to: ${emailContent.to}`);

        } catch (error) {
            console.error('❌ Custom email send failed:', error);

            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    throw new Error('Email send timeout - The operation is taking longer than expected. Please try again.');
                } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
                    throw new Error('Cannot connect to the email agent service. Please ensure the email agent is running on port 8000');
                }
            }

            throw error;
        }
    }

    /**
     * Send email using the outreach workflow service (port 8004)
     * This drafts and sends in one operation using the outreach agent workflow
     * The email is sent via Gmail SMTP using credentials from .env.dev
     */
    static async sendEmailViaOutreach(lead: Lead, goal: string, customFields?: {
        websiteCritique?: string;
        demoUrl?: string;
    }): Promise<{ success: boolean; message?: string; emailContent?: any }> {
        console.log('📧 Sending email via outreach workflow for:', lead.name, 'with goal:', goal);

        try {
            if (!lead.emails || lead.emails.length === 0) {
                throw new Error('No email address available for this lead');
            }

            const startTime = Date.now();

            // Build the State object for the outreach workflow
            // Note: The 'goal' is embedded in the email generation prompt, not passed explicitly
            const stateRequest = {
                client_name: lead.name,
                client_email: lead.emails[0], // ALWAYS use this for demo (not shown on screen)
                client_phone_number: lead.phone_number, // ALWAYS use this for demo (not shown on screen)
                sender_name: EMAIL_CONFIG.SENDER_NAME,
                sender_title: EMAIL_CONFIG.SENDER_TITLE,
                website_critique: lead.website_review ||
                    customFields?.websiteCritique ||
                    `We noticed some areas where ${lead.name}'s website could be improved with modern design and better user experience. Our team specializes in creating high-converting, professional websites that help businesses grow. ${goal ? `Our goal: ${goal}` : ''}`,
                demo_url: customFields?.demoUrl || lead.deployed_website_url || lead.website || 'https://example.com',
                web_agency_name: EMAIL_CONFIG.WEB_AGENCY_NAME,
                web_agency_logo: EMAIL_CONFIG.WEB_AGENCY_LOGO,
            };

            console.log('📤 Sending workflow request to outreach service:', {
                client_name: stateRequest.client_name,
                client_email: stateRequest.client_email,
                sender_name: stateRequest.sender_name,
                hasWebsiteCritique: !!stateRequest.website_critique,
                demo_url: stateRequest.demo_url,
            });

            // Call the outreach workflow endpoint
            const response = await fetch(`${EMAIL_CONFIG.OUTREACH_API_URL}/workflow/create-workflow`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify(stateRequest),
                signal: AbortSignal.timeout(120000) // 2 minute timeout for workflow
            });

            if (!response.ok) {
                const errorMessage = await ApiErrorHandler.parseError(response);
                throw new Error(errorMessage);
            }

            const workflowResponse = await response.json();
            console.log('✅ Outreach workflow completed:', workflowResponse);

            const endTime = Date.now();
            const duration = (endTime - startTime) / 1000;
            console.log(`🎯 Email workflow completed in ${duration}s`);

            // Extract results from the workflow response
            const finalState = workflowResponse.final_state || {};
            const emailSent = finalState.email_sent || false;
            const emailContents = finalState.email_contents || {};

            return {
                success: emailSent,
                message: emailSent
                    ? 'Email sent successfully via outreach workflow'
                    : 'Email failed to send',
                emailContent: emailContents,
            };

        } catch (error) {
            console.error('❌ Outreach email send failed:', error);

            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    throw new Error('Email send timeout - The outreach agent is taking longer than expected. Please try again.');
                } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
                    throw new Error('Cannot connect to the outreach service. Please ensure:\n1. The outreach service is running on port 8004\n2. Docker containers are started: docker-compose -f docker-compose.dev.yml up outreach\n3. Gmail credentials are set in .env.dev (SENDER_EMAIL_ADDRESS, SENDER_EMAIL_PASSWORD)');
                }
            }

            throw error;
        }
    }
=======
      // Use the existing send-email endpoint with the custom goal
      const sendRequest: EmailSendRequest = {
        lead: tempLead,
        goal: customGoal,
        max_words: 10000, // Large number to avoid truncation
      };

      console.log('📤 Sending custom email request to email agent');
      console.log('📋 Request payload:', {
        lead: {
          name: tempLead.name,
          emails: tempLead.emails,
          emailCount: tempLead.emails.length
        },
        goalPreview: customGoal.substring(0, 200) + '...',
        max_words: 10000
      });

      // Make the API call to email agent
      const response = await fetch(`${EMAIL_CONFIG.EMAIL_AGENT_API_URL}/send-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(sendRequest),
        signal: AbortSignal.timeout(60000) // 1 minute timeout
      });

      // Handle errors
      if (!response.ok) {
        const errorMessage = await ApiErrorHandler.parseError(response);
        throw new Error(errorMessage);
      }

      // Parse successful response
      const sendResponse: EmailSendResponse = await response.json();
      console.log('✅ Custom email sent via Gmail:', sendResponse);

      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;
      console.log(`🎯 Custom email sent in ${duration}s to: ${emailContent.to}`);

    } catch (error) {
      console.error('❌ Custom email send failed:', error);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Email send timeout - The operation is taking longer than expected. Please try again.');
        } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
          throw new Error('Cannot connect to the email agent service. Please ensure the email agent is running on port 8000');
        }
      }
      
      throw error;
    }
  }
>>>>>>> main-holder
}

// Export the service as default for backward compatibility
export const leadsApi = {
<<<<<<< HEAD
    testConnection: LeadsApiService.testConnection,
    createWorkflow: LeadsApiService.searchLeads,
=======
  testConnection: LeadsApiService.testConnection,
  createWorkflow: LeadsApiService.searchLeads,
>>>>>>> main-holder
};
