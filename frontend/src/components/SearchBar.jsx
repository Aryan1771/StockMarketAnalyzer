import { Search } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../services/api.js";

export default function SearchBar({ onSelect }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    const handle = setTimeout(() => {
      setLoading(true);
      api.search(query)
        .then((payload) => setResults(payload.data || []))
        .catch(() => setResults([]))
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(handle);
  }, [query]);

  const choose = (symbol) => {
    setQuery("");
    setResults([]);
    onSelect(symbol);
  };

  const submit = (event) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) {
      return;
    }
    const firstResult = results[0]?.symbol;
    choose(firstResult || trimmed.toUpperCase());
  };

  return (
    <form className="relative w-full max-w-xl" onSubmit={submit}>
      <Search className="absolute left-3 top-2.5 text-slate-400" size={18} />
      <input
        className="input pl-10 pr-24"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search ticker, company, or symbol"
      />
      <button type="submit" className="absolute right-1.5 top-1.5 rounded-md bg-accent px-3 py-1.5 text-sm font-semibold text-white transition hover:bg-emerald-700">
        Search
      </button>
      {(results.length > 0 || loading) && (
        <div className="absolute mt-2 w-full overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg dark:border-slate-800 dark:bg-slate-900">
          {loading && <div className="p-3 text-sm text-slate-500">Searching...</div>}
          {results.map((item) => (
            <button type="button" key={item.symbol} className="block w-full px-4 py-3 text-left hover:bg-slate-100 dark:hover:bg-slate-800" onClick={() => choose(item.symbol)}>
              <span className="font-semibold">{item.symbol}</span>
              <span className="ml-2 text-sm text-slate-500">{item.name}</span>
            </button>
          ))}
        </div>
      )}
    </form>
  );
}
