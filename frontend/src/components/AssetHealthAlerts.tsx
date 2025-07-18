import { useMemo } from 'react';
import { AlertTriangle, Clock, UserX } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { Asset } from '@/types/asset';

interface AssetHealthAlertsProps {
  data: Asset[];
}

interface HealthAlert {
  id: string;
  type: 'expired' | 'aging' | 'unassigned';
  severity: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  asset: Asset;
}

export function AssetHealthAlerts({ data }: AssetHealthAlertsProps) {
  const alerts = useMemo(() => {
    const today = new Date();
    const alerts: HealthAlert[] = [];
    const fourYearsAgo = new Date(today.getFullYear() - 4, today.getMonth(), today.getDate());

    data.forEach(asset => {
      // Skip non-active assets
      if (asset.status?.toLowerCase() !== 'active') return;

      // Check for expired warranty
      if (asset.warranty_expires) {
        const warrantyDate = new Date(asset.warranty_expires);
        if (warrantyDate < today) {
          alerts.push({
            id: `expired-${asset.id}`,
            type: 'expired',
            severity: 'high',
            title: 'Expired Warranty',
            description: `${asset.asset_name} (${asset.asset_tag}) warranty expired ${warrantyDate.toLocaleDateString()}`,
            asset
          });
        }
      }

      // Check for aging assets (>4 years old)
      if (asset.created_at) {
        const createdDate = new Date(asset.created_at);
        if (createdDate < fourYearsAgo) {
          alerts.push({
            id: `aging-${asset.id}`,
            type: 'aging',
            severity: 'medium',
            title: 'Aging Asset',
            description: `${asset.asset_name} (${asset.asset_tag}) is over 4 years old`,
            asset
          });
        }
      }

      // Check for unassigned department
      if (!asset.department) {
        alerts.push({
          id: `unassigned-${asset.id}`,
          type: 'unassigned',
          severity: 'low',
          title: 'No Department',
          description: `${asset.asset_name} (${asset.asset_tag}) has no department assigned`,
          asset
        });
      }
    });

    // Sort by severity: high -> medium -> low
    const severityOrder = { high: 0, medium: 1, low: 2 };
    return alerts.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);
  }, [data]);

  const getIcon = (type: HealthAlert['type']) => {
    switch (type) {
      case 'expired':
        return <AlertTriangle className="w-4 h-4" />;
      case 'aging':
        return <Clock className="w-4 h-4" />;
      case 'unassigned':
        return <UserX className="w-4 h-4" />;
    }
  };

  const getBadgeVariant = (severity: HealthAlert['severity']) => {
    switch (severity) {
      case 'high':
        return 'destructive' as const;
      case 'medium':
        return 'default' as const;
      case 'low':
        return 'secondary' as const;
    }
  };

  if (alerts.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500">
        <div className="text-center">
          <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-green-500" />
          <p>No health alerts found</p>
          <p className="text-sm">All active assets are in good condition</p>
        </div>
      </div>
    );
  }

  const displayAlerts = alerts.slice(0, 10); // Show top 10 alerts

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-600">
          {alerts.length} alert{alerts.length !== 1 ? 's' : ''} found
        </span>
        {alerts.length > 10 && (
          <span className="text-xs text-slate-500">Showing top 10</span>
        )}
      </div>
      
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {displayAlerts.map(alert => (
          <div 
            key={alert.id}
            className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200"
          >
            <div className={`flex-shrink-0 p-1 rounded ${
              alert.severity === 'high' ? 'text-red-600 bg-red-100' :
              alert.severity === 'medium' ? 'text-orange-600 bg-orange-100' :
              'text-slate-600 bg-slate-100'
            }`}>
              {getIcon(alert.type)}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium text-sm text-slate-900">
                  {alert.title}
                </span>
                <Badge variant={getBadgeVariant(alert.severity)} className="text-xs">
                  {alert.severity}
                </Badge>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                {alert.description}
              </p>
              {alert.asset.department && (
                <p className="text-xs text-slate-500 mt-1">
                  Department: {alert.asset.department}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}