import { useState } from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { ExternalLink, Mail, Phone, Building2, Globe, Loader2, CheckCircle, RefreshCw, X, Send, Eye, AlertCircle } from 'lucide-react';
import { BuilderApiService, EmailApiService } from '../services/api';
import type { Lead, EmailContent } from '../types';
import { EMAIL_CONFIG } from '../config/email';

// Normalize email agent response to structured format
const normalizeEmailResponse = (rawResponse: any, fallbackEmail: string): EmailContent => {
  console.log('🔍 Normalizing email agent response...');
  console.log('Raw response:', rawResponse);
  
  // Helper to safely extract string from potentially nested object
  const extractString = (value: any, keys: string[]): string => {
    if (typeof value === 'string') return value;
    if (!value) return '';
    if (typeof value === 'object' && !Array.isArray(value)) {
      // Try to extract from nested keys
      for (const key of keys) {
        if (value[key] && typeof value[key] === 'string') {
          return value[key];
        }
      }
      // If no nested key works, stringify the object
      return JSON.stringify(value);
    }
    return String(value);
  };
  
  // Helper to extract email addresses from various formats
  const extractEmails = (value: any): string => {
    if (!value) return '';
    if (typeof value === 'string') return value;
    if (Array.isArray(value)) {
      // Guard against empty arrays
      if (value.length === 0) return '';
      return value.map(item => {
        if (typeof item === 'string') return item;
        if (typeof item === 'object' && item && item.email) return item.email;
        if (typeof item === 'object' && item && item.address) return item.address;
        return String(item);
      }).filter(Boolean).join(', ');
    }
    if (typeof value === 'object' && value && value.email) return value.email;
    if (typeof value === 'object' && value && value.address) return value.address;
    return String(value);
  };
  
  // Helper to concatenate text blocks from array response
  const extractTextFromBlocks = (blocks: any[]): string => {
    if (!Array.isArray(blocks) || blocks.length === 0) return '';
    
    return blocks
      .filter(block => block && typeof block === 'object')
      .map(block => {
        // Extract text field, ignore extras
        if (block.type === 'text' && block.text) {
          return typeof block.text === 'string' ? block.text : String(block.text);
        }
        if (block.text) {
          return typeof block.text === 'string' ? block.text : String(block.text);
        }
        if (block.content) {
          return typeof block.content === 'string' ? block.content : String(block.content);
        }
        return '';
      })
      .filter(Boolean)
      .join('\n\n');
  };
  
  // Determine if response is array-based or object-based
  let rawText = '';
  
  if (Array.isArray(rawResponse)) {
    // Array response: concatenate all text blocks
    console.log('📦 Array-based response detected, extracting text blocks...');
    rawText = extractTextFromBlocks(rawResponse);
  } else if (Array.isArray(rawResponse.draft)) {
    // Nested array in draft field
    console.log('📦 Array in draft field detected, extracting text blocks...');
    rawText = extractTextFromBlocks(rawResponse.draft);
  } else if (Array.isArray(rawResponse.blocks)) {
    // Array in blocks field
    console.log('📦 Array in blocks field detected, extracting text blocks...');
    rawText = extractTextFromBlocks(rawResponse.blocks);
  } else {
    // Standard object response
    rawText = rawResponse.draft || rawResponse.message || rawResponse.content || 
              rawResponse.text || rawResponse.body || '';
    
    if (typeof rawText !== 'string') {
      rawText = extractString(rawText, ['text', 'content', 'value', 'message', 'html']);
    }
  }
  
  console.log('📝 Extracted raw text (first 200 chars):', rawText.substring(0, 200));
  
  // Extract SUBJECT from rawText or explicit field
  let subject = '';
  
  // First try explicit subject field
  if (rawResponse.subject && !Array.isArray(rawResponse)) {
    subject = extractString(rawResponse.subject, ['text', 'content', 'value']);
  }
  
  // If no explicit subject or it's invalid, parse from rawText
  if (!subject || subject === '{}' || subject === '[object Object]' || subject.trim() === '') {
    const subjectMatch = rawText.match(/Subject:\s*(.+?)(?:\n|$)/i);
    if (subjectMatch && subjectMatch[1]) {
      subject = subjectMatch[1].trim();
      // Normalize quotes and dashes
      subject = subject
        .replace(/[""]/g, '"')
        .replace(/['']/g, "'")
        .replace(/–/g, '-')
        .replace(/—/g, '-');
    } else {
      subject = 'AI-Generated Email';
    }
  }
  
  // Extract BODY from rawText
  let body = rawText;
  
  // Remove "Subject:" line if present
  if (body.includes('Subject:')) {
    const subjectLineMatch = body.match(/Subject:\s*.+?(\n|$)/i);
    if (subjectLineMatch) {
      const subjectLineEnd = body.indexOf(subjectLineMatch[0]) + subjectLineMatch[0].length;
      body = body.substring(subjectLineEnd).trim();
    }
  }
  
  // Remove any extras.signature or metadata blocks
  // Look for common signature separators
  const signatureSeparators = [
    /\n\s*---+\s*\n/,
    /\n\s*___+\s*\n/,
    /\n\s*\*\*\*+\s*\n/,
    /extras\.signature/i,
    /"signature":/i
  ];
  
  for (const separator of signatureSeparators) {
    const match = body.match(separator);
    if (match && match.index !== undefined) {
      body = body.substring(0, match.index).trim();
      break;
    }
  }
  
  // Normalize whitespace while preserving paragraph breaks
  body = body
    .replace(/\r\n/g, '\n') // Normalize CRLF to LF
    .replace(/\r/g, '\n')   // Normalize CR to LF
    .replace(/\n{3,}/g, '\n\n'); // Max 2 consecutive newlines (preserve paragraph spacing)
  
  // Only trim leading/trailing whitespace from the entire body, not internal spacing
  body = body.trim();
  
  // Extract TO field (support: to, receiver, receivers, contact_email)
  let to = fallbackEmail;
  if (!Array.isArray(rawResponse)) {
    if (rawResponse.to) {
      to = extractEmails(rawResponse.to);
    } else if (rawResponse.receiver) {
      to = extractEmails(rawResponse.receiver);
    } else if (rawResponse.receivers) {
      to = extractEmails(rawResponse.receivers);
    } else if (rawResponse.contact_email) {
      to = extractEmails(rawResponse.contact_email);
    }
  }
  
  // Extract CC and BCC
  const cc = !Array.isArray(rawResponse) ? extractEmails(rawResponse.cc || rawResponse.CC || '') : '';
  const bcc = !Array.isArray(rawResponse) ? extractEmails(rawResponse.bcc || rawResponse.BCC || '') : '';
  
  const normalized = {
    to: to || fallbackEmail,
    subject: subject || 'AI-Generated Email',
    body: body || 'No content available',
    cc: cc,
    bcc: bcc
  };
  
  console.log('✅ Normalized email content:', {
    to: normalized.to,
    subject: normalized.subject,
    bodyPreview: normalized.body.substring(0, 100) + '...',
    bodyLength: normalized.body.length,
    cc: normalized.cc,
    bcc: normalized.bcc
  });
  
  // Final validation: ensure no objects leaked through
  Object.entries(normalized).forEach(([key, value]) => {
    if (typeof value === 'object') {
      console.error(`❌ Object leaked in field "${key}":`, value);
      (normalized as any)[key] = JSON.stringify(value);
    }
    if (typeof value !== 'string') {
      console.error(`❌ Non-string value in field "${key}":`, typeof value);
      (normalized as any)[key] = String(value);
    }
  });
  
  return normalized;
};

