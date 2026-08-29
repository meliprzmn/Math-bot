import os
from flask import Flask, request
import telebot

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "سلام! 🤖\nبات فعاله و آماده‌ست.")


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200

    except Exception as e:
        print("Webhook error:", e)
        return "ERROR", 500


@app.route("/", methods=["GET"])
def home():
    return "Math Bot is running! 🤖", 200


if __name__ == "__main__":
    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if render_url:
        webhook_url = f"{render_url}/webhook"

        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)

        print("Webhook set to:", webhook_url)
    else:
        print("RENDER_EXTERNAL_URL not found!")

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
