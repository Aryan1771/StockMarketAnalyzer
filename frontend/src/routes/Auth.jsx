import { Check, Eye, EyeOff } from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ErrorMessage } from "../components/State.jsx";
import { useAuth } from "../context/AuthContext.jsx";

export default function Auth() {
  const navigate = useNavigate();
  const { login, register, isAuthenticated, user } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", password: "", displayName: "" });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const passwordChecks = useMemo(() => ([
    { label: "At least 8 characters", valid: form.password.length >= 8 },
    { label: "At least 1 lowercase letter", valid: /[a-z]/.test(form.password) },
    { label: "At least 1 uppercase letter", valid: /[A-Z]/.test(form.password) },
    { label: "At least 1 number", valid: /\d/.test(form.password) },
  ]), [form.password]);
  const passwordValid = passwordChecks.every((item) => item.valid);

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
        <form className="space-y-4" onSubmit={submit}>
          {mode === "register" && (
            <label className="block">
              <span className="muted">Display name</span>
              <input className="input mt-1" value={form.displayName} onChange={(event) => setForm({ ...form, displayName: event.target.value })} placeholder="Display Name" />
            </label>
          )}
          <label className="block">
            <span className="muted">Username</span>
            <input className="input mt-1" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} placeholder="user123" />
          </label>
          <label className="block">
            <span className="muted">Password</span>
            <div className="relative mt-1">
              <input
                className="input pr-12"
                type={showPassword ? "text" : "password"}
                value={form.password}
                onChange={(event) => setForm({ ...form, password: event.target.value })}
                placeholder="At least 8 characters"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 inline-flex items-center px-3 text-slate-500 transition hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                onClick={() => setShowPassword((value) => !value)}
                title={showPassword ? "Hide password" : "Show password"}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
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
