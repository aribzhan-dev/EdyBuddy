from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import *
from datetime import datetime

# User states in memory
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

    # 1️⃣ Выбор роли
    if text == "👨‍🏫 Преподаватель":
        user_state[chat_id] = {"role": "teacher", "step": "login"}
        await update.message.reply_text("Введите логин 👤:")
        return

    if text == "👩‍🎓 Студент":
        user_state[chat_id] = {"role": "student", "step": "login"}
        await update.message.reply_text("Введите логин 👤:")
        return

    # 2️⃣ Авторизация
    if chat_id in user_state:
        state = user_state[chat_id]
        role = state["role"]

        # Логин
        if state["step"] == "login":
            state["login"] = text
            state["step"] = "password"
            await update.message.reply_text("Введите пароль 🔒:")
            return

        # Пароль
        elif state["step"] == "password":
            state["password"] = text
            user = check_login(role, state["login"], state["password"])
            if not user:
                await update.message.reply_text("❌ Неверный логин или пароль.")
                del user_state[chat_id]
                return

            # Если преподаватель
            if role == "teacher":
                state["id"], state["name"] = user
                await show_teacher_menu(update)
            else:
                state["id"], state["name"], state["group_id"] = user
                await show_student_menu(update)
            state["step"] = "menu"
            return

        # ✅ Все дальнейшие действия
        if role == "teacher":
            await teacher_actions(update, state)
        else:
            await student_actions(update, state)


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
async def teacher_actions(update: Update, state):
    text = update.message.text
    teacher_id = state["id"]

    #  Мои студенты
    if text == "👨‍🎓 Мои студенты":
        students = get_students_by_teacher(teacher_id)
        if not students:
            await update.message.reply_text("❗ У вас пока нет студентов.")
        else:
            msg = "📋 Ваши студенты:\n" + "\n".join(
                [f"{i+1}. {s[1]} (ID: {s[0]})" for i, s in enumerate(students)]
            )
            await update.message.reply_text(msg)

    #  Поставить оценку
    elif text == "📝 Поставить оценку":
        await update.message.reply_text("Введите ID студента и оценку (например: 3 5)")
        state["step"] = "put_mark"
        return

    elif state.get("step") == "put_mark":
        try:
            sid, mark = map(int, text.split())
            insert_mark(sid, 1, teacher_id, 1, mark)  # временно subject_id=1, group_id=1
            await update.message.reply_text("✅ Оценка успешно добавлена!")
            state["step"] = "menu"
        except:
            await update.message.reply_text("⚠️ Формат неверный. Пример: 3 5")

    #  Расписание
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

    #  FAQ
    elif text == "💬 FAQ":
        await update.message.reply_text("Введите ваш вопрос:")
        state["step"] = "faq"

    elif state.get("step") == "faq":
        answer = get_faq_answer(text)
        await update.message.reply_text(answer)
        state["step"] = "menu"

    #  Случайный эмодзи
    elif text == "🎲 Случайный эмодзи":
        emoji = get_random_emoji()
        await update.message.reply_text(f"🎯 Ваш эмодзи: {emoji}")

    #  Выйти
    elif text == "🚪 Выйти":
        del user_state[update.effective_chat.id]
        await start_handler(update, context=None)


# ===== STUDENT ACTIONS =====
async def student_actions(update: Update, state):
    text = update.message.text
    sid = state["id"]
    group_id = state["group_id"]

    #  Мои оценки
    if text == "📊 Мои оценки":
        marks = get_student_marks(sid)
        if not marks:
            await update.message.reply_text("📭 У вас пока нет оценок.")
        else:
            msg = "\n".join(
                [f"{m[0]} — {m[1]} ({m[2]}) — {m[3]}" for m in marks]
            )
            await update.message.reply_text("📚 Ваши оценки:\n" + msg)

    #  Расписание
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

    #  Мои домашние задания
    elif text == "📚 Мои домашние задания":
        homeworks = get_homeworks_for_student(group_id)
        if not homeworks:
            await update.message.reply_text("📭 Домашних заданий пока нет.")
        else:
            msg = "📘 Ваши домашние задания:\n\n" + "\n".join(
                [f"{i+1}. {h[0]} — {h[1]}\n📅 Срок: {h[2]}\n👨‍🏫 {h[3]}" for i, h in enumerate(homeworks)]
            )
            await update.message.reply_text(msg)

    #  FAQ
    elif text == "💬 FAQ":
        await update.message.reply_text("Введите ваш вопрос:")
        state["step"] = "faq"

    elif state.get("step") == "faq":
        answer = get_faq_answer(text)
        await update.message.reply_text(answer)
        state["step"] = "menu"

    #  Случайный эмодзи
    elif text == "🎲 Случайный эмодзи":
        emoji = get_random_emoji()
        await update.message.reply_text(f"🎯 Ваш эмодзи: {emoji}")

    #  Выйти
    elif text == "🚪 Выйти":
        del user_state[update.effective_chat.id]
        await start_handler(update, context=None)