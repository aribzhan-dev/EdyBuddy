import requests
import re
import difflib
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import ContextTypes

from bot.db import *
from bot.config import DEEPSEEK_URL, AI_MODEL

user_state = {}

TEXTS = {
    "start_welcome": {
        "ru": "👋 Добро пожаловать в EduBuddy!\nВыберите язык:",
        "kz": "👋 EduBuddy-ге қош келдіңіз!\nТілді таңдаңыз:"
    },

    "lang_choose": {
        "ru": "🇷🇺 Язык: русский.",
        "kz": "🇰🇿 Тіл: қазақ тілі."
    },

    "role_teacher": {"ru": "👨‍🏫 Преподаватель", "kz": "👨‍🏫 Оқытушы"},
    "role_student": {"ru": "👩‍🎓 Студент", "kz": "👩‍🎓 Студент"},
    "ask_login": {"ru": "Введите логин 👤:", "kz": "Логин енгізіңіз 👤:"},
    "ask_password": {"ru": "Введите пароль 🔒:", "kz": "Құпиясөз енгізіңіз 🔒:"},
    "login_error": {"ru": "❌ Неверный логин или пароль.", "kz": "❌ Логин немесе құпиясөз қате."},
    "menu_teacher": {"ru": "👨‍🏫 Главное меню преподавателя", "kz": "👨‍🏫 Оқытушының басты мәзірі"},
    "teacher_students": {"ru": "👨‍🎓 Мои студенты", "kz": "👨‍🎓 Менің студенттерім"},
    "teacher_putmark": {"ru": "📝 Поставить оценку", "kz": "📝 Баға қою"},
    "teacher_schedule": {"ru": "📅 Мое расписание", "kz": "📅 Менің кестем"},
    "menu_student": {"ru": "👩‍🎓 Меню студента", "kz": "👩‍🎓 Студент мәзірі"},
    "student_marks": {"ru": "📊 Мои оценки", "kz": "📊 Менің бағаларым"},
    "student_today": {"ru": "📅 Расписание на сегодня", "kz": "📅 Бүгінгі кесте"},
    "student_hw": {"ru": "📚 Мои домашние задания", "kz": "📚 Үй тапсырмаларым"},
    "faq_btn": {"ru": "💬 FAQ", "kz": "💬 FAQ"},
    "faq_enter": {"ru": "Введите ваш вопрос:", "kz": "Сұрағыңызды жазыңыз:"},
    "answer_good_btn": {"ru": "✅ Ответ полезный", "kz": "✅ Жауап пайдалы"},
    "answer_bad_btn": {"ru": "❌ Ответ не подходит", "kz": "❌ Жауап сәйкес емес"},
    "answer_good": {"ru": "😊 Рад, что помог!", "kz": "😊 Көмектесе алғаныма қуаныштымын!"},
    "answer_bad": {"ru": "😔 Жаль! Попробуйте иначе.", "kz": "😔 Өкінішті! Басқаша қойып көріңіз."},
    "main_menu": {"ru": "🏠 Главное меню", "kz": "🏠 Басты мәзір"},
    "new_question": {"ru": "🆕 Задать новый вопрос", "kz": "🆕 Жаңа сұрақ қою"},
    "what_next": {"ru": "📨 Что дальше?", "kz": "📨 Келесі қадам?"},
    "settings_btn": {"ru": "⚙️ Настройки", "kz": "⚙️ Баптаулар"},
    "change_login_btn": {"ru": "🔑 Изменить логин", "kz": "🔑 Логинді өзгерту"},
    "change_password_btn": {"ru": "🔒 Изменить пароль", "kz": "🔒 Құпиясөзді өзгерту"},
    "enter_new_login": {"ru": "Введите новый логин:", "kz": "Жаңа логин енгізіңіз:"},
    "enter_new_password": {"ru": "Введите новый пароль:", "kz": "Жаңа құпиясөз енгізіңіз:"},
    "change_success_login": {"ru": "✅ Логин успешно изменён!", "kz": "✅ Логин сәтті өзгертілді!"},
    "change_success_password": {"ru": "✅ Пароль успешно изменён!", "kz": "✅ Құпиясөз сәтті өзгертілді!"},
    "map_btn": {"ru": "🗺 Карта AITU", "kz": "🗺 AITU картасы"},
    "exit_btn": {"ru": "🚪 Выйти", "kz": "🚪 Шығу"}
}



async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id

    user_state[cid] = {"step": "choose_lang"}

    keyboard = [[KeyboardButton("🇷🇺 Русский"), KeyboardButton("🇰🇿 Қазақша")]]

    await update.message.reply_text(
        TEXTS["start_welcome"]["ru"] + "\n\n" + TEXTS["start_welcome"]["kz"],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )




