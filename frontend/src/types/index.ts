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
  // Agent integration tracking fields
  deployed_website_url?: string;
  email_draft_status?: 'pending' | 'drafted' | 'sent';
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

// Builder Agent Types
export interface BuilderRequest {
  initial_website_url: string;
  initial_website_scrape_limit?: number;
  prompt?: string;
  pages_scraped?: any[];
  pages_screenshots?: any[];
  final_website_zip?: string;
}

export interface BuilderState {
  id: string;
  initial_website_url: string;
  initial_website_scrape_limit: number;
  prompt?: string;
  pages_scraped: any[];
  pages_screenshots: any[];
  final_website_zip?: string;
}

export interface BuilderWorkflowResponse {
  id: string;
  initial_state: BuilderState;
  final_state: BuilderState;
}

// Deployer Agent Types
export interface DeployerRequest {
  name: string;
  zip_base64: string;
}

export interface DeployerResponse {
  id: string;
  name: string;
  url: string;
}

// Email Agent Types (matching email_agent.py schema)
export interface EmailDraftRequest {
  lead: Lead;
  goal: string;
  max_words: number;
}

export interface EmailDraftResponse {
  success: boolean;
  lead_name: string;
  contact_email: string;
  draft: string; // Full email text content
}

export interface EmailSendRequest {
  lead: Lead;
  goal: string;
  max_words: number;
}

export interface EmailSendResponse {
  success: boolean;
  lead_name: string;
  contact_email: string;
  draft: string;
  sent: boolean;
}

// Email content structure for customization
export interface EmailContent {
  to: string;
  subject: string;
  body: string;
  cc?: string;
  bcc?: string;
}

// Lead action state for UI management
export interface LeadActionState {
  emailDraft: {
    loading: boolean;
    success: boolean;
    error: string | null;
    showPreview: boolean;
    draftContent: EmailContent;
    originalContent?: EmailContent; // Store original AI-generated content
    sending: boolean;
    sent: boolean;
  };
  websiteBuild: {
    loading: boolean;
    success: boolean;
    error: string | null;
    deployedUrl?: string;
  };
}

// Combined Build and Deploy Response
export interface BuildAndDeployResponse {
  websiteZip: string;
  deployedUrl: string;
  websiteId: string;
}
