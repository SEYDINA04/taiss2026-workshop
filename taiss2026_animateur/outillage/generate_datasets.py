# -*- coding: utf-8 -*-
"""Produit les fichiers de transcription des deux rounds.

Français : extraction (id, transcription) des lignes calibrées du manifeste,
ordre mélangé à graine fixe pour ne pas télégraphier les catégories.
Éwé : structure identique, lignes marquées [À REMPLIR PAR BABACAR],
aucune phrase éwé n'est générée ici.
"""

import json
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "taiss2026_workshop" / "data"
DEFECTS = Path(__file__).resolve().parent / "manifest_defects.json"

SEED = 4402


def main():
    manifest = pd.read_csv(DATA / "raw_manifest.csv", encoding="utf-8")
    curated = json.loads(DEFECTS.read_text(encoding="utf-8"))["curated_ids"]
    rng = random.Random(SEED)

    for rnd in (1, 2):
        ids = list(curated[f"round{rnd}"])
        rng.shuffle(ids)
        sub = manifest.set_index("id").loc[ids, ["transcription"]].reset_index()
        out = DATA / f"transcriptions_fr_round{rnd}.csv"
        sub.to_csv(out, index=False, encoding="utf-8")
        print(f"écrit : {out} ({len(sub)} lignes)")

    for rnd, n in ((1, 40), (2, 20)):
        rows = [{"id": f"ee_r{rnd}_{i:02d}",
                 "transcription": "[À REMPLIR PAR BABACAR]"} for i in range(1, n + 1)]
        out = DATA / f"transcriptions_ee_round{rnd}.csv"
        pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8")
        print(f"écrit : {out} ({n} lignes)")


if __name__ == "__main__":
    main()
