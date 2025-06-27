
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import type { Asset } from "@/types/asset"

interface StatusPieChartProps {
  data: Asset[];
}

const STATUS_COLORS = {
  Active: '#10b981',
  Damaged: '#641E16',
  Stock: '#3498DB',
  Disposed: '#ef4444',
  'Pending Rebuild': '#DC7633',
  'Pre-Disposal': '#808b96',
  'Allocated': '#2c3e50',
  Broken: '#808b96',
  Lost: '#808b96',
  Repair: '#808b96',
  Stolen: '#808b96'
};

export const StatusPieChart = ({ data }: StatusPieChartProps) => {
  const statusData = data.reduce((acc, asset) => {
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
              border: '1px solid #e2e8f0',
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