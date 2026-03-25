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

### 1. Create the PostgreSQL database

Go to [Render Dashboard](https://dashboard.render.com) and click **New > PostgreSQL**. Fill in:

| Field | Value |
|---|---|
| **Name** | `hellodb` |
| **Database** | `hellodb` |
| **User** | `hello` |
| **Region** | Same as your Web Service (e.g. Frankfurt EU) |
| **Plan** | Free |

Once created, copy the **Internal Database URL** from the database info page.

### 2. Create the Web Service

1. Click **New > Web Service** and connect your GitHub repo.
2. Render auto-detects the `Dockerfile`.
3. Add the following environment variable:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | *The Internal Database URL copied above* |

4. Click **Deploy**.
