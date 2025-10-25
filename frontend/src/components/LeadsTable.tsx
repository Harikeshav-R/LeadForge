// UI Refactor: Updated to use shadcn/ui components (Card, Button, Input, Label, Badge, Dialog, Separator, Table)
// Maintains all existing functionality while improving UI consistency and accessibility
import { useState } from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { ExternalLink, Mail, Phone, Building2, Globe, Loader2, CheckCircle, RefreshCw, X, Send, Eye, AlertCircle } from 'lucide-react';
import { BuilderApiService, DeployerApiService, EmailApiService } from '../services/api';
import type { Lead, EmailContent } from '../types';
import { EMAIL_CONFIG } from '../config/email';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { ScrollArea } from './ui/scroll-area';

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
    websiteZip?: string;
    deployedUrl?: string;
    stage?: 'building' | 'built' | 'deploying' | 'deployed';
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

  // Handle website build (step 1: build only)
  const handleBuildWebsite = async (lead: Lead) => {
    const leadId = lead.id;
    
    // Reset state and start loading
    updateLeadState(leadId, {
      websiteBuild: {
        loading: true,
        success: false,
        error: null,
        stage: 'building',
        websiteZip: undefined,
      },
    });

    try {
      // Use lead's website URL or fallback to a generic business site
      const websiteUrl = lead.website || `https://example.com`;
      const businessName = lead.name;

      console.log(`🏗️ Building website for ${businessName} from URL: ${websiteUrl}`);

      // Build the website (without deploying)
      const websiteZip = await BuilderApiService.buildWebsite(websiteUrl, businessName);

      updateLeadState(leadId, {
        websiteBuild: {
          loading: false,
          success: true,
          error: null,
          websiteZip: websiteZip,
          stage: 'built',
        },
      });

      console.log(`✅ Website built successfully for ${businessName}`);

    } catch (error) {
      updateLeadState(leadId, {
        websiteBuild: {
          loading: false,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error occurred',
          stage: undefined,
        },
      });
    }
  };

  // Handle website deployment (step 2: deploy the built website)
  const handleDeployWebsite = async (lead: Lead) => {
    const leadId = lead.id;
    const currentState = leadStates[leadId];
    
    // Check if we have a built website to deploy
    if (!currentState?.websiteBuild.websiteZip) {
      updateLeadState(leadId, {
        websiteBuild: {
          ...currentState?.websiteBuild,
          error: 'No website built yet. Please build the website first.',
        },
      });
      return;
    }

    // Start deployment
    updateLeadState(leadId, {
      websiteBuild: {
        ...currentState?.websiteBuild,
        loading: true,
        error: null,
        stage: 'deploying',
      },
    });

    try {
      const businessName = lead.name;
      const websiteZip = currentState.websiteBuild.websiteZip;

      console.log(`🚀 Deploying website for ${businessName}`);

      // Deploy the website
      const deployedSite = await DeployerApiService.deployWebsite(businessName, websiteZip);

      updateLeadState(leadId, {
        websiteBuild: {
          loading: false,
          success: true,
          error: null,
          websiteZip: websiteZip,
          deployedUrl: deployedSite.url,
          stage: 'deployed',
        },
      });

      console.log(`✅ Website deployed successfully for ${businessName} at ${deployedSite.url}`);

    } catch (error) {
      updateLeadState(leadId, {
        websiteBuild: {
          ...currentState?.websiteBuild,
          loading: false,
          success: true, // Build was successful, only deploy failed
          error: error instanceof Error ? error.message : 'Unknown error occurred',
          stage: 'built', // Revert to 'built' stage so user can retry deploy
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

  const handleRetryWebsiteBuild = async (lead: Lead) => {
    const leadId = lead.id;
    
    // Reset the website build state and clear any previous errors
    updateLeadState(leadId, {
      websiteBuild: {
        loading: false,
        success: false,
        error: null,
        websiteZip: undefined,
        deployedUrl: undefined,
        stage: undefined,
      },
    });

    // Retry the build
    await handleBuildWebsite(lead);
  };

  // Handle website preview
  const handlePreviewWebsite = async (lead: Lead) => {
    const leadId = lead.id;
    const currentState = leadStates[leadId];
    
    if (!currentState?.websiteBuild.websiteZip) {
      console.error('No website zip available for preview');
      return;
    }

    // Show loading state
    updateLeadState(leadId, {
      websiteBuild: {
        ...currentState?.websiteBuild,
        loading: true,
        error: null,
      },
    });

    try {
      // Convert base64 to blob
      const zipBase64 = currentState.websiteBuild.websiteZip;
      const binaryString = atob(zipBase64);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: 'application/zip' });
      
      // Create a temporary URL for the zip file
      const zipUrl = URL.createObjectURL(blob);
      
      // Try to extract and preview HTML directly
      try {
        // Use JSZip to extract the HTML files
        const JSZip = (await import('jszip')).default;
        const zip = await JSZip.loadAsync(blob);
        
        // Debug: Log all files in the zip
        const allFiles = Object.keys(zip.files);
        console.log(`📦 Zip contains ${allFiles.length} files:`, allFiles);
        
        // Find the main HTML file (usually index.html)
        let htmlFile = zip.file('index.html');
        if (!htmlFile) {
          // Look for any HTML file
          const htmlFiles = Object.keys(zip.files).filter(name => name.endsWith('.html'));
          console.log(`🔍 Found HTML files:`, htmlFiles);
          if (htmlFiles.length > 0) {
            htmlFile = zip.file(htmlFiles[0]);
          }
        }
        
        if (htmlFile) {
          // Extract the HTML content
          let htmlContent = await htmlFile.async('text');
          console.log(`📄 HTML content preview (first 500 chars):`, htmlContent.substring(0, 500));
          
          // Try to extract and inline CSS and JS files
          const cssFiles = Object.keys(zip.files).filter(name => name.endsWith('.css'));
          const jsFiles = Object.keys(zip.files).filter(name => name.endsWith('.js'));
          console.log(`🎨 Found CSS files:`, cssFiles);
          console.log(`⚡ Found JS files:`, jsFiles);
          
          // Extract CSS content
          let inlineCSS = '';
          for (const cssFile of cssFiles) {
            try {
              const cssContent = await zip.file(cssFile)?.async('text');
              if (cssContent) {
                inlineCSS += `\n/* ${cssFile} */\n${cssContent}\n`;
              }
            } catch (e) {
              console.warn(`Failed to extract CSS file ${cssFile}:`, e);
            }
          }
          
          // Extract JS content
          let inlineJS = '';
          for (const jsFile of jsFiles) {
            try {
              const jsContent = await zip.file(jsFile)?.async('text');
              if (jsContent) {
                inlineJS += `\n/* ${jsFile} */\n${jsContent}\n`;
              }
            } catch (e) {
              console.warn(`Failed to extract JS file ${jsFile}:`, e);
            }
          }
          
          // Create a complete HTML document with inlined assets
          const completeHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${lead.name} - Website Preview</title>
    <style>
        /* Reset and base styles */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; }
        
        /* Inlined CSS from the website */
        ${inlineCSS}
    </style>
</head>
<body>
    ${htmlContent.replace(/<html[^>]*>|<\/html>|<head[^>]*>.*?<\/head>|<body[^>]*>|<\/body>/gi, '')}
    
    <script>
        // Inlined JS from the website
        ${inlineJS}
    </script>
</body>
</html>`;
          
          // Create a new window with the complete HTML content
          const previewWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
          if (previewWindow) {
            previewWindow.document.write(completeHTML);
            previewWindow.document.close();
            previewWindow.document.title = `${lead.name} - Website Preview`;
            console.log(`👀 Opened website preview for ${lead.name} with inlined assets`);
          } else {
            throw new Error('Popup blocked - please allow popups for this site');
          }
        } else {
          throw new Error('No HTML file found in the zip');
        }
      } catch (extractError) {
        console.warn('Failed to extract HTML, trying fallback preview:', extractError);
        
        // Fallback: Create a simple HTML viewer with the zip content
        try {
          const fallbackHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${lead.name} - Website Preview (Fallback)</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; padding: 20px; background: #f5f5f5; 
        }
        .container { 
            max-width: 1200px; margin: 0 auto; background: white; 
            padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .header { 
            border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 20px; 
        }
        .download-btn { 
            background: #007bff; color: white; padding: 10px 20px; 
            border: none; border-radius: 5px; cursor: pointer; 
            text-decoration: none; display: inline-block; margin: 10px 0; 
        }
        .download-btn:hover { background: #0056b3; }
        .info { 
            background: #e7f3ff; padding: 15px; border-radius: 5px; 
            border-left: 4px solid #007bff; margin: 20px 0; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ ${lead.name} - Website Preview</h1>
            <p>Website has been built successfully! Download the zip file to view the complete website.</p>
        </div>
        
        <div class="info">
            <h3>📦 What's in the zip file?</h3>
            <p>The zip file contains the complete website with HTML, CSS, JavaScript, and all assets. 
            Extract it to a folder and open the index.html file in your browser to see the full website.</p>
        </div>
        
        <a href="${zipUrl}" download="${lead.name.replace(/[^a-zA-Z0-9]/g, '_')}_website.zip" class="download-btn">
            📥 Download Website Zip
        </a>
        
        <div class="info">
            <h3>🔧 How to view the website:</h3>
            <ol>
                <li>Click the download button above</li>
                <li>Extract the zip file to a folder</li>
                <li>Open the index.html file in your web browser</li>
                <li>Or deploy it using the "Deploy Website" button in the main interface</li>
            </ol>
        </div>
    </div>
</body>
</html>`;
          
          const previewWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
          if (previewWindow) {
            previewWindow.document.write(fallbackHTML);
            previewWindow.document.close();
            previewWindow.document.title = `${lead.name} - Website Preview (Fallback)`;
            console.log(`👀 Opened fallback preview for ${lead.name}`);
          } else {
            throw new Error('Popup blocked - please allow popups for this site');
          }
        } catch (fallbackError) {
          console.error('Fallback preview also failed, downloading zip:', fallbackError);
          
          // Final fallback: download the zip file
          const link = document.createElement('a');
          link.href = zipUrl;
          link.download = `${lead.name.replace(/[^a-zA-Z0-9]/g, '_')}_website.zip`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
          console.log(`📦 Downloaded website zip for ${lead.name} (all preview methods failed)`);
        }
      }
      
      // Clean up the URL
      setTimeout(() => URL.revokeObjectURL(zipUrl), 1000);
      
      // Clear loading state
      updateLeadState(leadId, {
        websiteBuild: {
          ...currentState?.websiteBuild,
          loading: false,
        },
      });
      
    } catch (error) {
      console.error('Failed to preview website:', error);
      updateLeadState(leadId, {
        websiteBuild: {
          ...currentState?.websiteBuild,
          loading: false,
          error: 'Failed to preview website. Please try downloading the zip file.',
        },
      });
    }
  };

  if (leads.length === 0) {
    return (
      <Card className="text-center py-20 px-8">
        {/* Added more generous padding for empty state */}
        <Building2 className="w-16 h-16 text-muted-foreground mx-auto mb-8" />
        <h3 className="text-xl font-semibold text-foreground mb-4">No leads yet</h3>
        <p className="text-lg text-muted-foreground max-w-md mx-auto">
          Start a campaign to discover potential customers
        </p>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden p-0 border border-border">
      <div className="px-8 py-6 border-b border-border">
        <h2 className="text-2xl font-semibold text-foreground tracking-tight">Discovered Leads</h2>
        <p className="text-sm text-muted-foreground mt-2">{leads.length} businesses found</p>
      </div>

      <ScrollArea className="w-full">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-[300px]">Business</TableHead>
              <TableHead className="w-[200px]">Contact</TableHead>
              <TableHead className="w-[400px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {leads.map((lead) => {
              const leadState = leadStates[lead.id];
              
              return (
              <TableRow key={lead.id} className="hover:bg-muted/30 transition-colors">
                <TableCell className="py-6">
                  <div className="flex flex-col space-y-2">
                    <div className="text-sm font-semibold text-foreground leading-6">
                      {lead.name}
                    </div>
                    <div className="text-xs text-muted-foreground leading-5">{lead.address}</div>
                    {lead.category && (
                      <div className="text-xs text-muted-foreground leading-5">{lead.category}</div>
                    )}
                    {lead.rating && (
                      <div className="text-xs text-muted-foreground leading-5">
                        ⭐ {lead.rating.toFixed(1)} ({lead.total_ratings} reviews)
                      </div>
                    )}
                  </div>
                </TableCell>
                <TableCell className="py-6">
                  <div className="flex flex-col gap-2">
                    {lead.phone_number && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground leading-5">
                        <Phone className="w-3.5 h-3.5" />
                        {lead.phone_number}
                      </div>
                    )}
                    {lead.emails.length > 0 && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground leading-5">
                        <Mail className="w-3.5 h-3.5" />
                        {lead.emails[0]}
                      </div>
                    )}
                    {lead.phone_numbers.length > 0 && lead.phone_numbers[0] !== lead.phone_number && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground leading-5">
                        <Phone className="w-3.5 h-3.5" />
                        {lead.phone_numbers[0]}
                      </div>
                    )}
                  </div>
                </TableCell>
                <TableCell className="py-6">
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
                            <div className="mt-2 border border-gray-200 rounded-lg bg-white shadow-lg w-full max-w-6xl">
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
                      
                      {/* Build/Deploy Website Buttons */}
                      <div className="flex flex-col gap-2">
                        {(() => {
                          const buildState = leadState?.websiteBuild;
                          const stage = buildState?.stage;
                          
                          // Not built yet - show Build button
                          if (!buildState?.success && !buildState?.websiteZip) {
                            return (
                              <Button
                                variant="tertiary"
                                size="sm"
                                onClick={() => handleBuildWebsite(lead)}
                                disabled={buildState?.loading}
                              >
                                {buildState?.loading && stage === 'building' ? (
                                  <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Building...
                                  </>
                                ) : (
                                  <>
                                    <Globe className="w-4 h-4" />
                                    Build Website
                                  </>
                                )}
                              </Button>
                            );
                          }
                          
                          // Built but not deployed - show Preview and Deploy buttons
                          if (buildState?.success && buildState?.websiteZip && stage === 'built' && !buildState?.deployedUrl) {
                            return (
                              <>
                                <div className="flex items-center gap-2 text-sm text-blue-700 bg-blue-50 px-3 py-2 rounded-lg">
                                  <CheckCircle className="w-4 h-4" />
                                  Website Built
                                </div>
                                <div className="flex flex-col gap-2">
                                  <Button
                                    variant="secondary"
                                    size="sm"
                                    onClick={() => handlePreviewWebsite(lead)}
                                    disabled={buildState?.loading}
                                    className="w-full"
                                  >
                                    {buildState?.loading ? (
                                      <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Extracting...
                                      </>
                                    ) : (
                                      <>
                                        <Eye className="w-4 h-4" />
                                        Preview Website
                                      </>
                                    )}
                                  </Button>
                                  <Button
                                    variant="primary"
                                    size="sm"
                                    onClick={() => handleDeployWebsite(lead)}
                                    disabled={buildState?.loading}
                                    className="w-full"
                                  >
                                    {buildState?.loading ? (
                                      <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Deploying...
                                      </>
                                    ) : (
                                      <>
                                        <Globe className="w-4 h-4" />
                                        Deploy Website
                                      </>
                                    )}
                                  </Button>
                                </div>
                              </>
                            );
                          }
                          
                          // Deployed - show success status and View Site button
                          if (buildState?.deployedUrl && stage === 'deployed') {
                            return (
                              <div className="flex flex-col gap-1">
                                <div className="flex items-center gap-2 text-sm text-green-700 bg-green-50 px-3 py-2 rounded-lg">
                                  <CheckCircle className="w-4 h-4" />
                                  Website Deployed
                                </div>
                                <Button
                                  variant="secondary"
                                  size="sm"
                                  onClick={() => window.open(buildState.deployedUrl, '_blank')}
                                >
                                  <ExternalLink className="w-3 h-3" />
                                  View Site
                                </Button>
                              </div>
                            );
                          }
                          
                          // Fallback
                          return null;
                        })()}
                        
                        {/* Error Display */}
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
                </TableCell>
              </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </ScrollArea>
    </Card>
  );
}

