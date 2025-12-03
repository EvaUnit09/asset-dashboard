import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Combobox } from '@/components/ui/combobox';
import { ArrowLeft, Save } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import type { Asset } from '@/types/asset';

export default function AssetEdit() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    // Fetch asset data
    const { data: asset, isLoading } = useQuery({
        queryKey: ['asset', id],
        queryFn: async () => {
            const response = await api.get(`/assets/${id}`);
            return response.data;
        },
    });
    // Fetch all assets for dropdown options
    const { data: allAssets = [] } = useQuery({
        queryKey: ['assets'],
        queryFn: async () => {
            const response = await api.get('/assets');
            return response.data;
        },
    });

    // Extract unique values for dropdowns
    const models = useMemo(() => 
        [...new Set(allAssets.map((a: Asset) => a.model))].filter((m): m is string => m != null).sort(), 
        [allAssets]
    );

    const manufacturers = useMemo(() => 
        [...new Set(allAssets.map((a: Asset) => a.manufacturer))].filter((m): m is string => m != null).sort(), 
        [allAssets]
    );

    const locations = useMemo(() => 
        [...new Set(allAssets.map((a: Asset) => a.location))].filter((l): l is string => l != null).sort(), 
        [allAssets]
    );

    const companies = useMemo(() => 
        [...new Set(allAssets.map((a: Asset) => a.company))].filter((c): c is string => c != null).sort(), 
        [allAssets]
    );

    const categories = useMemo(() => 
        [...new Set(allAssets.map((a: Asset) => a.category))].filter((c): c is string => c != null).sort(), 
        [allAssets]
    );
        
        // Form State
        const [formData, setFormData] = useState<Partial<Asset>>({});

        // Populate form when asset loads
        useEffect(() => {
            if (asset) {
                setFormData(asset);
            }
        }, [asset]);

    // Update mutation

    const updateMutation = useMutation({
        mutationFn: async (data: Partial<Asset>) => {
            return api.put(`/assets/${id}`, data);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['assets'] });
            navigate('/assets');
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        updateMutation.mutate(formData);
    };
    const handleChange = (field: keyof Asset, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    if (isLoading) return <div className='p-6'>Loading...</div>;

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
          <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
              <Button 
                variant="outline" 
                onClick={() => navigate('/assets')}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Back
              </Button>
              <h1 className="text-3xl font-bold text-slate-900">
                Edit Asset: {asset?.asset_name}
              </h1>
            </div>
    
            {/* Form */}
            <Card>
              <CardHeader>
                <CardTitle>Asset Details</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Asset Name */}
                    <div>
                      <label className="text-sm font-medium">Asset Name</label>
                      <Input
                        value={formData.asset_name || ''}
                        onChange={(e) => handleChange('asset_name', e.target.value)}
                      />
                    </div>
    
                    {/* Asset Tag (Read-only) */}
                    <div>
                      <label className="text-sm font-medium">Asset Tag</label>
                      <Input value={formData.asset_tag || ''} disabled />
                    </div>
    
                    {/* Model */}
                    <div>
                      <label className="text-sm font-medium">Model</label>
                      <Combobox
                        value={formData.model || ''}
                        onValueChange={(value) => handleChange('model', value)}
                        options={models}
                        placeholder="Select or type model..."
                      />
                    </div>
    
                    {/* Category */}
                    <div>
                      <label className="text-sm font-medium">Category</label>
                      <Combobox
                        value={formData.category || ''}
                        onValueChange={(value) => handleChange('category', value)}
                        options={categories}
                        placeholder="Select or type category..."
                      />
                    </div>
    
                    {/* Manufacturer */}
                    <div>
                      <label className="text-sm font-medium">Manufacturer</label>
                      <Combobox
                        value={formData.manufacturer || ''}
                        onValueChange={(value) => handleChange('manufacturer', value)}
                        options={manufacturers}
                        placeholder="Select or type manufacturer..."
                      />
                    </div>
    
                    {/* Serial */}
                    <div>
                      <label className="text-sm font-medium">Serial Number</label>
                      <Input
                        value={formData.serial || ''}
                        onChange={(e) => handleChange('serial', e.target.value)}
                      />
                    </div>
    
                    {/* Status */}
                    <div>
                      <label className="text-sm font-medium">Status</label>
                      <select
                        value={formData.status || ''}
                        onChange={(e) => handleChange('status', e.target.value)}
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      >
                        <option value="Active">Active</option>
                        <option value="Stock">Stock</option>
                        <option value="Pending Rebuild">Pending Rebuild</option>
                        <option value="Disposed">Disposed</option>
                      </select>
                    </div>
    
                    {/* Company */}
                    <div>
                      <label className="text-sm font-medium">Company</label>
                      <Combobox
                        value={formData.company || ''}
                        onValueChange={(value) => handleChange('company', value)}
                        options={companies}
                        placeholder="Select or type company..."
                      />
                    </div>
    
                    {/* Location */}
                    <div>
                      <label className="text-sm font-medium">Location</label>
                      <Combobox
                        value={formData.location || ''}
                        onValueChange={(value) => handleChange('location', value)}
                        options={locations}
                        placeholder="Select or type location..."
                      />
                    </div>
    
                    {/* Department */}
                    <div>
                      <label className="text-sm font-medium">Department</label>
                      <Input
                        value={formData.department || ''}
                        onChange={(e) => handleChange('department', e.target.value)}
                      />
                    </div>
    
                    {/* Assigned User - TODO: Autocomplete */}
                    <div>
                      <label className="text-sm font-medium">Assigned User</label>
                      <Input
                        value={formData.assigned_user_name || ''}
                        onChange={(e) => handleChange('assigned_user_name', e.target.value)}
                        placeholder="First Last"
                      />
                    </div>
    
                    {/* Warranty */}
                    <div>
                      <label className="text-sm font-medium">Warranty (months)</label>
                      <Input
                        value={formData.warranty || ''}
                        onChange={(e) => handleChange('warranty', e.target.value)}
                      />
                    </div>
                  </div>
    
                  {/* Action Buttons */}
                  <div className="flex gap-2 justify-end pt-4">
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={() => navigate('/assets')}
                    >
                      Cancel
                    </Button>
                    <Button 
                      type="submit" 
                      disabled={updateMutation.isPending}
                      className="flex items-center gap-2"
                    >
                      <Save className="w-4 h-4" />
                      {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      );
}