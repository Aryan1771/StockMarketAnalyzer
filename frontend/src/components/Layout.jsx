import { BarChart3, Bell, BriefcaseBusiness, Home, LogIn, LogOut, Moon, Search, Settings, Star, Sun, UserCircle2 } from "lucide-react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import SearchBar from "./SearchBar.jsx";
import { useAuth } from "../context/AuthContext.jsx";

const navItems = [
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/markets", label: "Markets", icon: BriefcaseBusiness },
  { to: "/stocks", label: "Stocks", icon: BarChart3 },
  { to: "/watchlist", label: "Watchlist", icon: Star },
  { to: "/news", label: "News", icon: Bell },
  { to: "/settings", label: "Settings", icon: Settings }
];

export default function Layout({ children, theme, onThemeChange }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    if (location.pathname === "/watchlist") {
      navigate("/auth");
      return;
    }
    navigate("/");
  };

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[250px_1fr]">
      <aside className="hidden border-r border-slate-200 bg-white px-4 py-5 dark:border-slate-800 dark:bg-slate-900 lg:block">
        <div className="mb-8 flex items-center gap-3 px-2">
          <div className="grid h-10 w-10 place-items-center rounded-lg bg-accent text-white">
            <Search size={20} />
          </div>
          <div>
            <p className="text-sm font-bold">StockMarketAnalyzer</p>
            <p className="muted">Signals and research</p>
          </div>
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition ${
                  isActive ? "bg-emerald-50 text-accent dark:bg-emerald-950" : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                }`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="min-w-0">
        <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <SearchBar onSelect={(symbol) => navigate(`/stocks/${symbol}`)} />
            <div className="flex items-center justify-between gap-2">
              <div className="hidden items-center gap-2 md:flex">
                {isAuthenticated ? (
                  <>
                    <div className="inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm dark:border-slate-700">
                      <UserCircle2 size={16} />
                      <span>{user.displayName || user.username}</span>
                    </div>
                    <button className="btn-secondary inline-flex items-center gap-2" onClick={handleLogout}>
                      <LogOut size={16} />
                      Logout
                    </button>
                  </>
                ) : (
                  <button className="btn-secondary inline-flex items-center gap-2" onClick={() => navigate("/auth")}>
                    <LogIn size={16} />
                    Login
                  </button>
                )}
              </div>
              <nav className="flex gap-1 lg:hidden">
                {navItems.map((item) => (
                  <NavLink key={item.to} to={item.to} className="rounded-md p-2 hover:bg-slate-100 dark:hover:bg-slate-800">
                    <item.icon size={18} />
                  </NavLink>
                ))}
              </nav>
              <div className="md:hidden">
                {isAuthenticated ? (
                  <button className="rounded-md border border-slate-200 p-2 dark:border-slate-700" onClick={handleLogout} title="Logout">
                    <LogOut size={18} />
                  </button>
                ) : (
                  <button className="rounded-md border border-slate-200 p-2 dark:border-slate-700" onClick={() => navigate("/auth")} title="Login">
                    <LogIn size={18} />
                  </button>
                )}
              </div>
              <button
                className="rounded-md border border-slate-200 p-2 dark:border-slate-700"
                onClick={() => onThemeChange(theme === "dark" ? "light" : "dark")}
                title="Toggle theme"
              >
                {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </div>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
      </div>
    </div>
  );
}
