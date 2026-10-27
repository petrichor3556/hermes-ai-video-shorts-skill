"""Post one video with an HTML caption to a Telegram channel (one post), edit a caption, or only check its length.

Environment: TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL (e.g. @my_channel). The bot must be a channel admin.

Usage:
  python tg_post_video.py check caption.html
  python tg_post_video.py video episode_upload.mp4 caption.html [--chat @other_chat_or_id]
  python tg_post_video.py edit 12 caption.html

Captions are read with utf-8-sig (a BOM would shift link offsets). Limit: 1024 visible characters.
Bots cannot send premium custom emoji into channels; use normal emoji or edit the post from a premium account.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path


def visible_len(html: str) -> int:
    return len(re.sub(r"<[^>]+>", "", html))


def read_caption(path: str) -> str:
    html = Path(path).read_text(encoding="utf-8-sig").strip()
    n = visible_len(html)
    if n > 1024:
        sys.exit(f"caption is {n} visible characters, limit is 1024")
    print(f"visible characters: {n} of 1024")
    return html


def call(method: str, fields: dict, files: dict | None = None) -> dict:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    boundary = uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, path in (files or {}).items():
        p = Path(path)
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{p.name}"\r\n'
                 f"Content-Type: video/mp4\r\n\r\n").encode() + p.read_bytes() + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/{method}", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode("utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["check", "video", "edit"])
    ap.add_argument("args", nargs="+")
    ap.add_argument("--chat", default=os.environ.get("TELEGRAM_CHANNEL"))
    a = ap.parse_args()
    if a.mode == "check":
        read_caption(a.args[0])
        return
    if a.mode == "video":
        video, cap = a.args
        r = call("sendVideo", {"chat_id": a.chat, "caption": read_caption(cap), "parse_mode": "HTML",
                               "supports_streaming": "true", "width": "1080", "height": "1920"}, {"video": video})
    else:
        mid, cap = a.args
        r = call("editMessageCaption", {"chat_id": a.chat, "message_id": mid, "caption": read_caption(cap),
                                        "parse_mode": "HTML"})
    print("ok:", r.get("ok"), r.get("description", ""))


if __name__ == "__main__":
    main()
