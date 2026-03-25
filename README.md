# webapp-sandbox

A minimal Flask "Hello World" app, ready to deploy on Render.com.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:10000

## Run with Docker

```bash
docker build -t webapp-sandbox .
docker run -p 10000:10000 webapp-sandbox
```

## Deploy on Render.com

1. Push this repo to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com) and click **New > Web Service**.
3. Connect your GitHub repo.
4. Render auto-detects the `Dockerfile` — no extra config needed.
5. Click **Deploy**. The app listens on the `PORT` env var set by Render (default 10000).
