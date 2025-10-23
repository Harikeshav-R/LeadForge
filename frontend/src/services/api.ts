import type { Lead, WorkflowResponse, SearchRequest } from '../types';

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

// Export the service as default for backward compatibility
export const leadsApi = {
  testConnection: LeadsApiService.testConnection,
  createWorkflow: LeadsApiService.searchLeads,
};
