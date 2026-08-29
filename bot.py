# =========================================================
# Telegram Math Bot
# Python 3 + python-telegram-bot
# Render Compatible
# =========================================================

import os
import threading

from flask import Flask

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


# =========================================================
# تنظیمات
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")


# =========================================================
# Flask برای زنده نگه داشتن Web Service در Render
# =========================================================

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "Telegram Math Bot is running!"


@web_app.route("/health")
def health():
    return "OK"


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(
        host="0.0.0.0",
        port=port
    )


# =========================================================
# اطلاعات کتاب‌ها
# =========================================================

BOOKS = {

    "tajrobi": {

        "دهم": {
            "ریاضی (۱)": [
                "فصل اول: مجموعه، الگو و دنباله",
                "فصل دوم: مثلثات",
                "فصل سوم: توان‌های گویا و عبارت‌های جبری",
                "فصل چهارم: معادله‌ها و نامعادله‌ها",
                "فصل پنجم: تابع",
                "فصل ششم: شمارش، بدون شمردن",
                "فصل هفتم: آمار و احتمال",
            ]
        },

        "یازدهم": {
            "ریاضی (۲)": [
                "فصل اول: هندسه تحلیلی و جبر",
                "فصل دوم: هندسه",
                "فصل سوم: تابع",
                "فصل چهارم: مثلثات",
                "فصل پنجم: توابع نمایی و لگاریتمی",
                "فصل ششم: مشتق",
                "فصل هفتم: کاربردهای مشتق",
            ]
        },

        "دوازدهم": {
            "ریاضی (۳)": [
                "فصل اول: تابع",
                "فصل دوم: مثلثات",
                "فصل سوم: حدهای نامتناهی و حد در بی‌نهایت",
                "فصل چهارم: مشتق",
                "فصل پنجم: کاربردهای مشتق",
                "فصل ششم: شمارش",
                "فصل هفتم: احتمال",
            ]
        },
    },

    "riazi": {

        "دهم": {
            "ریاضی (۱)": [
                "فصل اول: مجموعه، الگو و دنباله",
                "فصل دوم: مثلثات",
                "فصل سوم: توان‌های گویا و عبارت‌های جبری",
                "فصل چهارم: معادله‌ها و نامعادله‌ها",
                "فصل پنجم: تابع",
                "فصل ششم: شمارش، بدون شمردن",
                "فصل هفتم: آمار و احتمال",
            ],

            "هندسه (۱)": [
                "فصل اول: ترسیم‌های هندسی و استدلال",
                "فصل دوم: قضیه تالس، تشابه و کاربردهای آن",
                "فصل سوم: چندضلعی‌ها",
            ],
        },

        "یازدهم": {
            "حسابان (۱)": [
                "فصل اول: جبر و معادله",
                "فصل دوم: تابع",
                "فصل سوم: توابع نمایی و لگاریتمی",
                "فصل چهارم: مثلثات",
                "فصل پنجم: حد و پیوستگی",
            ],

            "هندسه (۲)": [
                "فصل اول: دایره",
                "فصل دوم: تبدیل‌های هندسی و کاربردها",
                "فصل سوم: روابط طولی در مثلث",
            ],

            "آمار و احتمال": [
                "فصل اول: آشنایی با مبانی ریاضیات",
                "فصل دوم: احتمال",
                "فصل سوم: آمار توصیفی",
                "فصل چهارم: آمار استنباطی",
            ],
        },

        "دوازدهم": {
            "حسابان (۲)": [
                "فصل اول: تابع",
                "فصل دوم: مثلثات",
                "فصل سوم: حدهای نامتناهی، حد در بی‌نهایت",
                "فصل چهارم: مشتق",
                "فصل پنجم: کاربردهای مشتق",
            ],

            "هندسه (۳)": [
                "فصل اول: ماتریس و کاربردها",
                "فصل دوم: آشنایی با مقاطع مخروطی",
                "فصل سوم: بردارها",
            ],

            "ریاضیات گسسته": [
                "فصل اول: آشنایی با نظریه اعداد",
                "فصل دوم: گراف و مدل‌سازی",
                "فصل سوم: ترکیبیات (شمارش)",
            ],
        },
    },
}


# =========================================================
# بخش‌های آموزشی
# =========================================================

LESSONS = {
    "lesson": "📚 درسنامه",
    "test": "📝 تست",
    "descriptive": "✍️ سوالات تشریحی",
    "review": "🔄 مرور نکات",
    "exam": "🎯 آزمون‌ها",
}


# =========================================================
# ذخیره انتخاب کاربران
# =========================================================

user_data = {}


