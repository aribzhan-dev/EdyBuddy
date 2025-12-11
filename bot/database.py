import sqlite3
from datetime import date, datetime
import random
from bot.config import DB_PATH


def connect():
    return sqlite3.connect(DB_PATH)


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



def insert_mark(student_id, subject_id, teacher_id, mark):
    conn = connect()
    c = conn.cursor()


    c.execute("SELECT group_id FROM students WHERE id = ?", (student_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return "❌ Студент с таким ID не найден."

    group_id = row[0]


    c.execute("""
        INSERT INTO marks (student_id, subject_id, teacher_id, group_id, mark, put_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (student_id, subject_id, teacher_id, group_id, mark, date.today()))
    conn.commit()
    conn.close()

    return "✅ Оценка успешно добавлена!"


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



def get_homeworks_for_student(group_id):
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


    clean_text = question_text.lower().replace('?', '').replace('!', '').replace('.', '').strip()

    c.execute("SELECT question, answer FROM faq")
    rows = c.fetchall()

    for q, a in rows:
        q_clean = q.lower().replace('?', '').replace('!', '').replace('.', '').strip()
        if q_clean == clean_text:
            conn.close()
            return a

    conn.close()
    return "❓ Ответ не найден."

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


def insert_feedback(user_id, faq_id, liked):
    conn = connect()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO feedback (faq_id, user_id, liked)
            VALUES (?, ?, ?)
        """, (faq_id, user_id, liked))
        conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Feedback insert failed: {e}")
    finally:
        conn.close()


def insert_ai_log(telegram_id, username, request, response, model="deepseek"):
    conn = connect()
    c = conn.cursor()
    c.execute("""
        INSERT INTO ai_logs (telegram_id, username, user_request, ai_response)
        VALUES (?, ?, ?, ?)
    """, (telegram_id, username, request, response))
    conn.commit()
    conn.close()


