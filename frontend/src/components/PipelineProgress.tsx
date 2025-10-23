import { Card } from './Card';
import { Badge } from './Badge';
import { Search, Mail, Phone, CheckCircle2, Loader2 } from 'lucide-react';
import type { PipelineStage } from '../types';

const iconMap = {
  search: Search,
  mail: Mail,
  phone: Phone,
  check: CheckCircle2,
};

export function PipelineProgress({ stages }: { stages: PipelineStage[] }) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="green">Completed</Badge>;
      case 'active':
        return <Badge variant="blue">In Progress</Badge>;
      case 'pending':
      default:
        return <Badge variant="gray">Pending</Badge>;
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {stages.map((stage) => {
        const Icon = iconMap[stage.icon];
        
        return (
          <Card key={stage.id} className="relative p-8">
            <div className="flex items-start gap-6">
              <div className={`flex-shrink-0 w-16 h-16 rounded-xl flex items-center justify-center ${
                stage.status === 'completed' ? 'bg-green-100' :
                stage.status === 'active' ? 'bg-blue-100' :
                'bg-gray-100'
              }`}>
                {stage.status === 'active' ? (
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                ) : (
                  <Icon className={`w-8 h-8 ${
                    stage.status === 'completed' ? 'text-green-600' :
                    'text-gray-400'
                  }`} />
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xl font-semibold text-gray-900">
                    {stage.name}
                  </h3>
                  {getStatusBadge(stage.status)}
                </div>
                <p className="text-base text-gray-600 leading-relaxed">
                  {stage.description}
                </p>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}

