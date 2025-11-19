import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "edybuddy.db")

class Database:
    def __init__(self, path=DB_PATH):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row

    def get_tables(self):
        q = "SELECT name FROM sqlite_master WHERE type='table'"
        return [row["name"] for row in self.conn.execute(q).fetchall()]

    def get_columns(self, table):
        q = f"PRAGMA table_info({table})"
        return [row["name"] for row in self.conn.execute(q).fetchall()]

    def get_rows(self, table):
        q = f"SELECT * FROM {table}"
        return self.conn.execute(q).fetchall()

    def insert_row(self, table, data: dict):
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())
        q = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        cur = self.conn.cursor()
        cur.execute(q, values)
        self.conn.commit()
        return cur.lastrowid