import { Check, Mail, ShieldCheck } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ErrorMessage } from "../components/State.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../services/api.js";

export default function Auth() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { login, register, refresh, isAuthenticated, user } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", password: "", displayName: "" });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [oauth, setOauth] = useState({ google: false, microsoft: false });

  const passwordChecks = useMemo(() => ([
    { label: "At least 8 characters", valid: form.password.length >= 8 },
    { label: "At least 1 lowercase letter", valid: /[a-z]/.test(form.password) },
    { label: "At least 1 uppercase letter", valid: /[A-Z]/.test(form.password) },
    { label: "At least 1 number", valid: /\d/.test(form.password) },
  ]), [form.password]);
  const passwordValid = passwordChecks.every((item) => item.valid);

  useEffect(() => {
    api.oauthProviders().then(setOauth).catch(() => {});
  }, []);

  useEffect(() => {
    const oauthStatus = searchParams.get("oauth");
    if (!oauthStatus) {
      return;
    }
    if (oauthStatus === "success") {
      refresh()
        .then(() => {
          setMessage("Signed in successfully.");
          navigate("/watchlist", { replace: true });
        })
        .catch(() => setError("Sign-in completed, but the session could not be refreshed."));
    } else if (oauthStatus === "error") {
      setError("Social sign-in could not be completed. Please try again.");
    }
    const nextParams = new URLSearchParams(searchParams);
    nextParams.delete("oauth");
    setSearchParams(nextParams, { replace: true });
  }, [navigate, refresh, searchParams, setSearchParams]);

  if (isAuthenticated) {
    return (
      <div className="space-y-6">
        <section>
          <p className="muted">Account</p>
          <h1 className="text-3xl font-bold">You are signed in</h1>
        </section>
        <div className="card space-y-3">
          <p className="text-lg font-semibold">{user.displayName}</p>
          <p className="muted">@{user.username}</p>
          {user.email && <p className="muted">{user.email}</p>}
          <button className="btn w-full sm:w-auto" onClick={() => navigate("/watchlist")}>Go to Watchlist</button>
        </div>
      </div>
    );
  }

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      if (mode === "login") {
        await login({ username: form.username, password: form.password });
        navigate("/watchlist");
      } else {
        await register(form);
        setMessage("Account created. You are now signed in.");
        navigate("/watchlist");
      }
    } catch (exc) {
      setError(exc.message);
    }
  };

  const beginOauth = (provider) => {
    window.location.href = `${api.baseUrl}/api/user/oauth/${provider}/start?next=/watchlist`;
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <section>
        <p className="muted">Account access</p>
        <h1 className="text-3xl font-bold">Login or create an account</h1>
      </section>
      <div className="card space-y-4">
        <div className="inline-flex rounded-lg border border-slate-200 p-1 dark:border-slate-700">
          {["login", "register"].map((item) => (
            <button
              key={item}
              type="button"
              className={`rounded-md px-4 py-2 text-sm font-medium ${mode === item ? "bg-accent text-white" : "text-slate-600 dark:text-slate-300"}`}
              onClick={() => {
                setMode(item);
                setError("");
                setMessage("");
              }}
            >
              {item === "login" ? "Login" : "Register"}
            </button>
          ))}
        </div>
        <ErrorMessage message={error} />
        {message && <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950">{message}</div>}
        <div className="grid gap-3 md:grid-cols-2">
          <button
            type="button"
            className="btn-secondary justify-center"
            onClick={() => beginOauth("google")}
            disabled={!oauth.google}
            title={oauth.google ? "Continue with Google" : "Google sign-in is not configured"}
          >
            <Mail size={16} />
            {mode === "login" ? "Sign in with Google" : "Sign up with Google"}
          </button>
          <button
            type="button"
            className="btn-secondary justify-center"
            onClick={() => beginOauth("microsoft")}
            disabled={!oauth.microsoft}
            title={oauth.microsoft ? "Continue with Outlook" : "Outlook sign-in is not configured"}
          >
            <ShieldCheck size={16} />
            {mode === "login" ? "Sign in with Outlook" : "Sign up with Outlook"}
          </button>
        </div>
        <div className="relative py-2">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-200 dark:border-slate-700" /></div>
          <div className="relative flex justify-center text-xs uppercase tracking-wide text-slate-500">
            <span className="bg-white px-3 dark:bg-slate-900">or use your account</span>
          </div>
        </div>
        <form className="space-y-4" onSubmit={submit}>
          {mode === "register" && (
            <label className="block">
              <span className="muted">Display name</span>
              <input className="input mt-1" value={form.displayName} onChange={(event) => setForm({ ...form, displayName: event.target.value })} placeholder="Aryan" />
            </label>
          )}
          <label className="block">
            <span className="muted">Username</span>
            <input className="input mt-1" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} placeholder="user123" />
          </label>
          <label className="block">
            <span className="muted">Password</span>
            <input className="input mt-1" type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder="At least 8 characters" />
          </label>
          {mode === "register" && (
            <div className="grid gap-2 rounded-lg border border-slate-200 p-4 text-sm dark:border-slate-700">
              {passwordChecks.map((item) => (
                <div key={item.label} className={`flex items-center gap-2 ${item.valid ? "text-emerald-600" : "text-slate-500 dark:text-slate-400"}`}>
                  <Check size={16} />
                  <span>{item.label}</span>
                </div>
              ))}
            </div>
          )}
          <button className="btn w-full sm:w-auto" disabled={mode === "register" && !passwordValid}>{mode === "login" ? "Login" : "Create account"}</button>
        </form>
      </div>
    </div>
  );
}
