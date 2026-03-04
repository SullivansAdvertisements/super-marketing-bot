import sqlite3
from pathlib import Path
import threading

DB_PATH = Path("data/marketing_os.db")
_LOCK = threading.Lock()

class DB:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Thread-safe for Streamlit reruns
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.init()

    def init(self):
        with _LOCK:
            c = self.conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY, name TEXT, notes TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS campaigns (id INTEGER PRIMARY KEY, name TEXT, platform TEXT, payload TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, msg TEXT)")
            self.conn.commit()

    def insert(self, table, data):
        # Safety: whitelist tables (prevents accidental injection in f-string table name)
        allowed = {"clients", "campaigns", "logs"}
        if table not in allowed:
            raise ValueError(f"Invalid table: {table}")

        keys = ",".join(data.keys())
        q = ",".join(["?"] * len(data))

        with _LOCK:
            self.conn.execute(
                f"INSERT INTO {table} ({keys}) VALUES ({q})",
                tuple(data.values())
            )
            self.conn.commit()

    def list(self, table):
        allowed = {"clients", "campaigns", "logs"}
        if table not in allowed:
            raise ValueError(f"Invalid table: {table}")

        with _LOCK:
            cur = self.conn.execute(f"SELECT * FROM {table}")
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]

db = DB()