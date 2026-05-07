import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ErrorMessage, LoadingCard } from "../components/State.jsx";
import { api } from "../services/api.js";

const PAGE_SIZE = 20;
const QUOTE_BUFFER = 5;

export default function Markets() {
  const [catalog, setCatalog] = useState([]);
  const [selectedId, setSelectedId] = useState("sp500");
  const [filter, setFilter] = useState("");
  const [quoteMap, setQuoteMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [error, setError] = useState("");
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const [activeRange, setActiveRange] = useState({ start: 0, end: PAGE_SIZE - 1 });
  const loadMoreRef = useRef(null);
  const rowRefs = useRef(new Map());
  const visibleIndicesRef = useRef(new Set());
  const quoteMapRef = useRef({});
  const requestedSymbolsRef = useRef(new Set());

  useEffect(() => {
    quoteMapRef.current = quoteMap;
  }, [quoteMap]);

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

  const visibleStocks = useMemo(
    () => filteredStocks.slice(0, visibleCount),
    [filteredStocks, visibleCount]
  );

  useEffect(() => {
    setVisibleCount(PAGE_SIZE);
    setQuoteMap({});
    quoteMapRef.current = {};
    setError("");
    visibleIndicesRef.current = new Set();
    requestedSymbolsRef.current = new Set();
    setActiveRange({ start: 0, end: PAGE_SIZE - 1 });
  }, [selectedId, filter]);

  useEffect(() => {
    const node = loadMoreRef.current;
    if (!node || visibleCount >= filteredStocks.length) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          setVisibleCount((current) => Math.min(current + PAGE_SIZE, filteredStocks.length));
        }
      },
      { rootMargin: "300px 0px" }
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [filteredStocks.length, visibleCount]);

  useEffect(() => {
    if (!visibleStocks.length) {
      setQuoteMap({});
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          const index = Number(entry.target.getAttribute("data-index"));
          if (Number.isNaN(index)) {
            continue;
          }
          if (entry.isIntersecting) {
            visibleIndicesRef.current.add(index);
          } else {
            visibleIndicesRef.current.delete(index);
          }
        }

        const indices = [...visibleIndicesRef.current].sort((a, b) => a - b);
        if (indices.length) {
          setActiveRange({ start: indices[0], end: indices[indices.length - 1] });
        }
      },
      {
        threshold: 0.2,
        rootMargin: "120px 0px",
      }
    );

    for (const [index, node] of rowRefs.current.entries()) {
      if (index < visibleStocks.length && node) {
        observer.observe(node);
      }
    }

    return () => observer.disconnect();
  }, [visibleStocks]);

  useEffect(() => {
    if (!visibleStocks.length) {
      setQuoteMap({});
      quoteMapRef.current = {};
      requestedSymbolsRef.current = new Set();
      return;
    }

    const bufferStart = Math.max(0, activeRange.start - QUOTE_BUFFER);
    const bufferEnd = Math.min(visibleStocks.length - 1, activeRange.end + QUOTE_BUFFER);
    const windowStocks = visibleStocks.slice(bufferStart, bufferEnd + 1);
    const windowSymbols = new Set(windowStocks.map((stock) => stock.symbol).filter(Boolean));
    const previousWindowQuotes = quoteMapRef.current;

    setQuoteMap((current) => {
      const next = {};
      for (const [symbol, quote] of Object.entries(current)) {
        if (windowSymbols.has(symbol)) {
          next[symbol] = quote;
        }
      }
      const sameSize = Object.keys(next).length === Object.keys(current).length;
      if (sameSize && Object.keys(current).every((symbol) => next[symbol] === current[symbol])) {
        return current;
      }
      quoteMapRef.current = next;
      return next;
    });

    requestedSymbolsRef.current = new Set(
      [...requestedSymbolsRef.current].filter((symbol) => windowSymbols.has(symbol))
    );

    const symbolsToFetch = windowStocks
      .map((stock) => stock.symbol)
      .filter((symbol) =>
        symbol &&
        !previousWindowQuotes[symbol] &&
        !requestedSymbolsRef.current.has(symbol)
      );

    if (!symbolsToFetch.length) {
      return;
    }

    let cancelled = false;
    symbolsToFetch.forEach((symbol) => requestedSymbolsRef.current.add(symbol));
    setQuoteLoading(true);
    api.compare(symbolsToFetch)
      .then((payload) => {
        if (cancelled) {
          return;
        }
        const nextQuotes = {};
        for (const quote of payload.data || []) {
          if (windowSymbols.has(quote.symbol)) {
            nextQuotes[quote.symbol] = quote;
          }
        }
        setQuoteMap((current) => {
          const trimmed = {};
          for (const [symbol, quote] of Object.entries(current)) {
            if (windowSymbols.has(symbol)) {
              trimmed[symbol] = quote;
            }
          }
          const merged = { ...trimmed, ...nextQuotes };
          quoteMapRef.current = merged;
          return merged;
        });
        setError("");
      })
      .catch(() => {
        if (!cancelled) {
          setError("Some live market quotes could not be loaded right now.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          symbolsToFetch.forEach((symbol) => requestedSymbolsRef.current.delete(symbol));
          setQuoteLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [activeRange, visibleStocks]);

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
                      Live quote previews stay focused on the rows around your viewport: what you can see now, plus a small buffer above and below for smoother scrolling.
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
                  {visibleStocks.map((stock, index) => {
                    const quote = quoteMap[stock.symbol];
                    const positive = Number(quote?.changePercent || 0) >= 0;
                    return (
                      <Link
                        key={`${stock.symbol}-${index}`}
                        to={`/stocks/${encodeURIComponent(stock.symbol)}`}
                        data-index={index}
                        ref={(node) => {
                          if (node) {
                            rowRefs.current.set(index, node);
                          } else {
                            rowRefs.current.delete(index);
                          }
                        }}
                        className="grid grid-cols-[1.1fr_2fr_1.2fr_1fr_1fr] gap-3 px-5 py-3 text-sm transition hover:bg-slate-50 dark:hover:bg-slate-800/60"
                      >
                        <div className="font-semibold">{stock.displaySymbol || stock.symbol}</div>
                        <div>
                          <p className="font-medium">{stock.name}</p>
                          <p className="muted">{stock.exchange}</p>
                        </div>
                        <div className="text-slate-600 dark:text-slate-300">{stock.sector}</div>
                        <div className="font-medium">
                          {quote ? `${quote.currency || ""} ${Number(quote.price || 0).toFixed(2)}` : (quoteLoading ? "Loading..." : "--")}
                        </div>
                        <div className={positive ? "text-emerald-600" : "text-rose-600"}>
                          {quote ? `${positive ? "+" : ""}${Number(quote.changePercent || 0).toFixed(2)}%` : "--"}
                        </div>
                      </Link>
                    );
                  })}
                </div>
                {visibleCount < filteredStocks.length && (
                  <div
                    ref={loadMoreRef}
                    className="border-t border-slate-200 px-5 py-4 text-center text-sm text-slate-500 dark:border-slate-800 dark:text-slate-400"
                  >
                    Loading more symbols...
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
