import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "backend.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(upload_id) REFERENCES uploads(id)
            )
        """)


def create_upload(upload_id: str, filename: str, path: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO uploads (id, filename, path, created_at) VALUES (?, ?, ?, ?)",
            (upload_id, filename, path, datetime.utcnow().isoformat())
        )


def get_upload(upload_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM uploads WHERE id = ?", (upload_id,)).fetchone()
        return dict(row) if row else None


def insert_raw_records(upload_id: str, rows: List[Dict[str, Any]]) -> int:
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.executemany(
            "INSERT INTO raw_records (upload_id, payload, created_at) VALUES (?, ?, ?)",
            [(upload_id, json.dumps(r, ensure_ascii=False), now) for r in rows]
        )
    return len(rows)


def get_raw_records(upload_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    with _connect() as conn:
        cur = conn.execute(
            "SELECT id, payload, created_at FROM raw_records WHERE upload_id = ? ORDER BY id ASC LIMIT ?",
            (upload_id, limit)
        )
        out = []
        for row in cur.fetchall():
            out.append({
                "id": row["id"],
                "created_at": row["created_at"],
                "payload": json.loads(row["payload"]),
            })
        return out

# -------------------------
# API functions for router
# -------------------------

def init_uploads_storage_db():
    return init_db()


def create_upload_row(upload_id: str, filename: str, path: str):
    return create_upload(upload_id, filename, path)


def get_upload_row(upload_id: str):
    return get_upload(upload_id)


def insert_raw_records_rows(upload_id: str, rows):
    return insert_raw_records(upload_id, rows)


def get_raw_records_rows(upload_id: str, limit: int = 20):
    return get_raw_records(upload_id, limit)

def save_data_to_db_api(*args, **kwargs):
    return save_data_to_db(*args, **kwargs)