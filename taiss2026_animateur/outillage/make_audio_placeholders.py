# -*- coding: utf-8 -*-
"""Génère trois fichiers WAV de remplacement pour audio_demo/.

Signal synthétique (bourdon modulé, pas de parole), 16 kHz mono 16 bits, aux
durées attendues par la séquence 2. Babacar les remplace par de vrais
enregistrements ; en attendant, le notebook et les vérifications disposent de
fichiers lisibles aux bonnes propriétés.
"""

import wave
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent.parent / "taiss2026_workshop" / "audio_demo"
SR = 16000
SEED = 7


def write_wav(path, seconds, f0):
    rng = np.random.default_rng(SEED)
    t = np.arange(int(seconds * SR)) / SR
    # bourdon à deux harmoniques, enveloppe lente : reconnaissable comme
    # placeholder à l'oreille, inoffensif pour un test de haut-parleurs
    signal = (0.5 * np.sin(2 * np.pi * f0 * t)
              + 0.25 * np.sin(2 * np.pi * 2 * f0 * t)
              + 0.02 * rng.standard_normal(t.size))
    envelope = 0.6 + 0.4 * np.sin(2 * np.pi * 1.5 * t)
    data = (signal * envelope * 0.4 * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print(f"écrit : {path} ({seconds} s, {SR} Hz, mono)")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    write_wav(OUT / "01_conforme.wav", 5.0, 220.0)
    write_wav(OUT / "02_tronque.wav", 0.4, 220.0)
    write_wav(OUT / "03_transcription_fausse.wav", 4.0, 165.0)


if __name__ == "__main__":
    main()
