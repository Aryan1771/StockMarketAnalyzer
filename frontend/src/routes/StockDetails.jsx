import { Plus } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import PriceChart from "../components/PriceChart.jsx";
import SearchBar from "../components/SearchBar.jsx";
import { ErrorMessage, LoadingCard } from "../components/State.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../services/api.js";

const ranges = ["10d", "1mo", "3mo", "6mo", "1y"];

export default function StockDetails() {
  const { symbol = "AAPL" } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [range, setRange] = useState("1mo");
  const [quote, setQuote] = useState(null);
  const [history, setHistory] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError("");
    setMessage("");
    Promise.all([api.quote(symbol), api.history(symbol, range), api.analysis(symbol, "10d")])
      .then(([quotePayload, historyPayload, analysisPayload]) => {
        setQuote(quotePayload.data);
        setHistory(historyPayload.data || []);
        setAnalysis(analysisPayload);
      })
      .catch((exc) => setError(exc.message))
      .finally(() => setLoading(false));
  }, [symbol, range]);

  const metrics = useMemo(() => analysis?.analysis?.metrics || {}, [analysis]);

  const addToWatchlist = async () => {
    setError("");
    setMessage("");
    if (!isAuthenticated) {
      navigate("/auth");
      return;
    }

    try {
      await api.addWatchlist(symbol);
      setMessage(`${symbol.toUpperCase()} added to your watchlist.`);
    } catch (exc) {
      setError(exc.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-[1fr_340px] lg:items-end">
        <div className="space-y-3">
          <div>
            <p className="muted">Deep analysis</p>
            <h1 className="text-3xl font-bold">{symbol.toUpperCase()}</h1>
          </div>
          <SearchBar onSelect={(nextSymbol) => navigate(`/stocks/${nextSymbol}`)} />
        </div>
        <div className="flex justify-start lg:justify-end">
          <button className="btn" onClick={addToWatchlist}><Plus size={18} /> Add to watchlist</button>
        </div>
      </div>
      <ErrorMessage message={error} />
      {message && <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950">{message}</div>}
      {loading ? <LoadingCard lines={5} /> : quote && (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <Metric label="Price" value={`${quote.currency} ${Number(quote.price).toFixed(2)}`} />
            <Metric label="Change" value={`${Number(quote.changePercent).toFixed(2)}%`} />
            <Metric label="Moving Avg" value={metrics.moving_average?.toFixed?.(2) || "n/a"} />
            <Metric label="Trend" value={analysis?.trend?.label || "neutral"} />
          </div>
          <div className="card">
            <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 className="text-xl font-bold">{quote.name}</h2>
                <p className="muted">Provider: {quote.provider}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                {ranges.map((item) => (
                  <button key={item} className={`rounded-md px-3 py-2 text-sm ${range === item ? "bg-accent text-white" : "bg-slate-100 dark:bg-slate-800"}`} onClick={() => setRange(item)}>
                    {item}
                  </button>
                ))}
              </div>
            </div>
            <PriceChart data={history} />
          </div>
        </>
      )}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="card">
      <p className="muted">{label}</p>
      <p className="mt-2 text-2xl font-bold capitalize">{value}</p>
    </div>
  );
}
