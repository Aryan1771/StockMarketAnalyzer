import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ErrorMessage } from "../components/State.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../services/api.js";

export default function Settings({ theme, onThemeChange }) {
  const { user, isAuthenticated, logout } = useAuth();
  const [prefs, setPrefs] = useState({ theme, defaultRange: "1mo", refreshInterval: 60 });
  const [keys, setKeys] = useState({});
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getPreferences(), api.apiKeyStatus()])
      .then(([preferences, status]) => {
        setPrefs(preferences);
        setKeys(status);
      })
      .catch((exc) => setError(exc.message));
  }, []);

  const save = async (event) => {
    event.preventDefault();
    const nextPrefs = { ...prefs, theme };
    const saved = await api.savePreferences(nextPrefs);
    setPrefs(saved);
    onThemeChange(saved.theme);
    setMessage("Preferences saved.");
  };

  return (
    <div className="space-y-6">
      <section>
        <p className="muted">Application controls</p>
        <h1 className="text-3xl font-bold">Settings</h1>
      </section>
      <ErrorMessage message={error} />
      {message && <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950">{message}</div>}
      <form className="card space-y-4" onSubmit={save}>
        <label className="block">
          <span className="muted">Theme</span>
          <select className="input mt-1" value={theme} onChange={(event) => onThemeChange(event.target.value)}>
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
        </label>
        <label className="block">
          <span className="muted">Default chart range</span>
          <select className="input mt-1" value={prefs.defaultRange} onChange={(event) => setPrefs({ ...prefs, defaultRange: event.target.value })}>
            <option value="10d">10 days</option>
            <option value="1mo">1 month</option>
            <option value="3mo">3 months</option>
            <option value="6mo">6 months</option>
            <option value="1y">1 year</option>
          </select>
        </label>
        <label className="block">
          <span className="muted">Refresh interval seconds</span>
          <input className="input mt-1" type="number" min="15" value={prefs.refreshInterval} onChange={(event) => setPrefs({ ...prefs, refreshInterval: Number(event.target.value) })} />
        </label>
        <button className="btn">Save preferences</button>
      </form>
      <div className="card space-y-3">
        <h2 className="text-xl font-bold">Account</h2>
        {isAuthenticated ? (
          <>
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Signed in as <span className="font-semibold">{user.displayName}</span> (@{user.username})
            </p>
            <button className="btn-secondary w-full sm:w-auto" onClick={() => logout()}>Logout</button>
          </>
        ) : (
          <>
            <p className="muted">Create an account to save a personal watchlist and keep preferences separate.</p>
            <Link className="btn inline-flex w-full justify-center sm:w-auto" to="/auth">Login or Register</Link>
          </>
        )}
      </div>
      <div className="card">
        <h2 className="text-xl font-bold">API Provider Status</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-3 xl:grid-cols-5">
          <Provider label="Yahoo Finance" enabled={keys.yahooFinance} />
          <Provider label="Alpha Vantage" enabled={keys.alphaVantage} />
          <Provider label="Finnhub" enabled={keys.finnhub} />
          <Provider label="Google OAuth" enabled={keys.oauth?.google} />
          <Provider label="Outlook OAuth" enabled={keys.oauth?.microsoft} />
        </div>
        <p className="muted mt-4">
          All external provider keys are loaded from environment variables when the Flask API starts.
        </p>
        <p className="muted mt-2">
          News is aggregated from Finnhub and Alpha Vantage when their keys are present. Add
          <span className="font-medium text-slate-700 dark:text-slate-200"> ALPHA_VANTAGE_API_KEY </span>
          and
          <span className="font-medium text-slate-700 dark:text-slate-200"> FINNHUB_API_KEY </span>
          to your
          <span className="font-medium text-slate-700 dark:text-slate-200"> .env </span>
          before starting Flask.
        </p>
        <p className="muted mt-2">
          For account sessions across Vercel and Render, also set
          <span className="font-medium text-slate-700 dark:text-slate-200"> SECRET_KEY </span>,
          <span className="font-medium text-slate-700 dark:text-slate-200"> PASSWORD_SALT </span>,
          <span className="font-medium text-slate-700 dark:text-slate-200"> FRONTEND_ORIGINS </span>,
          <span className="font-medium text-slate-700 dark:text-slate-200"> FRONTEND_APP_URL </span>,
          <span className="font-medium text-slate-700 dark:text-slate-200"> SESSION_COOKIE_SECURE </span>,
          and
          <span className="font-medium text-slate-700 dark:text-slate-200"> SESSION_COOKIE_SAMESITE </span>.
        </p>
        <p className="muted mt-2">
          Social sign-in also needs
          <span className="font-medium text-slate-700 dark:text-slate-200"> GOOGLE_CLIENT_ID </span>,
          <span className="font-medium text-slate-700 dark:text-slate-200"> GOOGLE_CLIENT_SECRET </span>,
          <span className="font-medium text-slate-700 dark:text-slate-200"> MICROSOFT_CLIENT_ID </span>,
          <span className="font-medium text-slate-700 dark:text-slate-200"> MICROSOFT_CLIENT_SECRET </span>,
          and optionally
          <span className="font-medium text-slate-700 dark:text-slate-200"> MICROSOFT_TENANT_ID </span>.
        </p>
      </div>
    </div>
  );
}

function Provider({ label, enabled }) {
  return (
    <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-800">
      <p className="font-semibold">{label}</p>
      <p className={`mt-1 text-sm ${enabled ? "text-emerald-600" : "text-amber-600"}`}>{enabled ? "Configured" : "Not configured"}</p>
    </div>
  );
}
