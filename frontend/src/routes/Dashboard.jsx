import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import PriceChart from "../components/PriceChart.jsx";
import { ErrorMessage, LoadingCard } from "../components/State.jsx";
import StockCard from "../components/StockCard.jsx";
import { api } from "../services/api.js";

const REGION_ORDER = ["india", "us"];

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [activeRegion, setActiveRegion] = useState("india");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.dashboard()
      .then((payload) => setDashboard(payload))
      .catch((exc) => setError(exc.message))
      .finally(() => setLoading(false));
  }, []);

  const currentRegion = useMemo(() => dashboard?.regions?.[activeRegion], [dashboard, activeRegion]);

  return (
    <div className="space-y-6">
      <section>
        <p className="muted">Market command center</p>
        <h1 className="text-3xl font-bold">Dashboard</h1>
      </section>
      <ErrorMessage message={error} />
      {loading ? (
        <div className="grid gap-4 md:grid-cols-3"><LoadingCard /><LoadingCard /><LoadingCard /></div>
      ) : dashboard && currentRegion ? (
        <>
          <div className="card">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <h2 className="text-2xl font-bold">Two-Market Watch</h2>
                <p className="muted mt-1">
                  Track market pulse, core leaders, growth leaders, defensive names, and technical risk markers across India and the US.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                {REGION_ORDER.map((regionId) => {
                  const region = dashboard.regions?.[regionId];
                  if (!region) {
                    return null;
                  }
                  const active = activeRegion === regionId;
                  return (
                    <button
                      key={regionId}
                      className={`rounded-md px-4 py-2 text-sm font-semibold transition ${active ? "bg-accent text-white" : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200"}`}
                      onClick={() => setActiveRegion(regionId)}
                    >
                      {region.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <Section title={`${currentRegion.label} Market Pulse`} subtitle="Index and sector trend indicators">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {currentRegion.pulse.map((quote) => <StockCard key={quote.symbol} quote={quote} />)}
            </div>
          </Section>

          <div className="grid gap-4 xl:grid-cols-[1.35fr_1fr]">
            <div className="card">
              <div className="mb-4">
                <h2 className="text-xl font-bold">{currentRegion.chart.label} 1M Trend</h2>
                <p className="muted">Historical close prices via {currentRegion.chart.provider || "provider"}</p>
              </div>
              <PriceChart data={currentRegion.chart.data || []} />
            </div>
            <div className="card">
              <h2 className="mb-4 text-xl font-bold">Market News</h2>
              <div className="space-y-4">
                {(dashboard.news || []).map((item) => (
                  <a
                    key={item.id}
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="block rounded-md border border-slate-200 p-3 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800"
                  >
                    <p className="font-semibold">{item.title}</p>
                    <p className="muted">{item.source} · {item.sentiment}</p>
                  </a>
                ))}
              </div>
            </div>
          </div>

          <Section title="Core Leaders" subtitle="Large-cap stability anchors">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              {currentRegion.core.map((quote) => <StockCard key={quote.symbol} quote={quote} />)}
            </div>
          </Section>

          <Section title="Growth Leaders" subtitle="Higher-beta names tied to secular trends">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              {currentRegion.growth.map((quote) => <StockCard key={quote.symbol} quote={quote} />)}
            </div>
          </Section>

          <Section title="Defensive Leaders" subtitle="Cash-flow and downside-balance names">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-2">
              {currentRegion.defensive.map((quote) => <StockCard key={quote.symbol} quote={quote} />)}
            </div>
          </Section>

          <div className="grid gap-4 lg:grid-cols-2">
            <TechnicalTable
              title="Top Gainers & Losers"
              gainers={currentRegion.technicals.topGainers || []}
              losers={currentRegion.technicals.topLosers || []}
            />
            <TechnicalGrid
              title="Trend & Risk Markers"
              above200={currentRegion.technicals.above200Sma || []}
              rsiWatch={currentRegion.technicals.rsiWatch || []}
            />
          </div>
        </>
      ) : null}
    </div>
  );
}

function Section({ title, subtitle, children }) {
  return (
    <section className="space-y-3">
      <div>
        <h2 className="text-xl font-bold">{title}</h2>
        <p className="muted">{subtitle}</p>
      </div>
      {children}
    </section>
  );
}

function TechnicalTable({ title, gainers, losers }) {
  return (
    <div className="card">
      <h2 className="text-xl font-bold">{title}</h2>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <MetricList title="Top Gainers" items={gainers} positive />
        <MetricList title="Top Losers" items={losers} />
      </div>
    </div>
  );
}

function MetricList({ title, items, positive = false }) {
  return (
    <div>
      <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">{title}</p>
      <div className="space-y-3">
        {items.map((item) => (
          <Link
            key={`${title}-${item.symbol}`}
            to={`/stocks/${encodeURIComponent(item.symbol)}`}
            className="flex items-start justify-between gap-3 rounded-md border border-slate-200 px-3 py-3 transition hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800"
          >
            <div>
              <p className="font-semibold">{item.label}</p>
              <p className="muted">{item.symbol}</p>
            </div>
            <div className={`text-right font-semibold ${positive ? "text-emerald-600" : "text-rose-600"}`}>
              {Number(item.changePercent || 0).toFixed(2)}%
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

function TechnicalGrid({ title, above200, rsiWatch }) {
  return (
    <div className="card">
      <h2 className="text-xl font-bold">{title}</h2>
      <div className="mt-4 space-y-4">
        <div>
          <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Above 200-Day SMA</p>
          <div className="space-y-3">
            {above200.map((item) => (
              <Link
                key={`sma-${item.symbol}`}
                to={`/stocks/${encodeURIComponent(item.symbol)}`}
                className="flex items-center justify-between gap-3 rounded-md border border-slate-200 px-3 py-3 transition hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800"
              >
                <div>
                  <p className="font-semibold">{item.label}</p>
                  <p className="muted">{item.symbol}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-emerald-600">{item.momentum}</p>
                  <p className="muted">SMA200 {item.sma200 ?? "--"}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>

        <div>
          <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">RSI / 52-Week Range</p>
          <div className="space-y-3">
            {rsiWatch.map((item) => (
              <Link
                key={`rsi-${item.symbol}`}
                to={`/stocks/${encodeURIComponent(item.symbol)}`}
                className="rounded-md border border-slate-200 px-3 py-3 transition hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800"
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold">{item.label}</p>
                    <p className="muted">{item.symbol}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">RSI {item.rsi14 ?? "--"}</p>
                    <p className="muted">{item.momentum}</p>
                  </div>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-md bg-slate-100 px-3 py-2 dark:bg-slate-800">
                    <p className="muted">From 52W High</p>
                    <p className="font-semibold">{formatPercent(item.distanceTo52WeekHigh)}</p>
                  </div>
                  <div className="rounded-md bg-slate-100 px-3 py-2 dark:bg-slate-800">
                    <p className="muted">From 52W Low</p>
                    <p className="font-semibold">{formatPercent(item.distanceTo52WeekLow)}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }
  const numeric = Number(value);
  return `${numeric > 0 ? "+" : ""}${numeric.toFixed(2)}%`;
}
