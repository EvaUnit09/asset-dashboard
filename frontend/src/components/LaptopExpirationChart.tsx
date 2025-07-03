import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LabelList,
} from 'recharts';
import type { Asset } from '@/types/asset';
import { useMemo } from 'react';

/* ---------- constants ------------------------------------------------- */
const TARGET_MODELS = [
  'Apple',
  'Lenovo - X13 Gen 1',
  'Lenovo - X13 Gen 2',
  'Lenovo - X390',
] as const;
type TargetKey = (typeof TARGET_MODELS)[number];

const COLOR_MAP: Record<TargetKey, string> = {
  Apple:               '#3b82f6', // blue
  'Lenovo - X13 Gen 1':'#f97316', // orange
  'Lenovo - X13 Gen 2':'#9ca3af', // grey
  'Lenovo - X390':     '#fbbf24', // yellow
} as const;

/* ---------- helper ---------------------------------------------------- */
const getExpirationQuarter = (iso: string) => {
  const d = new Date(iso);
  return `Qtr${Math.ceil((d.getMonth() + 1) / 3)} ${d.getFullYear()}`;
};

/* ---------- component ------------------------------------------------- */
interface Props {
  data: Asset[];
}

export const LaptopExpirationChart = ({ data }: Props) => {
  /* 1️⃣ filter + aggregate only once per `data` change */
  const chartData = useMemo(() => {
    const expiration: Record<string, Partial<Record<TargetKey, number>>> = {};

    data
      .filter(a =>
        a.category === 'laptop' &&
        (
          a.manufacturer === 'Apple' ||
          (a.manufacturer === 'Lenovo' &&
           ['X13 Gen 1', 'X13 Gen 2', 'X390'].includes(a.model))
        ),
      )
      .forEach(l => {
        const quarter  = getExpirationQuarter(l.warranty_expires);
        const key: TargetKey =
          l.manufacturer === 'Apple' ? 'Apple' : (`Lenovo - ${l.model}` as TargetKey);

        expiration[quarter] ??= {};
        expiration[quarter]![key] = (expiration[quarter]![key] ?? 0) + 1;
      });

    /* transform → array + chronological sort */
    return Object.entries(expiration)
      .map(([quarter, models]) => ({ quarter, ...models }))
      .sort((a, b) => {
        const [qA, yA] = a.quarter.split(' ');
        const [qB, yB] = b.quarter.split(' ');
        return Number(yA) - Number(yB) ||
               Number(qA.slice(3)) - Number(qB.slice(3));
      });
  }, [data]);

  /* 2️⃣ render */
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />

          <XAxis
            dataKey="quarter"
            stroke="#64748b"
            fontSize={12}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis stroke="#64748b" fontSize={12} />

          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            }}
          />
          <Legend />

          {TARGET_MODELS.map(key => (
            <Bar key={key} dataKey={key} fill={COLOR_MAP[key]} radius={[2, 2, 0, 0]}>
              <LabelList
                dataKey={key}
                position="top"
                formatter={(label: React.ReactNode) => {
                  if (typeof label === 'number' && label > 0) {
                    return label.toString();
                  }
                  return '';
                }}
                fontSize={12}
                offset={4}
              />
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

