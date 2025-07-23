import { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { Asset } from '@/types/asset';
import type { User } from '@/types/user';

interface MacLenovoChartProps {
  data: Asset[];
  users?: User[];
}

export function MacLenovoChart({ data, users = [] }: MacLenovoChartProps) {
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

  // Helper function to get correct department for an asset
  const getAssetDepartment = (asset: Asset): string => {
    // First try asset department (for backwards compatibility)
    if (asset.department) {
      return asset.department;
    }
    
    // Then try user department (for AD-synced departments)
    if (asset.assigned_user_name) {
      const userDept = userDepartmentMap.get(asset.assigned_user_name);
      if (userDept) {
        return userDept;
      }
    }
    
    return 'Unassigned Department';
  };

  const chartData = useMemo(() => {
    // Group assets by department and count Mac vs Lenovo
    const departmentStats = data.reduce((acc, asset) => {
      const department = getAssetDepartment(asset);
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

    // Convert to array and sort by total count (descending)
    return Object.values(departmentStats)
      .filter(dept => dept.total > 0) // Only show departments with Mac/Lenovo assets
      .sort((a, b) => {
        // Put "Unassigned Department" at the end
        if (a.department === 'Unassigned Department') return 1;
        if (b.department === 'Unassigned Department') return -1;
        return b.total - a.total;
      });
  }, [data, getAssetDepartment]);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500">
        No Mac or Lenovo assets found
      </div>
    );
  }

  // Determine chart height based on number of departments
  const chartHeight = chartData.length > 8 ? 400 : 320;
  // Adjust bottom margin for department names
  const bottomMargin = chartData.length > 6 ? 100 : 80;

  return (
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
            fontSize={11}
            angle={-45}
            textAnchor="end"
            height={bottomMargin}
            interval={0}
            tick={{ fontSize: 11 }}
          />
          <YAxis stroke="#64748b" fontSize={12} />
          <Tooltip 
            contentStyle={{
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '6px'
            }}
            formatter={(value, name) => [value, name === 'Mac' ? 'Mac' : 'Lenovo']}
            labelFormatter={(label) => `Department: ${label}`}
          />
          <Legend />
          <Bar 
            dataKey="Mac" 
            name="Mac" 
            fill="#007AFF" 
            radius={[2, 2, 0, 0]}
          />
          <Bar 
            dataKey="Lenovo" 
            name="Lenovo" 
            fill="#E60012" 
            radius={[2, 2, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}