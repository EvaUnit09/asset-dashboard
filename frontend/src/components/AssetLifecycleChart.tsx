import { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { Asset } from '@/types/asset';

interface AssetLifecycleChartProps {
  data: Asset[];
}

export function AssetLifecycleChart({ data }: AssetLifecycleChartProps) {
  const chartData = useMemo(() => {
    // Group assets by creation month and manufacturer
    const monthlyData = data.reduce((acc, asset) => {
      if (!asset.created_at) return acc;
      
      const createdDate = new Date(asset.created_at);
      const monthKey = `${createdDate.getFullYear()}-${String(createdDate.getMonth() + 1).padStart(2, '0')}`;
      const manufacturer = asset.manufacturer?.toLowerCase();
      
      if (!acc[monthKey]) {
        acc[monthKey] = {
          month: monthKey,
          displayMonth: createdDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short' }),
          Mac: 0,
          Lenovo: 0,
          Other: 0,
          total: 0
        };
      }
      
      if (manufacturer?.includes('apple')) {
        acc[monthKey].Mac++;
      } else if (manufacturer?.includes('lenovo')) {
        acc[monthKey].Lenovo++;
      } else {
        acc[monthKey].Other++;
      }
      
      acc[monthKey].total++;
      
      return acc;
    }, {} as Record<string, { 
      month: string; 
      displayMonth: string; 
      Mac: number; 
      Lenovo: number; 
      Other: number; 
      total: number 
    }>);

    // Convert to array and sort by month
    const sortedData = Object.values(monthlyData)
      .sort((a, b) => a.month.localeCompare(b.month))
      .slice(-24); // Show last 24 months

    return sortedData;
  }, [data]);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500">
        No asset creation data found
      </div>
    );
  }

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="displayMonth" 
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
            labelFormatter={(label) => `Month: ${label}`}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="Mac" 
            name="Mac Assets Added"
            stroke="#007AFF" 
            strokeWidth={3}
            dot={{ fill: '#007AFF', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line 
            type="monotone" 
            dataKey="Lenovo" 
            name="Lenovo Assets Added"
            stroke="#E60012" 
            strokeWidth={3}
            dot={{ fill: '#E60012', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line 
            type="monotone" 
            dataKey="Other" 
            name="Other Assets Added"
            stroke="#6b7280" 
            strokeWidth={2}
            dot={{ fill: '#6b7280', strokeWidth: 2, r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}