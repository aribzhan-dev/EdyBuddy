import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from bot.db import *
from bot.config import DEEPSEEK_URL, AI_MODEL
import re
import difflib

user_state = {}


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    username = update.effective_user.username or "пользователь"
    full_name = update.effective_user.full_name

    insert_user(telegram_id, username, full_name)

    text = f"👋 Привет, @{username}!\nДобро пожаловать в *EduBuddy* 📚"
    keyboard = [[KeyboardButton("👨‍🏫 Преподаватель"), KeyboardButton("👩‍🎓 Студент")]]

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )




async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    # Role selection
    if text == "👨‍🏫 Преподаватель":
        user_state[chat_id] = {"role": "teacher", "step": "login"}
        await update.message.reply_text("Введите логин 👤:")
        return

    if text == "👩‍🎓 Студент":
        user_state[chat_id] = {"role": "student", "step": "login"}
        await update.message.reply_text("Введите логин 👤:")
        return


    if chat_id in user_state:
        state = user_state[chat_id]
        role = state["role"]
        step = state["step"]

        # LOGIN
        if step == "login":
            state["login"] = text
            state["step"] = "password"
            await update.message.reply_text("Введите пароль 🔒:")
            return

        # PASSWORD
        elif step == "password":
            state["password"] = text
            user = check_login(role, state["login"], state["password"])

            if not user:
                await update.message.reply_text("❌ Неверный логин или пароль.")
                del user_state[chat_id]
                return


            if role == "teacher":
                state["id"], state["name"] = user
                await show_teacher_menu(update, context)


            else:
                state["id"], state["name"], state["group_id"] = user
                await show_student_menu(update, context)

            state["step"] = "menu"
            return


        elif step == "faq":
            await handle_faq(update, context, state)
            return

        elif step == "faq_feedback":
            await handle_faq_feedback(update, context, state)
            return


        elif role == "teacher":
            await teacher_actions(update, context, state)
        else:
            await student_actions(update, context, state)




async def show_teacher_menu(update: Update, context):
    keyboard = [
        [KeyboardButton("👨‍🎓 Мои студенты"), KeyboardButton("📝 Поставить оценку")],
        [KeyboardButton("📅 Мое расписание"), KeyboardButton("🎲 Случайный эмодзи")],
        [KeyboardButton("💬 FAQ"), KeyboardButton("🚪 Выйти")]
    ]
    await update.message.reply_text(
        "✅ Вы вошли как преподаватель 👨‍🏫",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )




async def show_student_menu(update: Update, context):
    keyboard = [
        [KeyboardButton("📊 Мои оценки"), KeyboardButton("📅 Расписание на сегодня")],
        [KeyboardButton("📚 Мои домашние задания"), KeyboardButton("💬 FAQ")],
        [KeyboardButton("🎲 Случайный эмодзи"), KeyboardButton("🚪 Выйти")]
    ]
    await update.message.reply_text(
        "✅ Вы вошли как студент 👩‍🎓",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )



async def teacher_actions(update, context, state):
    text = update.message.text
    teacher_id = state["id"]


    if state.get("step") == "put_mark":
        try:
            sid, mark = map(int, text.split())
            result = insert_mark(sid, 1, teacher_id, mark)
            await update.message.reply_text(result)
            state["step"] = "menu"
            return
        except:
            await update.message.reply_text("⚠️ Формат неверный. Пример: 3 5")
            return

    if text == "📝 Поставить оценку":
        await update.message.reply_text("Введите ID студента и оценку (например: 3 5)")
        state["step"] = "put_mark"
        return

    if text == "👨‍🎓 Мои студенты":
        students = get_students_by_teacher(teacher_id)
        if not students:
            await update.message.reply_text("❗ У вас пока нет студентов.")
        else:
            msg = "\n".join([f"{i+1}. {s[1]} (ID: {s[0]})" for i, s in enumerate(students)])
            await update.message.reply_text("📋 Ваши студенты:\n" + msg)

    elif text == "📅 Мое расписание":
        schedule = get_schedule_for_teacher(teacher_id)
        if not schedule:
            await update.message.reply_text("📅 Сегодня нет занятий.")
        else:
            msg = "\n".join([f"{i+1}. {s[0]} ({s[1]}) — группа {s[2]}" for i, s in enumerate(schedule)])
            await update.message.reply_text("📅 Сегодня:\n" + msg)

    elif text == "💬 FAQ":
        await update.message.reply_text("Введите ваш вопрос:")
        state["step"] = "faq"

    elif text == "🎲 Случайный эмодзи":
        emoji = get_random_emoji()
        await update.message.reply_text(f"🎯 Ваш эмодзи: {emoji}")

    elif text == "🚪 Выйти":
        del user_state[update.effective_chat.id]
        await start_handler(update, context)