async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    cid = update.effective_chat.id

    if cid not in user_state:
        await start_handler(update, context)
        return

    state = user_state[cid]
    step = state.get("step")


    if step == "choose_lang":
        if text == "🇷🇺 Русский":
            lang = "ru"
        elif text == "🇰🇿 Қазақша":
            lang = "kz"
        else:
            return

        state["lang"] = lang
        state["step"] = "role_choose"

        await update.message.reply_text(TEXTS["lang_choose"][lang], reply_markup=ReplyKeyboardRemove())

        kb = [[KeyboardButton(TEXTS["role_teacher"][lang]),
               KeyboardButton(TEXTS["role_student"][lang])]]

        await update.message.reply_text(
            "Выберите роль:" if lang == "ru" else "Рөліңізді таңдаңыз:",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
        )
        return


    if step == "role_choose":
        lang = state["lang"]

        if text == TEXTS["role_teacher"][lang]:
            state["role"] = "teacher"
        elif text == TEXTS["role_student"][lang]:
            state["role"] = "student"
        else:
            return

        state["step"] = "login"
        await update.message.reply_text(TEXTS["ask_login"][lang])
        return


    if step == "login":
        state["login"] = text
        state["step"] = "password"
        await update.message.reply_text(TEXTS["ask_password"][state["lang"]])
        return


    if step == "password":
        lang = state["lang"]
        role = state["role"]

        user = check_login(role, state["login"], text)

        if not user:
            await update.message.reply_text(TEXTS["login_error"][lang])
            del user_state[cid]
            return

        if role == "teacher":
            state["id"], state["name"] = user
            await show_teacher_menu(update, state)
        else:
            state["id"], state["name"], state["group_id"] = user
            await show_student_menu(update, state)

        state["step"] = "menu"
        return


    if step == "faq":
        await handle_faq(update, state)
        return

    if step == "faq_feedback":
        await handle_faq_feedback(update, state)
        return


    if step == "settings":
        await settings_actions(update, state)
        return

    if step == "change_login":
        await change_login(update, state)
        return

    if step == "change_password":
        await change_password(update, state)
        return


    if state.get("role") == "teacher":
        await teacher_actions(update, state)
    else:
        await student_actions(update, state)

    if state == "map":
        await update.message.reply_text("🔗 AITU Map:")
        await update.message.reply_text("https://yuujiso.github.io/aitumap/")
        return



async def show_teacher_menu(update, state):
    lang = state["lang"]

    kb = [
        [KeyboardButton(TEXTS["teacher_students"][lang]), KeyboardButton(TEXTS["teacher_putmark"][lang])],
        [KeyboardButton(TEXTS["teacher_schedule"][lang]), KeyboardButton(TEXTS["faq_btn"][lang])],
        [KeyboardButton(TEXTS["settings_btn"][lang]), KeyboardButton(TEXTS["map_btn"][lang])],
        [KeyboardButton(TEXTS["exit_btn"][lang])]
    ]

    await update.message.reply_text(
        TEXTS["menu_teacher"][lang],
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )


async def show_student_menu(update, state):
    lang = state["lang"]

    kb = [
        [KeyboardButton(TEXTS["student_marks"][lang]), KeyboardButton(TEXTS["student_today"][lang])],
        [KeyboardButton(TEXTS["student_hw"][lang]), KeyboardButton(TEXTS["faq_btn"][lang])],
        [KeyboardButton(TEXTS["settings_btn"][lang]), KeyboardButton(TEXTS["map_btn"][lang])],
        [KeyboardButton(TEXTS["exit_btn"][lang])]
    ]

    await update.message.reply_text(
        TEXTS["menu_student"][lang],
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )




