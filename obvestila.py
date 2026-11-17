"""Kratka obvestila Marku na Telegram (bot, ključ v TELEGRAM_TOKEN)."""
from __future__ import annotations

import json
import os
from pathlib import Path

import requests

CHAT_FILE = Path(__file__).parent / "state" / "telegram.json"


def _chat_id(tok: str) -> int | None:
    if CHAT_FILE.exists():
        return json.loads(CHAT_FILE.read_text()).get("chat_id")
    me = requests.get(f"https://api.telegram.org/bot{tok}/getMe", timeout=30).json()
    print("Telegram bot:", me.get("result", {}).get("username"), "ok" if me.get("ok") else me.get("description"))
    wh = requests.get(f"https://api.telegram.org/bot{tok}/getWebhookInfo", timeout=30).json()
    if wh.get("result", {}).get("url"):
        requests.get(f"https://api.telegram.org/bot{tok}/deleteWebhook", timeout=30)
        print("Telegram: odstranjen webhook")
    r = requests.get(f"https://api.telegram.org/bot{tok}/getUpdates", timeout=30).json()
    print("Telegram getUpdates:", r.get("ok"), len(r.get("result", [])), r.get("description", ""))
    chats = [u[k]["chat"]["id"] for u in r.get("result", [])
             for k in ("message", "edited_message", "my_chat_member") if k in u]
    if not chats:
        print("Telegram: botu še nihče ni pisal – pošlji mu »start«.")
        return None
    CHAT_FILE.parent.mkdir(exist_ok=True)
    CHAT_FILE.write_text(json.dumps({"chat_id": chats[-1]}))
    return chats[-1]


def send(text: str) -> None:
    tok = os.environ.get("TELEGRAM_TOKEN")
    if not tok:
        return
    try:
        cid = _chat_id(tok)
        if cid:
            requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", timeout=30,
                          data={"chat_id": cid, "text": text, "disable_web_page_preview": "true"})
    except Exception as e:  # obvestilo ne sme podreti objave
        print(f"Telegram ni uspel: {e}")


def send_video(path, caption: str) -> bool:
    """Pošlje video (do 50 MB) na Telegram; vrne True, če je uspelo."""
    tok = os.environ.get("TELEGRAM_TOKEN")
    if not tok:
        return False
    try:
        cid = _chat_id(tok)
        if not cid:
            return False
        with open(path, "rb") as f:
            r = requests.post(f"https://api.telegram.org/bot{tok}/sendVideo", timeout=180,
                              data={"chat_id": cid, "caption": caption[:1000], "supports_streaming": "true"},
                              files={"video": (Path(path).name, f, "video/mp4")}).json()
        if not r.get("ok"):
            print("Telegram video:", r.get("description"))
        return bool(r.get("ok"))
    except Exception as e:
        print(f"Telegram video ni uspel: {e}")
        return False
