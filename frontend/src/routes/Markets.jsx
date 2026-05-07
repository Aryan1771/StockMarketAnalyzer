import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ErrorMessage, LoadingCard } from "../components/State.jsx";
import { api } from "../services/api.js";

export default function Markets() {
  const [catalog, setCatalog] = useState([]);
  const [selectedId, setSelectedId] = useState("sp500");
  const [filter, setFilter] = useState("");
  const [quoteMap, setQuoteMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.catalog()
      .then((payload) => {
        const categories = payload.categories || [];
        setCatalog(categories);
        if (categories.length && !categories.some((item) => item.id === selectedId)) {
          setSelectedId(categories[0].id);
        }
      })
      .catch((exc) => setError(exc.message))
      .finally(() => setLoading(false));
  }, []);

  const selectedCategory = useMemo(
    () => catalog.find((category) => category.id === selectedId) || catalog[0],
    [catalog, selectedId]
  );

  const filteredStocks = useMemo(() => {
    const items = selectedCategory?.stocks || [];
    const query = filter.trim().toLowerCase();
    if (!query) {
      return items;
    }
    return items.filter((stock) =>
      [stock.displaySymbol, stock.symbol, stock.name, stock.sector]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(query))
    );
  }, [selectedCategory, filter]);

  useEffect(() => {
    const symbols = filteredStocks.slice(0, 15).map((stock) => stock.symbol);
    if (!symbols.length) {
      setQuoteMap({});
      return;
    }

    let cancelled = false;
    setQuoteLoading(true);
    api.compare(symbols)
      .then((payload) => {
        if (cancelled) {
          return;
        }
        const nextQuotes = {};
        for (const quote of payload.data || []) {
          nextQuotes[quote.symbol] = quote;
        }
        setQuoteMap(nextQuotes);
      })
      .catch(() => {
        if (!cancelled) {
          setQuoteMap({});
        }
      })
      .finally(() => {
        if (!cancelled) {
          setQuoteLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [filteredStocks]);

  return (
    <div className="space-y-6">
      <section>
        <p className="muted">Market directory</p>
        <h1 className="text-3xl font-bold">Browse Stocks By Index</h1>
      </section>
      <ErrorMessage message={error} />
      {loading ? (
        <div className="grid gap-4 md:grid-cols-3">
          <LoadingCard />
          <LoadingCard />
          <LoadingCard />
        </div>
      ) : (
        <>
          <div className="grid gap-4 xl:grid-cols-[320px_1fr]">
            <div className="space-y-4">
              {catalog.map((category) => (
                <button
                  key={category.id}
                  className={`card w-full text-left transition ${
                    selectedCategory?.id === category.id
                      ? "border-emerald-300 ring-2 ring-emerald-100 dark:border-emerald-700 dark:ring-emerald-950"
                      : "hover:border-slate-300 dark:hover:border-slate-700"
                  }`}
                  onClick={() => setSelectedId(category.id)}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-lg font-bold">{category.label}</p>
                      <p className="muted">{category.market}</p>
                    </div>
                    <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold dark:bg-slate-800">
                      {category.count}
                    </span>
                  </div>
                  <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{category.description}</p>
                  <p className="muted mt-3">Source: {category.source}</p>
                </button>
              ))}
            </div>

            <div className="space-y-4">
              <div className="card">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                  <div>
                    <h2 className="text-2xl font-bold">{selectedCategory?.label}</h2>
                    <p className="muted mt-1">
                      Live quote previews use the same provider stack as the rest of the app: Yahoo Finance first, with Alpha Vantage and Finnhub as fallbacks.
                    </p>
                  </div>
                  <div className="w-full lg:max-w-sm">
                    <label className="block">
                      <span className="muted">Filter symbols or companies</span>
                      <input
                        className="input mt-1"
                        value={filter}
                        onChange={(event) => setFilter(event.target.value)}
                        placeholder="Search within this category"
                      />
                    </label>
                  </div>
                </div>
              </div>

              <div className="card overflow-hidden p-0">
                <div className="grid grid-cols-[1.1fr_2fr_1.2fr_1fr_1fr] gap-3 border-b border-slate-200 px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:border-slate-800 dark:text-slate-400">
                  <div>Symbol</div>
                  <div>Company</div>
                  <div>Sector</div>
                  <div>Price</div>
                  <div>Change</div>
                </div>
                <div className="divide-y divide-slate-200 dark:divide-slate-800">
                  {filteredStocks.map((stock, index) => {
                    const quote = quoteMap[stock.symbol];
                    const positive = Number(quote?.changePercent || 0) >= 0;
                    return (
                      <Link
                        key={`${stock.symbol}-${index}`}
                        to={`/stocks/${encodeURIComponent(stock.symbol)}`}
                        className="grid grid-cols-[1.1fr_2fr_1.2fr_1fr_1fr] gap-3 px-5 py-3 text-sm transition hover:bg-slate-50 dark:hover:bg-slate-800/60"
                      >
                        <div className="font-semibold">{stock.displaySymbol || stock.symbol}</div>
                        <div>
                          <p className="font-medium">{stock.name}</p>
                          <p className="muted">{stock.exchange}</p>
                        </div>
                        <div className="text-slate-600 dark:text-slate-300">{stock.sector}</div>
                        <div className="font-medium">
                          {quote ? `${quote.currency || ""} ${Number(quote.price || 0).toFixed(2)}` : (index < 15 && quoteLoading ? "Loading..." : "--")}
                        </div>
                        <div className={positive ? "text-emerald-600" : "text-rose-600"}>
                          {quote ? `${positive ? "+" : ""}${Number(quote.changePercent || 0).toFixed(2)}%` : "--"}
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
