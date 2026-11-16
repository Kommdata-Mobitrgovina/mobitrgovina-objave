"""Ena objava.
SLOT=izdelek (privzeto) ali SLOT=odkup (oglas za gotovinski odkup);
FORMAT=story (zgodba na FB in IG, privzeto) ali FORMAT=reel (objava na zidu kot Reel)."""
from __future__ import annotations

import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import music
import social
import tts
import video


def main() -> int:
    dry = os.environ.get("DRY_RUN") == "1"
    slot = os.environ.get("SLOT", "izdelek")
    fmt = os.environ.get("FORMAT", "story")
    rnd = random.Random()
    st = social.load_state()
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    products = social.candidates()

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
        return 0

    ok = False
    targets = ((("Facebook zgodba", social.post_facebook_story), ("Instagram zgodba", social.post_instagram_story))
               if fmt == "story" else
               (("Facebook Reel", social.post_facebook_reel), ("Instagram Reel", social.post_instagram_reel)))
    for label, fn in targets:
        try:
            print(f"{label}: objavljeno {fn(mp4, text)}")
            ok = True
        except Exception as e:  # ena platforma ne sme ustaviti druge
            print(f"{label}: NAPAKA {e}", file=sys.stderr)
    if ok:
        st[key if fmt == "story" else f"{key}-reel"] = datetime.now(timezone.utc).isoformat()
        if fmt == "reel":
            st[key] = st[f"{key}-reel"]
        social.save_state(st)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
