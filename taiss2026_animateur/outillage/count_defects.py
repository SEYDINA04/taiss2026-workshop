# -*- coding: utf-8 -*-
"""Compte les 11 défauts du manifeste en lisant uniquement le CSV.

Vérification indépendante du générateur : aucune information de position
n'est réutilisée, chaque défaut est redétecté depuis les données. La date de
référence pour « date future » est le jour de l'atelier, fixée en dur pour
que le comptage soit reproductible après le 27 août 2026.
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "taiss2026_workshop" / "data" / "raw_manifest.csv"
REFERENCE_DATE = "2026-08-27"

FRENCH_STOPWORDS = {
    "les", "des", "une", "est", "dans", "pour", "avec", "sur", "pas", "que",
    "qui", "nous", "vous", "elle", "sont", "cette", "mais", "tout", "fait",
    "plus", "aussi", "être", "avoir", "chez", "leur", "notre", "votre",
}

EXPECTED = {
    "doublons_exacts": 12,
    "doublons_approx": 8,
    "durees_aberrantes": 6,
    "sample_rate_8000": 7,
    "channels_2": 5,
    "langue_incoherente": 6,
    "transcription_vide": 9,
    "wps_impossible": 6,
    "mojibake": 5,
    "speaker_manquant": 15,
    "date_future": 4,
}


def normalize(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def french_hits(text):
    tokens = re.findall(r"[\w'àâäéèêëîïôöùûüç]+", str(text).lower(), re.UNICODE)
    return len({t for t in tokens if t in FRENCH_STOPWORDS})


def count_defects(df):
    n = len(df)
    counts = {}
    flags = pd.DataFrame(index=df.index)

    dup_exact = df.duplicated(keep="first")
    counts["doublons_exacts"] = int(dup_exact.sum())
    flags["dup_exact"] = dup_exact

    norm = df.astype(str).apply(lambda col: col.map(normalize))
    dup_norm = norm.duplicated(keep="first")
    dup_approx = dup_norm & ~dup_exact
    counts["doublons_approx"] = int(dup_approx.sum())
    flags["dup_approx"] = dup_approx

    dur = pd.to_numeric(df["duration_s"], errors="coerce")
    aberrant = (dur < 0.5) | (dur > 20.0)
    counts["durees_aberrantes"] = int((aberrant & ~dup_norm).sum())
    flags["duree"] = aberrant

    sr = pd.to_numeric(df["sample_rate"], errors="coerce") != 16000
    counts["sample_rate_8000"] = int((sr & ~dup_norm).sum())
    flags["sr"] = sr

    ch = pd.to_numeric(df["channels"], errors="coerce") != 1
    counts["channels_2"] = int((ch & ~dup_norm).sum())
    flags["ch"] = ch

    trans = df["transcription"].fillna("")
    lang_bad = (df["language"] == "ee") & (trans.map(french_hits) >= 2)
    counts["langue_incoherente"] = int((lang_bad & ~dup_norm).sum())
    flags["lang"] = lang_bad

    empty = trans.str.strip() == ""
    counts["transcription_vide"] = int((empty & ~dup_norm).sum())
    flags["vide"] = empty

    words = trans.str.split().map(len)
    wps = words / dur.replace(0, pd.NA)
    wps_bad = (wps > 6.0).fillna(False)
    counts["wps_impossible"] = int((wps_bad & ~dup_norm).sum())
    flags["wps"] = wps_bad

    moji = trans.str.contains("Ã", regex=False) | trans.str.contains("â€", regex=False)
    counts["mojibake"] = int((moji & ~dup_norm).sum())
    flags["moji"] = moji

    spk = df["speaker_id"].fillna("").astype(str).str.strip() == ""
    counts["speaker_manquant"] = int((spk & ~dup_norm).sum())
    flags["spk"] = spk

    fut = df["recorded_at"].astype(str) > REFERENCE_DATE
    counts["date_future"] = int((fut & ~dup_norm).sum())
    flags["futur"] = fut

    any_defect = flags.any(axis=1)
    clean = int((~any_defect).sum())
    return counts, clean, n


def main():
    df = pd.read_csv(CSV, encoding="utf-8")
    counts, clean, n = count_defects(df)
    ok = True
    print(f"{'défaut':24} {'mesuré':>7} {'attendu':>8}")
    for k, exp in EXPECTED.items():
        got = counts[k]
        mark = "ok" if got == exp else "ECART"
        if got != exp:
            ok = False
        print(f"{k:24} {got:>7} {exp:>8}  {mark}")
    pct = 100 * clean / n
    in_range = 55.0 <= pct <= 65.0
    print(f"\nlignes propres : {clean}/{n} = {pct:.1f} %  "
          f"({'dans' if in_range else 'HORS'} [55, 65])")
    if not ok or not in_range:
        sys.exit(1)
    print("comptage conforme")


if __name__ == "__main__":
    main()
