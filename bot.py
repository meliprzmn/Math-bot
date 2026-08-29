import os
from flask import Flask, request
import telebot

# دریافت توکن از Environment Variable
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# دستور /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "سلام! 🤖\nبات فعاله و آماده‌ست."
    )


# دریافت پیام‌های تلگرام
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200

    return "Bad Request", 400


# صفحه بررسی وضعیت
@app.route("/", methods=["GET"])
def home():
    return "Math Bot is running! 🤖", 200


# اجرای سرور
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    # آدرس عمومی Render
    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if render_url:
        webhook_url = f"{render_url}/webhook"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)

    app.run(
        host="0.0.0.0",
        port=port
    )
