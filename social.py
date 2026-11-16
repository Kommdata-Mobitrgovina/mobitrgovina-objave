"""Izbor izdelkov iz WooCommerce, besedila (opis + govor) in objava na Facebook + Instagram (Reels).

Okoljske spremenljivke (GitHub Secrets):
  WC_URL            https://mobitrgovina.com
  WC_KEY, WC_SECRET WooCommerce REST ključ SAMO ZA BRANJE
  FB_PAGE_ID        ID Facebook strani
  FB_PAGE_TOKEN     dolgotrajni žeton strani
  IG_USER_ID        ID Instagram poslovnega računa, povezanega s stranjo
  DRY_RUN=1         samo naredi video in opis, ničesar ne objavi
"""
from __future__ import annotations

import html
import json
import os
import random
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

GRAPH = "https://graph.facebook.com/v24.0"
STATE = Path(__file__).parent / "state" / "posted.json"
REPOST_AFTER_DAYS = 21
NEW_DAYS = 30
UA = {"User-Agent": "mobitrgovina-social/2.0"}
BUYBACK_URL = "https://mobitrgovina.com/odkup-telefona/"


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


FIELDS = ("id,name,price,regular_price,sale_price,on_sale,permalink,images,categories,"
          "short_description,date_created,date_modified")


def candidates() -> list[dict]:
    """Objavljeni izdelki na zalogi s sliko: najnovejši + akcije."""
    out, seen = [], set()
    for extra in ({}, {"on_sale": "true"}):
        for page in range(1, 4):
            batch = wc_get("products", status="publish", stock_status="instock", per_page=100,
                           page=page, orderby="date", order="desc", _fields=FIELDS, **extra)
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


def is_phone(p: dict) -> bool:
    return any("APARAT" in c["name"].upper() for c in p.get("categories", []))


def _age_days(p: dict) -> float:
    try:
        d = datetime.fromisoformat(p["date_created"]).replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - d).days
    except Exception:
        return 9999


