import os, random, requests
from flask import Flask, request, jsonify, send_from_directory

TOKEN = os.environ["BOT_TOKEN"]
PUBLIC_URL = os.environ["PUBLIC_URL"].rstrip("/")
API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

MESSAGES = [
    "С тобой всё так.\n\nТы просто идёшь своим путём, а не тем, который от тебя ждали.\n\nНе сравнивай свою дорогу с чужой.",
]

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

@app.get("/")
def health():
    return "Хранитель работает 🪽"

@app.get("/cards/<path:filename>")
def card(filename):
    return send_from_directory("cards", filename)

@app.post("/telegram")
def telegram():
    update = request.get_json(silent=True) or {}

    # /start
    msg = update.get("message")
    if msg:
        chat_id = msg["chat"]["id"]
        tg(
            "sendMessage",
            chat_id=chat_id,
            text="🪽\n\nОстановись на мгновение.\nЗагадай внутри себя то, что сейчас важно.\n\nКогда будешь готова — нажми кнопку.",
            reply_markup=__import__("json").dumps(button(), ensure_ascii=False)
        )
        return jsonify(ok=True)

    # button press
    cq = update.get("callback_query")
    if cq:
        chat_id = cq["message"]["chat"]["id"]
        tg("answerCallbackQuery", callback_query_id=cq["id"])

        # Пока одна тестовая карточка. После подключения заменим на все 30.
        url = f"{PUBLIC_URL}/cards/01.png"
        tg("sendPhoto", chat_id=chat_id, photo=url)
        return jsonify(ok=True)

    return jsonify(ok=True)

@app.get("/set-webhook")
def set_webhook():
    result = tg("setWebhook", url=f"{PUBLIC_URL}/telegram")
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)