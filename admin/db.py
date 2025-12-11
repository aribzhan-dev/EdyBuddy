import psycopg2
import psycopg2.extras
from bot.config import POSTGRES_URL


def connect():
    return psycopg2.connect(POSTGRES_URL)


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(POSTGRES_URL)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


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


    def close(self):
        self.cur.close()
        self.conn.close()