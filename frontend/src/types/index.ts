// Shared type definitions for the Lead Generation application

export interface Lead {
  place_id: string;
  name: string;
  address: string;
  phone_number?: string;
  website?: string;
  rating?: number;
  total_ratings?: number;
  category?: string;
  price_level?: number;
  is_open?: boolean;
  lat: number;
  lng: number;
  emails: string[];
  phone_numbers: string[];
  social_media: string[];
  screenshots: Screenshot[];
  website_review?: string;
  id: string;
  state_id: string;
}

export interface Screenshot {
  device: string;
  image: string;
}

export interface SearchState {
  id: string;
  city: string;
  business_type: string;
  radius: number;
  min_rating: number;
  max_results: number;
  messages: string[];
  leads: Lead[];
}

export interface WorkflowResponse {
  id: string;
  initial_state: SearchState;
  final_state: SearchState;
}

export interface SearchRequest {
  city: string;
  business_type: string;
  radius?: number;
  min_rating?: number;
  max_results?: number;
  messages?: string[];
  leads?: Lead[];
}

export interface PipelineStage {
  id: string;
  name: string;
  status: 'pending' | 'active' | 'completed';
  icon: 'search' | 'mail' | 'phone' | 'check';
  description: string;
}

export interface CampaignData {
  searchQuery: string;
  leads: Lead[];
  isActive: boolean;
}

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}
