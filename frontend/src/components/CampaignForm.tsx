import { useState } from 'react';
import type { FormEvent } from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { Play, Loader2, Bug } from 'lucide-react';
import { LeadsApiService } from '../services/api';
import { FakeDataService } from '../services/fakeData';
import type { Lead } from '../types';

interface CampaignFormProps {
  onStart: (searchQuery: string, leads: Lead[]) => void;
}

export function CampaignForm({ onStart }: CampaignFormProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debugMode, setDebugMode] = useState(false);
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      let leads: Lead[];
      
      if (debugMode) {
        // Use fake data for UI development
        leads = FakeDataService.getFakeLeadsForQuery(searchQuery);
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
      } else {
        // Use real API
        await LeadsApiService.ensureConnection();
        leads = await LeadsApiService.searchLeads(searchQuery);
      }
      
      // Notify parent component of successful search
      onStart(searchQuery, leads);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to search for leads';
      setError(errorMessage);
      console.error('Campaign search failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQueryChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setSearchQuery(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  return (
    <Card className="max-w-3xl w-full">
      {/* Header Section */}
      <div className="text-center mb-10">
        <h2 className="text-3xl font-semibold text-gray-900 mb-3">
          Start a New Sales Campaign
        </h2>
        <p className="text-lg text-gray-600">
          Enter the location and business type to discover qualified leads
        </p>
      </div>

      {/* Debug Mode Toggle */}
      <div className="flex items-center justify-center mb-6">
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={debugMode}
            onChange={(e) => setDebugMode(e.target.checked)}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
          />
          <Bug className="w-5 h-5 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">
            Debug Mode (Use Fake Data)
          </span>
        </label>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Search Input */}
        <textarea
          placeholder="e.g. Matcha Places in San Francisco..."
          value={searchQuery}
          onChange={handleQueryChange}
          required
          disabled={isLoading}
          className="text-base w-full p-3 border border-gray-300 rounded-lg resize-none disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
        />

        {/* Error Message */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <Button 
          type="submit" 
          size="lg"
          disabled={isLoading || !searchQuery.trim()}
          className="w-full"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Searching for leads...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Start Search
            </>
          )}
        </Button>

        {/* Loading Progress Indicator */}
        {isLoading && (
          <div className="mt-4 text-center space-y-3">
            <div className="inline-flex items-center gap-2 text-sm text-gray-600">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <span className="ml-2">
                {debugMode ? 'Loading fake data for UI testing...' : 'AI agents are working on your search...'}
              </span>
            </div>
            
            {!debugMode && (
              <div className="text-xs text-gray-500 max-w-md mx-auto">
                <p className="mb-2">This may take 1-2 minutes as our agents:</p>
                <div className="space-y-1 text-left">
                  <div className="flex items-center gap-2">
                    <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                    <span>Search for businesses in your area</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                    <span>Find contact information and emails</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                    <span>Analyze websites and social media</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                    <span>Generate business insights</span>
                  </div>
                </div>
              </div>
            )}
            
            {debugMode && (
              <div className="text-xs text-gray-600 max-w-md mx-auto">
                <p className="mb-2">Debug mode active - using fake data for UI development</p>
              </div>
            )}
          </div>
        )}
      </form>
    </Card>
  );
}