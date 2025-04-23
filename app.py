import os
from flask import Flask, jsonify, Response, request
from telethon.sync import TelegramClient
import io

# ערכים קבועים לבדיקה מקומית
api_id = 20004067
api_hash = "78128bb0856041bc331169319625f533"
channel_username = "AvatarAangWatchFun"

# אתחול Telethon
client = TelegramClient("stremio_session", api_id, api_hash)
client.start()

# שליפת 20 ההודעות האחרונות
msgs = client.get_messages(channel_username, limit=20)
episodes = []
for msg in msgs:
    if msg.video:
        episodes.append({
            "id": str(msg.id),
            "title": msg.text or f"Episode {msg.id}",
            "msg_id": msg.id
        })

app = Flask(__name__)

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "id": "community.avatar-telegram",
        "version": "1.0.0",
        "name": "Avatar Telegram Addon",
        "description": "Avatar episodes from Telegram channel",
        "types": ["movie"],
        "catalogs": [{"type":"movie","id":"avatar_channel"}],
        "resources": ["catalog","stream"]
    })

@app.route("/catalog/movie/avatar_channel.json")
def catalog():
    return jsonify({
        "metas": [
            {
                "id": ep["id"],
                "type": "movie",
                "name": ep["title"],
                "poster": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f4/Avatar_Aang.png/220px-Avatar_Aang.png"
            }
            for ep in episodes
        ]
    })

@app.route("/stream/movie/<id>.json")
def stream(id):
    ep = next((e for e in episodes if e["id"] == id), None)
    if not ep:
        return jsonify({"streams": []})
    base = request.host_url.rstrip('/')
    video_url = f"{base}/video/{id}.mp4"
    return jsonify({
        "streams": [
            {"title": ep["title"], "url": video_url}
        ]
    })

@app.route("/video/<id>.mp4")
def video(id):
    msg_id = int(id)
    msg = client.get_messages(channel_username, ids=msg_id)
    if not msg or not msg.video:
        return "Not Found", 404
    buffer = io.BytesIO()
    client.download_media(msg, file=buffer)
    buffer.seek(0)
    return Response(buffer.read(), mimetype="video/mp4")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
