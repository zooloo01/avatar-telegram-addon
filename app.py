from flask import Flask, jsonify, send_file, abort
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaDocument
import os

api_id = int(os.environ.get("TELEGRAM_API_ID"))
api_hash = os.environ.get("TELEGRAM_API_HASH")
channel = os.environ.get("TELEGRAM_CHANNEL")

client = TelegramClient("stremio_session", api_id, api_hash)
client.connect()

app = Flask(__name__)

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "id": "avatar.telegram.addon",
        "version": "1.0.0",
        "name": "Avatar Telegram Channel",
        "description": "Watch Avatar episodes from Telegram in Stremio",
        "resources": ["catalog", "stream"],
        "types": ["movie"],
        "catalogs": [{
            "type": "movie",
            "id": "avatar_channel",
            "name": "Avatar Telegram"
        }],
        "idPrefixes": ["avatar_"]
    })

@app.route("/catalog/movie/avatar_channel.json")
def catalog():
    messages = client.get_messages(channel, limit=50)
    items = []
    for msg in messages:
        if msg.media and isinstance(msg.media, MessageMediaDocument):
            items.append({
                "id": f"avatar_{msg.id}",
                "name": msg.message or f"Episode {msg.id}",
                "poster": "https://upload.wikimedia.org/wikipedia/en/8/86/Avatar_Aang.png"
            })
    return jsonify({"metas": items})

@app.route("/stream/movie/<id>.json")
def stream(id):
    msg_id = int(id.replace("avatar_", ""))
    msg = client.get_messages(channel, ids=msg_id)

    if msg and msg.media and isinstance(msg.media, MessageMediaDocument):
        return jsonify({
            "streams": [{
                "title": msg.message or "Telegram Video",
                "url": f"{request.host_url}video/{msg_id}"  # לינק פנימי
            }]
        })
    return jsonify({"streams": []})

@app.route("/video/<msg_id>")
def video(msg_id):
    try:
        msg_id = int(msg_id)
        msg = client.get_messages(channel, ids=msg_id)

        if msg and msg.media and isinstance(msg.media, MessageMediaDocument):
            file = client.download_media(msg)
            return send_file(file, as_attachment=False)
    except:
        pass
    abort(404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
