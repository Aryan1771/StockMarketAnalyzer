import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function StockCard({ quote }) {
  const positive = Number(quote.changePercent || 0) >= 0;
  const Icon = positive ? ArrowUpRight : ArrowDownRight;
  const encodedSymbol = encodeURIComponent(quote.symbol);

  return (
    <Link to={`/stocks/${encodedSymbol}`} className="card block transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-lg font-bold">{quote.symbol}</p>
          <p className="muted line-clamp-1">{quote.name}</p>
        </div>
        <span className={`inline-flex items-center gap-1 rounded-md px-2 py-1 text-sm font-semibold ${positive ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950" : "bg-rose-100 text-rose-700 dark:bg-rose-950"}`}>
          <Icon size={16} />
          {Number(quote.changePercent || 0).toFixed(2)}%
        </span>
      </div>
      <div className="mt-5">
        <p className="text-2xl font-bold">{quote.currency || "USD"} {Number(quote.price || 0).toFixed(2)}</p>
        <p className="muted">via {quote.provider || "provider"}</p>
      </div>
    </Link>
  );
}
