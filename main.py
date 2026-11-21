"""Ena objava.
SLOT=izdelek (privzeto) ali SLOT=odkup (oglas za gotovinski odkup);
FORMAT=story (zgodba na FB in IG, privzeto), FORMAT=reel (objava na zidu kot Reel)
ali FORMAT=tiktok (angleški video za EU, pošlje se Marku na Telegram za objavo na TikToku)."""
from __future__ import annotations

import os
import random
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import music
import obvestila
import social
import tts
import video
import zabava


def main() -> int:
    dry = os.environ.get("DRY_RUN") == "1"
    slot = os.environ.get("SLOT", "izdelek")
    fmt = os.environ.get("FORMAT", "story")
    rnd = random.Random()
    st = social.load_state()
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    products = social.candidates()

    if fmt == "tiktok":
        return tiktok(dry, st, products, rnd, out_dir)
    if fmt == "reel" and slot == "izdelek" and zabava.is_fun_reel_turn(st):
        return reel_zabava(dry, st, rnd, out_dir)  # izmenično: Reel z izdelkom, potem zabaven Reel

    if slot == "odkup":
        key = "odkup-" + datetime.now(timezone.utc).strftime("%Y-%m-%d")
        phones = [p for p in products if social.is_phone(p) and not social.describe(p)["used"]][:12]
        imgs = []
        for p in rnd.sample(phones, min(3, len(phones))):
            imgs += social.download_images(p, 1)
        text = social.buyback_caption(rnd)
        script = rnd.choice(social.BUYBACK_SCRIPTS)
        renderer = video.BuybackVideo(imgs)
        name = "Gotovinski odkup"
    else:
        p = social.pick(products, st, rnd)
        if not p:
            print("Ni izdelkov za objavo.")
            return 0
        key = str(p["id"])
        d = social.describe(p)
        text = social.caption(d, rnd)
        script = social.voice_script(d, rnd)
        renderer = video.ProductVideo(d, social.download_images(p))
        name = f"{d['name']} – {d['price']} €"

    voice = tts.speak(script, out_dir / f"{key}.mp3")
    seconds = (voice[1] + 1.6) if voice else 10.0
    bed = music.make(out_dir / f"{key}.wav", max(9.0, seconds) + 0.5)
    mp4 = out_dir / f"{key}.mp4"
    video.render(renderer, mp4, seconds, music=bed, voice=voice[0] if voice else None)
    mp4.with_suffix(".txt").write_text(f"{text}\n\n--- govor ---\n{script}\n--- slog: {renderer.tname} ---")
    print(f"{slot} / {fmt}: {name}\nslog: {renderer.tname}\n\n{text}\n\nGovor: {script}\nVideo: {mp4}")
    if dry:
        print("DRY_RUN: nič objavljeno.")
        obvestila.send(f"🧪 Preizkus ({slot}/{fmt}): {name} – video narejen, nič objavljeno.")
        return 0

    ok = False
    targets = ((("Facebook zgodba", social.post_facebook_story), ("Instagram zgodba", social.post_instagram_story))
               if fmt == "story" else
               (("Facebook Reel", social.post_facebook_reel), ("Instagram Reel", social.post_instagram_reel)))
    results = []
    for label, fn in targets:
        try:
            print(f"{label}: objavljeno {fn(mp4, text)}")
            ok = True
            results.append(f"✅ {label}")
        except Exception as e:  # ena platforma ne sme ustaviti druge
            print(f"{label}: NAPAKA {e}", file=sys.stderr)
            results.append(f"❌ {label}: {str(e)[:150]}")
    vrsta = "Zgodba" if fmt == "story" else "Reel"
    obvestila.send(f"{'📣' if ok else '⚠️'} {vrsta} – {name}\n" + "\n".join(results))
    if ok:
        st[key if fmt == "story" else f"{key}-reel"] = datetime.now(timezone.utc).isoformat()
        if fmt == "reel":
            st[key] = st[f"{key}-reel"]
        social.save_state(st)
    return 0 if ok else 1


