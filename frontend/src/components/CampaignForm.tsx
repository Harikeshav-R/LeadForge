<<<<<<< HEAD
// UI Refactor: Updated to use shadcn/ui components (Input, Label, Switch, Card, Button)
// Maintains all existing functionality while improving UI consistency
=======
>>>>>>> main-holder
import { useState } from 'react';
import type { FormEvent } from 'react';
import { Card } from './Card';
import { Button } from './Button';
<<<<<<< HEAD
import { Label } from './ui/label';
import { Play, Loader2 } from 'lucide-react';
import { LeadsApiService } from '../services/api';
=======
import { Play, Loader2, Bug } from 'lucide-react';
import { LeadsApiService } from '../services/api';
import { FakeDataService } from '../services/fakeData';
>>>>>>> main-holder
import type { Lead } from '../types';

interface CampaignFormProps {
  onStart: (searchQuery: string, leads: Lead[]) => void;
}

export function CampaignForm({ onStart }: CampaignFormProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
<<<<<<< HEAD
  
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
=======
  const [debugMode, setDebugMode] = useState(false);
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

>>>>>>> main-holder
    setIsLoading(true);
    setError(null);
    
    try {
<<<<<<< HEAD
      // Always use the hardcoded query for demo
      const demoQuery = 'Cookie companies near Columbus, OH';
      
      // Always use real API for demo
      await LeadsApiService.ensureConnection();
      const leads = await LeadsApiService.searchLeads(demoQuery);
      
      // Notify parent component of successful search
      onStart(demoQuery, leads);
=======
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
>>>>>>> main-holder
      
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
<<<<<<< HEAD
    <Card className="max-w-3xl w-full p-8 glass">
      {/* Header Section */}
      <div className="text-center mb-12">
        <h2 className="text-3xl font-semibold text-foreground mb-4">
          Start a New Sales Campaign
        </h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
=======
    <Card className="max-w-3xl w-full">
      {/* Header Section */}
      <div className="text-center mb-10">
        <h2 className="text-3xl font-semibold text-gray-900 mb-3">
          Start a New Sales Campaign
        </h2>
        <p className="text-lg text-gray-600">
>>>>>>> main-holder
          Enter the location and business type to discover qualified leads
        </p>
      </div>

<<<<<<< HEAD
      {/* Search Form */}
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Search Input */}
        <div className="space-y-3">
          <Label htmlFor="search-query" className="text-sm font-medium">
            Search Query
          </Label>
          <textarea
            id="search-query"
            placeholder="Matcha places near Columbus, OH"
            value={searchQuery}
            onChange={handleQueryChange}
            required
            disabled={isLoading}
            className="text-base w-full p-4 border border-input rounded-md resize-none disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-ring focus:border-transparent bg-background min-h-[120px]"
            rows={3}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
=======
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
>>>>>>> main-holder
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <Button 
          type="submit" 
          size="lg"
          disabled={isLoading || !searchQuery.trim()}
<<<<<<< HEAD
          className="w-full h-12"
=======
          className="w-full"
>>>>>>> main-holder
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
<<<<<<< HEAD
          <div className="mt-6 text-center space-y-4 p-6 bg-muted/30 rounded-lg">
            {/* Added background and padding for better visual separation */}
            <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <span className="ml-2">
                AI agents are working on your search...
              </span>
            </div>
            
            <div className="text-xs text-muted-foreground max-w-md mx-auto">
              <p className="mb-3">This may take 1-2 minutes as our agents:</p>
              <div className="space-y-2 text-left">
                <div className="flex items-center gap-3">
                  <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full"></div>
                  <span>Search for businesses in your area</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full"></div>
                  <span>Find contact information and emails</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full"></div>
                  <span>Analyze websites and social media</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full"></div>
                  <span>Generate business insights</span>
                </div>
              </div>
            </div>
=======
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
>>>>>>> main-holder
          </div>
        )}
      </form>
    </Card>
  );
}