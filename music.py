"""Sestavi kratko, mirno glasbeno podlago (brez avtorskih pravic) – vsakič malo drugačno.

Akordi + mehke ploskve + rahel ritem; rezultat je WAV, ki ga video.py zmeša pod glas.
"""
from __future__ import annotations

import random
import wave
from pathlib import Path

import numpy as np

SR = 44100
PROGRESSIONS = [
    [0, 5, 3, 4],      # I–vi–IV–V
    [0, 4, 5, 3],      # I–V–vi–IV
    [5, 3, 0, 4],      # vi–IV–I–V
    [0, 3, 4, 3],      # I–IV–V–IV
]
MAJOR = [0, 2, 4, 5, 7, 9, 11]


def _chord(root_midi: int, degree: int) -> list[int]:
    idx = [degree, degree + 2, degree + 4]
    return [root_midi + MAJOR[i % 7] + 12 * (i // 7) for i in idx]


def _freq(m: int) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


def _env(n: int, a: float, r: float) -> np.ndarray:
    e = np.ones(n)
    na, nr = min(int(a * SR), n // 2), min(int(r * SR), n // 2)  # kratek zadnji kos ne sme podreti glasbe
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def make(out: Path, seconds: float, seed: int | None = None) -> Path:
    rnd = random.Random(seed)
    bpm = rnd.choice([84, 90, 96, 100, 104])
    beat = 60 / bpm
    bar = beat * 4
    key = rnd.choice([57, 58, 60, 62, 63, 65])  # A3 … F4
    prog = rnd.choice(PROGRESSIONS)
    bright = rnd.uniform(0.25, 0.6)
    n = int(seconds * SR)
    t_all = np.arange(n) / SR
    mix = np.zeros(n)

    # akordne ploskve
    t = 0.0
    i = 0
    while t < seconds:
        notes = _chord(key, prog[i % len(prog)])
        s0, s1 = int(t * SR), min(n, int((t + bar) * SR))
        tt = t_all[s0:s1] - t
        seg = np.zeros(s1 - s0)
        for m in notes + [notes[0] - 12]:
            f = _freq(m)
            seg += np.sin(2 * np.pi * f * tt) + bright * 0.3 * np.sin(2 * np.pi * 2 * f * tt + 0.3)
            seg += 0.5 * np.sin(2 * np.pi * f * 1.003 * tt)   # rahlo raztegnjeno = mehkejše
        seg *= _env(len(seg), 0.25, 0.4) * 0.07
        mix[s0:s1] += seg
        # arpeggio
        for k in range(8):
            ts = t + k * beat / 2
            if ts >= seconds:
                break
            m = notes[[0, 1, 2, 1][k % 4]] + 12
            a0, a1 = int(ts * SR), min(n, int((ts + beat / 2) * SR))
            ta = t_all[a0:a1] - ts
            mix[a0:a1] += 0.05 * np.sin(2 * np.pi * _freq(m) * ta) * np.exp(-ta * 6)
        t += bar
        i += 1

    # ritem: mehak boben in hi-hat
    k = 0
    while k * beat < seconds:
        ts = k * beat
        a0 = int(ts * SR)
        a1 = min(n, a0 + int(0.25 * SR))
        ta = t_all[a0:a1] - ts
        if k % 2 == 0:
            mix[a0:a1] += 0.22 * np.sin(2 * np.pi * (50 + 60 * np.exp(-ta * 30)) * ta) * np.exp(-ta * 12)
        h0, h1 = int((ts + beat / 2) * SR), min(n, int((ts + beat / 2 + 0.05) * SR))
        if h0 < n:
            noise = np.random.default_rng(k).standard_normal(h1 - h0)
            mix[h0:h1] += 0.025 * noise * np.exp(-np.arange(h1 - h0) / SR * 60)
        k += 1

    mix *= _env(n, 0.6, 1.2)
    mix = np.tanh(mix * 1.5) / 1.5
    mix /= max(1e-6, np.abs(mix).max()) / 0.8
    stereo = np.stack([mix, np.roll(mix, 220)], axis=1)
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return out
