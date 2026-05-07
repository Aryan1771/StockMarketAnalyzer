# StockMarketAnalyzer 2.0

Modern full-stack stock market dashboard with a Flask API, React/Vite frontend, live market data, news aggregation, account-based watchlists, saved preferences, MongoDB persistence, and a C++-inspired analysis pipeline with a production-safe Python fallback.

## Features

- Multi-market dashboard for India and United States
- Market browser for:
  - `S&P 500`
  - `Nifty 50`
  - `Sensex`
- Live quote, history, compare, and deep-analysis pages
- Search suggestions across US and Indian symbols such as `ONGC.NS`
- Aggregated news from multiple providers with source labels and direct links
- Username/password account system with:
  - register
  - login
  - logout
  - delete account
- MongoDB-backed users, watchlists, and preferences
- Watchlist persistence across sessions
- Theme and chart-range preferences
- Custom branding icon and polished sidebar/header UI
- Render keep-awake GitHub Actions workflow for free-tier cold-start reduction

## Project Structure

```text
api/
  app.py
  config.py
  routes/
  services/
  storage/
cpp_backend/
  analyzer.exe
  analyzer_fresh.exe
  include/
  src/
frontend/
  public/
  src/
  package.json
.github/
  workflows/
render.yaml
requirements.txt
```

## Tech Stack

### Backend
- Flask
- Flask-CORS
- Requests
- yfinance
- PyMongo
- Gunicorn

### Frontend
- React
- Vite
- React Router
- Recharts
- Tailwind CSS
- lucide-react

### Data / Storage
- MongoDB Atlas for deployed user data
- Local JSON fallback for development if MongoDB is not configured

## Local Development

### 1. Backend

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` file in the repository root and add:

```text
SECRET_KEY=replace-with-a-random-secret
PASSWORD_SALT=replace-with-a-random-salt
FRONTEND_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=Lax

MONGODB_URI=
MONGODB_DB_NAME=stockmarketanalyzer

ALPHA_VANTAGE_API_KEY=
FINNHUB_API_KEY=

CACHE_TTL_SECONDS=120
LOG_LEVEL=INFO
FLASK_DEBUG=true
```

Then run:

```powershell
python api\app.py
```

### 2. Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:

- [http://127.0.0.1:5173](http://127.0.0.1:5173)

For local Vite development, `VITE_API_BASE_URL` is usually not needed.

## API Overview

### Health
- `GET /api/health`

### Stocks
- `GET /api/stocks/search?q=AAPL`
- `GET /api/stocks/overview`
- `GET /api/stocks/dashboard`
- `GET /api/stocks/catalog`
- `GET /api/stocks/compare?symbols=AAPL,MSFT`
- `GET /api/stocks/<symbol>/quote`
- `GET /api/stocks/<symbol>/history?range=1mo`
- `GET /api/stocks/<symbol>/analysis?range=10d`

### News
- `GET /api/news`
- `GET /api/news?symbol=AAPL`
- `GET /api/news?category=general`

### Auth / User
- `POST /api/user/register`
- `POST /api/user/login`
- `POST /api/user/logout`
- `GET /api/user/me`
- `DELETE /api/user/account`
- `GET /api/user/preferences`
- `PUT /api/user/preferences`
- `GET /api/user/api-keys/status`

### Watchlist
- `GET /api/watchlist`
- `POST /api/watchlist`
- `DELETE /api/watchlist/<symbol>`

### Legacy
- `POST /analyze`

Example:

```http
POST /analyze
Content-Type: application/json

{ "symbol": "AAPL" }
```

## Environment Variables

### Required for deployed auth/session flow

```text
SECRET_KEY
PASSWORD_SALT
FRONTEND_ORIGINS
SESSION_COOKIE_SECURE
SESSION_COOKIE_SAMESITE
```

### Required for MongoDB persistence

```text
MONGODB_URI
MONGODB_DB_NAME
```

### Optional market/news providers

```text
ALPHA_VANTAGE_API_KEY
FINNHUB_API_KEY
```

### Optional runtime tuning

```text
FLASK_DEBUG
LOG_LEVEL
CACHE_TTL_SECONDS
VITE_API_BASE_URL
```

## News Providers

The news page aggregates from:

- Finnhub
- Alpha Vantage

If `general` market news comes back empty, the backend falls back to a market-symbol basket so the page still shows useful live stories instead of only a placeholder.

## Analysis Pipeline

The stock analysis endpoint uses:

- Yahoo Finance history/quote data
- the legacy C++ analyzer locally on Windows
- a Python fallback in production when the Windows executable is unavailable on Render

This means deployed analysis still returns useful values like:

- moving average
- stock span
- change percent

instead of failing outright on Linux.

## Recommended free-tier setup

- Frontend: Vercel
- Backend: Render
- Database: MongoDB Atlas

### Vercel

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Install command: `npm install`

Frontend environment variable:

```text
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

### Render

- Root directory: leave blank
- Build command: `pip install -r requirements.txt`
- Start command:

```text
cd api && gunicorn "app:create_app()"
```

The repo includes:

- [C:\Users\aryan\Documents\GitHub\StockMArketAnalyzer2.0\render.yaml](C:\Users\aryan\Documents\GitHub\StockMArketAnalyzer2.0\render.yaml)
- [C:\Users\aryan\Documents\GitHub\StockMArketAnalyzer2.0\frontend\vercel.json](C:\Users\aryan\Documents\GitHub\StockMArketAnalyzer2.0\frontend\vercel.json)

### Production environment example

Backend:

```text
SECRET_KEY=replace-with-a-random-secret
PASSWORD_SALT=replace-with-a-random-salt
FRONTEND_ORIGINS=https://your-app.vercel.app
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=None

MONGODB_URI=your_mongodb_connection_string
MONGODB_DB_NAME=stockmarketanalyzer

ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key

CACHE_TTL_SECONDS=120
LOG_LEVEL=INFO
FLASK_DEBUG=false
```

Frontend:

```text
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

## Render Free-Tier Keep-Awake Workflow

The repository includes:

- [C:\Users\aryan\Documents\GitHub\StockMArketAnalyzer2.0\.github\workflows\keep-render-awake.yml](C:\Users\aryan\Documents\GitHub\StockMArketAnalyzer2.0\.github\workflows\keep-render-awake.yml)

It pings the backend health endpoint every 10 minutes to reduce cold-start delays on Render free tier.

Default URL:

```text
https://stockmarketanalyzer2-0.onrender.com/api/health
```

Optional GitHub repository variable:

```text
RENDER_HEALTHCHECK_URL
```

Note: keeping a free Render service warm continuously uses most of the monthly free instance hours.

## Testing

From the repository root:

```powershell
python -m pytest
```

The current suite covers:

- health checks
- auth flows
- watchlist persistence
- account deletion
- MongoDB-backed user storage behavior
- market catalog route
- dashboard route
- news general-feed fallback behavior
- Python fallback analysis metrics

## Current Notes

- The frontend bundle is functional but large enough for Vite to warn about chunk size during production builds.
- Yahoo Finance does not require an API key in this project.
- If deployed data or analysis looks stale after a push, verify both:
  - Vercel redeployed the frontend
  - Render redeployed the backend
