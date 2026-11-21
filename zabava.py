"""Zabavni TikTok videi o mobilni telefoniji (angleško): zanimivosti, miti, kvizi in »POV« šale.

Vsak drugi TikTok je tak namesto oglasa za izdelek, da profil ni samo prodaja.
Vsebina je zbirka preverjenih kratkih zgodb; ista se ne ponovi, dokler niso porabljene vse.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone

import math

from PIL import Image, ImageDraw, ImageFilter

from video import H, W, Base, ease, font, wrap

# kind: fact = zanimivost, myth = mit ali dejstvo, quiz = ugani, pov = šala, tip = nasvet
ITEMS = [
    dict(id="first-call", prop="retro", kind="fact", hook="THE FIRST MOBILE PHONE CALL EVER",
         body=["April 3, 1973", "New York City", "Motorola engineer Martin Cooper called his rival at Bell Labs"],
         reveal="Talk about a flex.",
         voice="The first mobile phone call ever was made on April 3rd, 1973, in New York. "
               "Motorola engineer Martin Cooper used it to call his rival at Bell Labs. Talk about a flex."),
    dict(id="dynatac-price", prop="retro", kind="quiz", hook="HOW MUCH DID THE FIRST MOBILE PHONE COST?",
         body=["Motorola DynaTAC 8000X", "Year: 1983", "Weight: almost 800 g"],
         reveal="$3,995",
         voice="How much did the very first mobile phone cost? The Motorola DynaTAC, 1983, almost 800 grams. "
               "The answer: 3995 dollars. And about 30 minutes of talk time."),
    dict(id="first-sms", prop="chat", kind="fact", hook="THE FIRST TEXT MESSAGE EVER SENT SAID…",
         body=["December 3, 1992", "Sent from a computer to a phone", "Two words long"],
         reveal="\"Merry Christmas\"",
         voice="The first text message ever was sent on December 3rd, 1992. It was typed on a computer, "
               "sent to a phone, and it said: Merry Christmas."),
    dict(id="nokia-1100", prop="retro", kind="quiz", hook="THE BEST-SELLING PHONE OF ALL TIME IS…",
         body=["Not an iPhone", "Not a Samsung", "Over 250 million sold"],
         reveal="Nokia 1100",
         voice="The best-selling phone of all time? Not an iPhone. Not a Samsung. "
               "It's the Nokia 1100, with more than 250 million sold."),
    dict(id="snake", prop="retro", kind="fact", hook="SNAKE WAS ON NOKIA PHONES SINCE 1997",
         body=["First on the Nokia 6110", "No app store", "No Wi-Fi"],
         reveal="Still undefeated.",
         voice="Snake first showed up on the Nokia 6110 back in 1997. No app store, no Wi-Fi, "
               "and still one of the most addictive games ever."),
    dict(id="apollo", prop="phone", kind="fact", hook="YOUR PHONE VS. THE MOON LANDING",
         body=["Apollo 11 guidance computer: 1969", "Your phone: in your pocket", "Millions of times more powerful"],
         reveal="And we use it for memes.",
         voice="The phone in your pocket is millions of times more powerful than the computer that guided "
               "Apollo 11 to the Moon. And we mostly use it for memes."),
    dict(id="nomophobia", prop="phone", kind="fact", hook="THERE'S A WORD FOR THIS FEELING",
         body=["Phone not in your pocket", "Heart rate goes up", "Panic search begins"],
         reveal="Nomophobia",
         voice="That panic when you can't find your phone? There's a word for it. "
               "Nomophobia, the fear of being without your phone. Tag someone who has it."),
    dict(id="guess-3310", prop="retro", kind="quiz", hook="GUESS THE YEAR: NOKIA 3310",
         body=["Indestructible", "Battery for days", "Snake II included"],
         reveal="2000",
         voice="Guess the year. The Nokia 3310. Indestructible, battery for days, Snake 2 included. "
               "It came out in the year 2000."),
    dict(id="guess-iphone", prop="phone", kind="quiz", hook="GUESS THE YEAR: THE FIRST iPHONE",
         body=["3.5-inch screen", "No App Store at launch", "2 megapixel camera"],
         reveal="2007",
         voice="Guess the year. The first iPhone. A 3.5 inch screen, no App Store at launch, "
               "and a 2 megapixel camera. It launched in 2007."),
    dict(id="guess-android", prop="phone", kind="quiz", hook="GUESS THE YEAR: THE FIRST ANDROID PHONE",
         body=["HTC Dream / T-Mobile G1", "Slide-out keyboard", "Trackball"],
         reveal="2008",
         voice="Guess the year. The first Android phone, the HTC Dream, also called the T-Mobile G1. "
               "A slide-out keyboard and a trackball. It came out in 2008."),
    dict(id="guess-razr", prop="retro", kind="quiz", hook="GUESS THE YEAR: MOTOROLA RAZR V3",
         body=["Thin flip phone", "Metal body", "Everybody wanted one"],
         reveal="2004",
         voice="Guess the year. The Motorola Razr V3. Super thin, metal, and everybody wanted one. "
               "It came out in 2004."),
    dict(id="myth-overnight", prop="battery", kind="myth", hook="MYTH OR FACT: CHARGING OVERNIGHT KILLS YOUR BATTERY",
         body=["Modern phones stop charging when full", "Many can pause at 80% overnight", "Heat is the real enemy"],
         reveal="MYTH",
         voice="Myth or fact? Charging overnight kills your battery. Mostly a myth. Modern phones stop "
               "charging when they're full, and many can pause at 80 percent overnight. Heat is the real enemy."),
    dict(id="myth-close-apps", prop="phone", kind="myth", hook="MYTH OR FACT: CLOSING APPS SAVES BATTERY",
         body=["Your phone already freezes apps in the background", "Reopening them from zero costs more"],
         reveal="MYTH",
         voice="Myth or fact? Closing all your apps saves battery. Myth. Your phone already pauses apps "
               "in the background, and opening them again from zero actually uses more power."),
    dict(id="myth-megapixels", prop="phone", kind="myth", hook="MYTH OR FACT: MORE MEGAPIXELS = BETTER PHOTOS",
         body=["Sensor size matters", "Lens and processing matter", "Megapixels are just one number"],
         reveal="MYTH",
         voice="Myth or fact? More megapixels means better photos. Myth. Sensor size, the lens and the "
               "processing matter a lot more. Megapixels are just one number on the box."),
    dict(id="myth-drain", prop="battery", kind="myth", hook="MYTH OR FACT: DRAIN YOUR BATTERY TO 0% SOMETIMES",
         body=["That was for old battery types", "Lithium-ion likes the middle", "Try to stay between 20% and 80%"],
         reveal="MYTH",
         voice="Myth or fact? You should drain your battery to zero sometimes. Myth. That was for old batteries. "
               "Lithium ion is happiest between about 20 and 80 percent."),
    dict(id="fact-airplane", prop="battery", kind="myth", hook="MYTH OR FACT: AIRPLANE MODE CHARGES FASTER",
         body=["No searching for signal", "Fewer background tasks", "A little faster, not magic"],
         reveal="FACT",
         voice="Myth or fact? Airplane mode makes your phone charge faster. Fact, a little bit. "
               "Your phone stops searching for signal, so more power goes into the battery."),
    dict(id="pov-1percent", prop="battery", kind="pov", hook="POV: YOUR PHONE IS AT 1%",
         body=["Brightness: lowest", "Low power mode: ON", "Still trying to send one last voice message"],
         reveal="Phone: *dies*",
         voice="P O V. Your phone is at one percent. Brightness all the way down, low power mode on, "
               "and you still try to send one last voice message. And it dies."),
    dict(id="pov-holding", prop="phone", kind="pov", hook="POV: LOOKING FOR YOUR PHONE…",
         body=["Checks pockets", "Checks the couch", "Asks everyone in the room"],
         reveal="…while holding it",
         voice="P O V. You're looking for your phone. Pockets. Couch. You ask everyone in the room. "
               "And it was in your hand the whole time."),
    dict(id="pov-drop", prop="phone", kind="pov", hook="POV: YOU JUST DROPPED YOUR PHONE",
         body=["It lands face down", "Nobody moves", "The slowest pickup of your life"],
         reveal="Get a case. Seriously.",
         voice="P O V. You just dropped your phone. It lands face down. Nobody moves. "
               "The slowest pickup of your life. Get a case. Seriously."),
    dict(id="pov-one-notification", prop="chat", kind="pov", hook="\"I'LL JUST CHECK ONE NOTIFICATION\"",
         body=["9:00 – one notification", "9:05 – just one more video", "11:40 – how did this happen"],
         reveal="Every. Single. Time.",
         voice="I'll just check one notification. Nine o'clock. Just one more video. "
               "Suddenly it's eleven forty. Every single time."),
    dict(id="pov-20", prop="battery", kind="pov", hook="ME WHEN MY PHONE IS AT 21%",
         body=["Totally fine", "Living my life", "Not worried at all"],
         reveal="20%: PANIC MODE",
         voice="Me when my phone is at 21 percent. Totally fine, living my life. "
               "Twenty percent? Panic mode."),
    dict(id="tip-restart", prop="phone", kind="tip", hook="DO THIS ONCE A WEEK",
         body=["Restart your phone", "Clears stuck apps and memory", "Fixes a lot of weird bugs"],
         reveal="30 seconds. Big difference.",
         voice="Do this once a week. Just restart your phone. It clears stuck apps and memory, "
               "and fixes a lot of weird little bugs. Thirty seconds, big difference."),
    dict(id="tip-heat", prop="battery", kind="tip", hook="THE #1 THING THAT KILLS PHONE BATTERIES",
         body=["Not charging overnight", "Not old age alone", "It's this:"],
         reveal="HEAT",
         voice="The number one thing that kills phone batteries? Not charging overnight. "
               "It's heat. Don't leave your phone in a hot car or charge it under your pillow."),
    dict(id="tip-used", prop="phone", kind="tip", hook="WHAT TO CHECK BEFORE BUYING A USED PHONE",
         body=["Battery health", "Network unlocked", "Warranty from the seller"],
         reveal="No warranty? Walk away.",
         voice="What to check before you buy a used phone. Battery health. Is it unlocked? "
               "And does the seller give you a warranty? No warranty? Walk away."),
    dict(id="tot-os", prop="versus", kind="tot", hook="TEAM iPHONE OR TEAM ANDROID?",
         body=["A: iPhone", "B: Android"], reveal="Drop A or B below!",
         voice="Okay, the big one. Team iPhone, or team Android? No fence sitting. Comment A or B, and defend your choice."),
    dict(id="tot-case", prop="versus", kind="tot", hook="CASE OR NO CASE?",
         body=["A: Always a case", "B: Living dangerously"], reveal="Drop A or B below!",
         voice="Case, or no case? Are you protected, or are you living dangerously? Comment A or B."),
    dict(id="tot-dark", prop="versus", kind="tot", hook="DARK MODE OR LIGHT MODE?",
         body=["A: Dark mode", "B: Light mode"], reveal="Drop A or B below!",
         voice="Dark mode or light mode? One of these is correct. Comment A or B."),
    dict(id="tot-silent", prop="versus", kind="tot", hook="SILENT MODE OR RINGTONE ON?",
         body=["A: Always on silent", "B: Ringtone loud and proud"], reveal="Drop A or B below!",
         voice="Silent mode forever, or ringtone loud and proud? Comment A or B."),
    dict(id="list-2000s", prop="retro", kind="list", hook="ONLY 2000s KIDS REMEMBER…",
         body=["Polyphonic ringtones", "Swappable phone covers", "Counting every SMS character"],
         reveal="Which one hit you?",
         voice="Only 2000s kids remember this. Polyphonic ringtones. Swappable phone covers. "
               "And counting every single character in your text message. Which one hit you?"),
    dict(id="list-flip", prop="retro", kind="list", hook="THINGS THAT FELT ILLEGAL ON A FLIP PHONE",
         body=["Snapping it shut to end a call", "Pressing the internet button by accident", "Sending a picture message"],
         reveal="Pure power.",
         voice="Things that felt illegal on a flip phone. Snapping it shut to end a call. "
               "Hitting the internet button by accident and panicking. Sending a picture message. Pure power."),
    dict(id="battery-personality", prop="battery", kind="list", hook="WHAT YOUR BATTERY % SAYS ABOUT YOU",
         body=["100%: you have your life together", "50%: living on the edge", "5%: chaos is your lifestyle"],
         reveal="Which one are you?",
         voice="What your battery percentage says about you. A hundred percent, you have your life together. "
               "Fifty, you like living on the edge. Five percent? Chaos is your lifestyle. Which one are you?"),
    dict(id="sms-160", prop="chat", kind="fact", hook="WHY WERE TEXTS LIMITED TO 160 CHARACTERS?",
         body=["1985: engineer Friedhelm Hillebrand", "Typed out sentences and questions", "Almost all fit in 160 characters"],
         reveal="So 160 it was.",
         voice="Why were text messages limited to 160 characters? In 1985, engineer Friedhelm Hillebrand "
               "typed out typical sentences and questions, and almost all of them fit in 160 characters. So 160 it was."),
    dict(id="emoji", prop="chat", kind="fact", hook="THE FIRST EMOJI WERE MADE FOR PHONES",
         body=["1999, Japan", "Designer Shigetaka Kurita", "176 tiny 12x12 pixel icons"],
         reveal="Now they're in MoMA.",
         voice="The first emoji set was made for phones. 1999, Japan. Designer Shigetaka Kurita drew 176 tiny "
               "12 by 12 pixel icons. Today they're in the Museum of Modern Art in New York."),
    dict(id="bluetooth", prop="phone", kind="fact", hook="BLUETOOTH IS NAMED AFTER A VIKING KING",
         body=["King Harald \"Bluetooth\"", "United Denmark and Norway", "The logo = his initials in runes"],
         reveal="Viking tech.",
         voice="Bluetooth is named after a Viking king. Harald Bluetooth united Denmark and Norway, "
               "and the Bluetooth logo is his initials, written in runes. Viking tech."),
    dict(id="android-desserts", prop="phone", kind="fact", hook="ANDROID VERSIONS USED TO BE DESSERTS",
         body=["Cupcake, Donut, Eclair", "KitKat, Lollipop, Oreo", "Pie was the last one"],
         reveal="Then: just numbers.",
         voice="Android versions used to be named after desserts. Cupcake, Donut, Eclair, KitKat, Lollipop, "
               "Oreo. Pie was the last one. After that, just boring numbers."),
]

KIND_LABEL = {"fact": "DID YOU KNOW?", "myth": "MYTH OR FACT?", "quiz": "QUIZ TIME", "pov": "RELATABLE?",
              "tip": "PHONE TIP", "tot": "THIS OR THAT?", "list": "BE HONEST"}
KIND_TAGS = {"fact": ["#didyouknow", "#techfacts", "#phonehistory"],
             "myth": ["#mythorfact", "#techtips", "#batterylife"],
             "quiz": ["#guesstheyear", "#throwback", "#retrotech"],
             "pov": ["#pov", "#relatable", "#phoneproblems"],
             "tip": ["#techtips", "#phonetips", "#lifehack"],
             "tot": ["#thisorthat", "#iphonevsandroid", "#poll"],
             "list": ["#nostalgia", "#2000s", "#relatable"]}
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
    h = item["hook"].lower().replace("iphone", "iPhone").replace("sms", "SMS").replace("moma", "MoMA").replace("pov", "POV")
    first = rnd.choice(["📱", "🤯", "😂", "👀", "🔋"]) + " " + h[:1].upper() + h[1:]
    tags = KIND_TAGS[item["kind"]] + ["#phone", "#smartphone", "#techtok", "#fyp", "#mobitrgovina"]
    ask = {"quiz": "Did you guess it? 👇", "myth": "Did you believe it? 👇", "pov": "Be honest… 😅",
           "fact": "Did you know that? 👇", "tip": "Save this for later 📌",
           "tot": "A or B? Comment below 👇", "list": "Which one are you? 👇"}[item["kind"]]
    return "\n".join([first, "", ask, "", "📦 Phones with warranty & EU shipping: mobitrgovina.com (link in bio)",
                      "", " ".join(dict.fromkeys(tags))])


# ---------------------------------------------------------------- slovenska različica (FB/IG Reels)
# id: (naslov, alineje, razkritje, govor)
SL = {
    "first-call": ("PRVI KLIC Z MOBILNIKA V ZGODOVINI",
                   ["3. april 1973", "New York", "Martin Cooper iz Motorole je poklical tekmeca iz Bell Labs"],
                   "To je bil šele flex.",
                   "Prvi klic z mobilnega telefona je bil 3. aprila 1973 v New Yorku. Inženir Motorole Martin Cooper "
                   "je z njim poklical svojega tekmeca iz Bell Labs. To je bil šele flex."),
    "dynatac-price": ("KOLIKO JE STAL PRVI MOBILNI TELEFON?",
                      ["Motorola DynaTAC 8000X", "Leto 1983", "Teža: skoraj 800 g"],
                      "3.995 $",
                      "Koliko je stal prvi mobilni telefon? Motorola DynaTAC, leto 1983, skoraj 800 gramov. "
                      "Odgovor: 3995 dolarjev. In okoli 30 minut pogovora."),
    "first-sms": ("PRVI SMS V ZGODOVINI SE JE GLASIL…",
                  ["3. december 1992", "Poslan z računalnika na telefon", "Samo dve besedi"],
                  "»Merry Christmas«",
                  "Prvi SMS je bil poslan 3. decembra 1992. Natipkan je bil na računalniku, poslan na telefon, "
                  "in glasil se je: Merry Christmas."),
    "nokia-1100": ("NAJBOLJ PRODAJAN TELEFON VSEH ČASOV JE…",
                   ["Ni iPhone", "Ni Samsung", "Več kot 250 milijonov prodanih"],
                   "Nokia 1100",
                   "Najbolj prodajan telefon vseh časov? Ni iPhone. Ni Samsung. "
                   "To je Nokia 1100, z več kot 250 milijoni prodanih kosov."),
    "snake": ("KAČA JE NA NOKII ŽE OD LETA 1997",
              ["Najprej na Nokii 6110", "Brez trgovine z aplikacijami", "Brez Wi-Fi-ja"],
              "Še vedno neporažena.",
              "Igrica kača se je prvič pojavila na Nokii 6110 leta 1997. Brez aplikacij, brez Wi-Fi-ja, "
              "pa še vedno ena najbolj zasvojljivih iger."),
    "apollo": ("TVOJ TELEFON PROTI PRISTANKU NA LUNI",
               ["Računalnik Apolla 11: 1969", "Tvoj telefon: v žepu", "Milijonkrat zmogljivejši"],
               "Mi pa z njim gledamo meme.",
               "Telefon v tvojem žepu je milijonkrat zmogljivejši od računalnika, ki je Apollo 11 pripeljal na Luno. "
               "Mi pa z njim večinoma gledamo meme."),
    "nomophobia": ("ZA TA OBČUTEK OBSTAJA BESEDA",
                   ["Telefona ni v žepu", "Srce začne biti hitreje", "Začne se panično iskanje"],
                   "Nomofobija",
                   "Tista panika, ko ne najdeš telefona? Za to obstaja beseda. Nomofobija, strah pred tem, "
                   "da si brez telefona. Označi nekoga, ki jo ima."),
    "guess-3310": ("UGANI LETO: NOKIA 3310",
                   ["Neuničljiva", "Baterija za cel teden", "S kačo dva"],
                   "2000",
                   "Ugani leto. Nokia 3310. Neuničljiva, baterija za cel teden, kača dva. Prišla je leta 2000."),
    "guess-iphone": ("UGANI LETO: PRVI iPHONE",
                     ["Zaslon 3,5 palca", "Ob izidu brez App Stora", "Kamera 2 megapiksla"],
                     "2007",
                     "Ugani leto. Prvi iPhone. Zaslon tri cela pet palca, ob izidu brez App Stora in kamera z dvema "
                     "megapiksloma. Izšel je leta 2007."),
    "guess-android": ("UGANI LETO: PRVI ANDROID TELEFON",
                      ["HTC Dream / T-Mobile G1", "Izvlečna tipkovnica", "Sledilna kroglica"],
                      "2008",
                      "Ugani leto. Prvi telefon z Androidom, HTC Dream. Izvlečna tipkovnica in sledilna kroglica. "
                      "Izšel je leta 2008."),
    "guess-razr": ("UGANI LETO: MOTOROLA RAZR V3",
                   ["Tanek preklopni telefon", "Kovinsko ohišje", "Vsi so ga hoteli"],
                   "2004",
                   "Ugani leto. Motorola Razr V3. Super tanek, kovinski in vsi so ga hoteli. Izšel je leta 2004."),
    "myth-overnight": ("MIT ALI DEJSTVO: POLNJENJE ČEZ NOČ UNIČI BATERIJO",
                       ["Sodobni telefoni nehajo polniti, ko so polni", "Mnogi čez noč počakajo pri 80 %",
                        "Pravi sovražnik je vročina"],
                       "MIT",
                       "Mit ali dejstvo? Polnjenje čez noč uniči baterijo. Večinoma mit. Sodobni telefoni nehajo polniti, "
                       "ko so polni, mnogi pa čez noč počakajo pri osemdesetih odstotkih. Pravi sovražnik je vročina."),
    "myth-close-apps": ("MIT ALI DEJSTVO: ZAPIRANJE APLIKACIJ VARČUJE BATERIJO",
                        ["Telefon aplikacije v ozadju že sam ustavi", "Ponoven zagon od začetka porabi več"],
                        "MIT",
                        "Mit ali dejstvo? Zapiranje aplikacij varčuje baterijo. Mit. Telefon aplikacije v ozadju že sam "
                        "ustavi, ponovno odpiranje od začetka pa porabi več energije."),
    "myth-megapixels": ("MIT ALI DEJSTVO: VEČ MEGAPIKSLOV = BOLJŠE SLIKE",
                        ["Velikost senzorja šteje", "Objektiv in obdelava štejeta", "Megapiksli so le ena številka"],
                        "MIT",
                        "Mit ali dejstvo? Več megapikslov pomeni boljše slike. Mit. Velikost senzorja, objektiv in obdelava "
                        "štejejo veliko več. Megapiksli so le ena številka na škatli."),
    "myth-drain": ("MIT ALI DEJSTVO: BATERIJO OBČASNO IZPRAZNI DO 0 %",
                   ["To je veljalo za stare baterije", "Litij-ionske imajo rade sredino", "Drži se med 20 in 80 %"],
                   "MIT",
                   "Mit ali dejstvo? Baterijo moraš občasno izprazniti do nič. Mit. To je veljalo za stare baterije. "
                   "Litij ionska je najbolj srečna med dvajset in osemdeset odstotki."),
    "fact-airplane": ("MIT ALI DEJSTVO: V NAČINU ZA LETALO SE HITREJE POLNI",
                      ["Ne išče signala", "Manj opravil v ozadju", "Malo hitreje, ne čudežno"],
                      "DEJSTVO",
                      "Mit ali dejstvo? V načinu za letalo se telefon polni hitreje. Dejstvo, malo. "
                      "Telefon neha iskati signal, zato gre več energije v baterijo."),
    "pov-1percent": ("POV: TELEFON JE NA 1 %",
                     ["Svetlost: najnižja", "Varčevanje z energijo: VKLOP", "Še vedno pošiljaš zadnje glasovno sporočilo"],
                     "Telefon: *ugasne*",
                     "Pi o vi. Telefon je na enem odstotku. Svetlost čisto dol, varčevanje vklopljeno, "
                     "ti pa še vedno pošiljaš zadnje glasovno sporočilo. In ugasne."),
    "pov-holding": ("POV: IŠČEŠ SVOJ TELEFON…",
                    ["Preveriš žepe", "Preveriš kavč", "Vprašaš vse v sobi"],
                    "…medtem ko ga držiš v roki",
                    "Pi o vi. Iščeš svoj telefon. Žepi. Kavč. Vprašaš vse v sobi. In ves čas ga držiš v roki."),
    "pov-drop": ("POV: RAVNOKAR TI JE PADEL TELEFON",
                 ["Pristane z zaslonom navzdol", "Nihče se ne premakne", "Najpočasnejše pobiranje v življenju"],
                 "Kupi ovitek. Resno.",
                 "Pi o vi. Ravnokar ti je padel telefon. Pristane z zaslonom navzdol. Nihče se ne premakne. "
                 "Najpočasnejše pobiranje v tvojem življenju. Kupi ovitek. Resno."),
    "pov-one-notification": ("»SAMO ENO OBVESTILO POGLEDAM«",
                             ["21:00 – eno obvestilo", "21:05 – še en video", "23:40 – kako se je to zgodilo"],
                             "Vsakič. Znova.",
                             "Samo eno obvestilo pogledam. Devet zvečer. Še en video. Naenkrat je enajst in štirideset. "
                             "Vsakič znova."),
    "pov-20": ("JAZ, KO JE TELEFON NA 21 %",
               ["Čisto v redu", "Živim svoje življenje", "Sploh nisem zaskrbljen"],
               "20 %: PANIKA",
               "Jaz, ko je telefon na enaindvajsetih odstotkih. Čisto v redu, živim svoje življenje. "
               "Dvajset odstotkov? Panika."),
    "tip-restart": ("TO NAREDI ENKRAT NA TEDEN",
                    ["Ponovno zaženi telefon", "Počisti zataknjene aplikacije", "Odpravi veliko čudnih napak"],
                    "30 sekund. Velika razlika.",
                    "To naredi enkrat na teden. Ponovno zaženi telefon. Počisti zataknjene aplikacije in pomnilnik "
                    "ter odpravi kup čudnih napak. Trideset sekund, velika razlika."),
    "tip-heat": ("ŠTEVILKA 1, KI UNIČUJE BATERIJE",
                 ["Ni polnjenje čez noč", "Ni samo starost", "To je:"],
                 "VROČINA",
                 "Kaj najbolj uničuje baterije? Ne polnjenje čez noč. Vročina. Ne puščaj telefona v vročem avtu "
                 "in ga ne polni pod blazino."),
    "tip-used": ("KAJ PREVERITI PRED NAKUPOM RABLJENEGA TELEFONA",
                 ["Zdravje baterije", "Odklenjen za vsa omrežja", "Garancija prodajalca"],
                 "Brez garancije? Pojdi naprej.",
                 "Kaj preveriti pred nakupom rabljenega telefona. Zdravje baterije. Je odklenjen za vsa omrežja? "
                 "In ali prodajalec da garancijo? Brez garancije? Pojdi naprej."),
    "tot-os": ("EKIPA iPHONE ALI EKIPA ANDROID?",
               ["A: iPhone", "B: Android"], "Napiši A ali B!",
               "Dobro, največje vprašanje. Ekipa iPhone ali ekipa Android? Brez sedenja na dveh stolih. "
               "Napiši A ali B in zagovarjaj svojo izbiro."),
    "tot-case": ("OVITEK ALI BREZ OVITKA?",
                 ["A: Vedno ovitek", "B: Živim nevarno"], "Napiši A ali B!",
                 "Ovitek ali brez ovitka? Si zaščiten ali živiš nevarno? Napiši A ali B."),
    "tot-dark": ("TEMNI ALI SVETLI NAČIN?",
                 ["A: Temni način", "B: Svetli način"], "Napiši A ali B!",
                 "Temni ali svetli način? Samo eden je pravilen. Napiši A ali B."),
    "tot-silent": ("TIHI NAČIN ALI ZVONJENJE?",
                   ["A: Vedno tiho", "B: Glasno in ponosno"], "Napiši A ali B!",
                   "Za vedno na tiho ali zvonjenje glasno in ponosno? Napiši A ali B."),
    "list-2000s": ("SAMO OTROCI 2000-IH SE SPOMNIJO…",
                   ["Polifonih melodij zvonjenja", "Zamenljivih maskic", "Štetja vsakega znaka v SMS-u"],
                   "Kaj te je zadelo?",
                   "Samo otroci dvatisočih se spomnijo. Polifone melodije zvonjenja. Zamenljive maskice. "
                   "In štetje vsakega znaka v SMS-u. Kaj te je zadelo?"),
    "list-flip": ("STVARI, KI SO SE NA PREKLOPNEM TELEFONU ZDELE NEZAKONITE",
                  ["Zapreš ga, da končaš klic", "Pomotoma pritisneš gumb za internet", "Pošlješ MMS"],
                  "Čista moč.",
                  "Stvari, ki so se na preklopnem telefonu zdele nezakonite. Zapreš ga, da končaš klic. "
                  "Pomotoma pritisneš gumb za internet in paničariš. Pošlješ MMS. Čista moč."),
    "battery-personality": ("KAJ TVOJ % BATERIJE POVE O TEBI",
                            ["100 %: imaš življenje urejeno", "50 %: živiš na robu", "5 %: kaos je tvoj stil"],
                            "Kateri si ti?",
                            "Kaj tvoj odstotek baterije pove o tebi. Sto odstotkov, imaš življenje urejeno. "
                            "Petdeset, rad živiš na robu. Pet odstotkov? Kaos je tvoj stil. Kateri si ti?"),
    "sms-160": ("ZAKAJ JE BIL SMS OMEJEN NA 160 ZNAKOV?",
                ["1985: inženir Friedhelm Hillebrand", "Natipkal je tipične stavke in vprašanja",
                 "Skoraj vsi so šli v 160 znakov"],
                "Pa je bilo 160.",
                "Zakaj je bil SMS omejen na sto šestdeset znakov? Leta 1985 je inženir Friedhelm Hillebrand natipkal "
                "tipične stavke in vprašanja in skoraj vsi so šli v sto šestdeset znakov. Pa je bilo sto šestdeset."),
    "emoji": ("PRVI EMOJIJI SO BILI NAREJENI ZA TELEFONE",
              ["1999, Japonska", "Oblikovalec Shigetaka Kurita", "176 drobnih ikon 12 x 12 pikslov"],
              "Danes so v MoMA.",
              "Prvi emojiji so bili narejeni za telefone. Leta 1999 na Japonskem jih je oblikovalec Shigetaka Kurita "
              "narisal 176, vsakega dvanajst krat dvanajst pikslov. Danes so v Muzeju moderne umetnosti v New Yorku."),
    "bluetooth": ("BLUETOOTH JE DOBIL IME PO VIKINŠKEM KRALJU",
                  ["Kralj Harald »Bluetooth«", "Združil je Dansko in Norveško", "Logotip = njegovi inicialki v runah"],
                  "Vikinška tehnologija.",
                  "Bluetooth je dobil ime po vikinškem kralju. Harald Bluetooth je združil Dansko in Norveško, "
                  "logotip Bluetootha pa sta njegovi inicialki, zapisani v runah. Vikinška tehnologija."),
    "android-desserts": ("RAZLIČICE ANDROIDA SO BILE SLADICE",
                         ["Cupcake, Donut, Eclair", "KitKat, Lollipop, Oreo", "Pie je bila zadnja"],
                         "Potem: samo številke.",
                         "Različice Androida so bile poimenovane po sladicah. Cupcake, Donut, Eclair, KitKat, Lollipop, "
                         "Oreo. Pie je bila zadnja. Potem pa samo dolgočasne številke."),
}

TXT = {
    "en": dict(label=None, answer="ANSWER", guess="Guess before the answer!", ab="Comment A or B",
               side="Which side are you on?", end1="Phones with warranty", end2="shipped across the EU",
               foot="Follow for more phone stuff"),
    "sl": dict(label={"fact": "ALI SI VEDEL?", "myth": "MIT ALI DEJSTVO?", "quiz": "KVIZ", "pov": "SE NAJDEŠ?",
                      "tip": "NASVET", "tot": "TO ALI ONO?", "list": "BODI ISKREN"},
               answer="ODGOVOR", guess="Ugibaj, preden razkrijemo!", ab="Napiši A ali B",
               side="Na kateri strani si?", end1="Telefoni z garancijo", end2="dostava po vsej Sloveniji",
               foot="Sledi za več o telefonih"),
}
CTAS_SL = ["Sledi nam za več!", "Napiši odgovor v komentar!", "Označi prijatelja, ki mora to videti!"]
KIND_TAGS_SL = {"fact": ["#zanimivosti", "#aliveste"], "myth": ["#mitalidejstvo", "#nasveti"],
                "quiz": ["#kviz", "#nostalgija"], "pov": ["#pov", "#hecno"], "tip": ["#nasveti", "#triki"],
                "tot": ["#toalionot", "#iphonevsandroid"], "list": ["#nostalgija", "#2000s"]}


def localized(item: dict, lang: str) -> dict:
    if lang != "sl":
        return item
    hook, body, reveal, voice = SL[item["id"]]
    return {**item, "hook": hook, "body": body, "reveal": reveal, "voice": voice}


def key_sl(item: dict) -> str:
    return f"zabavasl-{item['id']}"  # namenoma brez »zabava-«, da ne zmede izmenjave na TikToku


def pick_sl(st: dict, rnd: random.Random) -> dict:
    fresh = [i for i in ITEMS if key_sl(i) not in st]
    if fresh:
        return rnd.choice(fresh)
    return min(ITEMS, key=lambda i: st[key_sl(i)])


def is_fun_reel_turn(st: dict) -> bool:
    """Reels na FB/IG: izmenično izdelek in zabava."""
    def last(pred):
        ts = [v for k, v in st.items() if pred(k)]
        return max(ts) if ts else ""
    return last(lambda k: k.startswith("zabavasl-")) <= last(lambda k: k.endswith("-reel"))


def script_sl(item: dict, rnd: random.Random) -> str:
    return f"{localized(item, 'sl')['voice']} {rnd.choice(CTAS_SL)}"


def caption_sl(item: dict, rnd: random.Random) -> str:
    h = localized(item, "sl")["hook"].lower().replace("iphone", "iPhone").replace("sms", "SMS").replace("pov", "POV")
    first = rnd.choice(["📱", "🤯", "😂", "👀", "🔋"]) + " " + h[:1].upper() + h[1:]
    ask = {"quiz": "Si uganil? 👇", "myth": "Si verjel? 👇", "pov": "Bodi iskren… 😅", "fact": "Si to vedel? 👇",
           "tip": "Shrani za pozneje 📌", "tot": "A ali B? Napiši v komentar 👇", "list": "Kateri si ti? 👇"}[item["kind"]]
    tags = KIND_TAGS_SL[item["kind"]] + ["#telefon", "#mobitel", "#slovenija", "#mobitrgovina"]
    return "\n".join([first, "", ask, "", "📦 Telefoni z garancijo in dostavo po vsej Sloveniji: mobitrgovina.com",
                      "", " ".join(dict.fromkeys(tags))])


def _pop(t: float) -> float:
    """Ease z rahlim prenihajem (back-out) za »poskočne« animacije."""
    t = max(0.0, min(1.0, t))
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


class FunVideo(Base):
    """Naslov se izpiše beseda za besedo ob rekvizitu (baterija, stari telefon, sporočila, A/B) →
    alineje → razkritje s konfeti in tresljajem → zaključna kartica. Ozadje se ves čas rahlo giblje."""

    def __init__(self, item: dict, theme=None, seed=None, lang="en"):
        super().__init__(theme, random.Random(seed))
        self.lang = lang
        self.tx = TXT[lang]
        self.it = localized(item, lang)
        self.prop = item.get("prop")
        self.ink_on_accent = (12, 15, 22) if self.tname in ("temna", "rdeca") else (255, 255, 255)
        r = self.rnd
        self.bubbles = [(r.uniform(0, W), r.uniform(0, H), r.uniform(40, 160), r.uniform(-25, 25),
                         r.uniform(-60, -15), r.uniform(0, 6.28)) for _ in range(14)]
        self.confetti = [(r.uniform(-1, 1), r.uniform(-1.4, -0.3), r.choice([self.t["accent"], (255, 255, 255),
                         (255, 196, 0), (80, 200, 255), (120, 230, 140)]), r.uniform(10, 22)) for _ in range(70)]

    def cuts(self, T):
        return [T * 0.24, T * 0.68, T - 2.2]

    # ---------------------------------------------------------------- ozadje in rekviziti
    def background(self, s):
        f = self.bg.copy()
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        col = self.t["glow"] or self.t["accent"]
        for x, y, r, vx, vy, ph in self.bubbles:
            cx = (x + vx * s + 30 * math.sin(s * 0.8 + ph)) % W
            cy = (y + vy * s) % H
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (22,))
        f.alpha_composite(layer)
        return f

    def battery(self, d, cx, cy, s, scale=1.0):
        w, h = int(300 * scale), int(150 * scale)
        x0, y0 = cx - w // 2, cy - h // 2
        ink = self.t["text"]
        d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(26 * scale), outline=ink, width=int(12 * scale))
        d.rounded_rectangle([x0 + w + 6, cy - h // 5, x0 + w + int(28 * scale), cy + h // 5], radius=8, fill=ink)
        level = max(0.02, 1 - (s % 4.0) / 3.2)  # se prazni, potem spet poln
        col = (60, 200, 90) if level > 0.5 else (255, 190, 0) if level > 0.2 else (230, 40, 55)
        pad = int(22 * scale)
        if level <= 0.2 and int(s * 4) % 2:
            return  # utripa, ko je skoraj prazna
        d.rounded_rectangle([x0 + pad, y0 + pad, x0 + pad + int((w - 2 * pad) * level), y0 + h - pad],
                            radius=int(12 * scale), fill=col)

    def retro(self, d, cx, cy, s, scale=1.0):
        rot = math.sin(s * 2.2) * 4
        w, h = int(230 * scale), int(420 * scale)
        im = Image.new("RGBA", (w + 40, h + 120), (0, 0, 0, 0))
        g = ImageDraw.Draw(im)
        body = (55, 62, 78)
        g.rounded_rectangle([20, 100, 20 + w, 100 + h], radius=60, fill=body)
        g.rectangle([w - 30, 10, w - 10, 110], fill=body)  # antena
        g.rounded_rectangle([50, 150, w - 10, 300], radius=16, fill=(150, 190, 120))
        g.text((w // 2 + 20, 225), "MOBI", font=font("Bold", 40), fill=(40, 60, 30), anchor="mm")
        for r_ in range(4):
            for c in range(3):
                kx, ky = 62 + c * 58, 330 + r_ * 44
                g.rounded_rectangle([kx, ky, kx + 44, ky + 30], radius=12, fill=(200, 205, 215))
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        return im, (int(cx - im.width / 2), int(cy - im.height / 2 + 8 * math.sin(s * 3)))

    def phone(self, d, cx, cy, s, scale=1.0):
        w, h = int(250 * scale), int(500 * scale)
        y = cy + 10 * math.sin(s * 2.5)
        d.rounded_rectangle([cx - w / 2, y - h / 2, cx + w / 2, y + h / 2], radius=44, fill=(20, 22, 30))
        d.rounded_rectangle([cx - w / 2 + 14, y - h / 2 + 14, cx + w / 2 - 14, y + h / 2 - 14], radius=34,
                            fill=self.t["accent"])
        d.rounded_rectangle([cx - 40, y - h / 2 + 26, cx + 40, y - h / 2 + 48], radius=11, fill=(20, 22, 30))
        for i in range(3):  # »obvestila«, ki zdrsnejo noter
            a = ease((s - 0.3 - i * 0.35) / 0.4)
            if a <= 0:
                continue
            ny = y - h / 2 + 90 + i * 110
            nx = cx - w / 2 + 30 + (1 - a) * 160
            d.rounded_rectangle([nx, ny, nx + w - 60, ny + 86], radius=20, fill=(255, 255, 255))
            d.ellipse([nx + 14, ny + 22, nx + 56, ny + 64], fill=self.t["accent"])
            d.rounded_rectangle([nx + 70, ny + 26, nx + w - 90, ny + 40], radius=7, fill=(200, 205, 215))
            d.rounded_rectangle([nx + 70, ny + 50, nx + w - 130, ny + 62], radius=6, fill=(225, 228, 235))

    def chat(self, d, cx, cy, s, scale=1.0):
        rows = [(-1, 360), (1, 300), (-1, 250)]
        for i, (side, bw) in enumerate(rows):
            a = _pop((s - 0.2 - i * 0.45) / 0.35)
            if a <= 0:
                continue
            bw = int(bw * a)
            y = cy - 150 + i * 120
            x0 = cx - 330 if side < 0 else cx + 330 - bw
            fill = (255, 255, 255) if side < 0 else self.t["accent"]
            d.rounded_rectangle([x0, y, x0 + bw, y + 90], radius=45, fill=fill)
            if i == 2 and a >= 1:  # »tipka …«
                for k in range(3):
                    r = 10 + 4 * math.sin(s * 8 - k)
                    dx = x0 + 70 + k * 50
                    d.ellipse([dx - r, y + 45 - r, dx + r, y + 45 + r], fill=(150, 155, 165))

    def versus(self, d, s):
        a = ease(s / 0.5)
        left, right = self.it["body"][0], self.it["body"][1]
        for k, (txt, col) in enumerate(((left, self.t["accent"]), (right, (40, 110, 230)))):
            x0 = 60 + k * 500 + int((1 - a) * (-500 if k == 0 else 500))
            d.rounded_rectangle([x0, 430, x0 + 460, 900], radius=48, fill=col)
            letter, label = txt.split(":", 1)
            d.text((x0 + 230, 580), letter, font=font("Bold", 190), fill=(255, 255, 255), anchor="mm")
            for j, ln in enumerate(wrap(d, label.strip(), font("Bold", 50), 400, 2)):
                d.text((x0 + 230, 760 + j * 62), ln, font=font("Bold", 50), fill=(255, 255, 255), anchor="mm")
        r = int(85 * _pop((s - 0.3) / 0.4))
        if r > 0:
            d.ellipse([W // 2 - r, 665 - r, W // 2 + r, 665 + r], fill=(255, 255, 255))
            d.text((W // 2, 665), "VS", font=font("Bold", int(70 * r / 85) or 1), fill=(16, 32, 64), anchor="mm")

    def draw_prop(self, f, s, cy=620, scale=1.0):
        d = ImageDraw.Draw(f)
        if self.prop == "battery":
            self.battery(d, W // 2, cy, s, scale)
        elif self.prop == "retro":
            im, pos = self.retro(d, W // 2, cy, s, scale * 0.9)
            f.alpha_composite(im, pos)
        elif self.prop == "phone":
            self.phone(d, W // 2, cy, s, scale * 0.85)
        elif self.prop == "chat":
            self.chat(d, W // 2, cy, s, scale)
        return ImageDraw.Draw(f)

    # ---------------------------------------------------------------- besedilo
    def label(self, d, a):
        if a <= 0:
            return
        txt = (self.tx["label"] or KIND_LABEL)[self.it["kind"]]
        f = font("Bold", 46)
        tw = d.textlength(txt, font=f) + 80
        x = int(W / 2 - tw / 2)
        y = 250 - int((1 - _pop(a)) * 60)
        d.rounded_rectangle([x, y, x + tw, y + 92], radius=46, fill=self.t["accent"])
        d.text((W // 2, y + 46), txt, font=f, fill=self.ink_on_accent, anchor="mm")

    def kinetic(self, d, text, cy, s, size=92, per_word=0.12, color=None, max_w=W - 160):
        """Beseda za besedo, vsaka poskoči na svoje mesto; zadnja beseda v barvi poudarka."""
        f = font("Bold", size)
        lines = wrap(d, text, f, max_w, 5)
        lh = int(size * 1.18)
        y0 = cy - (len(lines) - 1) * lh / 2
        sp = d.textlength(" ", font=f)
        idx, total = 0, sum(len(ln.split()) for ln in lines)
        for li, ln in enumerate(lines):
            words = ln.split()
            widths = [d.textlength(w_, font=f) for w_ in words]
            x = W / 2 - (sum(widths) + sp * (len(words) - 1)) / 2
            for w_, ww in zip(words, widths):
                a = _pop((s - idx * per_word) / 0.3)
                if a > 0:
                    col = self.t["accent"] if idx == total - 1 and not color else (color or self.t["text"])
                    d.text((x, y0 + li * lh + (1 - a) * 60), w_, font=f, fill=col, anchor="lm")
                x += ww + sp
                idx += 1

    def frame(self, s: float, T: float) -> Image.Image:
        c1, c2, c3 = self.cuts(T)
        f = self.background(s)
        d = ImageDraw.Draw(f)
        self.header(d)
        it = self.it
        if s < c1:
            self.label(d, s / 0.4)
            if self.prop == "versus":
                self.kinetic(d, it["hook"], 1200, s - 0.1)
                self.versus(d, s - 0.6)
            elif self.prop:
                d = self.draw_prop(f, s, 640)
                self.kinetic(d, it["hook"], 1220, s - 0.1, size=86)
            else:
                self.kinetic(d, it["hook"], 900, s - 0.1)
        elif s < c2:
            u = (s - c1) / (c2 - c1)
            self.label(d, 1)
            if self.prop == "versus":
                self.versus(d, 10)
                pulse = 1 + 0.04 * math.sin(s * 6)
                self.kinetic(d, self.tx["ab"], 1150, 10, size=int(88 * pulse))
                self.kinetic(d, self.tx["side"], 1300, 10, size=56, color=self.t["sub"])
            else:
                for ln_i, ln in enumerate(wrap(d, it["hook"], font("Bold", 56), W - 160, 3)):
                    d.text((W // 2, 420 + ln_i * 68), ln, font=font("Bold", 56), fill=self.t["sub"], anchor="mm")
                n = len(it["body"])
                for i, txt in enumerate(it["body"]):
                    a = _pop(u * (n + 0.6) - i)
                    if a <= 0:
                        continue
                    fb = font("Bold", 56)
                    lines = wrap(d, txt, fb, W - 300, 2)
                    y = 680 + i * 250
                    x = 70 + int((1 - a) * -300)
                    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    cd = ImageDraw.Draw(card)
                    col = self.t["chip"] if len(self.t["chip"]) == 4 else self.t["chip"] + (255,)
                    cd.rounded_rectangle([x, y, x + W - 140, y + 210], radius=40,
                                         fill=col[:3] + (int(col[3] * min(1, a)),))
                    f.alpha_composite(card)
                    d = ImageDraw.Draw(f)
                    d.ellipse([x + 30, y + 65, x + 110, y + 145], fill=self.t["accent"])
                    d.text((x + 70, y + 105), str(i + 1), font=font("Bold", 50), fill=self.ink_on_accent,
                           anchor="mm")
                    y0 = y + 105 - (len(lines) - 1) * 34
                    for k, ln in enumerate(lines):
                        d.text((x + 140, y0 + k * 68), ln, font=fb, fill=self.t["text"], anchor="lm")
                if it["kind"] in ("quiz", "myth"):  # ura teče – ugibaj!
                    bx0, bx1, by = 120, W - 120, 1520
                    d.rounded_rectangle([bx0, by, bx1, by + 30], radius=15, fill=self.t["sub"])
                    d.rounded_rectangle([bx0, by, bx0 + max(30, int((bx1 - bx0) * (1 - u))), by + 30], radius=15,
                                        fill=self.t["accent"])
                    d.text((W // 2, by + 90), self.tx["guess"], font=font("Medium", 44),
                           fill=self.t["sub"], anchor="mm")
        elif s < c3:
            u = s - c2
            a = _pop(u / 0.35)
            shake = int(14 * math.sin(u * 60) * max(0, 1 - u / 0.4))
            top = 600
            pad = int(40 * (1 - min(1, a)))
            d.rounded_rectangle([70 + pad + shake, top + pad, W - 70 - pad + shake, top + 660 - pad], radius=60,
                                fill=self.t["accent"])
            if it["kind"] in ("quiz", "myth"):
                d.text((W // 2 + shake, top + 120), self.tx["answer"], font=font("Bold", 50), fill=self.ink_on_accent,
                       anchor="mm")
            if a > 0.3:
                self.kinetic(d, it["reveal"], top + 340, u - 0.15, size=112 if len(it["reveal"]) < 12 else 84,
                             per_word=0.08, color=self.ink_on_accent, max_w=W - 260)
            if self.prop in ("battery", "chat") and u > 0.4:
                d = self.draw_prop(f, s, 1480, 0.6)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            cd = ImageDraw.Draw(layer)
            for vx, vy, col, r in self.confetti:  # konfeti
                t = u * 1.6
                cx = W / 2 + vx * 900 * t
                cy = top + 330 + vy * 1100 * t + 1300 * t * t
                if 0 < cy < H and t < 1.4:
                    cd.rectangle([cx - r / 2, cy - r / 2, cx + r / 2, cy + r * 0.8], fill=col + (230,))
            f.alpha_composite(layer)
            d = ImageDraw.Draw(f)
        else:
            u = (s - c3) / max(0.1, T - c3)
            a = _pop(u / 0.3)
            top = int(700 + (1 - a) * 200)
            d.rounded_rectangle([60, top, W - 60, top + 520], radius=54, fill=(255, 255, 255))
            ink = (16, 32, 64)
            d.text((W // 2, top + 120), self.tx["end1"], font=font("Bold", 64), fill=ink, anchor="mm")
            d.text((W // 2, top + 210), self.tx["end2"], font=font("Medium", 52), fill=(110, 118, 130),
                   anchor="mm")
            y = top + 370
            p = 1 + 0.03 * math.sin(s * 7)
            hw = int((W - 280) / 2 * p)
            d.rounded_rectangle([W // 2 - hw, y - 60, W // 2 + hw, y + 60], radius=60, fill=(230, 40, 55))
            d.text((W // 2, y), "mobitrgovina.com", font=font("Bold", 58), fill=(255, 255, 255), anchor="mm")
        self.footer(d, self.tx["foot"])
        return f.convert("RGB")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
