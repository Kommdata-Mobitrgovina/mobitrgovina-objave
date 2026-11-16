"""Navpični videi (1080x1920) za FB/IG Reels: izdelek ali oglas za odkup.

Vsak video dobi naključen slog (barve, postavitev, vrstni red prizorov), glas in glasbeno podlago,
tako da si objave niso podobne kot jajce jajcu.
"""
from __future__ import annotations

import io
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
FONT_DIR = Path(__file__).parent / "fonts"

THEMES = {
    "svetla": dict(top=(238, 242, 248), bottom=(255, 255, 255), text=(16, 32, 64), sub=(105, 114, 128),
                   accent=(230, 40, 55), head=(16, 32, 64), head_text=(255, 255, 255), card=(255, 255, 255),
                   chip=(232, 238, 248), glow=None),
    "temna": dict(top=(12, 15, 22), bottom=(30, 37, 52), text=(255, 255, 255), sub=(170, 180, 196),
                  accent=(255, 196, 0), head=(255, 196, 0), head_text=(12, 15, 22), card=(40, 48, 66),
                  chip=(48, 58, 80), glow=(255, 196, 0)),
    "modra": dict(top=(18, 52, 120), bottom=(70, 30, 140), text=(255, 255, 255), sub=(205, 215, 240),
                  accent=(255, 90, 95), head=(255, 255, 255), head_text=(30, 45, 120), card=(255, 255, 255),
                  chip=(255, 255, 255, 40), glow=(140, 170, 255)),
    "rdeca": dict(top=(200, 20, 40), bottom=(120, 10, 30), text=(255, 255, 255), sub=(255, 215, 215),
                  accent=(255, 220, 0), head=(255, 255, 255), head_text=(180, 20, 35), card=(255, 255, 255),
                  chip=(255, 255, 255, 45), glow=(255, 120, 120)),
}


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / f"Poppins-{weight}.ttf"), size)


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def fmt_price(v: float) -> str:
    return f"{v:,.2f}".replace(",", " ").replace(".", ",") + " €"


def wrap(draw, text, fnt, max_w, max_lines=3):
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


def gradient(top, bottom) -> Image.Image:
    col = Image.new("RGB", (1, H))
    for y in range(H):
        k = y / (H - 1)
        col.putpixel((0, y), tuple(int(top[i] * (1 - k) + bottom[i] * k) for i in range(3)))
    return col.resize((W, H))


def cutout(raw: bytes, box: int) -> Image.Image:
    im = Image.open(io.BytesIO(raw)).convert("RGBA")
    im.thumbnail((1200, 1200))
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r > 244 and g > 244 and b > 244:
                px[x, y] = (r, g, b, 0)
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)  # brez prosojnega roba, da senca sede tik pod izdelek
    im.thumbnail((box, box), Image.LANCZOS)
    return im


