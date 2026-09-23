import os
import random
import json
import requests
from flask import Flask, request, jsonify, send_from_directory

TOKEN = os.environ["BOT_TOKEN"]
PUBLIC_URL = (os.environ.get("PUBLIC_URL") or os.environ.get("RENDER_EXTERNAL_URL") or "").rstrip("/")
API = f"https://api.telegram.org/bot{TOKEN}"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

@app.get("/webapp")
def webapp():
    return send_from_directory(
        os.path.join(BASE_DIR, "webapp"),
        "index.html"
    )

def tg(method, **data):
    r = requests.post(f"{API}/{method}", data=data, timeout=30)
    r.raise_for_status()
    return r.json()


def card_files():
    return [
        os.path.join(BASE_DIR, f)
        for f in os.listdir(BASE_DIR)
        if f.lower().endswith(".png") and f[:-4].isdigit()
]
@app.get("/random-card")
def random_card():
    files = card_files()

    if not files:
        return "Карточки не найдены", 404

    path = random.choice(files)

    return send_from_directory(
        BASE_DIR,
        os.path.basename(path)
    )
def tg_photo(chat_id, path):
    filename = os.path.basename(path)
    with open(path, "rb") as photo:
        r = requests.post(
            f"{API}/sendPhoto",
            data={"chat_id": chat_id},
            files={"photo": (filename, photo, "image/png")},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()


def button():
    return {"inline_keyboard": [[
        {
            "text": "🪽 Получить послание",
            "url": "https://t.me/poslanie_ot_hraniteley_bot/poslanie"
        }
    ]]}


@app.get("/")
def health():
    return "Хранитель уже летит 🪽"


@app.post("/telegram")
def telegram():
    update = request.get_json(silent=True) or {}

    msg = update.get("message")
    if msg:
        chat_id = msg["chat"]["id"]
        tg(
    "sendMessage",
    chat_id=chat_id,
    text="<i>Остановись на мгновение…</i>\n\n<b>Загадай внутри себя то</b>, что сейчас важно. ✨",
    parse_mode="HTML",
    reply_markup=json.dumps(button(), ensure_ascii=False),
)
        return jsonify(ok=True)

    cq = update.get("callback_query")
    if cq:
        chat_id = cq["from"]["id"]
        tg("answerCallbackQuery", callback_query_id=cq["id"])

        files = card_files()

        if not files:
            tg(
                "sendMessage",
                chat_id=chat_id,
                text="Карточки пока не загружены."
            )
            return jsonify(ok=True)

        tg_photo(chat_id, random.choice(files))
        return jsonify(ok=True)

    return jsonify(ok=True)


@app.get("/set-webhook")
def set_webhook():
    if not PUBLIC_URL:
        return jsonify(
            ok=False,
            error="PUBLIC_URL/RENDER_EXTERNAL_URL is not set"
        ), 500

    result = tg(
        "setWebhook",
        url=f"{PUBLIC_URL}/telegram"
    )

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
