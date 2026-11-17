"""Slovenski glas (Microsoft Edge nevronski glasovi prek paketa edge-tts)."""
from __future__ import annotations

import asyncio
import random
import subprocess
from pathlib import Path

VOICES = ["sl-SI-RokNeural", "sl-SI-PetraNeural"]
EN_VOICES = ["en-US-AndrewNeural", "en-US-AvaNeural", "en-US-BrianNeural", "en-US-EmmaNeural", "en-GB-RyanNeural"]


def speak(text: str, out: Path, voice: str | None = None, en: bool = False) -> tuple[Path, float] | None:
    """Vrne (mp3, trajanje v s) ali None, če glas ni na voljo – video gre potem samo z glasbo."""
    try:
        import edge_tts

        v = voice or random.choice(EN_VOICES if en else VOICES)
        rate = random.choice(["+8%", "+12%"] if en else ["+0%", "+5%", "+8%"])
        asyncio.run(edge_tts.Communicate(text, v, rate=rate).save(str(out)))
        dur = float(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)]).strip())
        return out, dur
    except Exception as e:  # brez glasu raje objavimo kot nič
        print(f"Glas ni uspel: {e}")
        return None
