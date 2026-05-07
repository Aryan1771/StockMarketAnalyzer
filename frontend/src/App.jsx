import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext.jsx";
import Layout from "./components/Layout.jsx";
import Auth from "./routes/Auth.jsx";
import Dashboard from "./routes/Dashboard.jsx";
import Markets from "./routes/Markets.jsx";
import News from "./routes/News.jsx";
import Settings from "./routes/Settings.jsx";
import StockDetails from "./routes/StockDetails.jsx";
import Watchlist from "./routes/Watchlist.jsx";
import { api } from "./services/api.js";

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");

  useEffect(() => {
    api.getPreferences()
      .then((prefs) => setTheme(prefs.theme || "dark"))
      .catch(() => {});
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <AuthProvider>
      <Layout theme={theme} onThemeChange={setTheme}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/markets" element={<Markets />} />
          <Route path="/stocks/:symbol?" element={<StockDetails />} />
          <Route path="/watchlist" element={<Watchlist />} />
          <Route path="/news" element={<News />} />
          <Route path="/settings" element={<Settings theme={theme} onThemeChange={setTheme} />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </AuthProvider>
  );
}
