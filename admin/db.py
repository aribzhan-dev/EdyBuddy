import psycopg2
import psycopg2.extras
from bot.config import POSTGRES_URL


def connect():
    return psycopg2.connect(POSTGRES_URL)


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(POSTGRES_URL)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def execute(self, q, params=()):
        self.cur.execute(q, params)
        self.conn.commit()


    def fetchall(self, sql, params=()):
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def fetchone(self, sql, params=()):
        self.cur.execute(sql, params)
        return self.cur.fetchone()

    def get_tables(self):
        q = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        self.cur.execute(q)
        rows = self.cur.fetchall()
        return [r["table_name"] for r in rows]


    def get_columns(self, table):
        q = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
        """
        self.cur.execute(q, (table,))
        rows = self.cur.fetchall()
        return [r["column_name"] for r in rows]


    def get_rows(self, table, limit=100):
        q = f"SELECT * FROM {table} LIMIT %s"
        self.cur.execute(q, (limit,))
        return self.cur.fetchall()


    def insert_row(self, table, data: dict):
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = list(data.values())

        q = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

        self.cur.execute(q, values)
        self.conn.commit()


    def close(self):
        self.cur.close()
        self.conn.close()