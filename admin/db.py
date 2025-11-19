import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "edubuddy.db")
DB_PATH = os.path.abspath(DB_PATH)

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def fetchall(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

    def fetchone(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchone()

    def get_tables(self):
        q = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        rows = self.conn.execute(q).fetchall()
        return [r["name"] for r in rows]

    def get_columns(self, table):
        q = f"PRAGMA table_info({table})"
        rows = self.conn.execute(q).fetchall()
        return [r["name"] for r in rows]

    def get_rows(self, table):
        q = f"SELECT * FROM {table}"
        return self.conn.execute(q).fetchall()