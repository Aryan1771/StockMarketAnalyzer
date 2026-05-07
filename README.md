# StockMarketAnalyzer

Modern full-stack stock analysis app with a Flask API, React/Vite frontend, Yahoo Finance integration, optional Alpha Vantage and Finnhub fallbacks, account-based watchlists, preferences, news, and the original C++ analytics engine.

## Current Architecture

```text
api/
  app.py
  routes/
  services/
  storage/
cpp_backend/
  analyzer.exe
  include/
  src/
frontend/
  src/
  package.json
```

## Backend Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python api\app.py
```

The legacy endpoint is still available:

```http
POST http://localhost:5000/analyze
{ "symbol": "AAPL" }
```

New API routes include:

- `GET /api/stocks/search?q=AAPL`
- `GET /api/stocks/<symbol>/quote`
- `GET /api/stocks/<symbol>/history?range=1mo`
- `GET /api/stocks/<symbol>/analysis`
- `GET /api/stocks/compare?symbols=AAPL,MSFT`
- `GET /api/news?symbol=AAPL`
- `GET|POST /api/watchlist`
- `DELETE /api/watchlist/<symbol>`
- `POST /api/user/register`
- `POST /api/user/login`
- `POST /api/user/logout`
- `GET /api/user/me`
- `GET|PUT /api/user/preferences`
- `GET /api/user/api-keys/status`

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` and `/analyze` to Flask on port `5000`.

## API Keys

Yahoo Finance works without a key. All external provider keys and auth/session settings are loaded from environment variables when the Flask API starts. For richer fallbacks, multi-source live news, and deployed account sessions, set these in `.env`:

```text
SECRET_KEY=replace-with-a-random-secret
PASSWORD_SALT=replace-with-a-random-salt
FRONTEND_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=Lax
ALPHA_VANTAGE_API_KEY=your_key
FINNHUB_API_KEY=your_key
```

With both keys configured, the News page aggregates stories from multiple providers, shows the source under each article, and links directly to the original publisher.

Frontend deployments can optionally point to a separate backend with:

```text
VITE_API_BASE_URL=https://your-backend.example.com
```

## Deployment Notes

Recommended free deployment split:

- Backend: Render web service
- Frontend: Vercel project rooted at `frontend/`

The repo includes:

- [C:\Users\aryan\Documents\GitHub\StockMarketAnalyzer\render.yaml](C:\Users\aryan\Documents\GitHub\StockMarketAnalyzer\render.yaml)
- [C:\Users\aryan\Documents\GitHub\StockMarketAnalyzer\frontend\vercel.json](C:\Users\aryan\Documents\GitHub\StockMarketAnalyzer\frontend\vercel.json)

For Vercel + Render sessions, update these values in production:

```text
FRONTEND_ORIGINS=https://your-vercel-app.vercel.app
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=None
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

## Tests

```powershell
pytest
```

The tests mock provider calls where possible so core routes, watchlist persistence, and normalization can be validated without depending on live market APIs.
