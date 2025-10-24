import { useState } from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { ExternalLink, Mail, Phone, Building2, Globe, Loader2, CheckCircle, RefreshCw, X, Send, Eye } from 'lucide-react';
import { BuilderApiService, EmailApiService } from '../services/api';
import type { Lead } from '../types';
import { EMAIL_CONFIG } from '../config/email';

interface LeadsTableProps {
  leads: Lead[];
}

// State management for individual lead actions
interface LeadActionState {
  emailDraft: {
    loading: boolean;
    success: boolean;
    error: string | null;
    draftId?: string;
    draftContent?: {
      subject: string;
      body: string;
      to: string;
    };
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
    
    // Reset state and start loading
    updateLeadState(leadId, {
      emailDraft: {
        loading: true,
        success: false,
        error: null,
        showPreview: false,
        sending: false,
        sent: false,
      },
    });

    try {
      const result = await EmailApiService.createEmailDraft(lead);
      
      if (result.success) {
        updateLeadState(leadId, {
          emailDraft: {
            loading: false,
            success: true,
            error: null,
            draftId: result.draft_id,
            draftContent: result.draft_content,
            showPreview: true,
            sending: false,
            sent: false,
          },
        });
      } else {
        updateLeadState(leadId, {
          emailDraft: {
            loading: false,
            success: false,
            error: result.error || 'Failed to create email draft',
            showPreview: false,
            sending: false,
            sent: false,
          },
        });
      }
    } catch (error) {
      updateLeadState(leadId, {
        emailDraft: {
          loading: false,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error occurred',
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

  // Handle sending the approved email draft
  const handleSendEmail = async (lead: Lead) => {
    const leadId = lead.id;
    const leadState = leadStates[leadId];
    
    if (!leadState?.emailDraft.draftId) {
      return;
    }

    // Start sending
    updateLeadState(leadId, {
      emailDraft: {
        loading: false,
        success: true,
        error: null,
        sending: true,
        sent: false,
        showPreview: true,
      },
    });

    try {
      const result = await EmailApiService.sendEmail(leadState.emailDraft.draftId, lead);
      
      if (result.success) {
        updateLeadState(leadId, {
          emailDraft: {
            loading: false,
            success: true,
            error: null,
            sending: false,
            sent: true,
            showPreview: false,
          },
        });
      } else {
        updateLeadState(leadId, {
          emailDraft: {
            loading: false,
            success: true,
            error: result.error || 'Failed to send email',
            sending: false,
            sent: false,
            showPreview: true,
          },
        });
      }
    } catch (error) {
      updateLeadState(leadId, {
        emailDraft: {
          loading: false,
          success: true,
          error: error instanceof Error ? error.message : 'Unknown error occurred while sending email',
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
        loading: currentState?.emailDraft.loading || false,
        success: currentState?.emailDraft.success || false,
        error: currentState?.emailDraft.error || null,
        showPreview: false,
        sending: currentState?.emailDraft.sending || false,
        sent: currentState?.emailDraft.sent || false,
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
                                      loading: currentState?.emailDraft.loading || false,
                                      success: currentState?.emailDraft.success || false,
                                      error: currentState?.emailDraft.error || null,
                                      showPreview: true,
                                      sending: currentState?.emailDraft.sending || false,
                                      sent: currentState?.emailDraft.sent || false,
                                    },
                                  });
                                }}
                                >
                                  <Eye className="w-4 h-4" />
                                  Review Draft
                                </Button>
                              );
                            }
                            
                            // Default: show draft email button
                            return (
                              <Button
                                variant="primary"
                                size="sm"
                                onClick={() => handleCreateEmailDraft(lead)}
                                disabled={emailState?.loading || lead.emails.length === 0}
                                title={lead.emails.length === 0 ? "No email address available for this lead" : ""}
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
                            );
                          })()}

                          {/* Email Preview Dropdown */}
                          {leadState?.emailDraft.showPreview && leadState?.emailDraft.draftContent && (
                            <div className="mt-2 border border-gray-200 rounded-lg bg-white shadow-lg w-full max-w-2xl">
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
                              
                              {/* Email Content */}
                              <div className="p-4 space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  <div>
                                    <div className="text-sm font-medium text-gray-700 mb-1">To:</div>
                                    <div className="text-base text-gray-900 bg-gray-50 p-2 rounded">{leadState.emailDraft.draftContent.to}</div>
                                  </div>
                                  <div>
                                    <div className="text-sm font-medium text-gray-700 mb-1">From:</div>
                                    <div className="text-base text-gray-900 bg-gray-50 p-2 rounded">{EMAIL_CONFIG.SENDER_EMAIL}</div>
                                  </div>
                                </div>
                                <div>
                                  <div className="text-sm font-medium text-gray-700 mb-1">Subject:</div>
                                  <div className="text-base font-medium text-gray-900 bg-gray-50 p-2 rounded">{leadState.emailDraft.draftContent.subject}</div>
                                </div>
                                <div>
                                  <div className="text-sm font-medium text-gray-700 mb-1">Message:</div>
                                  <div className="text-base text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded min-h-64 max-h-96 overflow-y-auto border">
                                    {leadState.emailDraft.draftContent.body}
                                  </div>
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

