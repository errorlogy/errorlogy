# Security Policy

## Reporting a vulnerability

Open a [GitHub issue](https://github.com/errorlogy/errorlogy/issues) with the **security** label,
or contact the maintainers via https://errorlogy.com. Do not commit secrets or live credentials
in issues or pull requests.

## Secrets and environment variables

- **Never commit** `.env`, API keys, OAuth client secrets, or JWT signing keys.
- Copy `errorlogy-mas/.env.example` to `errorlogy-mas/.env` locally only.
- If a key was ever stored on disk outside `.env`, **rotate/revoke** it with the provider
  immediately — even if the file was gitignored.

Relevant variables (see `errorlogy-mas/mas/config.py`):

| Variable | Risk if leaked |
|----------|----------------|
| `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, … | LLM provider billing / abuse |
| `EXA_API_KEY` | Search API abuse |
| `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_SECRET` | OAuth impersonation |
| `JWT_SECRET` | Session / token forgery |
| `TELEGRAM_BOT_TOKEN` | Bot impersonation |

## Default development settings (not production-safe)

The API ships with insecure defaults intended for local development only:

1. **JWT secret** — if `JWT_SECRET` is unset, the fallback is
   `errorlogy-dev-secret-change-in-prod` (`errorlogy-mas/mas/config.py`).
   Set a strong random secret before any shared or production deployment.

2. **CORS** — `allow_origins=["*"]` with `allow_credentials=True`
   (`errorlogy-mas/api/main.py`). Restrict origins in production.

3. **Cross-layer endpoints** — `/api/events/cross-layer*` has no auth by design for MVP
   institutional stub ingress. Do not expose an unauthenticated instance to the public internet
   without a reverse proxy and rate limits.

## Supported versions

Security fixes are applied on `main`. Older tags may not receive backports.
