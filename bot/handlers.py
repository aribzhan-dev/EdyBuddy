import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from bot.database import *
from bot.config import DEEPSEEK_URL, AI_MODEL
import re
import difflib

user_state = {}


# ===== /START =====
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


# ===== UNIVERSAL MESSAGE HANDLER =====
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id


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
        step = state.get("step")

        print(f"DEBUG → step: {step} | text: {text}")


        if step == "login":
            state["login"] = text
            state["step"] = "password"
            await update.message.reply_text("Введите пароль 🔒:")
            return


        elif step == "password":
            state["password"] = text
            user = check_login(role, state["login"], state["password"])

            if not user:
                await update.message.reply_text("❌ Неверный логин или пароль.")
                del user_state[chat_id]
                return

            if role == "teacher":
                state["id"], state["name"] = user
                await show_teacher_menu(update)
            else:
                state["id"], state["name"], state["group_id"] = user
                await show_student_menu(update)

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


# ===== TEACHER MENU =====
async def show_teacher_menu(update: Update):
    keyboard = [
        [KeyboardButton("👨‍🎓 Мои студенты"), KeyboardButton("📝 Поставить оценку")],
        [KeyboardButton("📅 Мое расписание"), KeyboardButton("🎲 Случайный эмодзи")],
        [KeyboardButton("💬 FAQ"), KeyboardButton("🚪 Выйти")]
    ]
    await update.message.reply_text(
        "✅ Вы вошли как преподаватель 👨‍🏫",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ===== STUDENT MENU =====
async def show_student_menu(update: Update):
    keyboard = [
        [KeyboardButton("📊 Мои оценки"), KeyboardButton("📅 Расписание на сегодня")],
        [KeyboardButton("📚 Мои домашние задания"), KeyboardButton("💬 FAQ")],
        [KeyboardButton("🎲 Случайный эмодзи"), KeyboardButton("🚪 Выйти")]
    ]
    await update.message.reply_text(
        "✅ Вы вошли как студент 👩‍🎓",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ===== TEACHER ACTIONS =====
async def teacher_actions(update: Update, context, state):
    text = update.message.text
    teacher_id = state["id"]

    print(f"DEBUG → step: {state.get('step')} | text: {text}")


    if state.get("step") == "put_mark":
        try:
            print("DEBUG → inside put_mark")
            sid, mark = map(int, text.split())

            result = insert_mark(sid, 1, teacher_id, mark)

            print(f"DEBUG → insert_mark result: {result}")
            await update.message.reply_text(result)

            state["step"] = "menu"
            return

        except ValueError as e:
            print("DEBUG → ValueError:", e)
            await update.message.reply_text("⚠️ Формат неверный. Пример: 3 5")
            return


    if state.get("step") == "faq":
        await handle_faq(update, context, state)
        return


    if text == "👨‍🎓 Мои студенты":
        students = get_students_by_teacher(teacher_id)
        if not students:
            await update.message.reply_text("❗ У вас пока нет студентов.")
        else:
            msg = "📋 Ваши студенты:\n" + "\n".join(
                [f"{i+1}. {s[1]} (ID: {s[0]})" for i, s in enumerate(students)]
            )
            await update.message.reply_text(msg)

    elif text == "📝 Поставить оценку":
        await update.message.reply_text("Введите ID студента и оценку (например: 3 5)")
        state["step"] = "put_mark"
        print("DEBUG → step set to put_mark")
        return

    elif text == "📅 Мое расписание":
        weekday = datetime.now().strftime("%A")
        schedule = get_schedule_for_teacher(teacher_id)
        if not schedule:
            await update.message.reply_text(f"📅 Сегодня {weekday}.\nУ вас нет занятий.")
        else:
            msg = f"📅 Сегодня {weekday}:\n" + "\n".join(
                [f"{i+1}. {s[0]} ({s[1]}) — группа {s[2]}" for i, s in enumerate(schedule)]
            )
            await update.message.reply_text(msg)

    elif text == "💬 FAQ":
        await update.message.reply_text("Введите ваш вопрос:")
        state["step"] = "faq"

    elif text == "🎲 Случайный эмодзи":
        emoji = get_random_emoji()
        await update.message.reply_text(f"🎯 Ваш эмодзи: {emoji}")

    elif text == "🚪 Выйти":
        del user_state[update.effective_chat.id]
        await start_handler(update, context=None)


# ===== STUDENT ACTIONS =====
async def student_actions(update: Update, context, state):
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
        weekday = datetime.now().strftime("%A")
        schedule = get_schedule_for_student(group_id)
        if not schedule:
            await update.message.reply_text(f"📅 Сегодня {weekday}.\nУ вас нет пар.")
        else:
            msg = f"📅 Сегодня {weekday}:\n" + "\n".join(
                [f"{i+1}. {s[0]} ({s[1]}) — {s[2]}" for i, s in enumerate(schedule)]
            )
            await update.message.reply_text(msg)

    elif text == "📚 Мои домашние задания":
        homeworks = get_homeworks_for_student(group_id)
        if not homeworks:
            await update.message.reply_text("📭 Домашних заданий пока нет.")
        else:
            msg = "📘 Ваши домашние задания:\n\n" + "\n".join(
                [f"{i+1}. {h[0]} — {h[1]}\n📅 Срок: {h[2]}\n👨‍🏫 {h[3]}" for i, h in enumerate(homeworks)]
            )
            await update.message.reply_text(msg)

    elif text == "💬 FAQ":
        await update.message.reply_text("Введите ваш вопрос:")
        state["step"] = "faq"

    elif text == "🎲 Случайный эмодзи":
        emoji = get_random_emoji()
        await update.message.reply_text(f"🎯 Ваш эмодзи: {emoji}")

    elif text == "🚪 Выйти":
        del user_state[update.effective_chat.id]
        await start_handler(update, context=None)


# ======== AI-FAQ HANDLER ========
async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    text = update.message.text.strip()


    if text == "🏠 Главное меню":
        state["step"] = "menu"
        if state["role"] == "teacher":
            await show_teacher_menu(update)
        else:
            await show_student_menu(update)
        return


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
        print(f"DEBUG → FAQ match {best_score:.2f} with DB question")
        return


    await update.message.reply_text("🤔 Не найдено в базе, обращаюсь к AI...")

    payload = {
        "model": AI_MODEL,
        "prompt": f"Отвечай кратко и дружелюбно: {text}",
        "stream": False
    }
    try:
        response = requests.post(DEEPSEEK_URL, json=payload, timeout=60)
        ai_answer = response.json().get("response", "⚠️ Не удалось получить ответ.")
    except Exception as e:
        ai_answer = f"⚠️ Ошибка подключения к AI: {e}"

    emoji = get_random_emoji()
    keyboard = [
        [KeyboardButton("✅ Ответ полезный"), KeyboardButton("❌ Ответ не подходит")],
        [KeyboardButton("🏠 Главное меню")]
    ]
    await update.message.reply_text(
        f"{emoji} {ai_answer}",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

    state["step"] = "faq_feedback"
    state["faq_id"] = None


# ======== FEEDBACK HANDLER ========
async def handle_faq_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    text = update.message.text.strip()
    telegram_id = update.effective_user.id
    faq_id = state.get("faq_id")

    print(f"DEBUG → step: {state.get('step')} | text: {text}")


    if text == "🆕 Задать новый вопрос":
        await update.message.reply_text(
            "✍️ Напишите свой вопрос:",
            reply_markup=ReplyKeyboardRemove()
        )

        state["step"] = "faq"
        state["faq_id"] = None
        return


    if text == "🏠 Главное меню":
        state["step"] = "menu"
        if state["role"] == "teacher":
            await show_teacher_menu(update)
        else:
            await show_student_menu(update)
        return


    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    user_id = row[0] if row else None


    if text == "✅ Ответ полезный":
        await update.message.reply_text("😊 Рад, что помог!", reply_markup=ReplyKeyboardRemove())
        if user_id:
            insert_feedback(user_id, faq_id, 1)
    elif text == "❌ Ответ не подходит":
        await update.message.reply_text("😔 Жаль! Попробуйте задать вопрос иначе.", reply_markup=ReplyKeyboardRemove())
        if user_id:
            insert_feedback(user_id, faq_id, 0)
    else:
        await update.message.reply_text("📩 Напишите новый вопрос или вернитесь в меню.")
        return


    keyboard = [
        [KeyboardButton("🆕 Задать новый вопрос")],
        [KeyboardButton("🏠 Главное меню")]
    ]
    await update.message.reply_text(
        "📨 Что дальше?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


    state["step"] = "faq_feedback"