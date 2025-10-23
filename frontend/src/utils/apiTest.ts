// API Testing utilities for development and debugging

import { LeadsApiService } from '../services/api';

/**
 * Test suite for API functionality
 */
export class ApiTester {
  /**
   * Run all API tests
   */
  static async runAllTests(): Promise<void> {
    console.log('🧪 Starting API Tests...');
    
    try {
      await this.testConnection();
      await this.testSearchLeads();
      console.log('✅ All API tests passed!');
    } catch (error) {
      console.error('❌ API tests failed:', error);
      throw error;
    }
  }

  /**
   * Test API connection
   */
  static async testConnection(): Promise<void> {
    console.log('🔗 Testing API connection...');
    
    const isConnected = await LeadsApiService.testConnection();
    if (!isConnected) {
      throw new Error('API connection test failed');
    }
    
    console.log('✅ API connection successful');
  }

  /**
   * Test lead search functionality
   */
  static async testSearchLeads(): Promise<void> {
    console.log('🔍 Testing lead search...');
    
    const testQueries = [
      'restaurants in Columbus',
      'coffee shops',
      'pizza places near downtown'
    ];

    for (const query of testQueries) {
      console.log(`Testing query: "${query}"`);
      
      try {
        const leads = await LeadsApiService.searchLeads(query);
        console.log(`✅ Found ${leads.length} leads for "${query}"`);
        
        // Validate lead structure
        if (leads.length > 0) {
          this.validateLeadStructure(leads[0]);
        }
      } catch (error) {
        console.error(`❌ Search failed for "${query}":`, error);
        throw error;
      }
    }
  }

  /**
   * Validate that a lead has the expected structure
   */
  static validateLeadStructure(lead: unknown): void {
    if (!lead || typeof lead !== 'object') {
      throw new Error('Lead must be an object');
    }
    
    const leadObj = lead as Record<string, unknown>;
    const requiredFields = ['id', 'name', 'address', 'place_id', 'lat', 'lng'];
    
    for (const field of requiredFields) {
      if (!(field in leadObj)) {
        throw new Error(`Lead missing required field: ${field}`);
      }
    }
    
    console.log('✅ Lead structure validation passed');
  }

  /**
   * Test error handling
   */
  static async testErrorHandling(): Promise<void> {
    console.log('🚫 Testing error handling...');
    
    try {
      // Test with empty query
      await LeadsApiService.searchLeads('');
      throw new Error('Expected error for empty query');
    } catch (error) {
      if (error instanceof Error && error.message.includes('empty')) {
        console.log('✅ Empty query error handling works');
      } else {
        throw error;
      }
    }
  }
}

/**
 * Quick test function for development
 */
export async function quickApiTest(): Promise<void> {
  try {
    console.log('🚀 Running quick API test...');
    
    const isConnected = await LeadsApiService.testConnection();
    console.log('Connection status:', isConnected ? '✅ Connected' : '❌ Disconnected');
    
    if (isConnected) {
      const leads = await LeadsApiService.searchLeads('restaurants');
      console.log(`Found ${leads.length} restaurants`);
      
      if (leads.length > 0) {
        console.log('Sample lead:', {
          name: leads[0].name,
          address: leads[0].address,
          rating: leads[0].rating,
        });
      }
    }
  } catch (error) {
    console.error('Quick test failed:', error);
  }
}

// Make test functions available globally for browser console
if (typeof window !== 'undefined') {
  (window as typeof window & { apiTest: unknown }).apiTest = {
    runAll: ApiTester.runAllTests,
    quick: quickApiTest,
    connection: ApiTester.testConnection,
    search: ApiTester.testSearchLeads,
    diagnostics: LeadsApiService.runDiagnostics,
  };
}
