import { Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ErrorMessage, LoadingCard } from "../components/State.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import StockCard from "../components/StockCard.jsx";
import { api } from "../services/api.js";

export default function Watchlist() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [payload, setPayload] = useState({ symbols: [], quotes: [] });
  const [symbol, setSymbol] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    setError("");
    api.watchlist()
      .then(setPayload)
      .catch((exc) => setError(exc.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    load();
  }, [isAuthenticated]);

  if (authLoading) {
    return <LoadingCard />;
  }

  if (!isAuthenticated) {
    return (
      <div className="space-y-6">
        <section>
          <p className="muted">Personal workspace</p>
          <h1 className="text-3xl font-bold">Watchlist</h1>
        </section>
        <div className="card space-y-3">
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Sign in to keep a personal watchlist that follows your account across sessions.
          </p>
          <Link className="btn inline-flex w-full justify-center sm:w-auto" to="/auth">Login or Register</Link>
        </div>
      </div>
    );
  }

  const add = async (event) => {
    event.preventDefault();
    if (!symbol.trim()) return;
    await api.addWatchlist(symbol);
    setSymbol("");
    load();
  };

  const remove = async (item) => {
    await api.removeWatchlist(item);
    load();
  };

  return (
    <div className="space-y-6">
      <section>
        <p className="muted">Your tracked symbols</p>
        <h1 className="text-3xl font-bold">Watchlist</h1>
      </section>
      <ErrorMessage message={error} />
      <form className="card flex flex-col gap-3 sm:flex-row" onSubmit={add}>
        <input className="input" value={symbol} onChange={(event) => setSymbol(event.target.value)} placeholder="Add symbol, e.g. NVDA" />
        <button className="btn">Add</button>
      </form>
      {loading ? <LoadingCard /> : (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {payload.quotes.map((quote) => <StockCard key={quote.symbol} quote={quote} />)}
          </div>
          <div className="card">
            <h2 className="mb-3 text-xl font-bold">Manage Symbols</h2>
            <div className="flex flex-wrap gap-2">
              {payload.symbols.map((item) => (
                <button key={item} className="inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 dark:border-slate-700" onClick={() => remove(item)}>
                  {item}<Trash2 size={15} />
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
