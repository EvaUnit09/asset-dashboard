import { useMemo, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { Asset } from '@/types/asset';
import type { User } from '@/types/user';

interface MacLenovoChartProps {
  data: Asset[];
  users?: User[];
}

export function MacLenovoChart({ data, users = [] }: MacLenovoChartProps) {
  const [showUnassigned, setShowUnassigned] = useState(false);
  const [viewMode, setViewMode] = useState<'count' | 'percentage'>('count');

  // Create user department mapping
  const userDepartmentMap = useMemo(() => {
    const map = new Map<string, string>();
    users.forEach(user => {
      if (user.first_name && user.last_name && user.department_name) {
        const fullName = `${user.first_name} ${user.last_name}`.trim();
        map.set(fullName, user.department_name);
      }
    });
    return map;
  }, [users]);

  const chartData = useMemo(() => {
    // Filter Mac/Lenovo assets first
    const macLenovoAssets = data.filter(asset => {
      const manufacturer = asset.manufacturer?.toLowerCase();
      return manufacturer?.includes('apple') || manufacturer?.includes('lenovo');
    });

    // Group by user's current department (more reliable than asset.department)
    const departmentStats = macLenovoAssets.reduce((acc, asset) => {
      let department = 'Unassigned';
      
      // Use assigned user's current department from users table
      if (asset.assigned_user_name) {
        const userDept = userDepartmentMap.get(asset.assigned_user_name);
        if (userDept) {
          department = userDept;
        }
      }
      
      // Skip unassigned if not showing them
      if (!showUnassigned && department === 'Unassigned') {
        return acc;
      }
      
      const manufacturer = asset.manufacturer?.toLowerCase();
      
      if (!acc[department]) {
        acc[department] = { department, Mac: 0, Lenovo: 0, total: 0 };
      }
      
      if (manufacturer?.includes('apple')) {
        acc[department].Mac++;
      } else if (manufacturer?.includes('lenovo')) {
        acc[department].Lenovo++;
      }
      
      acc[department].total = acc[department].Mac + acc[department].Lenovo;
      
      return acc;
    }, {} as Record<string, { department: string; Mac: number; Lenovo: number; total: number }>);

    // Convert to array and calculate percentages if needed
    const departmentArray = Object.values(departmentStats)
      .filter(dept => dept.total > 0)
      .sort((a, b) => {
        if (a.department === 'Unassigned') return 1;
        if (b.department === 'Unassigned') return -1;
        return b.total - a.total;
      });

    // Add percentage data if in percentage mode
    if (viewMode === 'percentage') {
      return departmentArray.map(dept => ({
        ...dept,
        Mac: Math.round((dept.Mac / dept.total) * 100),
        Lenovo: Math.round((dept.Lenovo / dept.total) * 100),
      }));
    }

    return departmentArray;
  }, [data, userDepartmentMap, showUnassigned, viewMode]);

  const totalAssets = useMemo(() => {
    return data.filter(asset => {
      const manufacturer = asset.manufacturer?.toLowerCase();
      return manufacturer?.includes('apple') || manufacturer?.includes('lenovo');
    }).length;
  }, [data]);

  const assignedCount = useMemo(() => {
    return data.filter(asset => {
      const manufacturer = asset.manufacturer?.toLowerCase();
      const isAppleOrLenovo = manufacturer?.includes('apple') || manufacturer?.includes('lenovo');
      const isAssigned = asset.assigned_user_name && userDepartmentMap.get(asset.assigned_user_name);
      return isAppleOrLenovo && isAssigned;
    }).length;
  }, [data, userDepartmentMap]);

  if (chartData.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-slate-500 space-y-2">
        <p>No {showUnassigned ? '' : 'assigned '}Mac or Lenovo assets found</p>
        {!showUnassigned && (
          <button 
            onClick={() => setShowUnassigned(true)}
            className="text-blue-600 hover:text-blue-800 text-sm underline"
          >
            Show unassigned assets
          </button>
        )}
      </div>
    );
  }

  // Dynamic sizing
  const chartHeight = chartData.length > 8 ? 420 : 340;
  const bottomMargin = chartData.length > 6 ? 120 : 100;

  return (
    <div className="w-full space-y-4">
      {/* Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-3 bg-slate-50 rounded-lg">
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showUnassigned}
              onChange={(e) => setShowUnassigned(e.target.checked)}
              className="rounded"
            />
            Show Unassigned ({totalAssets - assignedCount})
          </label>
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-600">View:</span>
            <select
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value as 'count' | 'percentage')}
              className="text-sm border rounded px-2 py-1"
            >
              <option value="count">Count</option>
              <option value="percentage">Percentage</option>
            </select>
          </div>
        </div>
        
        <div className="text-sm text-slate-600">
          Showing {assignedCount} assigned of {totalAssets} total Mac/Lenovo assets
        </div>
      </div>

      {/* Chart */}
      <div className="w-full" style={{ height: chartHeight }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: bottomMargin }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              dataKey="department" 
              stroke="#64748b"
              fontSize={10}
              angle={-45}
              textAnchor="end"
              height={bottomMargin}
              interval={0}
              tick={{ fontSize: 10 }}
            />
            <YAxis 
              stroke="#64748b" 
              fontSize={12}
              label={{ 
                value: viewMode === 'percentage' ? 'Percentage (%)' : 'Count', 
                angle: -90, 
                position: 'insideLeft' 
              }}
              domain={viewMode === 'percentage' ? [0, 100] : undefined}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '6px'
              }}
              formatter={(value, name) => [
                viewMode === 'percentage' ? `${value}%` : value, 
                name === 'Mac' ? 'Mac' : 'Lenovo'
              ]}
              labelFormatter={(label) => `Department: ${label}`}
            />
            <Legend />
            <Bar 
              dataKey="Mac" 
              name="Mac" 
              fill="#007AFF" 
              radius={[2, 2, 0, 0]}
              stackId={viewMode === 'percentage' ? 'stack' : undefined}
            />
            <Bar 
              dataKey="Lenovo" 
              name="Lenovo" 
              fill="#E60012" 
              radius={[2, 2, 0, 0]}
              stackId={viewMode === 'percentage' ? 'stack' : undefined}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}