import { useEffect, useState } from "react";
import { ErrorMessage, LoadingCard } from "../components/State.jsx";
import { api } from "../services/api.js";

export default function News() {
  const [symbol, setSymbol] = useState("");
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    setError("");
    api.news(symbol ? { symbol } : { category: "general" })
      .then((payload) => setArticles(payload.data || []))
      .catch((exc) => setError(exc.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  return (
    <div className="space-y-6">
      <section>
        <p className="muted">Market headlines</p>
        <h1 className="text-3xl font-bold">News</h1>
      </section>
      <form className="card flex flex-col gap-3 sm:flex-row" onSubmit={(event) => { event.preventDefault(); load(); }}>
        <input className="input" value={symbol} onChange={(event) => setSymbol(event.target.value)} placeholder="Optional symbol filter" />
        <button className="btn">Refresh</button>
      </form>
      <ErrorMessage message={error} />
      {loading ? <LoadingCard lines={5} /> : (
        <div className="grid gap-4 lg:grid-cols-2">
          {articles.map((article) => (
            <a
              key={article.id}
              href={article.url}
              target="_blank"
              rel="noreferrer"
              className="card transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-lg font-bold">{article.title}</p>
                  <p className="muted mt-1">{article.source}</p>
                </div>
                <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold capitalize dark:bg-slate-800">{article.sentiment}</span>
              </div>
              <p className="mt-4 text-sm text-slate-600 dark:text-slate-300">{article.summary}</p>
              <div className="mt-4 flex items-center justify-between gap-3 text-xs">
                <span className="rounded-md bg-slate-100 px-2 py-1 font-medium uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                  via {article.provider || "source"}
                </span>
                <span className="muted">
                  {article.source}
                </span>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
