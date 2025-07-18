import { useEffect, useState } from 'react';
import { Package, AlertTriangle, Clock } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api';
import type { User } from '@/types/user';
import type { Asset } from '@/types/asset';

interface UserAssetsModalProps {
  user: User | null;
  isOpen: boolean;
  onClose: () => void;
}

export function UserAssetsModal({ user, isOpen, onClose }: UserAssetsModalProps) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && user) {
      fetchUserAssets();
    }
  }, [isOpen, user]);

  const fetchUserAssets = async () => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get<Asset[]>(`/users/${user.id}/assets`);
      setAssets(response.data);
    } catch (err) {
      setError('Failed to load user assets');
      console.error('Error fetching user assets:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower === 'active') {
      return <Badge className="bg-green-100 text-green-800">Active</Badge>;
    } else if (statusLower === 'pending rebuild') {
      return <Badge className="bg-orange-100 text-orange-800">Pending Rebuild</Badge>;
    } else if (statusLower === 'stock') {
      return <Badge className="bg-blue-100 text-blue-800">Stock</Badge>;
    } else {
      return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const isWarrantyExpired = (warrantyExpires: string | null) => {
    if (!warrantyExpires) return false;
    return new Date(warrantyExpires) < new Date();
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  if (!user) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <Package className="w-5 h-5 text-blue-600" />
            Assets for {user.first_name} {user.last_name}
          </DialogTitle>
          <div className="text-sm text-slate-600">
            {user.email} • {user.department_name || 'No Department'}
          </div>
        </DialogHeader>

        <div className="space-y-4">
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <div className="text-slate-600">Loading assets...</div>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
              <AlertTriangle className="w-4 h-4" />
              {error}
            </div>
          )}

          {!isLoading && !error && assets.length === 0 && (
            <div className="text-center py-8 text-slate-500">
              <Package className="w-12 h-12 mx-auto mb-3 text-slate-300" />
              <p>No assets assigned to this user</p>
            </div>
          )}

          {!isLoading && assets.length > 0 && (
            <div className="space-y-3">
              <div className="text-sm font-medium text-slate-600 mb-4">
                {assets.length} asset{assets.length !== 1 ? 's' : ''} assigned
              </div>
              
              {assets.map(asset => (
                <div 
                  key={asset.id}
                  className="border border-slate-200 rounded-lg p-4 hover:bg-slate-50"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-medium text-slate-900">
                        {asset.asset_name || 'Unnamed Asset'}
                      </h3>
                      <div className="text-sm text-slate-600">
                        {asset.asset_tag} • {asset.model || 'Unknown Model'}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(asset.status)}
                      {isWarrantyExpired(asset.warranty_expires) && (
                        <Badge variant="destructive" className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          Warranty Expired
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-slate-500">Manufacturer:</span>
                      <div className="font-medium">{asset.manufacturer || 'N/A'}</div>
                    </div>
                    <div>
                      <span className="text-slate-500">Serial:</span>
                      <div className="font-medium font-mono text-xs">
                        {asset.serial || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-500">Category:</span>
                      <div className="font-medium">{asset.category || 'N/A'}</div>
                    </div>
                    <div>
                      <span className="text-slate-500">Warranty Expires:</span>
                      <div className={`font-medium ${
                        isWarrantyExpired(asset.warranty_expires) ? 'text-red-600' : ''
                      }`}>
                        {formatDate(asset.warranty_expires)}
                      </div>
                    </div>
                  </div>

                  {asset.location && (
                    <div className="mt-3 pt-3 border-t border-slate-100">
                      <span className="text-slate-500 text-sm">Location:</span>
                      <div className="font-medium text-sm">{asset.location}</div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}