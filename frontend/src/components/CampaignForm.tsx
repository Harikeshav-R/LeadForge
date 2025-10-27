// UI Refactor: Updated to use shadcn/ui components (Input, Label, Switch, Card, Button)
import type {FormEvent} from 'react';
// Maintains all existing functionality while improving UI consistency
import {useState} from 'react';
import {Card} from './Card';
import {Button} from './Button';
import {Label} from './ui/label';
import {Loader2, Play} from 'lucide-react';
import {LeadsApiService} from '../services/api';
import type {Lead} from '../types';

interface CampaignFormProps {
    onStart: (searchQuery: string, leads: Lead[]) => void;
}

export function CampaignForm({onStart}: CampaignFormProps) {
    const [searchQuery, setSearchQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        setIsLoading(true);
        setError(null);

        try {
            // Always use the hardcoded query for demo
            const demoQuery = 'Cookie companies near Columbus, OH';

            // Always use real API for demo
            await LeadsApiService.ensureConnection();
            const leads = await LeadsApiService.searchLeads(demoQuery);

            // Notify parent component of successful search
            onStart(demoQuery, leads);

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
        <Card className="max-w-3xl w-full p-8 glass">
            {/* Header Section */}
            <div className="text-center mb-12">
                <h2 className="text-3xl font-semibold text-foreground mb-4">
                    Start a New Sales Campaign
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                    Enter the location and business type to discover qualified leads
                </p>
            </div>

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

                        <p className="text-sm text-red-600">{error}</p>
                    </div>
                )}

                {/* Submit Button */}
                <Button
                    type="submit"
                    size="lg"
                    disabled={isLoading || !searchQuery.trim()}
                    className="w-full h-12"
                >
                    {isLoading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin"/>
                            Searching for leads...
                        </>
                    ) : (
                        <>
                            <Play className="w-5 h-5"/>
                            Start Search
                        </>
                    )}
                </Button>

                {/* Loading Progress Indicator */}
                {isLoading && (
                    <div className="mt-6 text-center space-y-4 p-6 bg-muted/30 rounded-lg">
                        {/* Added background and padding for better visual separation */}
                        <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
                            <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-primary rounded-full animate-bounce"
                                 style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-primary rounded-full animate-bounce"
                                 style={{animationDelay: '0.2s'}}></div>
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
                    </div>
                )}
            </form>
        </Card>
    );
}