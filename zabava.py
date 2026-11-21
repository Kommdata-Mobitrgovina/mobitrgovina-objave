"""Zabavni TikTok videi o mobilni telefoniji (angleško): zanimivosti, miti, kvizi in »POV« šale.

Vsak drugi TikTok je tak namesto oglasa za izdelek, da profil ni samo prodaja.
Vsebina je zbirka preverjenih kratkih zgodb; ista se ne ponovi, dokler niso porabljene vse.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone

from PIL import Image, ImageDraw

from video import H, W, Base, ease, font, wrap

# kind: fact = zanimivost, myth = mit ali dejstvo, quiz = ugani, pov = šala, tip = nasvet
ITEMS = [
    dict(id="first-call", kind="fact", hook="THE FIRST MOBILE PHONE CALL EVER",
         body=["April 3, 1973", "New York City", "Motorola engineer Martin Cooper called his rival at Bell Labs"],
         reveal="Talk about a flex.",
         voice="The first mobile phone call ever was made on April 3rd, 1973, in New York. "
               "Motorola engineer Martin Cooper used it to call his rival at Bell Labs. Talk about a flex."),
    dict(id="dynatac-price", kind="quiz", hook="HOW MUCH DID THE FIRST MOBILE PHONE COST?",
         body=["Motorola DynaTAC 8000X", "Year: 1983", "Weight: almost 800 g"],
         reveal="$3,995",
         voice="How much did the very first mobile phone cost? The Motorola DynaTAC, 1983, almost 800 grams. "
               "The answer: 3995 dollars. And about 30 minutes of talk time."),
    dict(id="first-sms", kind="fact", hook="THE FIRST TEXT MESSAGE EVER SENT SAID…",
         body=["December 3, 1992", "Sent from a computer to a phone", "Two words long"],
         reveal="\"Merry Christmas\"",
         voice="The first text message ever was sent on December 3rd, 1992. It was typed on a computer, "
               "sent to a phone, and it said: Merry Christmas."),
    dict(id="nokia-1100", kind="quiz", hook="THE BEST-SELLING PHONE OF ALL TIME IS…",
         body=["Not an iPhone", "Not a Samsung", "Over 250 million sold"],
         reveal="Nokia 1100",
         voice="The best-selling phone of all time? Not an iPhone. Not a Samsung. "
               "It's the Nokia 1100, with more than 250 million sold."),
    dict(id="snake", kind="fact", hook="SNAKE WAS ON NOKIA PHONES SINCE 1997",
         body=["First on the Nokia 6110", "No app store", "No Wi-Fi"],
         reveal="Still undefeated.",
         voice="Snake first showed up on the Nokia 6110 back in 1997. No app store, no Wi-Fi, "
               "and still one of the most addictive games ever."),
    dict(id="apollo", kind="fact", hook="YOUR PHONE VS. THE MOON LANDING",
         body=["Apollo 11 guidance computer: 1969", "Your phone: in your pocket", "Millions of times more powerful"],
         reveal="And we use it for memes.",
         voice="The phone in your pocket is millions of times more powerful than the computer that guided "
               "Apollo 11 to the Moon. And we mostly use it for memes."),
    dict(id="nomophobia", kind="fact", hook="THERE'S A WORD FOR THIS FEELING",
         body=["Phone not in your pocket", "Heart rate goes up", "Panic search begins"],
         reveal="Nomophobia",
         voice="That panic when you can't find your phone? There's a word for it. "
               "Nomophobia, the fear of being without your phone. Tag someone who has it."),
    dict(id="guess-3310", kind="quiz", hook="GUESS THE YEAR: NOKIA 3310",
         body=["Indestructible", "Battery for days", "Snake II included"],
         reveal="2000",
         voice="Guess the year. The Nokia 3310. Indestructible, battery for days, Snake 2 included. "
               "It came out in the year 2000."),
    dict(id="guess-iphone", kind="quiz", hook="GUESS THE YEAR: THE FIRST iPHONE",
         body=["3.5-inch screen", "No App Store at launch", "2 megapixel camera"],
         reveal="2007",
         voice="Guess the year. The first iPhone. A 3.5 inch screen, no App Store at launch, "
               "and a 2 megapixel camera. It launched in 2007."),
    dict(id="guess-android", kind="quiz", hook="GUESS THE YEAR: THE FIRST ANDROID PHONE",
         body=["HTC Dream / T-Mobile G1", "Slide-out keyboard", "Trackball"],
         reveal="2008",
         voice="Guess the year. The first Android phone, the HTC Dream, also called the T-Mobile G1. "
               "A slide-out keyboard and a trackball. It came out in 2008."),
    dict(id="guess-razr", kind="quiz", hook="GUESS THE YEAR: MOTOROLA RAZR V3",
         body=["Thin flip phone", "Metal body", "Everybody wanted one"],
         reveal="2004",
         voice="Guess the year. The Motorola Razr V3. Super thin, metal, and everybody wanted one. "
               "It came out in 2004."),
    dict(id="myth-overnight", kind="myth", hook="MYTH OR FACT: CHARGING OVERNIGHT KILLS YOUR BATTERY",
         body=["Modern phones stop charging when full", "Many can pause at 80% overnight", "Heat is the real enemy"],
         reveal="MYTH",
         voice="Myth or fact? Charging overnight kills your battery. Mostly a myth. Modern phones stop "
               "charging when they're full, and many can pause at 80 percent overnight. Heat is the real enemy."),
    dict(id="myth-close-apps", kind="myth", hook="MYTH OR FACT: CLOSING APPS SAVES BATTERY",
         body=["Your phone already freezes apps in the background", "Reopening them from zero costs more"],
         reveal="MYTH",
         voice="Myth or fact? Closing all your apps saves battery. Myth. Your phone already pauses apps "
               "in the background, and opening them again from zero actually uses more power."),
    dict(id="myth-megapixels", kind="myth", hook="MYTH OR FACT: MORE MEGAPIXELS = BETTER PHOTOS",
         body=["Sensor size matters", "Lens and processing matter", "Megapixels are just one number"],
         reveal="MYTH",
         voice="Myth or fact? More megapixels means better photos. Myth. Sensor size, the lens and the "
               "processing matter a lot more. Megapixels are just one number on the box."),
    dict(id="myth-drain", kind="myth", hook="MYTH OR FACT: DRAIN YOUR BATTERY TO 0% SOMETIMES",
         body=["That was for old battery types", "Lithium-ion likes the middle", "Try to stay between 20% and 80%"],
         reveal="MYTH",
         voice="Myth or fact? You should drain your battery to zero sometimes. Myth. That was for old batteries. "
               "Lithium ion is happiest between about 20 and 80 percent."),
    dict(id="fact-airplane", kind="myth", hook="MYTH OR FACT: AIRPLANE MODE CHARGES FASTER",
         body=["No searching for signal", "Fewer background tasks", "A little faster, not magic"],
         reveal="FACT",
         voice="Myth or fact? Airplane mode makes your phone charge faster. Fact, a little bit. "
               "Your phone stops searching for signal, so more power goes into the battery."),
    dict(id="pov-1percent", kind="pov", hook="POV: YOUR PHONE IS AT 1%",
         body=["Brightness: lowest", "Low power mode: ON", "Still trying to send one last voice message"],
         reveal="Phone: *dies*",
         voice="P O V. Your phone is at one percent. Brightness all the way down, low power mode on, "
               "and you still try to send one last voice message. And it dies."),
    dict(id="pov-holding", kind="pov", hook="POV: LOOKING FOR YOUR PHONE…",
         body=["Checks pockets", "Checks the couch", "Asks everyone in the room"],
         reveal="…while holding it",
         voice="P O V. You're looking for your phone. Pockets. Couch. You ask everyone in the room. "
               "And it was in your hand the whole time."),
    dict(id="pov-drop", kind="pov", hook="POV: YOU JUST DROPPED YOUR PHONE",
         body=["It lands face down", "Nobody moves", "The slowest pickup of your life"],
         reveal="Get a case. Seriously.",
         voice="P O V. You just dropped your phone. It lands face down. Nobody moves. "
               "The slowest pickup of your life. Get a case. Seriously."),
    dict(id="pov-one-notification", kind="pov", hook="\"I'LL JUST CHECK ONE NOTIFICATION\"",
         body=["9:00 – one notification", "9:05 – just one more video", "11:40 – how did this happen"],
         reveal="Every. Single. Time.",
         voice="I'll just check one notification. Nine o'clock. Just one more video. "
               "Suddenly it's eleven forty. Every single time."),
    dict(id="pov-20", kind="pov", hook="ME WHEN MY PHONE IS AT 21%",
         body=["Totally fine", "Living my life", "Not worried at all"],
         reveal="20%: PANIC MODE",
         voice="Me when my phone is at 21 percent. Totally fine, living my life. "
               "Twenty percent? Panic mode."),
    dict(id="tip-restart", kind="tip", hook="DO THIS ONCE A WEEK",
         body=["Restart your phone", "Clears stuck apps and memory", "Fixes a lot of weird bugs"],
         reveal="30 seconds. Big difference.",
         voice="Do this once a week. Just restart your phone. It clears stuck apps and memory, "
               "and fixes a lot of weird little bugs. Thirty seconds, big difference."),
    dict(id="tip-heat", kind="tip", hook="THE #1 THING THAT KILLS PHONE BATTERIES",
         body=["Not charging overnight", "Not old age alone", "It's this:"],
         reveal="HEAT",
         voice="The number one thing that kills phone batteries? Not charging overnight. "
               "It's heat. Don't leave your phone in a hot car or charge it under your pillow."),
    dict(id="tip-used", kind="tip", hook="WHAT TO CHECK BEFORE BUYING A USED PHONE",
         body=["Battery health", "Network unlocked", "Warranty from the seller"],
         reveal="No warranty? Walk away.",
         voice="What to check before you buy a used phone. Battery health. Is it unlocked? "
               "And does the seller give you a warranty? No warranty? Walk away."),
]

KIND_LABEL = {"fact": "DID YOU KNOW?", "myth": "MYTH OR FACT?", "quiz": "QUIZ TIME", "pov": "RELATABLE?",
              "tip": "PHONE TIP"}
KIND_TAGS = {"fact": ["#didyouknow", "#techfacts", "#phonehistory"],
             "myth": ["#mythorfact", "#techtips", "#batterylife"],
             "quiz": ["#guesstheyear", "#throwback", "#retrotech"],
             "pov": ["#pov", "#relatable", "#phoneproblems"],
             "tip": ["#techtips", "#phonetips", "#lifehack"]}
CTAS = ["Follow for more phone stuff!", "Comment your answer below!", "Tag a friend who needs to see this!",
        "Follow for more!"]


def key(item: dict) -> str:
    return f"zabava-{item['id']}"


def pick(st: dict, rnd: random.Random) -> dict:
    """Še ne uporabljena vsebina; ko je vse porabljeno, najstarejša."""
    fresh = [i for i in ITEMS if key(i) not in st]
    if fresh:
        return rnd.choice(fresh)
    return min(ITEMS, key=lambda i: st[key(i)])


def is_fun_turn(st: dict) -> bool:
    """Izmenično: če je bil zadnji TikTok oglas za izdelek, je zdaj na vrsti zabava (in obratno)."""
    def last(pred):
        ts = [v for k, v in st.items() if pred(k)]
        return max(ts) if ts else ""
    return last(lambda k: k.startswith("zabava-")) <= last(lambda k: k.endswith("-tt"))


def script(item: dict, rnd: random.Random) -> str:
    return f"{item['voice']} {rnd.choice(CTAS)}"


def caption(item: dict, rnd: random.Random) -> str:
    first = rnd.choice(["📱", "🤯", "😂", "👀", "🔋"]) + " " + item["hook"].capitalize()
    tags = KIND_TAGS[item["kind"]] + ["#phone", "#smartphone", "#techtok", "#fyp", "#mobitrgovina"]
    ask = {"quiz": "Did you guess it? 👇", "myth": "Did you believe it? 👇", "pov": "Be honest… 😅",
           "fact": "Did you know that? 👇", "tip": "Save this for later 📌"}[item["kind"]]
    return "\n".join([first, "", ask, "", "📦 Phones with warranty & EU shipping: mobitrgovina.com (link in bio)",
                      "", " ".join(dict.fromkeys(tags))])


class FunVideo(Base):
    """Besedilni prizori: velik naslov → alineje ena za drugo → razkritje → kratek zaključek."""

    def __init__(self, item: dict, theme=None, seed=None):
        super().__init__(theme, random.Random(seed))
        self.it = item
        self.ink_on_accent = (12, 15, 22) if self.tname in ("temna", "rdeca") else (255, 255, 255)

    def cuts(self, T):
        return [T * 0.22, T * 0.68, T - 2.2]

    def label(self, d, a):
        if a <= 0:
            return
        txt = KIND_LABEL[self.it["kind"]]
        f = font("Bold", 46)
        tw = d.textlength(txt, font=f) + 80
        x = int(W / 2 - tw / 2)
        y = 260 - int((1 - ease(a)) * 60)
        d.rounded_rectangle([x, y, x + tw, y + 92], radius=46, fill=self.t["accent"])
        d.text((W // 2, y + 46), txt, font=f, fill=self.ink_on_accent, anchor="mm")

    def big(self, d, text, y, a, size=96, color=None):
        f = font("Bold", size)
        lines = wrap(d, text, f, W - 160, 5)
        y = y - (len(lines) - 1) * size * 0.6 + int((1 - ease(a)) * 70)
        for k, ln in enumerate(lines):
            d.text((W // 2, y + k * size * 1.2), ln, font=f, fill=color or self.t["text"], anchor="mm")

    def frame(self, s: float, T: float) -> Image.Image:
        c1, c2, c3 = self.cuts(T)
        f = self.bg.copy()
        d = ImageDraw.Draw(f)
        self.header(d)
        it = self.it
        if s < c1:
            self.label(d, s / 0.5)
            self.big(d, it["hook"], 900, (s - 0.15) / 0.5)
        elif s < c2:
            u = (s - c1) / (c2 - c1)
            self.label(d, 1)
            self.big(d, it["hook"], 520, 1, size=62, color=self.t["sub"])
            n = len(it["body"])
            for i, txt in enumerate(it["body"]):
                a = ease(u * (n + 0.6) - i)
                if a <= 0:
                    continue
                fb = font("Bold", 56)
                lines = wrap(d, txt, fb, W - 260, 2)
                y = 820 + i * 260
                x = 70 + int((1 - a) * -260)
                card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                cd = ImageDraw.Draw(card)
                col = self.t["chip"] if len(self.t["chip"]) == 4 else self.t["chip"] + (255,)
                cd.rounded_rectangle([x, y, x + W - 140, y + 210], radius=40, fill=col[:3] + (int(col[3] * a),))
                f.alpha_composite(card)
                d = ImageDraw.Draw(f)
                d.ellipse([x + 35, y + 75, x + 95, y + 135], fill=self.t["accent"])
                y0 = y + 105 - (len(lines) - 1) * 34
                for k, ln in enumerate(lines):
                    d.text((x + 130, y0 + k * 68), ln, font=fb, fill=self.t["text"], anchor="lm")
        elif s < c3:
            u = (s - c2) / max(0.1, c3 - c2)
            a = ease(u / 0.25)
            r = int(60 * a)
            top = 640
            d.rounded_rectangle([70 - r // 3, top - r // 3, W - 70 + r // 3, top + 640 + r // 3], radius=60,
                                fill=self.t["accent"])
            d.text((W // 2, top + 120), "ANSWER" if it["kind"] in ("quiz", "myth") else "", font=font("Bold", 50),
                   fill=self.ink_on_accent, anchor="mm")
            self.big(d, it["reveal"], top + 330, a, size=110 if len(it["reveal"]) < 12 else 84,
                     color=self.ink_on_accent)
        else:
            u = (s - c3) / max(0.1, T - c3)
            a = ease(u / 0.3)
            top = int(700 + (1 - a) * 200)
            d.rounded_rectangle([60, top, W - 60, top + 520], radius=54, fill=(255, 255, 255))
            ink = (16, 32, 64)
            d.text((W // 2, top + 120), "Phones with warranty", font=font("Bold", 64), fill=ink, anchor="mm")
            d.text((W // 2, top + 210), "shipped across the EU", font=font("Medium", 52), fill=(110, 118, 130),
                   anchor="mm")
            y = top + 370
            d.rounded_rectangle([140, y - 60, W - 140, y + 60], radius=60, fill=(230, 40, 55))
            d.text((W // 2, y), "mobitrgovina.com", font=font("Bold", 58), fill=(255, 255, 255), anchor="mm")
        self.footer(d, "Follow for more phone stuff")
        return f.convert("RGB")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()

