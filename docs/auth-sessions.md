# Auth and per-user chat sessions

Username-only login with Postgres-backed sessions.

## Flow

1. **Register** — first name, last name, email (optional), unique username  
2. **Login** — username only (no password)  
3. Chat UI shows **Hello, {first_name}!**  
4. Sidebar lists **only that user’s** sessions  
5. **New chat** / **Delete** per session  
6. Session memory (“My name is XYZ”) stays on that session only  

Same username on another browser loads the same sessions (owned by `user_id` in Postgres).

## Docker Postgres

`docker-compose.app.yml` runs `postgres:16-alpine`.

- Inside Compose: `DATABASE_URL=postgresql://glyco:glyco@postgres:5432/glycochat`  
- From the host (local backend): `DATABASE_URL=postgresql://glyco:glyco@127.0.0.1:5433/glycochat`  
  (host port **5433** avoids clashing with a local Postgres on 5432)

```powershell
$env:Path = "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin;$env:Path"
docker compose -f docker-compose.app.yml up -d postgres
```

## API

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/auth/register` | no |
| POST | `/api/v1/auth/login` | no |
| GET | `/api/v1/auth/me` | Bearer JWT |
| POST/GET/DELETE | `/api/v1/sessions` | Bearer JWT |
| POST | `/api/v1/chat` | Bearer JWT |

## Local run

```powershell
# Terminal 1 — Postgres (Docker)
docker compose -f docker-compose.app.yml up -d postgres

# Terminal 2 — API
$env:PYTHONPATH = "$PWD\packages;$PWD\apps\backend\src"
$env:DATABASE_URL = "postgresql://glyco:glyco@127.0.0.1:5433/glycochat"
.\.venv\Scripts\python.exe -m api.server

# Terminal 3 — UI
cd apps\frontend\src
..\..\..\.venv\Scripts\streamlit.exe run app.py
```
