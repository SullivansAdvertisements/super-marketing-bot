import json
import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/app.db")

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = _conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS research_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      source TEXT NOT NULL,
      keyword TEXT,
      payload_json TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS copy_bank (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      brand TEXT,
      product TEXT,
      platform TEXT,
      payload_json TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS budget_plan (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      total REAL NOT NULL,
      allocations_json TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS campaign_drafts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      platform TEXT NOT NULL,
      name TEXT NOT NULL,
      payload_json TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# -----------------------
# Budget Plans
# -----------------------
def db_insert_budget_plan(name: str, total: float, allocations: dict):
    conn = _conn()
    conn.execute(
        "INSERT INTO budget_plan (name, total, allocations_json) VALUES (?, ?, ?)",
        (name, float(total), json.dumps(allocations, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()

def db_list_budget_plans(limit: int = 50) -> pd.DataFrame:
    conn = _conn()
    df = pd.read_sql_query(
        "SELECT id, name, total, allocations_json, created_at FROM budget_plan ORDER BY id DESC LIMIT ?",
        conn,
        params=(int(limit),),
    )
    conn.close()
    return df

# -----------------------
# Research Items
# -----------------------
def db_insert_research_item(source: str, keyword: str, payload):
    conn = _conn()
    conn.execute(
        "INSERT INTO research_items (source, keyword, payload_json) VALUES (?, ?, ?)",
        (source, keyword, json.dumps(payload, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()

def db_list_research_items(limit: int = 50) -> pd.DataFrame:
    conn = _conn()
    df = pd.read_sql_query(
        "SELECT id, source, keyword, created_at FROM research_items ORDER BY id DESC LIMIT ?",
        conn,
        params=(int(limit),),
    )
    conn.close()
    return df

def db_get_research_payload(item_id: int):
    conn = _conn()
    row = conn.execute("SELECT payload_json FROM research_items WHERE id=?", (int(item_id),)).fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

# -----------------------
# Copy Bank
# -----------------------
def db_insert_copy_bank(brand: str, product: str, platform: str, payload: dict):
    conn = _conn()
    conn.execute(
        "INSERT INTO copy_bank (brand, product, platform, payload_json) VALUES (?, ?, ?, ?)",
        (brand, product, platform, json.dumps(payload, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()

def db_list_copy_bank(limit: int = 50) -> pd.DataFrame:
    conn = _conn()
    df = pd.read_sql_query(
        "SELECT id, brand, product, platform, created_at FROM copy_bank ORDER BY id DESC LIMIT ?",
        conn,
        params=(int(limit),),
    )
    conn.close()
    return df

def db_get_copy_payload(item_id: int):
    conn = _conn()
    row = conn.execute("SELECT payload_json FROM copy_bank WHERE id=?", (int(item_id),)).fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

# -----------------------
# Campaign Drafts
# -----------------------
def db_insert_campaign_draft(platform: str, name: str, payload: dict):
    conn = _conn()
    conn.execute(
        "INSERT INTO campaign_drafts (platform, name, payload_json) VALUES (?, ?, ?)",
        (platform, name, json.dumps(payload, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()

def db_list_campaign_drafts(limit: int = 50) -> pd.DataFrame:
    conn = _conn()
    df = pd.read_sql_query(
        "SELECT id, platform, name, created_at FROM campaign_drafts ORDER BY id DESC LIMIT ?",
        conn,
        params=(int(limit),),
    )
    conn.close()
    return df

def db_get_campaign_payload(item_id: int):
    conn = _conn()
    row = conn.execute("SELECT payload_json FROM campaign_drafts WHERE id=?", (int(item_id),)).fetchone()
    conn.close()
    return json.loads(row[0]) if row else None
