import sqlite3
from datetime import date, datetime
import random
from config import DB_PATH


def connect():
    return sqlite3.connect(DB_PATH)


# ===== CREATE TABLES =====
def create_tables():
    conn = connect()
    c = conn.cursor()

    # ===== USERS =====
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        full_name TEXT,
        role TEXT CHECK(role IN ('teacher','student','unknown')) DEFAULT 'unknown'
    )""")

    # ===== GROUPS =====
    c.execute("""CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )""")

    # ===== SUBJECTS =====
    c.execute("""CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )""")

    # ===== TEACHERS =====
    c.execute("""CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        subject_id INTEGER,
        login TEXT UNIQUE,
        password TEXT,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    )""")

    # ===== STUDENTS =====
    c.execute("""CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        group_id INTEGER,
        city TEXT,
        login TEXT UNIQUE,
        password TEXT,
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )""")

    # ===== MARKS =====
    c.execute("""CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        teacher_id INTEGER,
        group_id INTEGER,
        mark INTEGER,
        put_date TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(subject_id) REFERENCES subjects(id),
        FOREIGN KEY(teacher_id) REFERENCES teachers(id),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )""")

    # ===== HOMEWORKS =====
    c.execute("""CREATE TABLE IF NOT EXISTS homeworks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER,
        teacher_id INTEGER,
        group_id INTEGER,
        task TEXT,
        deadline TEXT,
        FOREIGN KEY(subject_id) REFERENCES subjects(id),
        FOREIGN KEY(teacher_id) REFERENCES teachers(id),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )""")

    # ===== SCHEDULES =====
    c.execute("""CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        weekday TEXT,
        time TEXT,
        subject_id INTEGER,
        teacher_id INTEGER,
        group_id INTEGER,
        FOREIGN KEY(subject_id) REFERENCES subjects(id),
        FOREIGN KEY(teacher_id) REFERENCES teachers(id),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )""")

    # ===== FAQ =====
    c.execute("""CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT UNIQUE,
        answer TEXT
    )""")

    # ===== EMOJIS =====
    c.execute("""CREATE TABLE IF NOT EXISTS emojis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT
    )""")

    conn.commit()
    conn.close()
    print("✅ Все таблицы успешно созданы/проверены с поддержкой group_id!")


# ===== USERS =====
def insert_user(telegram_id, username, full_name, role="unknown"):
    conn = connect()
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO users (telegram_id, username, full_name, role)
                 VALUES (?, ?, ?, ?)""", (telegram_id, username, full_name, role))
    conn.commit()
    conn.close()


def delete_user(telegram_id):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()


# ===== LOGIN CHECK =====
def check_login(role, login, password):
    conn = connect()
    c = conn.cursor()
    if role == "teacher":
        c.execute("SELECT id, full_name FROM teachers WHERE login=? AND password=?", (login, password))
    else:
        c.execute("SELECT id, full_name, group_id FROM students WHERE login=? AND password=?", (login, password))
    result = c.fetchone()
    conn.close()
    return result


# ===== MARKS =====
def insert_mark(student_id, subject_id, teacher_id, group_id, mark):
    conn = connect()
    c = conn.cursor()
    c.execute("""INSERT INTO marks (student_id, subject_id, teacher_id, group_id, mark, put_date)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (student_id, subject_id, teacher_id, group_id, mark, date.today()))
    conn.commit()
    conn.close()


def get_student_marks(student_id):
    conn = connect()
    c = conn.cursor()
    c.execute("""SELECT s.name, m.mark, m.put_date, t.full_name
                 FROM marks m
                 JOIN subjects s ON m.subject_id = s.id
                 JOIN teachers t ON m.teacher_id = t.id
                 WHERE m.student_id = ?
                 ORDER BY m.put_date DESC""", (student_id,))
    data = c.fetchall()
    conn.close()
    return data


# ===== HOMEWORKS =====
def get_homeworks_for_student(group_id):
    """Возвращает домашние задания по group_id"""
    conn = connect()
    c = conn.cursor()
    c.execute("""
        SELECT s.name, h.task, h.deadline, t.full_name
        FROM homeworks h
        JOIN subjects s ON h.subject_id = s.id
        JOIN teachers t ON h.teacher_id = t.id
        WHERE h.group_id = ?
        ORDER BY h.deadline ASC
    """, (group_id,))
    rows = c.fetchall()
    conn.close()
    return rows


# ===== FAQ =====
def get_faq_answer(question_text):
    conn = connect()
    c = conn.cursor()
    clean_text = question_text.lower().replace('?', '').strip()
    c.execute("SELECT answer FROM faq WHERE lower(question) LIKE ?", (f"%{clean_text}%",))
    row = c.fetchone()
    conn.close()
    return row[0] if row else "❓ Ответ не найден."


# ===== EMOJI =====
def get_random_emoji():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT symbol FROM emojis")
    all_emo = [r[0] for r in c.fetchall()]
    conn.close()
    return random.choice(all_emo) if all_emo else "🙂"


# ===== STUDENTS BY TEACHER =====
def get_students_by_teacher(teacher_id):
    conn = connect()
    c = conn.cursor()
    c.execute("""SELECT DISTINCT st.id, st.full_name
                 FROM students st
                 JOIN marks m ON m.student_id = st.id
                 WHERE m.teacher_id = ?""", (teacher_id,))
    data = c.fetchall()
    conn.close()
    return data


# ===== SCHEDULES =====
def get_schedule_for_student(group_id):
    conn = connect()
    c = conn.cursor()
    weekday = datetime.now().strftime("%A")
    c.execute("""
        SELECT s.name, sch.time, t.full_name
        FROM schedules sch
        JOIN subjects s ON sch.subject_id = s.id
        JOIN teachers t ON sch.teacher_id = t.id
        WHERE sch.group_id = ? AND sch.weekday = ?
        ORDER BY sch.time
    """, (group_id, weekday))
    rows = c.fetchall()
    conn.close()
    return rows


def get_schedule_for_teacher(teacher_id):
    conn = connect()
    c = conn.cursor()
    weekday = datetime.now().strftime("%A")
    c.execute("""
        SELECT s.name, sch.time, g.name
        FROM schedules sch
        JOIN subjects s ON sch.subject_id = s.id
        JOIN groups g ON sch.group_id = g.id
        WHERE sch.teacher_id = ? AND sch.weekday = ?
        ORDER BY sch.time
    """, (teacher_id, weekday))
    rows = c.fetchall()
    conn.close()
    return rows


def setup_all():
    create_tables()
    print("✅ Все таблицы проверены или созданы успешно!")


if __name__ == "__main__":
    setup_all()