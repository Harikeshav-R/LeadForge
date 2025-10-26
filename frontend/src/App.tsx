<<<<<<< HEAD
// UI Refactor: Updated to use shadcn/ui components and improved styling
// Maintains all existing functionality while using consistent design system
=======
>>>>>>> main-holder
import { useState, useEffect } from 'react';
import { Navigation } from './components/Navigation';
import { CampaignForm } from './components/CampaignForm';
import { LeadsTable } from './components/LeadsTable';
<<<<<<< HEAD
import { Button } from './components/Button';
import { Badge } from './components/ui/badge';
=======
>>>>>>> main-holder
import type { Lead, CampaignData } from './types';

function App() {
  const [campaignData, setCampaignData] = useState<CampaignData>({
    searchQuery: '',
    leads: [],
    isActive: false,
  });

  const [isScrolledDown, setIsScrolledDown] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const searchSectionHeight = windowHeight * 0.6;
      
      setIsScrolledDown(scrollTop > searchSectionHeight);
    };

    let ticking = false;
    const throttledHandleScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', throttledHandleScroll, { passive: true });
    return () => window.removeEventListener('scroll', throttledHandleScroll);
  }, []);

  const handleStartCampaign = (searchQuery: string, leads: Lead[]) => {
    setCampaignData({
      searchQuery,
      leads,
      isActive: true,
    });

    setTimeout(() => {
      const dashboardElement = document.getElementById('dashboard-section');
      if (dashboardElement) {
        dashboardElement.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }
    }, 300);
  };

  return (
<<<<<<< HEAD
    <div className="min-h-screen">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        {/* Search Section - Always Visible */}
        <section className="mb-24 min-h-screen flex flex-col justify-center">
          <div className="text-center mb-16 px-4">
            <h1 className="text-4xl font-bold text-foreground mb-4 tracking-tight">
              Lead Generation Pipeline
            </h1>
            <p className="text-base text-muted-foreground max-w-2xl mx-auto leading-6">
              Find and analyze potential business leads with AI-powered insights
            </p>
          </div>

          <div className="flex justify-center px-4">
=======
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-0">
        {/* Search Section - Always Visible */}
        <section className="mb-20 min-h-screen flex flex-col justify-center">
          <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Lead Generation Pipeline
          </h1>
            <p className="text-lg text-gray-600">
              Find and analyze potential business leads with AI-powered insights
            </p>
        </div>

          <div className="flex justify-center">
>>>>>>> main-holder
            <CampaignForm onStart={handleStartCampaign} />
          </div>
        </section>

        {/* Dashboard Section - Always visible */}
<<<<<<< HEAD
        <section id="dashboard-section" className="bg-card border-t border-border rounded-xl">
          <div className="py-16">
            {/* Added more generous padding for better breathing room */}
            {campaignData.isActive ? (
              /* Dashboard with Results */
              <div className="space-y-16 fade-in-up">
                {/* Results Header */}
                <div className="text-center px-4">
                  <h2 className="text-3xl font-semibold text-foreground mb-4 tracking-tight">
                    Search Results
                  </h2>
                  <p className="text-sm text-muted-foreground max-w-3xl mx-auto leading-6">
                    Found <Badge variant="secondary" className="mx-1">{campaignData.leads.length}</Badge> businesses for: "{campaignData.searchQuery}"
=======
        <section id="dashboard-section" className="bg-white border-t border-gray-200 shadow-lg">
          <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-12">
            {campaignData.isActive ? (
              /* Dashboard with Results */
              <div className="space-y-12 fade-in-up">
                {/* Results Header */}
                <div className="text-center">
                  <h2 className="text-3xl font-semibold text-gray-900 mb-3">
                    Search Results
                  </h2>
                  <p className="text-lg text-gray-600">
                    Found {campaignData.leads.length} businesses for: "{campaignData.searchQuery}"
>>>>>>> main-holder
                  </p>
                </div>

                {/* Leads Table */}
<<<<<<< HEAD
                <div className="px-4">
=======
                <div>
>>>>>>> main-holder
                  <LeadsTable leads={campaignData.leads} />
                </div>

                {/* Action Buttons */}
<<<<<<< HEAD
                <div className="flex justify-center gap-6 pt-12 px-4">
                  <Button
=======
                <div className="flex justify-center gap-4 pt-8">
                  <button
>>>>>>> main-holder
                    onClick={() => {
                      setCampaignData({ searchQuery: '', leads: [], isActive: false });
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
<<<<<<< HEAD
                    variant="primary"
                    size="lg"
                    className="bg-green-600 hover:bg-green-700 text-white"
=======
                    className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 flex items-center gap-2"
>>>>>>> main-holder
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    New Search
<<<<<<< HEAD
                  </Button>
                  <Button
                    onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                    variant="secondary"
                    size="lg"
=======
                  </button>
                  <button
                    onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2"
>>>>>>> main-holder
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                    </svg>
                    Back to Top
<<<<<<< HEAD
                  </Button>
=======
                  </button>
>>>>>>> main-holder
                </div>
              </div>
            ) : (
              /* Empty Dashboard - Always visible */
<<<<<<< HEAD
              <div className="space-y-16">
                {/* Dashboard Header */}
                <div className="text-center px-4">
                  <h2 className="text-3xl font-semibold text-foreground mb-4 tracking-tight">
                    Dashboard
                  </h2>
                  <p className="text-sm text-muted-foreground max-w-2xl mx-auto leading-6">
=======
              <div className="space-y-12">
                {/* Dashboard Header */}
                <div className="text-center">
                  <h2 className="text-3xl font-semibold text-gray-900 mb-3">
                    Dashboard
                  </h2>
                  <p className="text-lg text-gray-600">
>>>>>>> main-holder
                    Your search results will appear here
                  </p>
                </div>

<<<<<<< HEAD
                {/* Results Preview */}
                <div className="px-4">
                  <h3 className="text-2xl font-semibold text-foreground mb-8 tracking-tight">
                    Business Results
                  </h3>
                  <div className="bg-muted/50 rounded-xl p-12 border border-dashed border-border">
                    {/* Added more padding inside preview cards for better visual balance */}
                    <div className="text-center">
                      <svg className="w-16 h-16 text-muted-foreground mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      <h4 className="text-lg font-semibold text-foreground mb-3">Business Leads</h4>
                      <p className="text-muted-foreground max-w-md mx-auto">Detailed business information with contact details will appear here</p>
=======

                {/* Results Preview */}
                <div>
                  <h3 className="text-2xl font-semibold text-gray-900 mb-6">
                    Business Results
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-8 border-2 border-dashed border-gray-300">
                    <div className="text-center">
                      <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      <h4 className="text-lg font-semibold text-gray-700 mb-2">Business Leads</h4>
                      <p className="text-gray-500">Detailed business information with contact details will appear here</p>
>>>>>>> main-holder
                    </div>
                  </div>
                </div>

                {/* Additional Preview Sections for More Scrollable Content */}
<<<<<<< HEAD
                <div className="px-4">
                  <h3 className="text-2xl font-semibold text-foreground mb-8 tracking-tight">
                    Contact Information
                  </h3>
                  <div className="bg-muted/50 rounded-xl p-12 border border-dashed border-border">
                    {/* Consistent spacing and design tokens throughout */}
                    <div className="text-center">
                      <svg className="w-16 h-16 text-muted-foreground mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <h4 className="text-lg font-semibold text-foreground mb-3">Contact Details</h4>
                      <p className="text-muted-foreground max-w-md mx-auto">Email addresses, phone numbers, and social media links</p>
=======
                <div>
                  <h3 className="text-2xl font-semibold text-gray-900 mb-6">
                    Contact Information
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-8 border-2 border-dashed border-gray-300">
                    <div className="text-center">
                      <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <h4 className="text-lg font-semibold text-gray-700 mb-2">Contact Details</h4>
                      <p className="text-gray-500">Email addresses, phone numbers, and social media links</p>
>>>>>>> main-holder
                    </div>
                  </div>
                </div>

<<<<<<< HEAD
                <div className="px-4">
                  <h3 className="text-2xl font-semibold text-foreground mb-8 tracking-tight">
                    Business Insights
                  </h3>
                  <div className="bg-muted/50 rounded-xl p-12 border border-dashed border-border">
                    <div className="text-center">
                      <svg className="w-16 h-16 text-muted-foreground mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      <h4 className="text-lg font-semibold text-foreground mb-3">AI Analysis</h4>
                      <p className="text-muted-foreground max-w-md mx-auto">Website reviews, business ratings, and market insights</p>
=======
                <div>
                  <h3 className="text-2xl font-semibold text-gray-900 mb-6">
                    Business Insights
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-8 border-2 border-dashed border-gray-300">
                    <div className="text-center">
                      <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      <h4 className="text-lg font-semibold text-gray-700 mb-2">AI Analysis</h4>
                      <p className="text-gray-500">Website reviews, business ratings, and market insights</p>
>>>>>>> main-holder
                    </div>
                  </div>
                </div>

                {/* Call to Action */}
<<<<<<< HEAD
                <div className="text-center pt-12 pb-20 px-4">
                  <Button
                    onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                    variant="primary"
                    size="lg"
                    className="flex items-center gap-2 mx-auto"
=======
                <div className="text-center pt-8 pb-16">
                  <button
                    onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                    className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2 mx-auto"
>>>>>>> main-holder
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                    </svg>
                    Back to Search
<<<<<<< HEAD
                  </Button>
=======
                  </button>
>>>>>>> main-holder
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Scroll Hint - Shows when search is active but user is at top */}
        {campaignData.isActive && !isScrolledDown && (
<<<<<<< HEAD
          <section className="text-center py-20 px-4">
            {/* Added more generous padding and spacing for scroll hint */}
            <div className="max-w-2xl mx-auto">
              <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-8">
=======
          <section className="text-center py-16">
            <div className="max-w-2xl mx-auto">
              <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
>>>>>>> main-holder
                <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
<<<<<<< HEAD
              <h3 className="text-xl font-semibold text-foreground mb-4">
                Search Complete!
              </h3>
              <p className="text-muted-foreground mb-8 max-w-lg mx-auto">
                Found {campaignData.leads.length} businesses for "{campaignData.searchQuery}". Scroll down to view the results.
              </p>
              
              <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg max-w-md mx-auto">
=======
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Search Complete!
              </h3>
              <p className="text-gray-600 mb-6">
                Found {campaignData.leads.length} businesses for "{campaignData.searchQuery}". Scroll down to view the results.
              </p>
              
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
>>>>>>> main-holder
                <div className="flex items-center justify-center gap-2 text-blue-700">
                  <svg className="w-5 h-5 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                  <span className="text-sm font-medium">Scroll down to view your search results</span>
                </div>
<<<<<<< HEAD
              </div>
            </div>
=======
            </div>
          </div>
>>>>>>> main-holder
          </section>
        )}

      </main>
    </div>
  );
}

export default App;
