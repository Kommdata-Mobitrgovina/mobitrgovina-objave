"""Izdela navpičen video (1080x1920, ~10 s) za en izdelek: slike + ime + cena.

Okvirje riše Pillow, ffmpeg jih zapiše v MP4 (H.264 + tiha zvočna sled),
ki ga sprejmeta Facebook in Instagram Reels.
"""
from __future__ import annotations

import io
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
FONT_DIR = Path(__file__).parent / "fonts"

NAVY = (16, 32, 64)
ACCENT = (230, 40, 55)      # rdeča za akcijo
GREEN = (20, 140, 90)
GREY = (110, 118, 130)
BG_TOP = (238, 242, 248)
BG_BOTTOM = (255, 255, 255)


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / f"Poppins-{weight}.ttf"), size)


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def fmt_price(v: float) -> str:
    return f"{v:,.2f}".replace(",", " ").replace(".", ",") + " €"


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_w: int, max_lines: int = 3) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" ,.") + "…"
    return lines


def background() -> Image.Image:
    bg = Image.new("RGB", (W, H), BG_BOTTOM)
    d = ImageDraw.Draw(bg)
    for y in range(H):
        k = y / H
        c = tuple(int(BG_TOP[i] * (1 - k) + BG_BOTTOM[i] * k) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    return bg


def prepare_product_image(raw: bytes, box: int = 880) -> Image.Image:
    im = Image.open(io.BytesIO(raw)).convert("RGBA")
    # bela ozadja izdelkov naredimo prosojna, da se zlijejo z ozadjem
    px = im.getdata()
    im.putdata([(r, g, b, 0) if r > 245 and g > 245 and b > 245 else (r, g, b, a) for r, g, b, a in px])
    im.thumbnail((box, box), Image.LANCZOS)
    return im


class Renderer:
    def __init__(self, product: dict, images: list[bytes]):
        self.p = product
        self.imgs = [prepare_product_image(b) for b in images[:3]] or []
        self.bg = background()
        self.f_brand = font("Bold", 54)
        self.f_tag = font("Bold", 46)
        self.f_name = font("Bold", 64)
        self.f_info = font("Medium", 44)
        self.f_old = font("Medium", 62)
        self.f_price = font("Bold", 150)
        self.f_cta = font("Bold", 58)
        self.f_small = font("Regular", 40)

    # ---- elementi -------------------------------------------------------
    def header(self, d: ImageDraw.ImageDraw):
        d.rounded_rectangle([60, 70, W - 60, 190], radius=36, fill=NAVY)
        d.text((W // 2, 130), "MobiTrgovina", font=self.f_brand, fill="white", anchor="mm")

    def tag(self, d: ImageDraw.ImageDraw, alpha: float):
        if alpha <= 0:
            return
        label, color = self.p["tag"], (ACCENT if self.p.get("discount") else GREEN)
        tw = d.textlength(label, font=self.f_tag) + 70
        x = int(60 - (1 - ease(alpha)) * 400)
        d.rounded_rectangle([x, 230, x + tw, 320], radius=45, fill=color)
        d.text((x + tw / 2, 275), label, font=self.f_tag, fill="white", anchor="mm")
        if self.p.get("discount"):
            r = 110
            cx, cy = W - 60 - r, 300
            s = ease(alpha)
            rr = int(r * s)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=ACCENT)
            if s > 0.6:
                d.text((cx, cy), f"-{self.p['discount']}%", font=font("Bold", 64), fill="white", anchor="mm")

    def product(self, frame: Image.Image, idx: int, t: float, top: int = 380):
        if not self.imgs:
            return
        im = self.imgs[idx % len(self.imgs)]
        z = 1.0 + 0.07 * t  # počasen zoom
        w, h = int(im.width * z), int(im.height * z)
        imz = im.resize((w, h), Image.LANCZOS)
        cx, cy = W // 2, top + 470
        # mehka senca
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.ellipse([cx - w // 2.6, cy + h // 2 - 30, cx + w // 2.6, cy + h // 2 + 30], fill=(0, 0, 0, 60))
        shadow = shadow.filter(ImageFilter.GaussianBlur(25))
        frame.alpha_composite(shadow)
        frame.alpha_composite(imz, (cx - w // 2, cy - h // 2))

    def name_block(self, d: ImageDraw.ImageDraw, alpha: float, y0: int = 1400):
        if alpha <= 0:
            return
        dy = int((1 - ease(alpha)) * 80)
        lines = wrap(d, self.p["name"], self.f_name, W - 160, 2)
        y = y0 + dy
        for ln in lines:
            d.text((W // 2, y), ln, font=self.f_name, fill=NAVY, anchor="mm")
            y += 84
        info = self.p.get("info", [])
        for ln in info[:2]:
            d.text((W // 2, y + 20), ln, font=self.f_info, fill=GREY, anchor="mm")
            y += 62

    def price_card(self, d: ImageDraw.ImageDraw, alpha: float):
        a = ease(alpha)
        top = int(1180 + (1 - a) * 300)
        d.rounded_rectangle([60, top, W - 60, top + 560], radius=50, fill="white", outline=(225, 230, 238), width=4)
        y = top + 90
        if self.p.get("regular") and self.p["regular"] > self.p["price"]:
            old = fmt_price(self.p["regular"])
            d.text((W // 2, y), old, font=self.f_old, fill=GREY, anchor="mm")
            ow = d.textlength(old, font=self.f_old)
            d.line([(W // 2 - ow / 2 - 8, y + 4), (W // 2 + ow / 2 + 8, y + 4)], fill=ACCENT, width=7)
            y += 150
        else:
            y += 60
        d.text((W // 2, y), fmt_price(self.p["price"]), font=self.f_price,
               fill=ACCENT if self.p.get("discount") else NAVY, anchor="mm")
        y += 170
        d.rounded_rectangle([170, y - 55, W - 170, y + 55], radius=55, fill=NAVY)
        d.text((W // 2, y), "mobitrgovina.com", font=self.f_cta, fill="white", anchor="mm")

    def footer(self, d: ImageDraw.ImageDraw):
        d.text((W // 2, H - 90), "Dostava po vsej Sloveniji · Garancija", font=self.f_small, fill=GREY, anchor="mm")

    # ---- prizori --------------------------------------------------------
    def frame(self, sec: float) -> Image.Image:
        f = self.bg.convert("RGBA")
        d = ImageDraw.Draw(f)
        self.header(d)
        if sec < 3.6:                               # 1: slika + ime
            t = sec / 3.6
            self.product(f, 0, t)
            d = ImageDraw.Draw(f)
            self.tag(d, sec / 0.6)
            self.name_block(d, (sec - 0.4) / 0.6)
        elif sec < 6.6:                             # 2: druga slika + stanje
            t = (sec - 3.6) / 3.0
            self.product(f, 1, t)
            d = ImageDraw.Draw(f)
            self.tag(d, 1)
            self.name_block(d, 1)
        else:                                       # 3: cena + poziv
            t = (sec - 6.6) / 3.4
            self.product(f, 2 if len(self.imgs) > 2 else 0, t, top=260)
            d = ImageDraw.Draw(f)
            self.tag(d, 1)
            self.price_card(d, t / 0.25)
        self.footer(d)
        return f.convert("RGB")


def render(product: dict, images: list[bytes], out: Path, seconds: float = 10.0) -> Path:
    r = Renderer(product, images)
    n = int(seconds * FPS)
    fade = int(0.35 * FPS)
    cuts = [int(3.6 * FPS), int(6.6 * FPS)]
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    prev = None
    for i in range(n):
        cur = r.frame(i / FPS)
        # mehak prehod med prizori
        for c in cuts:
            if c <= i < c + fade and prev is not None:
                k = (i - c) / fade
                cur = Image.blend(r.frame((c - 1) / FPS), cur, k)
        proc.stdin.write(cur.tobytes())
        prev = cur
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg ni uspel")
    return out
