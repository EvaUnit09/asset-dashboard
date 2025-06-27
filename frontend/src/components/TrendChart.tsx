import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useMemo } from "react";
import type { Asset } from "@/types/asset";

interface Props {
  data: Asset[];
}

/** normalise DB status strings → bucket names used in the chart */
const bucket = (raw?: string | null) => {
  const s = (raw ?? "").toLowerCase();
  if (s.includes("pending") && s.includes("rebuild")) return "pending";
  if (s.includes("active"))                           return "active";
  if (s.includes("stock"))                            return "stock";
  return "other";
};

export const TrendChart = ({ data }: Props) => {
  /* 1 — roll up rows into   yyyy-mm → {active, pending, stock} */
  const monthly = useMemo(() => {
    const map: Record<
      string,
      { monthLabel: string; active: number; pending: number; stock: number }
    > = {};

    data.forEach(a => {
      const d = new Date(a.created_at ?? "");
      if (Number.isNaN(d.getTime())) return; // skip rows without date
      const key   = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`; // "2025-03"
      const label = d.toLocaleDateString(undefined, { month: "short", year: "numeric" }); // "Mar 2025"

      if (!map[key]) map[key] = { monthLabel: label, active: 0, pending: 0, stock: 0 };

      switch (bucket(a.status)) {
        case "active":  map[key].active  += 1; break;
        case "pending": map[key].pending += 1; break;
        case "stock":   map[key].stock   += 1; break;
      }
    });

    /* sort chronologically for Recharts */
    return Object
      .entries(map)
      .sort(([k1], [k2]) => k1.localeCompare(k2))
      .map(([, v]) => v);
  }, [data]);

  /* 2 — nothing to show yet? */
  if (!monthly.length) return <p className="p-4">No trend data found.</p>;

  /* 3 — chart */
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={monthly} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="monthLabel" stroke="#64748b" fontSize={12} />
          <YAxis stroke="#64748b" fontSize={12} allowDecimals={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#ffffff",
              border: "1px solid #e2e8f0",
              borderRadius: "8px",
              boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
            }}
          />

          <Area
            type="monotone"
            dataKey="stock"
            stackId="1"
            stroke="#8b5cf6"
            fill="#8b5cf6"
            fillOpacity={0.9}
          />
          <Area
            type="monotone"
            dataKey="pending"
            stackId="1"
            stroke="#f59e0b"
            fill="#f59e0b"
            fillOpacity={0.9}
          />
          <Area
            type="monotone"
            dataKey="active"
            stackId="1"
            stroke="#10b981"
            fill="#10b981"
            fillOpacity={0.9}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

