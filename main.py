"""Ena objava: izberi izdelek → naredi video → objavi na FB in IG → zapiši v state/posted.json."""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import social
import video


def main() -> int:
    dry = os.environ.get("DRY_RUN") == "1"
    st = social.load_state()
    p = social.pick(social.candidates(), st)
    if not p:
        print("Ni izdelkov za objavo.")
        return 0
    d = social.describe(p)
    text = social.caption(d)
    imgs = social.download_images(p)
    out = Path("out") / f"{p['id']}.mp4"
    out.parent.mkdir(exist_ok=True)
    video.render(d, imgs, out)
    (out.with_suffix(".txt")).write_text(text)
    print(f"Izdelek {p['id']}: {d['name']} – {d['price']} €\n{text}\nVideo: {out}")
    if dry:
        print("DRY_RUN: nič objavljeno.")
        return 0

    ok = False
    for name, fn in (("Facebook", social.post_facebook_reel), ("Instagram", social.post_instagram_reel)):
        try:
            print(f"{name}: objavljeno {fn(out, text)}")
            ok = True
        except Exception as e:  # ena platforma ne sme ustaviti druge
            print(f"{name}: NAPAKA {e}", file=sys.stderr)
    if ok:
        st[str(p["id"])] = datetime.now(timezone.utc).isoformat()
        social.save_state(st)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
