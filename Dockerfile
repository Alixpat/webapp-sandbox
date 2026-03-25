FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app.py .
COPY templates/ templates/

RUN mkdir -p uploads

ENV PORT=10000
EXPOSE ${PORT}

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} app:app"]
