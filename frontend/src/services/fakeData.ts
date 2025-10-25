import type { Lead } from '../types';

export class FakeDataService {
  private static readonly FAKE_LEADS: Lead[] = [
    {
      id: 'fake-1',
      place_id: 'ChIJN1t_tDeuEmsRUsoyG83frY4',
      name: 'Bella Vista Restaurant',
      address: '123 Main Street, Columbus, OH 43215',
      phone_number: '+1 (614) 555-0123',
      website: 'https://bellavista-restaurant.com',
      rating: 4.5,
      total_ratings: 127,
      category: 'Italian Restaurant',
      price_level: 2,
      is_open: true,
      lat: 39.9612,
      lng: -82.9988,
      emails: ['contact@bellavista-restaurant.com', 'reservations@bellavista-restaurant.com'],
      phone_numbers: ['+1 (614) 555-0123', '+1 (614) 555-0124'],
      social_media: ['https://facebook.com/bellavista', 'https://instagram.com/bellavista'],
      screenshots: [
        {
          device: 'desktop',
          image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzM3NDE1MSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkJlbGxhIFZpc3RhIFJlc3RhdXJhbnQ8L3RleHQ+PC9zdmc+'
        }
      ],
      website_review: 'Beautiful Italian restaurant with authentic cuisine and excellent service.',
      state_id: 'fake-state-1'
    },
    {
      id: 'fake-2',
      place_id: 'ChIJN1t_tDeuEmsRUsoyG83frY5',
      name: 'Tech Solutions Inc',
      address: '456 Business Ave, Columbus, OH 43215',
      phone_number: '+1 (614) 555-0234',
      website: 'https://techsolutions-columbus.com',
      rating: 4.2,
      total_ratings: 89,
      category: 'IT Services',
      price_level: 3,
      is_open: true,
      lat: 39.9612,
      lng: -82.9988,
      emails: ['info@techsolutions-columbus.com', 'support@techsolutions-columbus.com'],
      phone_numbers: ['+1 (614) 555-0234'],
      social_media: ['https://linkedin.com/company/techsolutions'],
      screenshots: [
        {
          device: 'desktop',
          image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzM3NDE1MSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPlRlY2ggU29sdXRpb25zIEluYzwvdGV4dD48L3N2Zz4='
        }
      ],
      website_review: 'Professional IT services company specializing in business technology solutions.',
      state_id: 'fake-state-2'
    },
    {
      id: 'fake-3',
      place_id: 'ChIJN1t_tDeuEmsRUsoyG83frY6',
      name: 'Green Thumb Garden Center',
      address: '789 Plant Street, Columbus, OH 43215',
      phone_number: '+1 (614) 555-0345',
      website: 'https://greenthumb-garden.com',
      rating: 4.7,
      total_ratings: 203,
      category: 'Garden Center',
      price_level: 2,
      is_open: true,
      lat: 39.9612,
      lng: -82.9988,
      emails: ['plants@greenthumb-garden.com'],
      phone_numbers: ['+1 (614) 555-0345'],
      social_media: ['https://facebook.com/greenthumbgarden', 'https://instagram.com/greenthumbgarden'],
      screenshots: [
        {
          device: 'desktop',
          image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzM3NDE1MSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkdyZWVuIFRodW1iIEdhcmRlbjwvdGV4dD48L3N2Zz4='
        }
      ],
      website_review: 'Local garden center with expert advice and high-quality plants.',
      state_id: 'fake-state-3'
    },
    {
      id: 'fake-4',
      place_id: 'ChIJN1t_tDeuEmsRUsoyG83frY7',
      name: 'Downtown Coffee Co',
      address: '321 Coffee Lane, Columbus, OH 43215',
      phone_number: '+1 (614) 555-0456',
      website: 'https://downtowncoffee-oh.com',
      rating: 4.3,
      total_ratings: 156,
      category: 'Coffee Shop',
      price_level: 1,
      is_open: true,
      lat: 39.9612,
      lng: -82.9988,
      emails: ['hello@downtowncoffee-oh.com'],
      phone_numbers: ['+1 (614) 555-0456'],
      social_media: ['https://instagram.com/downtowncoffeeoh'],
      screenshots: [
        {
          device: 'desktop',
          image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzM3NDE1MSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRvd250b3duIENvZmZlZTwvdGV4dD48L3N2Zz4='
        }
      ],
      website_review: 'Cozy coffee shop with locally roasted beans and friendly atmosphere.',
      state_id: 'fake-state-4'
    },
    {
      id: 'fake-5',
      place_id: 'ChIJN1t_tDeuEmsRUsoyG83frY8',
      name: 'Elite Fitness Studio',
      address: '654 Workout Way, Columbus, OH 43215',
      phone_number: '+1 (614) 555-0567',
      website: 'https://elitefitness-columbus.com',
      rating: 4.6,
      total_ratings: 92,
      category: 'Fitness Center',
      price_level: 3,
      is_open: true,
      lat: 39.9612,
      lng: -82.9988,
      emails: ['membership@elitefitness-columbus.com', 'info@elitefitness-columbus.com'],
      phone_numbers: ['+1 (614) 555-0567'],
      social_media: ['https://facebook.com/elitefitnesscolumbus'],
      screenshots: [
        {
          device: 'desktop',
          image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzM3NDE1MSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkVsaXRlIEZpdG5lc3M8L3RleHQ+PC9zdmc+'
        }
      ],
      website_review: 'Premium fitness studio with personal trainers and state-of-the-art equipment.',
      state_id: 'fake-state-5'
    }
  ];

  /**
   * Get fake leads for testing
   */
  static getFakeLeads(): Lead[] {
    return [...this.FAKE_LEADS];
  }

  /**
   * Get fake leads based on search query (simulates filtering)
   */
  static getFakeLeadsForQuery(query: string): Lead[] {
    const lowerQuery = query.toLowerCase();
    
    // Filter leads based on query keywords
    const filteredLeads = this.FAKE_LEADS.filter(lead => {
      const searchableText = [
        lead.name,
        lead.category,
        lead.address,
        lead.website_review
      ].join(' ').toLowerCase();
      
      return searchableText.includes(lowerQuery) || 
             lowerQuery.includes('restaurant') ||
             lowerQuery.includes('business') ||
             lowerQuery.includes('columbus') ||
             lowerQuery.includes('ohio');
    });

    // Return filtered results or all leads if no specific match
    return filteredLeads.length > 0 ? filteredLeads : this.FAKE_LEADS;
  }

  /**
   * Get a single fake lead by ID
   */
  static getFakeLeadById(id: string): Lead | undefined {
    return this.FAKE_LEADS.find(lead => lead.id === id);
  }
}
