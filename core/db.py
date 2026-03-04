import sqlite3
from pathlib import Path

DB = Path("data/marketing_os.db")

class DBEngine:

    def __init__(self):
        DB.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(DB)
        self.init()

    def init(self):
        c=self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY,name TEXT,notes TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS campaigns(id INTEGER PRIMARY KEY,name TEXT,platform TEXT,payload TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY,msg TEXT)")
        self.conn.commit()

    def insert(self,table,data):
        keys=",".join(data.keys())
        q=",".join(["?"]*len(data))
        self.conn.execute(f"INSERT INTO {table}({keys}) VALUES({q})",tuple(data.values()))
        self.conn.commit()

    def list(self,table):
        cur=self.conn.execute(f"SELECT * FROM {table}")
        cols=[d[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in cur.fetchall()]

db=DBEngine()
