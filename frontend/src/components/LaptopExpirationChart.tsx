import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList } from 'recharts';
import type { Asset } from '@/types/asset';
import { useMemo } from 'react';



interface LaptopExpirationChartProps {
    data: Asset[];
}

export const LaptopExpirationChart = ({ data }: LaptopExpirationChartProps) => {
  // 1. Filter laptops
  const laptops = useMemo(
    () => data.filter(asset => asset.category === 'laptop'),
    [data]
  );

  // 2. Quarter helper
  const getExpirationQuarter = (isoDate: string) => {
    const d       = new Date(isoDate);
    const year    = d.getFullYear();
    const quarter = Math.ceil((d.getMonth() + 1) / 3); // 1-4
    return `Qtr${quarter} ${year}`;
  };

  // 3. Aggregate counts
  const expirationData: Record<string, Record<string, number>> = {};
  laptops.forEach(laptop => {
    const quarter   = getExpirationQuarter(laptop.warranty_expires);
    const modelKey  = `${laptop.manufacturer} - ${laptop.model}`;

    expirationData[quarter] ??= {};
    expirationData[quarter][modelKey] =
      (expirationData[quarter][modelKey] ?? 0) + 1;
  });

  // 4. Convert to array + sort
  const chartData = Object.entries(expirationData)
    .map(([quarter, models]) => ({ quarter, ...models }))
    .sort((a, b) => {
      const [qA, yA] = a.quarter.split(' ');
      const [qB, yB] = b.quarter.split(' ');
      return Number(yA) - Number(yB) || Number(qA.slice(3)) - Number(qB.slice(3));
    });

  // 5. Unique model list for <Bar>s
  const allModels = [...new Set(laptops.map(l => `${l.manufacturer} - ${l.model}`))];

  /* … render (kept the same) … */


  
  // Color palette for different models
  const colors = [
    '#3b82f6', // Blue
    '#f59e0b', // Orange  
    '#8b5cf6', // Purple
    '#10b981', // Green
    '#ef4444', // Red
    '#06b6d4', // Cyan
    '#f97316', // Orange-alt
    '#84cc16', // Lime
  ];
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis 
            dataKey="quarter" 
            stroke="#64748b"
            fontSize={12}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis 
            stroke="#64748b"
            fontSize={12}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
            }}
          />
          <Legend />
          {allModels.map((model, index) => (
            <Bar 
              key={model}
              dataKey={model} 
              fill={colors[index % colors.length]}
              name={model}
              radius={[2, 2, 0, 0]}
            >
                {/* one label per bar on top */}
                <LabelList
                dataKey={model}
                position="top"
                formatter={(label: React.ReactNode) =>
                    typeof label === 'number' && label > 0 ? label.toString() : ''
                }
                fontSize={12}
                offset={4}
                fontWeight="bold"
                
            />
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
