services:
  - type: web
    name: stockmarketanalyzer-api
    env: python
    rootDir: .
    buildCommand: pip install -r requirements.txt
    startCommand: cd api && gunicorn "app:create_app()"
    envVars:
      - key: FLASK_DEBUG
        value: "false"
      - key: LOG_LEVEL
        value: INFO
      - key: CACHE_TTL_SECONDS
        value: "120"
      - key: SESSION_COOKIE_SECURE
        value: "true"
      - key: SESSION_COOKIE_SAMESITE
        value: None
