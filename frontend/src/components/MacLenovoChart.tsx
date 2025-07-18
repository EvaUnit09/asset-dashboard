import { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { Asset } from '@/types/asset';

interface MacLenovoChartProps {
  data: Asset[];
}

export function MacLenovoChart({ data }: MacLenovoChartProps) {
  const chartData = useMemo(() => {
    // Group assets by department and count Mac vs Lenovo
    const departmentStats = data.reduce((acc, asset) => {
      // Better department handling
      let department = asset.department;
      if (!department || department.trim() === '') {
        department = 'Unassigned Department';
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

    // Convert to array and sort by total count (descending)
    return Object.values(departmentStats)
      .filter(dept => dept.total > 0) // Only show departments with Mac/Lenovo assets
      .sort((a, b) => {
        // Put "Unassigned Department" at the end
        if (a.department === 'Unassigned Department') return 1;
        if (b.department === 'Unassigned Department') return -1;
        return b.total - a.total;
      });
  }, [data]);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500">
        No Mac or Lenovo assets found
      </div>
    );
  }

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="department" 
            stroke="#64748b"
            fontSize={12}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis stroke="#64748b" fontSize={12} />
          <Tooltip 
            contentStyle={{
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '6px'
            }}
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