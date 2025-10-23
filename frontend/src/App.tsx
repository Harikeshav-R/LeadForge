import { useState, useEffect } from 'react';
import { Navigation } from './components/Navigation';
import { CampaignForm } from './components/CampaignForm';
import { LeadsTable } from './components/LeadsTable';
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
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
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
            <CampaignForm onStart={handleStartCampaign} />
          </div>
        </section>

        {/* Dashboard Section - Always visible */}
        <section id="dashboard-section" className="bg-white border-t border-gray-200 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
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
                  </p>
                </div>

                {/* Leads Table */}
                <div>
                  <LeadsTable leads={campaignData.leads} />
                </div>

                {/* Action Buttons */}
                <div className="flex justify-center gap-4 pt-8">
                  <button
                    onClick={() => {
                      setCampaignData({ searchQuery: '', leads: [], isActive: false });
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 flex items-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    New Search
                  </button>
                  <button
                    onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                    </svg>
                    Back to Top
                  </button>
                </div>
              </div>
            ) : (
              /* Empty Dashboard - Always visible */
              <div className="space-y-12">
                {/* Dashboard Header */}
                <div className="text-center">
                  <h2 className="text-3xl font-semibold text-gray-900 mb-3">
                    Dashboard
                  </h2>
                  <p className="text-lg text-gray-600">
                    Your search results will appear here
                  </p>
                </div>


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
                    </div>
                  </div>
                </div>

                {/* Additional Preview Sections for More Scrollable Content */}
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
                    </div>
                  </div>
                </div>

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
                    </div>
                  </div>
                </div>

                {/* Call to Action */}
                <div className="text-center pt-8 pb-16">
                  <button
                    onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                    className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2 mx-auto"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                    </svg>
                    Back to Search
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Scroll Hint - Shows when search is active but user is at top */}
        {campaignData.isActive && !isScrolledDown && (
          <section className="text-center py-16">
            <div className="max-w-2xl mx-auto">
              <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Search Complete!
              </h3>
              <p className="text-gray-600 mb-6">
                Found {campaignData.leads.length} businesses for "{campaignData.searchQuery}". Scroll down to view the results.
              </p>
              
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-center gap-2 text-blue-700">
                  <svg className="w-5 h-5 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                  <span className="text-sm font-medium">Scroll down to view your search results</span>
                </div>
            </div>
          </div>
          </section>
        )}

      </main>
    </div>
  );
}

export default App;
