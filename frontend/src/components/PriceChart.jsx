import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function PriceChart({ data }) {
  return (
    <div className="h-80 w-full">
      <ResponsiveContainer>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="price" x1="0" x2="0" y1="0" y2="1">
              <stop offset="5%" stopColor="#0f9f7f" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#0f9f7f" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#94a3b855" />
          <XAxis dataKey="date" minTickGap={28} tick={{ fontSize: 12 }} />
          <YAxis domain={["auto", "auto"]} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Area type="monotone" dataKey="close" stroke="#0f9f7f" fill="url(#price)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
