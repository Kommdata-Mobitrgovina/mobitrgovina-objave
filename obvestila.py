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
    r = requests.get(f"https://api.telegram.org/bot{tok}/getUpdates", timeout=30).json()
    chats = [u["message"]["chat"]["id"] for u in r.get("result", []) if "message" in u]
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
