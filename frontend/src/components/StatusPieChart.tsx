
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import type { Asset } from "@/types/asset"

interface StatusPieChartProps {
  data: Asset[];
}

const STATUS_COLORS = {
  Active: '#10b981',
  Stock: '#3498DB',
  'Pending Rebuild': '#DC7633'
};

export const StatusPieChart = ({ data }: StatusPieChartProps) => {
  const allowedStatuses = ['Active', 'Stock', 'Pending Rebuild'];
  
  const statusData = data
    .filter(asset => allowedStatuses.includes(asset.status))
    .reduce((acc, asset) => {
      acc[asset.status] = (acc[asset.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

  const chartData = Object.entries(statusData).map(([status, count]) => ({
    name: status.charAt(0).toUpperCase() + status.slice(1),
    value: count,
    color: STATUS_COLORS[status as keyof typeof STATUS_COLORS] || '#6b7280',
  }));

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            outerRadius={100}
            innerRadius={60}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#ffffff',
              border: '1px solidrgb(230, 226, 240)',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};