async def student_actions(update, context, state):
    text = update.message.text
    sid = state["id"]
    group_id = state["group_id"]

    if text == "📊 Мои оценки":
        marks = get_student_marks(sid)
        if not marks:
            await update.message.reply_text("📭 У вас пока нет оценок.")
        else:
            msg = "\n".join([f"{m[0]} — {m[1]} ({m[2]}) — {m[3]}" for m in marks])
            await update.message.reply_text("📚 Ваши оценки:\n" + msg)

    elif text == "📅 Расписание на сегодня":
        schedule = get_schedule_for_student(group_id)
        if not schedule:
            await update.message.reply_text("📅 Сегодня нет пар.")
        else:
            msg = "\n".join([f"{i+1}. {s[0]} ({s[1]}) — {s[2]}" for i, s in enumerate(schedule)])
            await update.message.reply_text("📅 Сегодня:\n" + msg)

    elif text == "📚 Мои домашние задания":
        hw = get_homeworks_for_student(group_id)
        if not hw:
            await update.message.reply_text("📭 Домашних заданий нет.")
        else:
            msg = "\n".join([f"{i+1}. {h[0]} — {h[1]}\n📅 Срок: {h[2]}\n👨‍🏫 {h[3]}" for i, h in enumerate(hw)])
            await update.message.reply_text("📘 Ваши ДЗ:\n" + msg)

    elif text == "💬 FAQ":
        state["step"] = "faq"
        await update.message.reply_text("Введите ваш вопрос:")

    elif text == "🎲 Случайный эмодзи":
        await update.message.reply_text(f"🎯 {get_random_emoji()}")

    elif text == "🚪 Выйти":
        del user_state[update.effective_chat.id]
        await start_handler(update, context)



async def handle_faq(update, context, state):
    text = update.message.text.strip()
    clean_text = re.sub(r"[^\w\s]", "", text.lower())


    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, question, answer FROM faq")
    faqs = c.fetchall()
    conn.close()


    best_match = None
    best_score = 0.0

    for faq_id, question, answer in faqs:
        q_clean = re.sub(r"[^\w\s]", "", question.lower())
        score = difflib.SequenceMatcher(None, clean_text, q_clean).ratio()
        if score > best_score:
            best_score = score
            best_match = (faq_id, answer)

    # FOUND IN DB
    if best_score >= 0.7:
        faq_id, db_answer = best_match
        emoji = get_random_emoji()

        keyboard = [
            [KeyboardButton("✅ Ответ полезный"), KeyboardButton("❌ Ответ не подходит")],
            [KeyboardButton("🏠 Главное меню")]
        ]

        await update.message.reply_text(
            f"{emoji} {db_answer}",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

        state["step"] = "faq_feedback"
        state["faq_id"] = faq_id
        return


    await update.message.reply_text("🤔 Не найдено в базе, обращаюсь к AI...")

    payload = {
        "model": AI_MODEL,
        "prompt": f"Отвечай кратко и дружелюбно: {text}",
        "stream": False
    }

    try:
        response = requests.post(DEEPSEEK_URL, json=payload, timeout=40)
        ai_answer = response.json().get("response", "⚠️ AI не ответил.")
    except:
        ai_answer = "⚠️ Ошибка подключения к AI."

    insert_ai_log(update.effective_user.id, update.effective_user.username, text, ai_answer)

    keyboard = [
        [KeyboardButton("✅ Ответ полезный"), KeyboardButton("❌ Ответ не подходит")],
        [KeyboardButton("🏠 Главное меню")]
    ]

    await update.message.reply_text(
        f"{get_random_emoji()} {ai_answer}",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

    state["step"] = "faq_feedback"
    state["faq_id"] = None


async def handle_faq_feedback(update, context, state):
    text = update.message.text
    telegram_id = update.effective_user.id
    faq_id = state.get("faq_id")


    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
    row = c.fetchone()
    conn.close()

    user_id = row[0] if row else None

    if text == "✅ Ответ полезный":
        if user_id:
            insert_feedback(user_id, faq_id, 1)
        await update.message.reply_text("😊 Рад, что помог!", reply_markup=ReplyKeyboardRemove())

    elif text == "❌ Ответ не подходит":
        if user_id:
            insert_feedback(user_id, faq_id, 0)
        await update.message.reply_text("😔 Жаль! Попробуйте иначе.", reply_markup=ReplyKeyboardRemove())

    keyboard = [
        [KeyboardButton("🆕 Задать новый вопрос")],
        [KeyboardButton("🏠 Главное меню")]
    ]

    await update.message.reply_text(
        "📨 Что дальше?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

    state["step"] = "faq_feedback"