# =========================================================
# /start
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            "📐 رشته ریاضی",
            "🧬 رشته تجربی",
        ]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "سلام 👋\n\n"
        "به ربات آموزش ریاضی خوش آمدی 🌱\n\n"
        "لطفاً رشته خودت را انتخاب کن:",
        reply_markup=reply_markup
    )


# =========================================================
# انتخاب رشته
# =========================================================

async def select_field(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    text = update.message.text

    if text == "🧬 رشته تجربی":
        field = "tajrobi"
        title = "🧬 رشته تجربی"

    elif text == "📐 رشته ریاضی":
        field = "riazi"
        title = "📐 رشته ریاضی"

    else:
        return

    user_id = update.effective_user.id

    user_data[user_id] = {
        "field": field,
        "grade": None,
        "book": None,
        "chapter": None,
    }

    await show_grades(update, field, title)


# =========================================================
# نمایش پایه‌ها
# =========================================================

async def show_grades(update, field, title):

    grades = list(BOOKS[field].keys())

    keyboard = []

    for grade in grades:

        keyboard.append([
            InlineKeyboardButton(
                f"📚 پایه {grade}",
                callback_data=f"grade|{field}|{grade}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 بازگشت به انتخاب رشته",
            callback_data="back_field"
        )
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"{title}\n\n"
        "پایه موردنظر خودت را انتخاب کن:",
        reply_markup=reply_markup
    )


# =========================================================
# نمایش کتاب‌ها
# =========================================================

async def show_books(query, field, grade):

    books = BOOKS[field][grade]

    keyboard = []

    for index, book in enumerate(books):

        keyboard.append([
            InlineKeyboardButton(
                f"📖 {book}",
                callback_data=f"book|{field}|{grade}|{index}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 بازگشت به پایه‌ها",
            callback_data=f"back_grades|{field}"
        )
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"📚 پایه {grade}\n\n"
        "کتاب موردنظر را انتخاب کن:",
        reply_markup=reply_markup
    )


# =========================================================
# نمایش فصل‌ها
# =========================================================

async def show_chapters(query, field, grade, book):

    chapters = BOOKS[field][grade][book]

    keyboard = []

    for index, chapter in enumerate(chapters):

        keyboard.append([
            InlineKeyboardButton(
                f"📘 {chapter}",
                callback_data=(
                    f"chapter|{field}|{grade}|"
                    f"{list(BOOKS[field][grade].keys()).index(book)}|{index}"
                )
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 بازگشت به کتاب‌ها",
            callback_data=f"back_books|{field}|{grade}"
        )
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"📖 {book}\n\n"
        "فصل موردنظر را انتخاب کن:",
        reply_markup=reply_markup
    )


# =========================================================
# منوی آموزشی فصل
# =========================================================

async def show_lesson_menu(
    query,
    field,
    grade,
    book,
    chapter_index
):

    chapter = BOOKS[field][grade][book][chapter_index]

    keyboard = [

        [
            InlineKeyboardButton(
                "📚 درسنامه",
                callback_data=(
                    f"content|lesson|{field}|{grade}|"
                    f"{list(BOOKS[field][grade].keys()).index(book)}|"
                    f"{chapter_index}"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "📝 تست",
                callback_data=(
                    f"content|test|{field}|{grade}|"
                    f"{list(BOOKS[field][grade].keys()).index(book)}|"
                    f"{chapter_index}"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "✍️ سوالات تشریحی",
                callback_data=(
                    f"content|descriptive|{field}|{grade}|"
                    f"{list(BOOKS[field][grade].keys()).index(book)}|"
                    f"{chapter_index}"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "🔄 مرور نکات",
                callback_data=(
                    f"content|review|{field}|{grade}|"
                    f"{list(BOOKS[field][grade].keys()).index(book)}|"
                    f"{chapter_index}"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "🎯 آزمون‌ها",
                callback_data=(
                    f"content|exam|{field}|{grade}|"
                    f"{list(BOOKS[field][grade].keys()).index(book)}|"
                    f"{chapter_index}"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "🔙 بازگشت به فصل‌ها",
                callback_data=(
                    f"back_chapters|{field}|{grade}|"
                    f"{list(BOOKS[field][grade].keys()).index(book)}"
                )
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"📘 {chapter}\n\n"
        "بخش موردنظر خودت را انتخاب کن:",
        reply_markup=reply_markup
    )


# =========================================================
# نمایش محتوا
# =========================================================

async def show_content(
    query,
    content_type,
    field,
    grade,
    book,
    chapter_index
):

    chapter = BOOKS[field][grade][book][chapter_index]

    title = LESSONS[content_type]

    keyboard = [
        [
            InlineKeyboardButton(
                "🔙 بازگشت",
                callback_data=(
                    f"chapter|{field}|{grade}|"
                    f"{list(BOOKS[field][grade].keys()).index(book)}|"
                    f"{chapter_index}"
                )
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"{title}\n\n"
        f"📚 کتاب: {book}\n"
        f"📘 {chapter}\n\n"
        "⏳ محتوای این بخش هنوز وارد نشده است.\n\n"
        "ساختار بات آماده است و در مرحله بعد "
        "می‌توانیم درسنامه، تست، سوالات تشریحی، "
        "مرور نکات و آزمون‌ها را اضافه کنیم."
    )

    await query.edit_message_text(
        text,
        reply_markup=reply_markup
    )


# =========================================================
# مدیریت دکمه‌ها
# =========================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data.split("|")
    action = data[0]

    # انتخاب پایه
    if action == "grade":

        field = data[1]
        grade = data[2]

        user_id = query.from_user.id

        user_data[user_id] = {
            "field": field,
            "grade": grade,
            "book": None,
            "chapter": None,
        }

        await show_books(query, field, grade)

    # انتخاب کتاب
    elif action == "book":

        field = data[1]
        grade = data[2]
        book_index = int(data[3])

        books = list(BOOKS[field][grade].keys())
        book = books[book_index]

        user_id = query.from_user.id

        user_data[user_id] = {
            "field": field,
            "grade": grade,
            "book": book,
            "chapter": None,
        }

        await show_chapters(
            query,
            field,
            grade,
            book
        )

    # انتخاب فصل
    elif action == "chapter":

        field = data[1]
        grade = data[2]
        book_index = int(data[3])
        chapter_index = int(data[4])

        books = list(BOOKS[field][grade].keys())
        book = books[book_index]

        user_id = query.from_user.id

        user_data[user_id] = {
            "field": field,
            "grade": grade,
            "book": book,
            "chapter": chapter_index,
        }

        await show_lesson_menu(
            query,
            field,
            grade,
            book,
            chapter_index
        )

    # محتوای آموزشی
    elif action == "content":

        content_type = data[1]
        field = data[2]
        grade = data[3]
        book_index = int(data[4])
        chapter_index = int(data[5])

        books = list(BOOKS[field][grade].keys())
        book = books[book_index]

        await show_content(
            query,
            content_type,
            field,
            grade,
            book,
            chapter_index
        )

    # بازگشت به رشته‌ها
    elif action == "back_field":

        keyboard = [
            [
                "📐 رشته ریاضی",
                "🧬 رشته تجربی",
            ]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await query.message.reply_text(
            "لطفاً رشته خودت را انتخاب کن:",
            reply_markup=reply_markup
        )

    # بازگشت به پایه‌ها
    elif action == "back_grades":

        field = data[1]

        title = (
            "📐 رشته ریاضی"
            if field == "riazi"
            else "🧬 رشته تجربی"
        )

        grades = list(BOOKS[field].keys())

        keyboard = []

        for grade in grades:

            keyboard.append([
                InlineKeyboardButton(
                    f"📚 پایه {grade}",
                    callback_data=f"grade|{field}|{grade}"
                )
            ])

        keyboard.append([
            InlineKeyboardButton(
                "🔙 بازگشت به رشته‌ها",
                callback_data="back_field"
            )
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"{title}\n\n"
            "پایه موردنظر را انتخاب کن:",
            reply_markup=reply_markup
        )

    # بازگشت به کتاب‌ها
    elif action == "back_books":

        field = data[1]
        grade = data[2]

        await show_books(
            query,
            field,
            grade
        )

    # بازگشت به فصل‌ها
    elif action == "back_chapters":

        field = data[1]
        grade = data[2]
        book_index = int(data[3])

        books = list(BOOKS[field][grade].keys())
        book = books[book_index]

        await show_chapters(
            query,
            field,
            grade,
            book
        )


# =========================================================
# مدیریت خطا
# =========================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):

    print("\n========== ERROR ==========")
    print(context.error)
    print("============================\n")


# =========================================================
# اجرای ربات
# =========================================================

def main():

    print("================================")
    print("      Telegram Math Bot")
    print("         Starting...")
    print("================================")

    # اجرای وب‌سرور Render در یک Thread
    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True
    )

    web_thread.start()

    # ساخت Telegram Application
    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # پیام‌های متنی
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            select_field
        )
    )

    # دکمه‌های Inline
    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # خطاها
    app.add_error_handler(
        error_handler
    )

    print("================================")
    print("      Telegram Math Bot")
    print("         Bot is running")
    print("================================")

    # اجرای Telegram Bot
    app.run_polling()


# =========================================================
# شروع
# =========================================================

if __name__ == "__main__":
    main()
