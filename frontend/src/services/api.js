const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    credentials: "include",
    ...options
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "Request failed");
  }
  return payload;
}

export const api = {
  baseUrl: API_BASE,
  dashboard: () => request("/api/stocks/dashboard"),
  overview: () => request("/api/stocks/overview"),
  catalog: () => request("/api/stocks/catalog"),
  quote: (symbol) => request(`/api/stocks/${symbol}/quote`),
  history: (symbol, range = "1mo") => request(`/api/stocks/${symbol}/history?range=${range}`),
  analysis: (symbol, range = "10d") => request(`/api/stocks/${symbol}/analysis?range=${range}`),
  search: (query) => request(`/api/stocks/search?q=${encodeURIComponent(query)}`),
  compare: (symbols) => request(`/api/stocks/compare?symbols=${symbols.join(",")}`),
  news: (params = {}) => {
    const search = new URLSearchParams(params);
    return request(`/api/news?${search.toString()}`);
  },
  watchlist: () => request("/api/watchlist"),
  addWatchlist: (symbol) => request("/api/watchlist", {
    method: "POST",
    body: JSON.stringify({ symbol })
  }),
  removeWatchlist: (symbol) => request(`/api/watchlist/${symbol}`, { method: "DELETE" }),
  getPreferences: () => request("/api/user/preferences"),
  savePreferences: (prefs) => request("/api/user/preferences", {
    method: "PUT",
    body: JSON.stringify(prefs)
  }),
  me: () => request("/api/user/me"),
  register: (payload) => request("/api/user/register", {
    method: "POST",
    body: JSON.stringify(payload)
  }),
  login: (payload) => request("/api/user/login", {
    method: "POST",
    body: JSON.stringify(payload)
  }),
  logout: () => request("/api/user/logout", { method: "POST" }),
  deleteAccount: () => request("/api/user/account", { method: "DELETE" }),
  apiKeyStatus: () => request("/api/user/api-keys/status"),
  legacyAnalyze: (symbol) => request("/analyze", {
    method: "POST",
    body: JSON.stringify({ symbol })
  })
};
