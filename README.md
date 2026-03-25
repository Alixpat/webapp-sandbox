# webapp-sandbox

A minimal Flask "Hello World" app with PostgreSQL, ready to deploy on Render.com.

## Run locally with Docker Compose

```bash
docker compose up --build
```

Open http://localhost:10000

## Run locally without Docker

Requires a running PostgreSQL instance. Set the `DATABASE_URL` env var:

```bash
export DATABASE_URL=postgresql://hello:hello@localhost:5432/hellodb
pip install -r requirements.txt
python app.py
```

## Deploy on Render.com

1. Push this repo to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com) and create a **PostgreSQL** database.
3. Create a **New > Web Service**, connect your GitHub repo.
4. Render auto-detects the `Dockerfile`.
5. Add the env var `DATABASE_URL` with the **Internal Database URL** from your Render PostgreSQL instance.
6. Click **Deploy**.