class Base:
    def __init__(self, theme: str | None, rnd: random.Random):
        self.rnd = rnd
        self.tname = theme or rnd.choice(list(THEMES))
        self.t = THEMES[self.tname]
        self.bg = gradient(self.t["top"], self.t["bottom"]).convert("RGBA")
        if self.t["glow"]:
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gx, gy = rnd.choice([(W // 2, 760), (W // 3, 650), (2 * W // 3, 820)])
            gd.ellipse([gx - 480, gy - 480, gx + 480, gy + 480], fill=self.t["glow"] + (70,))
            self.bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
        self.header_style = rnd.choice(["pill", "line"])

    def header(self, d):
        t = self.t
        if self.header_style == "pill":
            d.rounded_rectangle([60, 70, W - 60, 185], radius=58, fill=t["head"])
            d.text((W // 2, 128), "MobiTrgovina", font=font("Bold", 52), fill=t["head_text"], anchor="mm")
        else:
            d.text((70, 128), "MobiTrgovina", font=font("Bold", 56), fill=t["text"], anchor="lm")
            d.text((W - 70, 128), "mobitrgovina.com", font=font("Medium", 34), fill=t["sub"], anchor="rm")
            d.line([(70, 190), (W - 70, 190)], fill=t["accent"], width=5)

    def place(self, frame, im, cx, cy, z=1.0, shadow=True):
        w, h = int(im.width * z), int(im.height * z)
        imz = im.resize((w, h), Image.LANCZOS)
        if shadow:
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse([cx - w * 0.38, cy + h / 2 - 28, cx + w * 0.38, cy + h / 2 + 28],
                                       fill=(0, 0, 0, 70))
            frame.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
        frame.alpha_composite(imz, (int(cx - w / 2), int(cy - h / 2)))

    def footer(self, d, text="Dostava po vsej Sloveniji · Garancija"):
        d.text((W // 2, H - 95), text, font=font("Regular", 38), fill=self.t["sub"], anchor="mm")


class ProductVideo(Base):
    def __init__(self, p: dict, images: list[bytes], theme=None, seed=None):
        super().__init__(theme, random.Random(seed))
        self.p = p
        self.imgs = [cutout(b, 860) for b in images[:3]]
        self.small = [cutout(b, 520) for b in images[:3]]
        self.mid_variant = self.rnd.choice(["chips", "split"])

    def tag(self, d, a):
        if a <= 0:
            return
        t, p = self.t, self.p
        label = p["tag"]
        f = font("Bold", 44)
        tw = d.textlength(label, font=f) + 70
        x = int(60 - (1 - ease(a)) * 420)
        d.rounded_rectangle([x, 230, x + tw, 318], radius=44, fill=t["accent"])
        d.text((x + tw / 2, 274), label, font=f, fill=(255, 255, 255) if self.tname != "temna" else (12, 15, 22),
               anchor="mm")
        if p.get("discount"):
            r = int(108 * ease(a))
            cx, cy = W - 170, 300
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=t["accent"])
            if a > 0.6:
                d.text((cx, cy), f"-{p['discount']}%", font=font("Bold", 62),
                       fill=(255, 255, 255) if self.tname != "temna" else (12, 15, 22), anchor="mm")

    def name(self, d, a, y0=1390):
        if a <= 0:
            return
        y = y0 + int((1 - ease(a)) * 90)
        for ln in wrap(d, self.p["name"], font("Bold", 66), W - 150, 2):
            d.text((W // 2, y), ln, font=font("Bold", 66), fill=self.t["text"], anchor="mm")
            y += 86
        for ln in self.p.get("info", [])[:2]:
            d.text((W // 2, y + 22), ln, font=font("Medium", 42), fill=self.t["sub"], anchor="mm")
            y += 60

    def chips(self, frame, d, a):
        items = [x for x in (self.p.get("chips") or []) if x][:4]
        y = 1290
        for i, txt in enumerate(items):
            ai = ease(a * 2.2 - i * 0.35)
            if ai <= 0:
                continue
            f = font("Medium", 44)
            tw = d.textlength(txt, font=f) + 140
            x = W // 2 - tw / 2 + (1 - ai) * 200
            chip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            cd = ImageDraw.Draw(chip)
            col = self.t["chip"] if len(self.t["chip"]) == 4 else self.t["chip"] + (255,)
            cd.rounded_rectangle([x, y, x + tw, y + 96], radius=48, fill=col[:3] + (int(col[3] * ai),))
            frame.alpha_composite(chip)
            d = ImageDraw.Draw(frame)
            d.line([(x + 40, y + 50), (x + 55, y + 64), (x + 82, y + 34)], fill=self.t["accent"], width=8, joint="curve")
            d.text((x + 105, y + 48), txt, font=f, fill=self.t["text"], anchor="lm")
            y += 120
        return ImageDraw.Draw(frame)

    def price(self, d, a):
        t, p = self.t, self.p
        e = ease(a)
        top = int(1150 + (1 - e) * 320)
        d.rounded_rectangle([60, top, W - 60, top + 580], radius=54, fill=(255, 255, 255))
        ink = (16, 32, 64)
        y = top + 95
        if p.get("regular") and p["regular"] > p["price"]:
            old = fmt_price(p["regular"])
            fo = font("Medium", 60)
            d.text((W // 2, y), old, font=fo, fill=(120, 128, 140), anchor="mm")
            ow = d.textlength(old, font=fo)
            d.line([(W // 2 - ow / 2 - 8, y + 4), (W // 2 + ow / 2 + 8, y + 4)], fill=(230, 40, 55), width=7)
            y += 150
        else:
            y += 65
        d.text((W // 2, y), fmt_price(p["price"]), font=font("Bold", 150),
               fill=(230, 40, 55) if p.get("discount") else ink, anchor="mm")
        y += 175
        d.rounded_rectangle([160, y - 56, W - 160, y + 56], radius=56, fill=ink)
        d.text((W // 2, y), "mobitrgovina.com", font=font("Bold", 56), fill=(255, 255, 255), anchor="mm")

    def frame(self, s: float, T: float) -> Image.Image:
        c1, c2 = T * 0.36, T * 0.66
        f = self.bg.copy()
        d = ImageDraw.Draw(f)
        self.header(d)
        n = len(self.imgs)
        if s < c1:
            if n:
                self.place(f, self.imgs[0], W // 2, 850, 1 + 0.08 * s / c1)
            d = ImageDraw.Draw(f)
            self.tag(d, s / 0.6)
            self.name(d, (s - 0.4) / 0.6)
        elif s < c2:
            u = (s - c1) / (c2 - c1)
            if self.mid_variant == "split" and n:
                self.place(f, self.small[1 % n], W // 2, 760, 1 + 0.06 * u)
                d = self.chips(f, ImageDraw.Draw(f), u)
            else:
                if n:
                    self.place(f, self.imgs[1 % n], W // 2, 850, 1.08 - 0.06 * u)
                d = ImageDraw.Draw(f)
                self.name(d, 1)
            self.tag(d, 1)
        else:
            u = (s - c2) / (T - c2)
            if n:
                self.place(f, self.small[2 % n] if n > 2 else self.small[0], W // 2, 700, 1 + 0.06 * u)
            d = ImageDraw.Draw(f)
            self.tag(d, 1)
            self.price(d, u / 0.22)
        self.footer(d)
        return f.convert("RGB")

    def cuts(self, T):
        return [T * 0.36, T * 0.66]


class BuybackVideo(Base):
    STEPS = [
        ["Prinesite telefon ali tablico", "Strokovno ga pregledamo", "Gotovina takoj ali menjava"],
        ["Pridite v našo prodajalno", "Ocenimo vaš aparat", "Izplačilo v gotovini"],
        ["Prinesite star aparat", "Hitra in poštena ocena", "Denar ali nov telefon"],
    ]
    HEADS = [("GOTOVINSKI", "ODKUP"), ("ODKUPIMO", "VAŠ TELEFON"), ("STAR TELEFON", "= GOTOVINA")]

    def __init__(self, images: list[bytes], theme=None, seed=None):
        super().__init__(theme, random.Random(seed))
        self.imgs = [cutout(b, 520) for b in images[:3]]
        self.steps = self.rnd.choice(self.STEPS)
        self.head = self.rnd.choice(self.HEADS)

    def frame(self, s: float, T: float) -> Image.Image:
        t = self.t
        c1, c2 = T * 0.34, T * 0.70
        f = self.bg.copy()
        d = ImageDraw.Draw(f)
        self.header(d)
        if s < c1:
            u = s / c1
            pos = [(W // 2 - 270, 800, -12), (W // 2 + 270, 800, 12), (W // 2, 760, 0)]
            for i, im in enumerate(self.imgs[:3]):
                a = ease(u * 3 - i * 0.4)
                if a <= 0:
                    continue
                x, y, rot = pos[i if len(self.imgs) > 1 else 2]
                r = im.rotate(rot * a, expand=True, resample=Image.BICUBIC)
                self.place(f, r, x, y + (1 - a) * 300, 0.9 + 0.1 * a)
            d = ImageDraw.Draw(f)
            a = ease((s - 0.3) / 0.7)
            y = 1300 + int((1 - a) * 80)
            d.text((W // 2, y), self.head[0], font=font("Bold", 104), fill=t["text"], anchor="mm")
            d.text((W // 2, y + 125), self.head[1], font=font("Bold", 104), fill=t["accent"], anchor="mm")
            d.text((W // 2, y + 245), "mobilnih telefonov in tablic", font=font("Medium", 48), fill=t["sub"],
                   anchor="mm")
        elif s < c2:
            u = (s - c1) / (c2 - c1)
            d.text((W // 2, 330), "Kako poteka?", font=font("Bold", 84), fill=t["text"], anchor="mm")
            for i, txt in enumerate(self.steps):
                a = ease(u * 2.4 - i * 0.45)
                if a <= 0:
                    continue
                y = 560 + i * 330
                x = 110 + (1 - a) * -300
                d.ellipse([x, y, x + 170, y + 170], fill=t["accent"])
                d.text((x + 85, y + 85), str(i + 1), font=font("Bold", 92),
                       fill=(12, 15, 22) if self.tname == "temna" else (255, 255, 255), anchor="mm")
                lines = wrap(d, txt, font("Bold", 56), int(W - x - 290), 2)
                y0 = y + 85 - (len(lines) - 1) * 36
                for k, ln in enumerate(lines):
                    d.text((x + 215, y0 + k * 72), ln, font=font("Bold", 56), fill=t["text"], anchor="lm")
        else:
            u = (s - c2) / (T - c2)
            a = ease(u / 0.25)
            top = int(520 + (1 - a) * 260)
            d.rounded_rectangle([60, top, W - 60, top + 900], radius=56, fill=(255, 255, 255))
            ink = (16, 32, 64)
            d.text((W // 2, top + 130), "Staro za novo", font=font("Bold", 86), fill=ink, anchor="mm")
            d.text((W // 2, top + 235), "ali gotovina na roko", font=font("Medium", 54), fill=(110, 118, 130),
                   anchor="mm")
            for k, ln in enumerate(["Odkupujemo delujoče in", "nepoškodovane aparate"]):
                d.text((W // 2, top + 380 + k * 64), ln, font=font("Regular", 46), fill=(110, 118, 130), anchor="mm")
            y = top + 640
            d.rounded_rectangle([110, y - 62, W - 110, y + 62], radius=62, fill=(230, 40, 55))
            d.text((W // 2, y), "Pridite k nam!", font=font("Bold", 60), fill=(255, 255, 255), anchor="mm")
            d.text((W // 2, y + 140), "mobitrgovina.com/odkup-telefona", font=font("Bold", 44), fill=ink, anchor="mm")
        self.footer(d, "Hitro · Pošteno · Brez skrbi")
        return f.convert("RGB")

    def cuts(self, T):
        return [T * 0.34, T * 0.70]


def render(r: Base, out: Path, seconds: float, music: Path | None = None, voice: Path | None = None) -> Path:
    T = max(9.0, seconds)
    n = int(T * FPS)
    fade = int(0.35 * FPS)
    cuts = [int(c * FPS) for c in r.cuts(T)]
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if music:
        cmd += ["-i", str(music)]
    else:
        cmd += ["-f", "lavfi", "-t", str(T), "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    if voice:
        cmd += ["-i", str(voice)]
        filt = ("[1:a]volume=0.55[m];[2:a]adelay=450|450,volume=1.5,aformat=channel_layouts=stereo,asplit[v1][v2];"
                "[m][v1]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=350[md];"
                f"[md][v2]amix=inputs=2:normalize=0,atrim=0:{T},afade=t=out:st={T - 0.8}:d=0.8[a]")
    else:
        filt = f"[1:a]volume=0.8,atrim=0:{T},afade=t=out:st={T - 0.8}:d=0.8[a]"
    cmd += ["-filter_complex", filt, "-map", "0:v", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-c:a", "aac", "-b:a", "160k", "-t", str(T), "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    cache = {}
    for i in range(n):
        cur = r.frame(i / FPS, T)
        for c in cuts:
            if c <= i < c + fade:
                if c not in cache:
                    cache[c] = r.frame((c - 1) / FPS, T)
                cur = Image.blend(cache[c], cur, (i - c) / fade)
        proc.stdin.write(cur.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg ni uspel")
    return out
