import psycopg2
from datetime import date, datetime
import random
from bot.config import POSTGRES_URL


def connect():
    return psycopg2.connect(
        database=POSTGRES_URL["database"],
        user=POSTGRES_URL["user"],
        password=POSTGRES_URL["password"],
        host=POSTGRES_URL["host"],
        port=POSTGRES_URL["port"],
    )



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
    c.execute("DELETE FROM users WHERE telegram_id = %s", (telegram_id,))
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

    result = c.fetchone()
    conn.close()
    return result



def insert_mark(student_id, subject_id, teacher_id, mark):
    conn = connect()
    c = conn.cursor()


    c.execute("SELECT group_id FROM students WHERE id = %s", (student_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return "❌ Студент с таким ID не найден."

    group_id = row[0]

    c.execute("""
        INSERT INTO marks (student_id, subject_id, teacher_id, group_id, mark, put_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (student_id, subject_id, teacher_id, group_id, mark, date.today()))

    conn.commit()
    conn.close()
    return "✅ Оценка успешно добавлена!"


def get_student_marks(student_id):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT s.name, m.mark, m.put_date, t.full_name
        FROM marks m
        JOIN subjects s ON m.subject_id = s.id
        JOIN teachers t ON m.teacher_id = t.id
        WHERE m.student_id = %s
        ORDER BY m.put_date DESC
    """, (student_id,))

    rows = c.fetchall()
    conn.close()
    return rows


# ===== HOMEWORKS =====
def get_homeworks_for_student(group_id):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT s.name, h.task, h.deadline, t.full_name
        FROM homeworks h
        JOIN subjects s ON h.subject_id = s.id
        JOIN teachers t ON h.teacher_id = t.id
        WHERE h.group_id = %s
        ORDER BY h.deadline ASC
    """, (group_id,))

    rows = c.fetchall()
    conn.close()
    return rows



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



def get_random_emoji():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT symbol FROM emojis")
    all_emo = [row[0] for row in c.fetchall()]

    conn.close()

    return random.choice(all_emo) if all_emo else "🙂"



def get_students_by_teacher(teacher_id):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT DISTINCT st.id, st.full_name
        FROM students st
        JOIN marks m ON m.student_id = st.id
        WHERE m.teacher_id = %s
    """, (teacher_id,))

    rows = c.fetchall()
    conn.close()
    return rows



def get_schedule_for_student(group_id):
    conn = connect()
    c = conn.cursor()

    weekday = datetime.now().strftime("%A")

    c.execute("""
        SELECT s.name, sch.time, t.full_name
        FROM schedules sch
        JOIN subjects s ON sch.subject_id = s.id
        JOIN teachers t ON sch.teacher_id = t.id
        WHERE sch.group_id = %s AND sch.weekday = %s
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
        WHERE sch.teacher_id = %s AND sch.weekday = %s
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
            VALUES (%s, %s, %s)
        """, (faq_id, user_id, liked))
        conn.commit()
    except Exception as e:
        print("[DB ERROR] Feedback insert failed:", e)
    finally:
        conn.close()



def insert_ai_log(telegram_id, username, request, response, model="deepseek"):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        INSERT INTO ai_logs (telegram_id, username, user_request, ai_response, model)
        VALUES (%s, %s, %s, %s, %s)
    """, (telegram_id, username, request, response, model))

    conn.commit()
    conn.close()