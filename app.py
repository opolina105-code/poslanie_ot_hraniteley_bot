import os
import requests
from flask import Flask, request, jsonify, send_from_directory

TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

def tg(method, **data):
    r = requests.post(f"{API}/{method}", data=data, timeout=30)
    r.raise_for_status()
    return r.json()

def button():
    return {
        "inline_keyboard": [[
            {"text": "🪽 Получить послание", "callback_data": "draw"}
        ]]
    }

@app.route("/")
def health():
    return "Хранитель работает 🪽"

@app.route("/cards/<filename>")
def card(filename):
    return send_from_directory("cards", filename)

@app.route("/telegram", methods=["POST"])
def telegram():
    update = request.get_json(force=True)

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]

        tg(
            "sendMessage",
            chat_id=chat_id,
            text=(
                "🪽\n\n"
                "Остановись на мгновение.\n"
                "Загадай внутри себя то, что сейчас важно.\n\n"
                "Когда будешь готова — нажми кнопку."
            ),
            reply_markup=str(button()).replace("'", '"')
        )

    if "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]

        tg(
            "answerCallbackQuery",
            callback_query_id=callback["id"]
        )

        with open("cards/01.png", "rb") as photo:
            requests.post(
                f"{API}/sendPhoto",
                data={"chat_id": chat_id},
                files={"photo": photo},
                timeout=30
            )

    return jsonify(ok=True)

@app.route("/set-webhook")
def set_webhook():
    url = os.environ["PUBLIC_URL"] + "/telegram"
    return jsonify(tg("setWebhook", url=url))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
