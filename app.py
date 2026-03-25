import os
from datetime import datetime, timezone

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql://hello:hello@localhost:5432/hellodb"
)
db = SQLAlchemy(app)


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )


with app.app_context():
    db.create_all()


@app.route("/")
def hello():
    visit = Visit()
    db.session.add(visit)
    db.session.commit()

    count = db.session.query(Visit).count()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello World</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
        }}
        .container {{
            text-align: center;
            padding: 2rem;
        }}
        h1 {{ font-size: 3rem; margin-bottom: 0.5rem; }}
        p {{ font-size: 1.2rem; opacity: 0.85; }}
        .db-status {{
            margin-top: 1.5rem;
            padding: 1rem 2rem;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            backdrop-filter: blur(4px);
        }}
        .db-status span {{ font-size: 1.8rem; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Hello, World!</h1>
        <p>Flask app running with PostgreSQL</p>
        <div class="db-status">
            <p>Database connected</p>
            <span>{count}</span>
            <p>visit{"s" if count != 1 else ""} recorded</p>
        </div>
    </div>
</body>
</html>"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