def tiktok(dry, st, products, rnd, out_dir) -> int:
    seen = {k[:-3]: v for k, v in st.items() if k.endswith("-tt")}
    p = social.pick([x for x in products if social.is_phone(x)], seen, rnd)
    # izmenično: oglas za telefon, potem zabavna vsebina o mobilni telefoniji (zanimivost, mit, kviz, šala)
    if not p or os.environ.get("TT_VRSTA") == "zabava" or (os.environ.get("TT_VRSTA") != "izdelek"
                                                           and zabava.is_fun_turn(st)):
        return tiktok_zabava(dry, st, rnd, out_dir)
    d = social.describe(p)
    screen_hook, spoken_hook = social.tiktok_hook(d, rnd)
    script = social.tiktok_script(d, spoken_hook, rnd)
    text = social.tiktok_caption(d, screen_hook, rnd)
    key = f"{p['id']}-tt"
    renderer = video.ProductVideo(social.describe_en(d), social.download_images(p), en=True, hook=screen_hook)
    voice = tts.speak(script, out_dir / f"{key}.mp3", en=True)
    seconds = (voice[1] + 1.8) if voice else 10.0
    bed = music.make(out_dir / f"{key}.wav", max(9.0, seconds) + 0.5)
    mp4 = out_dir / f"{key}.mp4"
    video.render(renderer, mp4, seconds, music=bed, voice=voice[0] if voice else None)
    mp4.with_suffix(".txt").write_text(f"{text}\n\n--- voice ---\n{script}")
    print(f"tiktok: {d['name']}\n\n{text}\n\nVoice: {script}")
    head = ("🧪 Preizkus – " if dry else "") + "🎵 TikTok video je pripravljen. Objavi ga s telefona, besedilo je spodaj."
    if not obvestila.send_video(mp4, head):
        print("Video na Telegram ni šel.")
        return 1
    obvestila.send(text)
    if not dry:
        st[key] = datetime.now(timezone.utc).isoformat()
        social.save_state(st)
        # arhiv za Marka: video in besedilo se shranita v repozitorij (mapa tiktok/),
        # od tam ju načrtovano opravilo prenese na njegov računalnik
        arhiv = Path("tiktok")
        arhiv.mkdir(exist_ok=True)
        ime = datetime.now(timezone.utc).strftime("%Y-%m-%d") + "_" + re.sub(r"[^A-Za-z0-9]+", "-", d["name"])[:60].strip("-")
        shutil.copy(mp4, arhiv / f"{ime}.mp4")
        (arhiv / f"{ime}.txt").write_text(text)
    return 0


def tiktok_zabava(dry, st, rnd, out_dir) -> int:
    it = zabava.pick(st, rnd)
    key = zabava.key(it)
    script = zabava.script(it, rnd)
    text = zabava.caption(it, rnd)
    voice = tts.speak(script, out_dir / f"{key}.mp3", en=True)
    seconds = (voice[1] + 2.6) if voice else 12.0
    bed = music.make(out_dir / f"{key}.wav", max(9.0, seconds) + 0.5)
    mp4 = out_dir / f"{key}.mp4"
    video.render(zabava.FunVideo(it), mp4, seconds, music=bed, voice=voice[0] if voice else None)
    mp4.with_suffix(".txt").write_text(f"{text}\n\n--- voice ---\n{script}")
    print(f"tiktok zabava: {it['id']}\n\n{text}\n\nVoice: {script}")
    head = ("🧪 Preizkus – " if dry else "") + "🎵 TikTok video (zabava) je pripravljen. Besedilo je spodaj."
    if not obvestila.send_video(mp4, head):
        print("Video na Telegram ni šel.")
        return 1
    obvestila.send(text)
    if not dry:
        st[key] = datetime.now(timezone.utc).isoformat()
        social.save_state(st)
        arhiv = Path("tiktok")
        arhiv.mkdir(exist_ok=True)
        ime = datetime.now(timezone.utc).strftime("%Y-%m-%d") + "_Zabava-" + re.sub(r"[^A-Za-z0-9]+", "-", it["id"])
        shutil.copy(mp4, arhiv / f"{ime}.mp4")
        (arhiv / f"{ime}.txt").write_text(text)
    return 0



def reel_zabava(dry, st, rnd, out_dir) -> int:
    """Zabaven Reel v slovenščini (zanimivost, mit, kviz, šala) na FB in IG."""
    it = zabava.pick_sl(st, rnd)
    key = zabava.key_sl(it)
    script = zabava.script_sl(it, rnd)
    text = zabava.caption_sl(it, rnd)
    voice = tts.speak(script, out_dir / f"{key}.mp3")
    seconds = (voice[1] + 2.6) if voice else 12.0
    bed = music.make(out_dir / f"{key}.wav", max(9.0, seconds) + 0.5)
    mp4 = out_dir / f"{key}.mp4"
    video.render(zabava.FunVideo(it, lang="sl"), mp4, seconds, music=bed, voice=voice[0] if voice else None)
    mp4.with_suffix(".txt").write_text(f"{text}\n\n--- govor ---\n{script}")
    print(f"reel zabava: {it['id']}\n\n{text}\n\nGovor: {script}")
    if dry:
        print("DRY_RUN: nič objavljeno.")
        obvestila.send_video(mp4, "🧪 Preizkus – zabaven Reel, nič objavljeno.")
        return 0
    ok, results = False, []
    for label, fn in (("Facebook Reel", social.post_facebook_reel), ("Instagram Reel", social.post_instagram_reel)):
        try:
            print(f"{label}: objavljeno {fn(mp4, text)}")
            ok = True
            results.append(f"✅ {label}")
        except Exception as e:  # ena platforma ne sme ustaviti druge
            print(f"{label}: NAPAKA {e}", file=sys.stderr)
            results.append(f"❌ {label}: {str(e)[:150]}")
    obvestila.send(f"{'🎉' if ok else '⚠️'} Zabaven Reel – {it['id']}\n" + "\n".join(results))
    if ok:
        st[key] = datetime.now(timezone.utc).isoformat()
        social.save_state(st)
    return 0 if ok else 1



if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        obvestila.send(f"⚠️ Objava ni uspela: {str(e)[:300]}")
        raise
