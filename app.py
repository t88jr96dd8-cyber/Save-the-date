from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DEFAULT_CHAT_ID = os.environ.get("CHAT_ID")


def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message
        },
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise Exception(result)

    return result


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "service": "Save the Date Backend"
    })


@app.route("/api/watch", methods=["POST"])
def create_watch():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Keine Daten erhalten"
        }), 400

    location = data.get("location")
    service = data.get("service")

    date_from = data.get("dateFrom")
    date_to = data.get("dateTo")

    time_from = data.get("timeFrom")
    time_to = data.get("timeTo")

    chat_id = data.get("telegramChatId") or DEFAULT_CHAT_ID

    if not chat_id:
        return jsonify({
            "success": False,
            "error": "Keine Telegram Chat-ID vorhanden"
        }), 400

    message = (
        "🔔 SAVE THE DATE\n\n"
        "Neue Überwachung erstellt!\n\n"
        f"📍 Location: {location or '-'}\n"
        f"📝 Service: {service or '-'}\n"
        f"📅 Von: {date_from or '-'}\n"
        f"📅 Bis: {date_to or '-'}\n"
        f"🕐 Von: {time_from or 'beliebige Uhrzeit'}\n"
        f"🕐 Bis: {time_to or 'beliebige Uhrzeit'}"
    )

    try:
        send_telegram(chat_id, message)

        return jsonify({
            "success": True,
            "message": "Überwachung erstellt"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