interface LeadsTableProps {
  leads: Lead[];
}

// State management for individual lead actions
interface LeadActionState {
  emailDraft: {
    loading: boolean;
    success: boolean;
    error: string | null;
    draftContent: EmailContent;
    originalContent?: EmailContent;
    showPreview: boolean;
    sending: boolean;
    sent: boolean;
  };
  websiteBuild: {
    loading: boolean;
    success: boolean;
    error: string | null;
    deployedUrl?: string;
    stage?: 'building' | 'deploying';
  };
}

export function LeadsTable({ leads }: LeadsTableProps) {
  // State management for each lead's actions
  const [leadStates, setLeadStates] = useState<Record<string, LeadActionState>>(() => {
    const initialStates: Record<string, LeadActionState> = {};
    leads.forEach(lead => {
      initialStates[lead.id] = {
        emailDraft: {
          loading: false,
          success: false,
          error: null,
          draftContent: {
            to: lead.emails[0] || '',
            subject: '',
            body: '',
            cc: '',
            bcc: ''
          },
          showPreview: false,
          sending: false,
          sent: false,
        },
        websiteBuild: {
          loading: false,
          success: false,
          error: null,
        },
      };
    });
    return initialStates;
  });

  // State for email goal customization
  const [emailGoals, setEmailGoals] = useState<Record<string, string>>(() => {
    const initialGoals: Record<string, string> = {};
    leads.forEach(lead => {
      initialGoals[lead.id] = EMAIL_CONFIG.DEFAULT_GOAL;
    });
    return initialGoals;
  });

  const [showGoalInput, setShowGoalInput] = useState<Record<string, boolean>>({});

  // Helper function to update lead state
  const updateLeadState = (leadId: string, updates: Partial<LeadActionState>) => {
    setLeadStates(prev => ({
      ...prev,
      [leadId]: {
        emailDraft: { ...prev[leadId]?.emailDraft, ...updates.emailDraft },
        websiteBuild: { ...prev[leadId]?.websiteBuild, ...updates.websiteBuild },
      },
    }));
  };

  // Handle email draft creation
  const handleCreateEmailDraft = async (lead: Lead) => {
    const leadId = lead.id;
    const goal = emailGoals[leadId] || EMAIL_CONFIG.DEFAULT_GOAL;
    
    // Reset state and start loading
    updateLeadState(leadId, {
      emailDraft: {
        loading: true,
        success: false,
        error: null,
        draftContent: {
          to: lead.emails[0] || '',
          subject: '',
          body: '',
          cc: '',
          bcc: ''
        },
        showPreview: false,
        sending: false,
        sent: false,
      },
    });

    try {
      const result = await EmailApiService.createEmailDraft(lead, goal, EMAIL_CONFIG.DEFAULT_MAX_WORDS);
      
      // Log the raw response for debugging
      console.log('📧 Email agent raw response:', result);
      
      // Normalize the response to ensure all fields are strings
      const normalizedContent = normalizeEmailResponse(result, lead.emails[0] || '');
      
      console.log('✅ Normalized and ready for display:', normalizedContent);
      
      // Update state with normalized content
      updateLeadState(leadId, {
        emailDraft: {
          loading: false,
          success: true,
          error: null,
          draftContent: normalizedContent,
          originalContent: normalizedContent, // Store original for reset functionality
          showPreview: true,
          sending: false,
          sent: false,
        },
      });
    } catch (error) {
      updateLeadState(leadId, {
        emailDraft: {
          loading: false,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error occurred',
          draftContent: {
            to: lead.emails[0] || '',
            subject: '',
            body: '',
            cc: '',
            bcc: ''
          },
          showPreview: false,
          sending: false,
          sent: false,
        },
      });
    }
  };

  // Handle website build and deployment
  const handleBuildWebsite = async (lead: Lead) => {
    const leadId = lead.id;
    
    // Reset state and start loading
    updateLeadState(leadId, {
      websiteBuild: {
        loading: true,
        success: false,
        error: null,
        stage: 'building',
      },
    });

    try {
      // Use lead's website URL or fallback to a generic business site
      const websiteUrl = lead.website || `https://example.com`;
      const businessName = lead.name;

      // Update stage to building
      updateLeadState(leadId, {
        websiteBuild: {
          loading: true,
          success: false,
          error: null,
          stage: 'building',
        },
      });

      // Build and deploy the website in one operation
      const deployedSite = await BuilderApiService.buildAndDeployWebsite(websiteUrl, businessName);

      updateLeadState(leadId, {
        websiteBuild: {
          loading: false,
          success: true,
          error: null,
          deployedUrl: deployedSite.deployedUrl,
        },
      });

    } catch (error) {
      updateLeadState(leadId, {
        websiteBuild: {
          loading: false,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error occurred',
        },
      });
    }
  };

  // Validate and clean email content before sending
  const validateAndCleanEmailContent = (content: EmailContent): { valid: boolean; error?: string; cleaned?: EmailContent } => {
    // Trim and validate subject
    const subject = content.subject?.trim() || '';
    if (!subject) {
      return { valid: false, error: 'Subject is required. Please add a subject line.' };
    }
    
    // Validate body (preserve internal line breaks, only trim start/end)
    const body = content.body || '';
    const trimmedBody = body.trim();
    if (!trimmedBody) {
      return { valid: false, error: 'Email body is required. Please add message content.' };
    }
    
    // Basic email validation helper
    const isValidEmail = (email: string): boolean => {
      return email.includes('@') && email.length > 3;
    };
    
    // Parse and clean recipients
    const parseEmails = (value: string): string[] => {
      if (!value || typeof value !== 'string') return [];
      return value
        .split(',')
        .map(email => email.trim())
        .filter(email => email.length > 0)
        .filter((email, index, arr) => 
          // Dedupe case-insensitively
          arr.findIndex(e => e.toLowerCase() === email.toLowerCase()) === index
        );
    };
    
    const toEmails = parseEmails(content.to);
    const ccEmails = parseEmails(content.cc || '');
    const bccEmails = parseEmails(content.bcc || '');
    
    // Validate at least one recipient
    if (toEmails.length === 0) {
      return { valid: false, error: 'At least one recipient is required. Please add a valid email address in the "To" field.' };
    }
    
    // Validate email format for all recipients
    const invalidToEmails = toEmails.filter(email => !isValidEmail(email));
    if (invalidToEmails.length > 0) {
      return { 
        valid: false, 
        error: `Invalid email address in "To" field: ${invalidToEmails[0]}. Please enter a valid email address.` 
      };
    }
    
    const invalidCcEmails = ccEmails.filter(email => !isValidEmail(email));
    if (invalidCcEmails.length > 0) {
      return { 
        valid: false, 
        error: `Invalid email address in "CC" field: ${invalidCcEmails[0]}. Please enter a valid email address.` 
      };
    }
    
    const invalidBccEmails = bccEmails.filter(email => !isValidEmail(email));
    if (invalidBccEmails.length > 0) {
      return { 
        valid: false, 
        error: `Invalid email address in "BCC" field: ${invalidBccEmails[0]}. Please enter a valid email address.` 
      };
    }
    
    // Return cleaned content (preserve body formatting)
    return {
      valid: true,
      cleaned: {
        subject,
        body: trimmedBody, // Only trim start/end, preserve internal line breaks
        to: toEmails.join(', '), // Keep as comma-separated string for display
        cc: ccEmails.join(', '),
        bcc: bccEmails.join(', ')
      }
    };
  };

  // Handle sending the approved email draft
  const handleSendEmail = async (lead: Lead) => {
    const leadId = lead.id;
    const currentState = leadStates[leadId];
    
    // Get the edited email content from the UI
    const editedContent = currentState?.emailDraft.draftContent;
    
    if (!editedContent) {
      console.error('No email content to send');
      updateLeadState(leadId, {
        emailDraft: {
          ...currentState?.emailDraft,
          error: 'No email content available. Please draft an email first.',
        },
      });
      return;
    }

    console.log('📧 Validating email content before sending...');
    
    // Validate and clean the content
    const validation = validateAndCleanEmailContent(editedContent);
    
    if (!validation.valid) {
      console.error('❌ Validation failed:', validation.error);
      updateLeadState(leadId, {
        emailDraft: {
          ...currentState?.emailDraft,
          error: validation.error || 'Validation failed',
          sending: false,
          sent: false,
        },
      });
      return;
    }
    
    const cleanedContent = validation.cleaned!;
    
    console.log('✅ Validation passed. Sending email with cleaned content:', {
      to: cleanedContent.to,
      subject: cleanedContent.subject,
      bodyPreview: cleanedContent.body.substring(0, 100) + '...',
      cc: cleanedContent.cc || '(none)',
      bcc: cleanedContent.bcc || '(none)',
    });

    // Start sending
    updateLeadState(leadId, {
      emailDraft: {
        ...currentState?.emailDraft,
        loading: false,
        success: true,
        error: null,
        sending: true,
        sent: false,
        showPreview: true,
      },
    });

    try {
      // Send the email with the cleaned content
      await EmailApiService.sendCustomEmail(cleanedContent);
      
      console.log('✅ Email sent successfully with edited content');
      
      updateLeadState(leadId, {
        emailDraft: {
          ...currentState?.emailDraft,
          loading: false,
          success: true,
          error: null,
          sending: false,
          sent: true,
          showPreview: false,
        },
      });
      
      // Show success message
      alert(`✅ Email sent successfully to ${cleanedContent.to}!`);
      
    } catch (error) {
      console.error('❌ Failed to send email:', error);
      
      // Extract detailed error message
      let errorMessage = 'Unknown error occurred while sending email';
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      updateLeadState(leadId, {
        emailDraft: {
          ...currentState?.emailDraft,
          loading: false,
          success: true,
          error: errorMessage,
          sending: false,
          sent: false,
          showPreview: true,
        },
      });
    }
  };

  // Handle closing the email preview
  const handleCloseEmailPreview = (leadId: string) => {
    const currentState = leadStates[leadId];
    updateLeadState(leadId, {
      emailDraft: {
        ...currentState?.emailDraft,
        showPreview: false,
      },
    });
  };

  // Handle retry for failed actions
  const handleRetryEmailDraft = (lead: Lead) => {
    handleCreateEmailDraft(lead);
  };

  const handleRetryWebsiteBuild = (lead: Lead) => {
    handleBuildWebsite(lead);
  };

  if (leads.length === 0) {
    return (
      <Card className="text-center py-16">
        <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-6" />
        <h3 className="text-xl font-semibold text-gray-900 mb-3">No leads yet</h3>
        <p className="text-lg text-gray-600">
          Start a campaign to discover potential customers
        </p>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden p-0">
      <div className="px-8 py-6 border-b border-gray-200 bg-gray-50">
        <h2 className="text-2xl font-semibold text-gray-900">Discovered Leads</h2>
        <p className="text-base text-gray-600 mt-2">{leads.length} businesses found</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-8 py-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wide">
                Business
              </th>
              <th className="px-8 py-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wide">
                Contact
              </th>
              <th className="px-8 py-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wide">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {leads.map((lead) => {
              const leadState = leadStates[lead.id];
              
              return (
              <tr key={lead.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-8 py-6">
                  <div className="flex flex-col">
                    <div className="text-base font-semibold text-gray-900 mb-1">
                      {lead.name}
                    </div>
                    <div className="text-sm text-gray-500 mb-1">{lead.address}</div>
                    {lead.category && (
                      <div className="text-xs text-gray-400">{lead.category}</div>
                    )}
                    {lead.rating && (
                      <div className="text-sm text-gray-600">
                        ⭐ {lead.rating.toFixed(1)} ({lead.total_ratings} reviews)
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-8 py-6">
                  <div className="flex flex-col gap-2">
                    {lead.phone_number && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Phone className="w-4 h-4" />
                        {lead.phone_number}
                      </div>
                    )}
                    {lead.emails.length > 0 && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Mail className="w-4 h-4" />
                        {lead.emails[0]}
                      </div>
                    )}
                    {lead.phone_numbers.length > 0 && lead.phone_numbers[0] !== lead.phone_number && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Phone className="w-4 h-4" />
                        {lead.phone_numbers[0]}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-8 py-6">
                    <div className="flex flex-col gap-3">
                      {/* Draft Email Section */}
                      {lead.emails.length > 0 && (
                  <div className="flex flex-col gap-2">
                          {/* Email Action Button */}
                          {(() => {
                            const emailState = leadState?.emailDraft;
                            
                            // If email has been sent, show sent status
                            if (emailState?.sent) {
                              return (
                                <div className="flex items-center gap-2 text-sm text-green-700 bg-green-50 px-3 py-2 rounded-lg">
                                  <CheckCircle className="w-4 h-4" />
                                  Email Sent
                                </div>
                              );
                            }
                            
                            // If draft has been created successfully, show review button
                            if (emailState?.success && emailState?.draftContent) {
                              return (
                                <Button
                                  variant="tertiary"
                                  size="sm"
                                  onClick={() => {
                                  const currentState = leadStates[lead.id];
                                  updateLeadState(lead.id, {
                                    emailDraft: {
                                      ...currentState?.emailDraft,
                                      showPreview: true,
                                    },
                                  });
                                }}
                                >
                                  <Eye className="w-4 h-4" />
                                  Review Draft
                                </Button>
                              );
                            }
                            
                            // Default: show goal input and draft email button
                            return (
                              <div className="space-y-2">
                                {/* Email Goal Customization */}
                                <div className="space-y-1">
                                  <div className="flex items-center justify-between">
                                    <label className="text-xs font-medium text-gray-600">Email Goal:</label>
                                    <Button
                                      variant="secondary"
                                      size="sm"
                                      className="text-xs px-2 py-1 h-6"
                                      onClick={() => {
                                        setShowGoalInput(prev => ({
                                          ...prev,
                                          [lead.id]: !prev[lead.id]
                                        }));
                                      }}
                                    >
                                      {showGoalInput[lead.id] ? 'Hide' : 'Customize'}
                                    </Button>
                                  </div>
                                  
                                  {showGoalInput[lead.id] ? (
                                    <textarea
                                      value={emailGoals[lead.id] || EMAIL_CONFIG.DEFAULT_GOAL}
                                      onChange={(e) => {
                                        setEmailGoals(prev => ({
                                          ...prev,
                                          [lead.id]: e.target.value
                                        }));
                                      }}
                                      className="w-full text-xs p-2 border border-gray-300 rounded resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                      rows={3}
                                      placeholder="Enter your email goal/pitch..."
                                    />
                                  ) : (
                                    <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded border truncate">
                                      {emailGoals[lead.id] || EMAIL_CONFIG.DEFAULT_GOAL}
                                    </div>
                                  )}
                                </div>

                                {/* Draft Email Button */}
                      <Button
                        variant="primary"
                                  size="sm"
                                  onClick={() => handleCreateEmailDraft(lead)}
                                  disabled={emailState?.loading || lead.emails.length === 0}
                                  title={lead.emails.length === 0 ? "No email address available for this lead" : ""}
                                  className="w-full"
                                >
                                  {emailState?.loading ? (
                                    <>
                                      <Loader2 className="w-4 h-4 animate-spin" />
                                      Drafting...
                                    </>
                                  ) : (
                                    <>
                        <Mail className="w-4 h-4" />
                                      {lead.emails.length === 0 ? "No Email Available" : "Draft Email"}
                                    </>
                                  )}
                                </Button>
                                
                                {/* Loading State Display */}
                                {emailState?.loading && (
                                  <div className="mt-2 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                    <div className="flex items-center gap-3">
                                      <Loader2 className="w-5 h-5 text-blue-600 animate-spin flex-shrink-0" />
                                      <div className="flex-1">
                                        <p className="text-sm font-medium text-blue-900">Generating draft...</p>
                                        <p className="text-xs text-blue-700 mt-1">The AI is crafting a personalized email for {lead.name}</p>
                                      </div>
                                    </div>
                                  </div>
                                )}
                                
                                {/* Error Display */}
                                {emailState?.error && !emailState?.loading && (
                                  <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                                    <div className="flex items-start gap-2">
                                      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                                      <div className="flex-1">
                                        <p className="text-sm font-medium text-red-900">Error Creating Draft</p>
                                        <p className="text-xs text-red-700 mt-1">{emailState.error}</p>
                                        <Button
                                          variant="secondary"
                                          size="sm"
                                          onClick={() => handleCreateEmailDraft(lead)}
                                          className="mt-2 text-xs"
                                        >
                                          Try Again
                                        </Button>
                                      </div>
                                    </div>
                                  </div>
                                )}
                              </div>
                            );
                          })()}

                          {/* Email Preview Dropdown */}
                          {leadState?.emailDraft.showPreview && leadState?.emailDraft.draftContent && (
                            <div className="mt-2 border border-gray-200 rounded-lg bg-white shadow-lg w-full max-w-4xl">
                              {/* Preview Header */}
                              <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
                                <h4 className="text-lg font-semibold text-gray-900">Email Preview</h4>
                                <Button
                                  variant="secondary"
                                  size="sm"
                                  className="p-1 h-8 w-8"
                                  onClick={() => handleCloseEmailPreview(lead.id)}
                                >
                                  <X className="w-4 h-4" />
                                </Button>
                              </div>
                              
                              {/* Email Content - Fully Customizable */}
                              <div className="p-4 space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  <div>
                                    <div className="text-sm font-medium text-gray-700 mb-1">To:</div>
                                    <input
                                      type="email"
                                      value={leadState.emailDraft.draftContent.to}
                                      onChange={(e) => {
                                        const currentState = leadStates[lead.id];
                                        updateLeadState(lead.id, {
                                          emailDraft: {
                                            ...currentState?.emailDraft,
                                            draftContent: {
                                              ...currentState?.emailDraft.draftContent,
                                              to: e.target.value
                                            }
                                          }
                                        });
                                      }}
                                      className="w-full text-base text-gray-900 bg-white p-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                      placeholder="Enter recipient email"
                                    />
                                  </div>
                                  <div>
                                    <div className="text-sm font-medium text-gray-700 mb-1">From:</div>
                                    <input
                                      type="email"
                                      value={EMAIL_CONFIG.SENDER_EMAIL}
                                      readOnly
                                      className="w-full text-base text-gray-900 bg-gray-50 p-2 rounded border border-gray-200"
                                    />
                                  </div>
                                </div>
                                <div>
                                  <div className="text-sm font-medium text-gray-700 mb-1">Subject:</div>
                                  <input
                                    type="text"
                                    value={leadState.emailDraft.draftContent.subject}
                                    onChange={(e) => {
                                      const currentState = leadStates[lead.id];
                                      updateLeadState(lead.id, {
                                        emailDraft: {
                                          ...currentState?.emailDraft,
                                          draftContent: {
                                            ...currentState?.emailDraft.draftContent,
                                            subject: e.target.value
                                          }
                                        }
                                      });
                                    }}
                                    className="w-full text-base font-medium text-gray-900 bg-white p-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="Enter email subject"
                                  />
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  <div>
                                    <div className="text-sm font-medium text-gray-700 mb-1">CC (Optional):</div>
                                    <input
                                      type="email"
                                      value={leadState.emailDraft.draftContent.cc || ''}
                                      onChange={(e) => {
                                        const currentState = leadStates[lead.id];
                                        updateLeadState(lead.id, {
                                          emailDraft: {
                                            ...currentState?.emailDraft,
                                            draftContent: {
                                              ...currentState?.emailDraft.draftContent,
                                              cc: e.target.value
                                            }
                                          }
                                        });
                                      }}
                                      className="w-full text-base text-gray-900 bg-white p-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                      placeholder="Enter CC email (optional)"
                                    />
                                  </div>
                                  <div>
                                    <div className="text-sm font-medium text-gray-700 mb-1">BCC (Optional):</div>
                                    <input
                                      type="email"
                                      value={leadState.emailDraft.draftContent.bcc || ''}
                                      onChange={(e) => {
                                        const currentState = leadStates[lead.id];
                                        updateLeadState(lead.id, {
                                          emailDraft: {
                                            ...currentState?.emailDraft,
                                            draftContent: {
                                              ...currentState?.emailDraft.draftContent,
                                              bcc: e.target.value
                                            }
                                          }
                                        });
                                      }}
                                      className="w-full text-base text-gray-900 bg-white p-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                      placeholder="Enter BCC email (optional)"
                                    />
                                  </div>
                                </div>
                                <div>
                                  <div className="flex items-center justify-between mb-1">
                                    <div className="text-sm font-medium text-gray-700">Message:</div>
                                    <Button
                                      variant="secondary"
                                      size="sm"
                                      className="text-xs px-2 py-1 h-6"
                                      onClick={() => {
                                        // Reset to original AI-generated content
                                        const currentState = leadStates[lead.id];
                                        if (currentState?.emailDraft.originalContent) {
                                          updateLeadState(lead.id, {
                                            emailDraft: {
                                              ...currentState?.emailDraft,
                                              draftContent: { ...currentState?.emailDraft.originalContent }
                                            }
                                          });
                                        }
                                      }}
                                    >
                                      <RefreshCw className="w-3 h-3" />
                                      Reset to AI Generated
                                    </Button>
                                  </div>
                                  <textarea
                                    value={leadState.emailDraft.draftContent.body}
                                    onChange={(e) => {
                                      const currentState = leadStates[lead.id];
                                      updateLeadState(lead.id, {
                                        emailDraft: {
                                          ...currentState?.emailDraft,
                                          draftContent: {
                                            ...currentState?.emailDraft.draftContent,
                                            body: e.target.value
                                          }
                                        }
                                      });
                                    }}
                                    className="w-full text-base text-gray-700 bg-white p-4 rounded border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-80 resize-y font-mono"
                                    style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}
                                    placeholder="Enter your email message"
                                    rows={16}
                                  />
                                </div>
                              </div>
                              
                              {/* Action Buttons */}
                              <div className="flex gap-3 p-4 border-t border-gray-200 bg-gray-50">
                                <Button
                                  variant="primary"
                                  size="sm"
                                  onClick={() => handleSendEmail(lead)}
                                  disabled={leadState?.emailDraft.sending}
                                >
                                  {leadState?.emailDraft.sending ? (
                                    <>
                                      <Loader2 className="w-4 h-4 animate-spin" />
                                      Sending...
                                    </>
                                  ) : (
                                    <>
                                      <Send className="w-4 h-4" />
                        Send Email
                                    </>
                                  )}
                                </Button>
                                <Button
                                  variant="secondary"
                                  size="sm"
                                  onClick={() => handleCloseEmailPreview(lead.id)}
                                >
                                  Cancel
                                </Button>
                              </div>
                            </div>
                          )}
                          
                          {/* Error Display */}
                          {leadState?.emailDraft.error && (
                            <div className="flex flex-col gap-2">
                              <div className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                                {leadState.emailDraft.error}
                              </div>
                              <Button
                                variant="secondary"
                                size="sm"
                                onClick={() => handleRetryEmailDraft(lead)}
                              >
                                <RefreshCw className="w-3 h-3" />
                                Retry
                              </Button>
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Build Website Button */}
                      <div className="flex flex-col gap-2">
                        {!leadState?.websiteBuild.success ? (
                          <Button
                            variant="tertiary"
                            size="sm"
                            onClick={() => handleBuildWebsite(lead)}
                            disabled={leadState?.websiteBuild.loading}
                          >
                            {leadState?.websiteBuild.loading ? (
                              <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                {leadState.websiteBuild.stage === 'building' ? 'Building...' : 'Deploying...'}
                              </>
                            ) : (
                              <>
                                <Globe className="w-4 h-4" />
                                Build Website
                              </>
                            )}
                          </Button>
                        ) : (
                          <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2 text-sm text-green-700 bg-green-50 px-3 py-2 rounded-lg">
                              <CheckCircle className="w-4 h-4" />
                              Website Deployed
                            </div>
                            {leadState.websiteBuild.deployedUrl && (
                              <Button
                                variant="secondary"
                                size="sm"
                                onClick={() => window.open(leadState.websiteBuild.deployedUrl, '_blank')}
                              >
                                <ExternalLink className="w-3 h-3" />
                                View Site
                      </Button>
                    )}
                          </div>
                        )}
                        
                        {leadState?.websiteBuild.error && (
                          <div className="flex flex-col gap-2">
                            <div className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded max-w-xs">
                              {leadState.websiteBuild.error}
                            </div>
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => handleRetryWebsiteBuild(lead)}
                            >
                              <RefreshCw className="w-3 h-3" />
                              Retry
                            </Button>
                          </div>
                        )}
                      </div>
                      
                      {/* Other Action Buttons */}
                      <div className="flex flex-col gap-2">
                    {/* Call Business Button */}
                    {(lead.phone_number || lead.phone_numbers.length > 0) && (
                      <Button
                        variant="secondary"
                            size="sm"
                            onClick={() => {
                              // Call button does nothing
                            }}
                      >
                            <Phone className="w-3 h-3" />
                            Call
                      </Button>
                    )}
                    
                    {/* View Website Button */}
                    {lead.website && (
                      <Button
                        variant="secondary"
                            size="sm"
                        onClick={() => window.open(lead.website, '_blank')}
                      >
                            <ExternalLink className="w-3 h-3" />
                            View Site
                      </Button>
                    )}
                      </div>
                    
                    {/* Show message if no contact info available */}
                    {lead.emails.length === 0 && !lead.phone_number && lead.phone_numbers.length === 0 && !lead.website && (
                      <div className="text-sm text-gray-500 italic">
                        No contact information available
                      </div>
                    )}
                  </div>
                </td>
              </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