async def teacher_actions(update, state):
    text = update.message.text
    lang = state["lang"]
    tid = state["id"]


    if state.get("step") == "put_mark":
        try:
            sid, mark = map(int, text.split())
            msg = insert_mark(sid, 1, tid, mark, lang)
            await update.message.reply_text(msg)
            state["step"] = "menu"
            return
        except:
            await update.message.reply_text("Формат неверный" if lang == "ru" else "Пішім қате")
            return

    if text == TEXTS["teacher_putmark"][lang]:
        state["step"] = "put_mark"
        await update.message.reply_text("Пример: 3 5" if lang == "ru" else "Мысалы: 3 5")
        return

    if text == TEXTS["teacher_students"][lang]:
        students = get_students_by_teacher(tid)
        if not students:
            await update.message.reply_text("Студентов нет." if lang == "ru" else "Студенттер жоқ.")
        else:
            msg = "\n".join([f"{i+1}. {s[1]} (ID: {s[0]})" for i, s in enumerate(students)])
            await update.message.reply_text(msg)
        return

    if text == TEXTS["teacher_schedule"][lang]:
        sched = get_schedule_for_teacher(tid)
        if not sched:
            await update.message.reply_text("Нет расписания." if lang == "ru" else "Кесте жоқ.")
        else:
            msg = "\n".join([f"{s[0]} — {s[1]}" for s in sched])
            await update.message.reply_text(msg)
        return

    if text == TEXTS["faq_btn"][lang]:
        state["step"] = "faq"
        await update.message.reply_text(TEXTS["faq_enter"][lang])
        return

    if text == TEXTS["settings_btn"][lang]:
        state["step"] = "settings"
        await settings_actions(update, state)
        return

    if text == TEXTS["map_btn"][lang]:
        state["step"] = "map"
        await update.message.reply_text("Открываю карту..." if lang == "ru" else "Картаны ашамын...")
        await update.message.reply_text("https://yuujiso.github.io/aitumap/")
        return

    if text == TEXTS["exit_btn"][lang]:
        del user_state[update.effective_chat.id]
        await start_handler(update, None)
        return




async def student_actions(update, state):
    text = update.message.text
    lang = state["lang"]
    sid = state["id"]
    gid = state["group_id"]

    if text == TEXTS["student_marks"][lang]:
        marks = get_student_marks(sid)
        if not marks:
            await update.message.reply_text("Пока нет оценок." if lang == "ru" else "Бағалар жоқ.")
        else:
            msg = "\n".join([f"{m[0]} — {m[1]} ({m[2]})" for m in marks])
            await update.message.reply_text(msg)
        return

    if text == TEXTS["student_hw"][lang]:
        hw = get_homeworks_for_student(gid, lang)
        if not hw:
            await update.message.reply_text("Домашних заданий нет." if lang == "ru" else "Үй тапсырмалары жоқ.")
        else:
            msg = "\n".join([
                f"📘 {h[0]}\n📝 {h[1]}\n📄 {h[2]}\n📅 {h[3]}\n👨‍🏫 {h[4]}\n"
                for h in hw
            ])
            await update.message.reply_text(msg)
        return

    if text == TEXTS["student_today"][lang]:
        sched = get_schedule_for_student(gid)
        if not sched:
            await update.message.reply_text("Нет расписания." if lang == "ru" else "Кесте жоқ.")
        else:
            msg = "\n".join([f"{s[0]} — {s[1]} — {s[2]}" for s in sched])
            await update.message.reply_text(msg)
        return

    if text == TEXTS["faq_btn"][lang]:
        state["step"] = "faq"
        await update.message.reply_text(TEXTS["faq_enter"][lang])
        return

    if text == TEXTS["settings_btn"][lang]:
        state["step"] = "settings"
        await settings_actions(update, state)
        return

    if text == TEXTS["map_btn"][lang]:
        state["step"] = "map"
        await update.message.reply_text("Открываю карту..." if lang == "ru" else "Картаны ашамын...")
        await update.message.reply_text("https://yuujiso.github.io/aitumap/")
        return

    if text == TEXTS["exit_btn"][lang]:
        del user_state[update.effective_chat.id]
        await start_handler(update, None)
        return




async def settings_actions(update, state):
    text = update.message.text
    lang = state["lang"]

    if text == TEXTS["settings_btn"][lang]:
        kb = [
            [KeyboardButton(TEXTS["change_login_btn"][lang])],
            [KeyboardButton(TEXTS["change_password_btn"][lang])],
            [KeyboardButton(TEXTS["main_menu"][lang])]
        ]

        await update.message.reply_text(
            TEXTS["settings_btn"][lang],
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
        )
        return

    if text == TEXTS["change_login_btn"][lang]:
        state["step"] = "change_login"
        await update.message.reply_text(TEXTS["enter_new_login"][lang])
        return

    if text == TEXTS["change_password_btn"][lang]:
        state["step"] = "change_password"
        await update.message.reply_text(TEXTS["enter_new_password"][lang])
        return

    if text == TEXTS["main_menu"][lang]:
        state["step"] = "menu"
        if state["role"] == "teacher":
            await show_teacher_menu(update, state)
        else:
            await show_student_menu(update, state)
        return