def pick(products: list[dict], st: dict, rnd: random.Random) -> dict | None:
    """Novi izdelki imajo prednost; občasno starejši telefon ali dodatna oprema."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=REPOST_AFTER_DAYS)
    fresh = [p for p in products
             if str(p["id"]) not in st or datetime.fromisoformat(st[str(p["id"])]) < cutoff]
    if not fresh:
        return None
    phones = [p for p in fresh if is_phone(p)]
    new = sorted([p for p in phones if _age_days(p) <= NEW_DAYS and str(p["id"]) not in st],
                 key=lambda p: p["date_created"], reverse=True)
    older = [p for p in phones if p not in new]
    acc = [p for p in fresh if not is_phone(p)]
    roll = rnd.random()
    if new and roll < 0.65:
        return new[0]
    if acc and roll > 0.85:
        sale = [p for p in acc if p.get("on_sale")]
        return rnd.choice(sale or acc)
    if older:
        sale = [p for p in older if p.get("on_sale")]
        return rnd.choice((sale or older)[:60])
    return (new or acc or fresh)[0]


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
    phone = is_phone(p)
    sd = clean(p.get("short_description", ""))
    parts = [x.strip() for x in sd.split(",") if x.strip()]
    keep = [x for x in parts if re.search(r"garancij|baterij|ohranjen|nov|embala|neaktiv|omrežj", x, re.I)]
    info = []
    if keep:
        info.append(" · ".join(k[:1].upper() + k[1:] for k in keep[:2]))
    warranty = next((k for k in parts if "garancij" in k.lower()), "")
    if warranty and not (info and warranty.lower() in info[0].lower()):
        info.append(warranty[:1].upper() + warranty[1:])
    chips = []
    for rx, label in ((r"\bnov\b", "Nov aparat"), (r"ohranjen", "Lepo ohranjen"), (r"garancij", None),
                      (r"baterij", None), (r"vsa omrežja", "Deluje na vsa omrežja"), (r"opreme|oprema", "Vsa oprema")):
        k = next((x for x in parts if re.search(rx, x, re.I)), None)
        if k:
            chips.append(label or (k[:1].upper() + k[1:]))
    if not used and "Nov aparat" not in chips and phone:
        chips.insert(0, "Nov aparat")
    if disc:
        tag = "AKCIJA"
    elif _age_days(p) <= NEW_DAYS:
        tag = "NOVO V PONUDBI"
    else:
        tag = "RABLJENO" if used else ("NOVO" if phone else "DODATKI")
    return {"name": clean(p["name"]), "price": price, "regular": reg, "discount": disc, "tag": tag,
            "info": info[:2], "chips": list(dict.fromkeys(chips))[:4], "url": p["permalink"], "used": used,
            "short": sd, "phone": phone, "warranty": warranty}


def _eur(v: float) -> str:
    return f"{v:.2f}".replace(".", ",") + " €"


def spoken_name(name: str) -> str:
    s = re.sub(r"\(.*?\)", " ", name)
    s = re.sub(r"\b\d+\s?GB(\s?/\s?\d+\s?GB)?\b", " ", s, flags=re.I)
    s = re.sub(r"\b(Dual SIM|5G|4G|LTE)\b", lambda m: " 5 G " if m.group(1) == "5G" else " ", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip()


def caption(d: dict, rnd: random.Random) -> str:
    brands = ("apple", "samsung", "xiaomi", "redmi", "poco", "huawei", "honor", "realme", "nokia", "motorola",
              "oneplus", "google", "oppo", "vivo", "sony", "lg", "nothing", "zte", "tcl", "doro", "cat")
    first = next((w for w in re.findall(r"[a-z]+", d["name"].lower()) if w in brands), "")
    brand = f" #{first}" if first else ""
    kind = ("rabljenitelefoni" if d["used"] else "novitelefoni") if d["phone"] else "dodatkizatelefone"
    if d["discount"]:
        head = rnd.choice([
            f"🔥 AKCIJA −{d['discount']} %: {d['name']}",
            f"💥 Znižano za {d['discount']} %! {d['name']}",
            f"⚡ Ugodna ponudba: {d['name']}",
        ])
        price = f"💶 Zdaj {_eur(d['price'])} namesto {_eur(d['regular'])}"
    else:
        icon = "♻️" if d["used"] else ("📱" if d["phone"] else "🔌")
        head = rnd.choice([f"{icon} {d['name']}", f"{icon} Novo v ponudbi: {d['name']}",
                           f"{icon} Iščete {spoken_name(d['name'])}? Imamo ga!"])
        price = f"💶 Cena: {_eur(d['price'])}"
    body = [head, price]
    if d["chips"]:
        body += [""] + [f"✅ {c}" for c in d["chips"]]
    outro = rnd.choice(["📦 Dostava po vsej Sloveniji", "🚚 Hitra dostava po vsej Sloveniji",
                        "🏪 Ogled možen tudi v naši prodajalni"])
    body += ["", f"🛒 Naroči: {d['url']}", outro, "",
             f"#mobitrgovina #telefoni #mobitel{brand} #{kind} #slovenija"]
    return "\n".join(body)


def voice_script(d: dict, rnd: random.Random) -> str:
    name = spoken_name(d["name"])
    intro = rnd.choice(["Novo v Mobitrgovini!", "Poglejte to ponudbo!", "Iščete nov telefon?" if d["phone"]
                        else "Potrebujete dodatno opremo?", "Pravkar prispelo!" if "NOVO" in d["tag"] else
                        "Super priložnost!"])
    if d["discount"]:
        deal = rnd.choice([f"{name}, zdaj za samo {_eur(d['price'])}.",
                           f"{name} je znižan za {d['discount']} odstotkov, samo še {_eur(d['price'])}."])
    else:
        deal = f"{name}, za {_eur(d['price'])}."
    cond = ""
    if d["phone"]:
        cond = "Rabljen, lepo ohranjen, z garancijo." if d["used"] else "Nov aparat z garancijo."
    cta = rnd.choice(["Naročite na mobitrgovina pika com.", "Več na mobitrgovina pika com, dostava po vsej Sloveniji.",
                      "Pohitite, dokler traja zaloga. Mobitrgovina pika com."])
    return " ".join(x for x in (intro, deal, cond, cta) if x)


BUYBACK_SCRIPTS = [
    "Imate doma star telefon, ki ga ne uporabljate več? V Mobitrgovini ga odkupimo za gotovino. "
    "Prinesite ga v našo prodajalno, strokovno ga pregledamo in vam takoj ponudimo odkupno ceno. "
    "Lahko ga zamenjate tudi za novega. Več na mobitrgovina pika com.",
    "Gotovinski odkup mobilnih telefonov in tablic! Pridite v Mobitrgovino, vaš aparat hitro ocenimo, "
    "denar dobite takoj. Ali pa ga zamenjate po sistemu staro za novo. Mobitrgovina pika com.",
    "Vaš stari telefon je vreden več, kot mislite. Odkupimo delujoče in nepoškodovane telefone in tablice. "
    "Gotovina takoj ali menjava za nov aparat. Obiščite Mobitrgovino.",
]

BUYBACK_CAPTIONS = [
    "💰 GOTOVINSKI ODKUP mobilnih telefonov in tablic!\n\nImate doma star telefon? Prinesite ga k nam – "
    "strokovno ga pregledamo in vam takoj ponudimo odkupno ceno.\n\n✅ Gotovina takoj\n✅ Ali menjava "
    "»staro za novo«\n✅ Hitra in poštena ocena",
    "📱➡️💶 Star telefon = gotovina!\n\nV Mobitrgovini odkupimo vaš telefon ali tablico. Izberete lahko "
    "gotovinsko izplačilo ali menjavo za aparat iz naše ponudbe.\n\n✅ Strokovna ocena\n✅ Izplačilo takoj",
    "🔄 Menjajte star telefon za novega – ali za gotovino!\n\nOdkupujemo delujoče in nepoškodovane "
    "telefone in tablice.\n\n✅ Staro za novo\n✅ Novo za staro\n✅ Gotovinsko izplačilo",
]


def buyback_caption(rnd: random.Random) -> str:
    return (rnd.choice(BUYBACK_CAPTIONS) + "\n\nℹ️ Pogoji: aparat mora biti delujoč, nepoškodovan in ne sme biti "
            f"zaklenjen (iCloud).\n👉 Več: {BUYBACK_URL}\n\n"
            "#odkuptelefonov #gotovina #mobitrgovina #rabljenitelefoni #staroZaNovo #slovenija")


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

# ---------------------------------------------------------------- zgodbe (stories)
def post_facebook_story(video: Path, text: str = "") -> str:
    page, tok = os.environ["FB_PAGE_ID"], os.environ["FB_PAGE_TOKEN"]
    start = _check(requests.post(f"{GRAPH}/{page}/video_stories",
                                 data={"upload_phase": "start", "access_token": tok}, timeout=60))
    vid = start["video_id"]
    size = video.stat().st_size
    with video.open("rb") as fh:
        _check(requests.post(start["upload_url"], data=fh, timeout=600,
                             headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(size)}))
    res = _check(requests.post(f"{GRAPH}/{page}/video_stories", timeout=60, data={
        "upload_phase": "finish", "video_id": vid, "access_token": tok}))
    return res.get("post_id", vid)


def post_instagram_story(video: Path, text: str = "") -> str:
    ig, tok = os.environ["IG_USER_ID"], os.environ["FB_PAGE_TOKEN"]
    c = _check(requests.post(f"{GRAPH}/{ig}/media", timeout=60, data={
        "media_type": "STORIES", "upload_type": "resumable", "access_token": tok}))
    cid, size = c["id"], video.stat().st_size
    with video.open("rb") as fh:
        _check(requests.post(c["uri"], data=fh, timeout=600,
                             headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(size)}))
    for _ in range(40):
        st = _check(requests.get(f"{GRAPH}/{cid}", params={"fields": "status_code", "access_token": tok}, timeout=60))
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram ni sprejel zgodbe: {st}")
        time.sleep(15)
    pub = _check(requests.post(f"{GRAPH}/{ig}/media_publish", timeout=60,
                               data={"creation_id": cid, "access_token": tok}))
    return pub["id"]
