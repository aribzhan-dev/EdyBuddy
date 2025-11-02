import sqlite3
from optparse import Values

DB_PATH = "data/edubuddy.db"

def connect():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = connect()
    c = conn.cursor()



    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        full_name TEXT,
        role TEXT CHECK(role IN ('teacher','student','unknown')) DEFAULT 'unknown'
    )
    """)

    # ===== GROUPS =====
    c.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    # ===== SUBJECTS =====
    c.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    # ===== TEACHERS =====
    c.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name VARCHAR(155),
        subject_id INTEGER,
        login VARCHAR(100) UNIQUE,
        password VARCHAR(100),
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    )
    """)

    # ===== STUDENTS =====
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name VARCHAR(100),
        group_id INTEGER,
        city VARCHAR(155),
        login VARCHAR(100) UNIQUE,
        password VARCHAR(100),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )
    """)

    # ===== SCHEDULES =====
    c.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        weekday TEXT,
        time TEXT,
        subject_id INTEGER,
        teacher_id INTEGER,
        group_id INTEGER,
        FOREIGN KEY(subject_id) REFERENCES subjects(id),
        FOREIGN KEY(teacher_id) REFERENCES teachers(id),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )
    """)

    # ===== MARKS =====
    c.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        teacher_id INTEGER,
        group_id INTEGER,
        mark INTEGER,
        put_date DATE,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(subject_id) REFERENCES subjects(id),
        FOREIGN KEY(teacher_id) REFERENCES teachers(id),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )
    """)

    # ===== HOMEWORKS =====
    c.execute("""
    CREATE TABLE IF NOT EXISTS homeworks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER,
        teacher_id INTEGER,
        group_id INTEGER,
        task TEXT,
        deadline DATE,
        FOREIGN KEY(subject_id) REFERENCES subjects(id),
        FOREIGN KEY(teacher_id) REFERENCES teachers(id),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )
    """)

    # ===== FAQ =====
    c.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT UNIQUE,
        answer TEXT
    )
    """)

    # ===== EMOJIS =====
    c.execute("""
    CREATE TABLE IF NOT EXISTS emojis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT
    )
    """)
    conn = connect()
    c = conn.cursor()

    # ===== GROUPS =====
    c.execute("""
              INSERT INTO groups (name)
              VALUES ('CS-101'),
                     ('CS-102'),
                     ('CS-103'),
                     ('IT-201'),
                     ('IT-202'),
                     ('AI-301'),
                     ('AI-302'),
                     ('SE-401'),
                     ('SE-402'),
                     ('CY-501')
              """)

    # ===== SUBJECTS =====
    c.execute("""
              INSERT INTO subjects (name)
              VALUES ('Программирование'),
                     ('Математика'),
                     ('Физика'),
                     ('История'),
                     ('Английский язык'),
                     ('Базы данных'),
                     ('Алгоритмы'),
                     ('Операционные системы'),
                     ('Компьютерные сети'),
                     ('Кибербезопасность')
              """)

    # ===== TEACHERS =====
    c.execute("""
              INSERT INTO teachers (full_name, subject_id, login, password)
              VALUES ('Иван Петров', 1, 'ivan_p', '1234'),
                     ('Мария Иванова', 2, 'maria_i', '1234'),
                     ('Алексей Смирнов', 3, 'alex_s', '1234'),
                     ('Ольга Кузнецова', 4, 'olga_k', '1234'),
                     ('Дмитрий Павлов', 5, 'dmitry_p', '1234'),
                     ('Наталья Соколова', 6, 'natalya_s', '1234'),
                     ('Сергей Волков', 7, 'sergey_v', '1234'),
                     ('Анна Лебедева', 8, 'anna_l', '1234'),
                     ('Роман Новиков', 9, 'roman_n', '1234'),
                     ('Екатерина Попова', 10, 'ekaterina_p', '1234')
              """)

    # ===== STUDENTS =====
    c.execute("""
              INSERT INTO students (full_name, group_id, city, login, password)
              VALUES ('Азамат Алиев', 1, 'Астана', 'azamat_a', '1234'),
                     ('Айгерим Нурлан', 1, 'Астана', 'aigerim_n', '1234'),
                     ('Ержан Касым', 2, 'Алматы', 'yerzhan_k', '1234'),
                     ('Диана Рахим', 2, 'Алматы', 'diana_r', '1234'),
                     ('Мадияр Бек', 3, 'Шымкент', 'madiyar_b', '1234'),
                     ('Айдана Тлеубек', 3, 'Шымкент', 'aidana_t', '1234'),
                     ('Арман Жан', 4, 'Караганда', 'arman_j', '1234'),
                     ('Салтанат Ермек', 5, 'Павлодар', 'saltanat_e', '1234'),
                     ('Ербол Сагын', 6, 'Атырау', 'erbol_s', '1234'),
                     ('Жансая Ахмет', 7, 'Костанай', 'zhansaya_a', '1234')
              """)

    # ===== SCHEDULES =====
    c.execute("""
              INSERT INTO schedules (weekday, time, subject_id, teacher_id, group_id)
              VALUES ('Monday', '09:00', 1, 1, 1),
                     ('Monday', '11:00', 2, 2, 1),
                     ('Tuesday', '09:00', 3, 3, 2),
                     ('Tuesday', '11:00', 4, 4, 2),
                     ('Wednesday', '10:00', 5, 5, 3),
                     ('Wednesday', '12:00', 6, 6, 3),
                     ('Thursday', '09:00', 7, 7, 4),
                     ('Thursday', '11:00', 8, 8, 5),
                     ('Friday', '09:00', 9, 9, 6),
                     ('Friday', '11:00', 10, 10, 7)
              """)

    # ===== MARKS =====
    c.execute("""
              INSERT INTO marks (student_id, subject_id, teacher_id, group_id, mark, put_date)
              VALUES (1, 1, 1, 1, 5, '2025-10-25'),
                     (2, 1, 1, 1, 4, '2025-10-25'),
                     (3, 3, 3, 2, 5, '2025-10-26'),
                     (4, 3, 3, 2, 3, '2025-10-26'),
                     (5, 5, 5, 3, 5, '2025-10-27'),
                     (6, 5, 5, 3, 4, '2025-10-27'),
                     (7, 7, 7, 4, 5, '2025-10-28'),
                     (8, 8, 8, 5, 4, '2025-10-28'),
                     (9, 9, 9, 6, 5, '2025-10-29'),
                     (10, 10, 10, 7, 5, '2025-10-29')
              """)

    # ===== HOMEWORKS =====
    c.execute("""
              INSERT INTO homeworks (subject_id, teacher_id, group_id, task, deadline)
              VALUES (1, 1, 1, 'Сделать проект на Python', '2025-11-05'),
                     (2, 2, 1, 'Решить 10 задач по математике', '2025-11-06'),
                     (3, 3, 2, 'Подготовить лабораторную работу №3', '2025-11-07'),
                     (4, 4, 2, 'Прочитать главы 2 и 3 по истории', '2025-11-08'),
                     (5, 5, 3, 'Выучить 20 новых слов на английском', '2025-11-09'),
                     (6, 6, 3, 'Создать ER-диаграмму для базы данных', '2025-11-10'),
                     (7, 7, 4, 'Написать псевдокод алгоритма', '2025-11-11'),
                     (8, 8, 5, 'Сделать отчёт по системам', '2025-11-12'),
                     (9, 9, 6, 'Нарисовать схему сети', '2025-11-13'),
                     (10, 10, 7, 'Пройти тест по безопасности', '2025-11-14')
              """)

    # ===== FAQ =====
    c.execute("""
              INSERT INTO faq (question, answer)
              VALUES ('Когда сессия?', 'Сессия начнётся 10 декабря.'),
                     ('Есть ли пары сегодня?', 'Да, проверь расписание.'),
                     ('Когда каникулы?', 'Каникулы начнутся 25 декабря.'),
                     ('Сколько длится пара?', 'Одна пара длится 90 минут.'),
                     ('Можно ли пересдать экзамен?', 'Да, после разрешения преподавателя.'),
                     ('Где кабинет директора?', 'На втором этаже, комната №205.'),
                     ('Когда сдавать отчёт?', 'Отчёт нужно сдать до конца недели.'),
                     ('Можно ли учиться дистанционно?', 'Да, по согласованию с куратором.'),
                     ('Как узнать свои оценки?', 'Через раздел "Мои оценки" в боте.'),
                     ('Есть ли завтра пары?', 'Проверь расписание на завтра.')
              """)

    # ===== EMOJIS =====
    c.execute("""
              INSERT INTO emojis (symbol)
              VALUES ('😀'),
                     ('😇'),
                     ('🤓'),
                     ('😎'),
                     ('🥳'),
                     ('😴'),
                     ('🤖'),
                     ('🐍'),
                     ('🔥'),
                     ('💪')
              """)




    conn.commit()
    conn.close()
    print("✅ Таблицы созданы и данные добавлены успешно!")


if __name__ == "__main__":
    create_tables()