async def change_login(update, state):
    lang = state["lang"]
    role = state["role"]
    uid = state["id"]
    new_login = update.message.text

    update_login(role, uid, new_login)

    await update.message.reply_text(TEXTS["change_success_login"][lang])

    state["step"] = "menu"
    if role == "teacher":
        await show_teacher_menu(update, state)
    else:
        await show_student_menu(update, state)


async def change_password(update, state):
    lang = state["lang"]
    role = state["role"]
    uid = state["id"]
    new_pass = update.message.text

    update_password(role, uid, new_pass)

    await update.message.reply_text(TEXTS["change_success_password"][lang])

    state["step"] = "menu"
    if role == "teacher":
        await show_teacher_menu(update, state)
    else:
        await show_student_menu(update, state)



async def handle_faq(update, state):
    lang = state["lang"]
    query = update.message.text.strip()

    clean = re.sub(r"[^\w\s]", "", query.lower())

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, question, answer FROM faq")
    faqs = c.fetchall()
    conn.close()

    best = None
    score = 0

    for fid, q, a in faqs:
        qc = re.sub(r"[^\w\s]", "", q.lower())
        s = difflib.SequenceMatcher(None, clean, qc).ratio()
        if s > score:
            score = s
            best = (fid, a)

    if score >= 0.7:
        fid, ans = best

        kb = [
            [KeyboardButton(TEXTS["answer_good_btn"][lang]), KeyboardButton(TEXTS["answer_bad_btn"][lang])],
            [KeyboardButton(TEXTS["main_menu"][lang])]
        ]

        await update.message.reply_text(ans, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

        state["step"] = "faq_feedback"
        state["faq_id"] = fid
        return

    await update.message.reply_text("Ищу ответ..." if lang == "ru" else "Жауап ізделуде...")

    if lang == "ru":
        ai_prompt = f"Ответь кратко и понятно на русском языке:\n{query}"
    else:
        ai_prompt = f"Қысқа әрі түсінікті түрде қазақ тілінде жауап бер:\n{query}"

    try:
        resp = requests.post(
            DEEPSEEK_URL,
            json={
                "model": AI_MODEL,
                "prompt": ai_prompt,
                "stream": False
            },
            timeout=20
        )
        ai_ans = resp.json().get("response", "⚠️ Ошибка")
    except requests.exceptions.Timeout:
        ai_ans = (
            "⚠️ Сервер не отвечает. Попробуйте позже."
            if lang == "ru"
            else "⚠️ Сервер жауап бермеді. Кейінірек көріңіз."
        )
    except Exception:
        ai_ans = (
            "⚠️ Произошла ошибка."
            if lang == "ru"
            else "⚠️ Қате орын алды."
        )

    insert_ai_log(
        update.effective_user.id,
        update.effective_user.username,
        query,
        ai_ans
    )

    kb = [
        [
            KeyboardButton(TEXTS["answer_good_btn"][lang]),
            KeyboardButton(TEXTS["answer_bad_btn"][lang])
        ],
        [KeyboardButton(TEXTS["main_menu"][lang])]
    ]

    await update.message.reply_text(
        "Жауап дайындалуда..." if lang == "kz" else "Ответ готовится..."
    )

    await update.message.reply_text(
        ai_ans,
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

    state["step"] = "faq_feedback"
    state["faq_id"] = None


async def handle_faq_feedback(update, state):
    text = update.message.text
    lang = state["lang"]
    uid = update.effective_user.id
    fid = state.get("faq_id")

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE telegram_id=%s", (uid,))
    row = c.fetchone()
    conn.close()

    user_id = row[0] if row else None

    if text == TEXTS["answer_good_btn"][lang]:
        if user_id:
            insert_feedback(user_id, fid, 1)
        await update.message.reply_text(TEXTS["answer_good"][lang])

    elif text == TEXTS["answer_bad_btn"][lang]:
        if user_id:
            insert_feedback(user_id, fid, 0)
        await update.message.reply_text(TEXTS["answer_bad"][lang])

    elif text == TEXTS["main_menu"][lang]:
        state["step"] = "menu"
        if state["role"] == "teacher":
            await show_teacher_menu(update, state)
        else:
            await show_student_menu(update, state)
        return

    elif text == TEXTS["new_question"][lang]:
        state["step"] = "faq"
        await update.message.reply_text(TEXTS["faq_enter"][lang])
        return

    kb = [
        [KeyboardButton(TEXTS["new_question"][lang])],
        [KeyboardButton(TEXTS["main_menu"][lang])]
    ]

    await update.message.reply_text(TEXTS["what_next"][lang],
                                    reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

    state["step"] = "faq_feedback"