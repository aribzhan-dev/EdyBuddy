import psycopg2
from datetime import date, datetime
import random
from bot.config import POSTGRES_URL


def connect():
    return psycopg2.connect(POSTGRES_URL)


# ---------------- USERS ----------------

def insert_user(telegram_id, username, full_name, role="unknown"):
    conn = connect()
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (telegram_id, username, full_name, role)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (telegram_id) DO NOTHING
    """, (telegram_id, username, full_name, role))
    conn.commit()
    conn.close()


def delete_user(telegram_id):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE telegram_id=%s", (telegram_id,))
    conn.commit()
    conn.close()




def check_login(role, login, password):
    conn = connect()
    c = conn.cursor()

    if role == "teacher":
        c.execute("""
            SELECT id, full_name
            FROM teachers
            WHERE login=%s AND password=%s
        """, (login, password))
    else:
        c.execute("""
            SELECT id, full_name, group_id
            FROM students
            WHERE login=%s AND password=%s
        """, (login, password))

    row = c.fetchone()
    conn.close()
    return row




def insert_mark(student_id, subject_id, teacher_id, mark, lang="ru"):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT group_id FROM students WHERE id=%s", (student_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return "❌ Студент не найден." if lang == "ru" else "❌ Студент табылмады."

    group_id = row[0]
    c.execute("""
        INSERT INTO marks (student_id, subject_id, teacher_id, group_id, mark, put_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (student_id, subject_id, teacher_id, group_id, mark, date.today()))

    conn.commit()
    conn.close()

    return "✅ Оценка добавлена!" if lang == "ru" else "✅ Баға қойылды!"


def get_student_marks(student_id):
    conn = connect()
    c = conn.cursor()
    c.execute("""
        SELECT s.name, m.mark, m.put_date, t.full_name
        FROM marks m
        JOIN subjects s ON m.subject_id = s.id
        JOIN teachers t ON t.id = m.teacher_id
        WHERE m.student_id = %s
        ORDER BY m.put_date DESC
    """, (student_id,))
    rows = c.fetchall()
    conn.close()
    return rows




def get_homeworks_for_student(group_id, lang):
    conn = connect()
    c = conn.cursor()
    c.execute("""
        SELECT s.name, h.title, h.description, h.deadline, t.full_name
        FROM homeworks h
        JOIN subjects s ON h.subject_id = s.id
        JOIN teachers t ON h.teacher_id = t.id
        WHERE h.group_id=%s AND h.lang_code=%s
        ORDER BY h.deadline ASC
    """, (group_id, lang))
    rows = c.fetchall()
    conn.close()
    return rows




def get_faq(lang):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, question, answer FROM faq WHERE lang_code=%s", (lang,))
    rows = c.fetchall()
    conn.close()
    return rows


def insert_feedback(user_id, faq_id, liked):
    conn = connect()
    c = conn.cursor()
    c.execute("""
        INSERT INTO feedback (faq_id, user_id, liked)
        VALUES (%s, %s, %s)
    """, (faq_id, user_id, liked))
    conn.commit()
    conn.close()




def get_schedule_for_student(group_id):
    conn = connect()
    c = conn.cursor()
    weekday = datetime.now().strftime("%A")

    c.execute("""
        SELECT s.name, sch.time, t.full_name
        FROM schedules sch
        JOIN subjects s ON sch.subject_id=s.id
        JOIN teachers t ON sch.teacher_id=t.id
        WHERE sch.group_id=%s AND sch.weekday=%s
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
        JOIN subjects s ON sch.subject_id=s.id
        JOIN groups g ON sch.group_id=g.id
        WHERE sch.teacher_id=%s AND sch.weekday=%s
        ORDER BY sch.time
    """, (teacher_id, weekday))

    rows = c.fetchall()
    conn.close()
    return rows


# ---------------- STUDENTS ----------------

def get_students_by_teacher(teacher_id):
    conn = connect()
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT s.id, s.full_name
        FROM students s
        JOIN schedules sch ON sch.group_id = s.group_id
        WHERE sch.teacher_id = %s
    """, (teacher_id,))
    rows = c.fetchall()
    conn.close()
    return rows


# ---------------- LOGS ----------------

def insert_ai_log(telegram_id, username, user_request, ai_response):
    conn = connect()
    c = conn.cursor()
    c.execute("""
        INSERT INTO ai_logs (telegram_id, username, user_request, ai_response)
        VALUES (%s, %s, %s, %s)
    """, (telegram_id, username or "", user_request, ai_response))
    conn.commit()
    conn.close()