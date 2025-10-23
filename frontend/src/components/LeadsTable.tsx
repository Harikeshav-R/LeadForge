import { Card } from './Card';
import { Badge } from './Badge';
import { Button } from './Button';
import { ExternalLink, Mail, Phone, Building2 } from 'lucide-react';
import type { Lead } from '../types';

interface LeadsTableProps {
  leads: Lead[];
}

export function LeadsTable({ leads }: LeadsTableProps) {
  const getStatusBadge = (isOpen?: boolean) => {
    if (isOpen === undefined) {
      return <Badge variant="gray">Unknown</Badge>;
    }
    return isOpen ? <Badge variant="green">Open</Badge> : <Badge variant="red">Closed</Badge>;
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
                Status
              </th>
              <th className="px-8 py-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wide">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {leads.map((lead) => (
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
                  {getStatusBadge(lead.is_open)}
                </td>
                <td className="px-8 py-6">
                  <div className="flex items-center gap-3">
                    {lead.website && (
                      <Button
                        variant="secondary"
                        className="text-sm py-2 px-3"
                        onClick={() => window.open(lead.website, '_blank')}
                      >
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                    )}
                    <Button variant="secondary" className="text-sm py-2 px-4">
                      View Details
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

