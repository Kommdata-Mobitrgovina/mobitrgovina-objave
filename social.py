"""Izbor izdelkov iz WooCommerce, opis objave in objava na Facebook + Instagram (Reels).

Okoljske spremenljivke (GitHub Secrets):
  WC_URL            https://mobitrgovina.com
  WC_KEY, WC_SECRET WooCommerce REST ključ SAMO ZA BRANJE
  FB_PAGE_ID        ID Facebook strani
  FB_PAGE_TOKEN     dolgotrajni žeton strani (pages_manage_posts, instagram_content_publish …)
  IG_USER_ID        ID Instagram poslovnega računa, povezanega s stranjo
  DRY_RUN=1         samo naredi video in opis, ničesar ne objavi
"""
from __future__ import annotations

import html
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

GRAPH = "https://graph.facebook.com/v24.0"
STATE = Path(__file__).parent / "state" / "posted.json"
REPOST_AFTER_DAYS = 21
UA = {"User-Agent": "mobitrgovina-social/1.0"}


# ---------------------------------------------------------------- WooCommerce
def wc_get(path: str, **params) -> list | dict:
    base = os.environ["WC_URL"].rstrip("/")
    params.update(consumer_key=os.environ["WC_KEY"], consumer_secret=os.environ["WC_SECRET"])
    for attempt in range(4):
        r = requests.get(f"{base}/wp-json/wc/v3/{path}", params=params, headers=UA, timeout=90)
        if r.ok:
            return r.json()
        time.sleep(10 * (attempt + 1))
    r.raise_for_status()


def candidates() -> list[dict]:
    """Objavljeni izdelki na zalogi s sliko; najprej akcije, nato novi."""
    fields = "id,name,price,regular_price,sale_price,on_sale,permalink,images,categories,short_description,date_modified"
    out, seen = [], set()
    for extra in ({"on_sale": "true"}, {}):
        for page in range(1, 4):
            batch = wc_get("products", status="publish", stock_status="instock", per_page=100,
                           page=page, orderby="date", order="desc", _fields=fields, **extra)
            for p in batch:
                if p["id"] not in seen and p.get("images") and p.get("price"):
                    seen.add(p["id"])
                    out.append(p)
            if len(batch) < 100:
                break
    return out


def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(st: dict):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(st, indent=1, sort_keys=True))


def pick(products: list[dict], st: dict) -> dict | None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=REPOST_AFTER_DAYS)
    fresh = [p for p in products
             if str(p["id"]) not in st or datetime.fromisoformat(st[str(p["id"])]) < cutoff]
    if not fresh:
        return None
    # nikoli objavljeni najprej, potem akcije, potem najnovejši
    fresh.sort(key=lambda p: (str(p["id"]) in st, not p.get("on_sale"), p.get("date_modified", "")), reverse=False)
    never = [p for p in fresh if str(p["id"]) not in st]
    pool = never or fresh
    sale = [p for p in pool if p.get("on_sale")]
    return (sale or pool)[0]


# ---------------------------------------------------------------- vsebina
def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip(" ,.…")


def to_float(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def describe(p: dict) -> dict:
    price = to_float(p.get("price"))
    reg = to_float(p.get("regular_price"))
    disc = round((1 - price / reg) * 100) if reg and price and reg > price else 0
    cats = " ".join(c["name"] for c in p.get("categories", [])).lower()
    used = "rablj" in cats
    sd = clean(p.get("short_description", ""))
    parts = [x.strip() for x in sd.split(",") if x.strip()]
    keep = [x for x in parts if re.search(r"garancij|baterij|ohranjen|nov|embala|neaktiv|omrežj", x, re.I)]
    info = []
    if keep:
        info.append(" · ".join(k[:1].upper() + k[1:] for k in keep[:2]))
    if any("garancij" in k.lower() for k in keep[2:]):
        info.append(next(k for k in keep if "garancij" in k.lower()))
    tag = "AKCIJA" if disc else ("RABLJENO" if used else "NOVO")
    return {"name": clean(p["name"]), "price": price, "regular": reg, "discount": disc,
            "tag": tag, "info": info, "url": p["permalink"], "used": used, "short": sd}


def caption(d: dict) -> str:
    brand = d["name"].split()[0].lower()
    lines = []
    if d["discount"]:
        lines.append(f"🔥 AKCIJA −{d['discount']} %: {d['name']}")
        lines.append(f"💶 Zdaj {d['price']:.2f} € namesto {d['regular']:.2f} €".replace(".", ","))
    else:
        lines.append(f"{'♻️' if d['used'] else '✨'} {d['name']}")
        lines.append(f"💶 Cena: {d['price']:.2f} €".replace(".", ","))
    if d["short"]:
        lines.append("")
        lines.append("✅ " + d["short"][:220])
    lines += ["", f"🛒 Naroči: {d['url']}", "📦 Dostava po vsej Sloveniji", "",
              f"#mobitrgovina #telefoni #mobitel #{brand} #{'rabljenitelefoni' if d['used'] else 'novitelefoni'} #slovenija"]
    return "\n".join(lines)


def download_images(p: dict, n: int = 3) -> list[bytes]:
    out = []
    for im in p["images"][:n]:
        try:
            r = requests.get(im["src"], headers=UA, timeout=60)
            if r.ok:
                out.append(r.content)
        except requests.RequestException:
            pass
    return out


# ---------------------------------------------------------------- Meta Graph API
def _check(r: requests.Response) -> dict:
    data = r.json() if r.content else {}
    if not r.ok or "error" in data:
        raise RuntimeError(f"Meta API napaka {r.status_code}: {data}")
    return data


def post_facebook_reel(video: Path, text: str) -> str:
    page, tok = os.environ["FB_PAGE_ID"], os.environ["FB_PAGE_TOKEN"]
    start = _check(requests.post(f"{GRAPH}/{page}/video_reels",
                                 data={"upload_phase": "start", "access_token": tok}, timeout=60))
    vid = start["video_id"]
    size = video.stat().st_size
    with video.open("rb") as fh:
        _check(requests.post(start["upload_url"], data=fh, timeout=600,
                             headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(size)}))
    _check(requests.post(f"{GRAPH}/{page}/video_reels", timeout=60, data={
        "upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
        "description": text, "access_token": tok}))
    return vid


def post_instagram_reel(video: Path, text: str) -> str:
    ig, tok = os.environ["IG_USER_ID"], os.environ["FB_PAGE_TOKEN"]
    c = _check(requests.post(f"{GRAPH}/{ig}/media", timeout=60, data={
        "media_type": "REELS", "upload_type": "resumable", "caption": text,
        "share_to_feed": "true", "access_token": tok}))
    cid, size = c["id"], video.stat().st_size
    with video.open("rb") as fh:
        _check(requests.post(c["uri"], data=fh, timeout=600,
                             headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(size)}))
    for _ in range(40):  # Instagram video obdeluje nekaj časa
        st = _check(requests.get(f"{GRAPH}/{cid}", params={"fields": "status_code", "access_token": tok}, timeout=60))
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram ni sprejel videa: {st}")
        time.sleep(15)
    pub = _check(requests.post(f"{GRAPH}/{ig}/media_publish", timeout=60,
                               data={"creation_id": cid, "access_token": tok}))
    return pub["id"]
