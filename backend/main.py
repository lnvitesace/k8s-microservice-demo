from fastapi import FastAPI
from contextlib import asynccontextmanager
import psycopg
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/app",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the hits table on startup."""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hits (
                id SERIAL PRIMARY KEY,
                path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
    yield


app = FastAPI(lifespan=lifespan)


def get_hit_count(path: str) -> int:
    """Insert a hit and return total count."""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hits (
                id SERIAL PRIMARY KEY,
                path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.execute("INSERT INTO hits (path) VALUES (%s)", (path,))
        conn.commit()
        row = conn.execute("SELECT COUNT(*) FROM hits").fetchone()
        return row[0]


@app.get("/")
def root():
    hits = get_hit_count("/")
    return {"hello!": "world", "hits": hits}


@app.get("/health")
def health():
    """Health check endpoint for Kubernetes probes."""
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            conn.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception:
        return {"status": "unhealthy"}, 503


@app.get("/{name}")
def greet(name: str):
    hits = get_hit_count(f"/{name}")
    return {"hello!": name, "hits": hits}