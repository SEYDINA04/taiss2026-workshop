# -*- coding: utf-8 -*-
"""Génère data/raw_manifest.csv : 200 lignes, 11 défauts plantés aux quantités
exactes du plan v3, entre 55 et 65 % de lignes propres, graine fixe.

Décisions de conception :
- Les 60 phrases calibrées sont des lignes PROPRES du manifeste. Les fichiers
  de round en sont l'extraction (id, transcription), ce qui fait tenir la
  promesse du plan : même fichier du début à la fin.
- Les lignes éwé légitimes reprennent verbatim des lignes du corpus fourni par
  Babacar (archive/ewe_pur.txt). Aucune phrase éwé n'est générée.
- Les doublons copient uniquement des lignes propres, sinon les quantités des
  autres défauts seraient faussées par les copies.
- Six lignes cumulent deux défauts (réalisme demandé par le prompt), les
  comptages restent exacts car chaque défaut est compté indépendamment.

Sortie : taiss2026_workshop/data/raw_manifest.csv
         kit_build/manifest_defects.json (positions des défauts, pour le
         dossier animateur ; jamais distribué)
"""

import json
import random
import re
import unicodedata
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from sentences_fr import SENTENCES, sanity_check

ROOT = Path(__file__).resolve().parent.parent
OUT_CSV = ROOT / "taiss2026_workshop" / "data" / "raw_manifest.csv"
OUT_JSON = Path(__file__).resolve().parent / "manifest_defects.json"
EWE_SOURCE = ROOT / "archive" / "ewe_pur.txt"

SEED = 20260827
WORKSHOP_DATE = date(2026, 8, 27)

REGIONS = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]
SOURCES = ["collecte_terrain", "radio_communautaire", "studio_lome", "contribution_mobile"]

# Lexique de mots outils français, sans collision avec l'éwé écrit
# (« le », « me », « de », « en », « eye » existent ou ressemblent à de l'éwé,
# ils sont volontairement exclus).
FRENCH_STOPWORDS = {
    "les", "des", "une", "est", "dans", "pour", "avec", "sur", "pas", "que",
    "qui", "nous", "vous", "elle", "sont", "cette", "mais", "tout", "fait",
    "plus", "aussi", "être", "avoir", "chez", "leur", "notre", "votre",
}


def french_stopword_hits(text):
    tokens = re.findall(r"[\w'àâäéèêëîïôöùûüç]+", str(text).lower(), re.UNICODE)
    return len({t for t in tokens if t in FRENCH_STOPWORDS})


# ---------------------------------------------------------------- fillers FR
SUBJECTS = [
    "Le chauffeur de taxi", "La vendeuse du marché", "Mon oncle", "La radio locale",
    "Le chef du village", "Ma coiffeuse", "Le mécanicien", "L'institutrice",
    "Le pasteur", "Notre voisin", "La présidente du groupement", "Le pharmacien",
]
ACTIONS = [
    "a annoncé la réunion de samedi prochain",
    "a réparé la pompe du quartier hier soir",
    "a ouvert une nouvelle boutique près du carrefour",
    "prépare la fête de fin d'année avec les jeunes",
    "a raconté son voyage à Sokodé la semaine dernière",
    "organise une collecte pour l'école du village",
    "a présenté le calendrier des vaccinations",
    "attend la livraison de ciment depuis lundi",
    "a expliqué le nouveau tarif du transport",
    "recense les familles pour le programme agricole",
]
TAILS = [
    "devant tout le monde", "sans prévenir personne", "avant la tombée de la nuit",
    "avec l'aide des femmes du quartier", "malgré la chaleur", "juste après la pluie",
    "pendant la coupure d'électricité", "au retour du champ", "",
]


def build_filler_sentences(rng, n):
    combos = [f"{s} {a} {t}".strip().replace("  ", " ") + "."
              for s in SUBJECTS for a in ACTIONS for t in TAILS]
    rng.shuffle(combos)
    assert len(combos) >= n
    return combos[:n]


# ---------------------------------------------------------------- éwé réel
def load_ewe_lines(n):
    lines = [l.strip().strip('"') for l in EWE_SOURCE.read_text(encoding="utf-8").splitlines()]
    picked = []
    for l in lines:
        words = l.split()
        if not (4 <= len(words) <= 14):
            continue
        if french_stopword_hits(l) >= 2:      # éviter tout faux positif du contrôle de langue
            continue
        if "Ã" in l or "â€" in l:             # éviter toute collision avec la détection mojibake
            continue
        picked.append(l)
        if len(picked) == n:
            break
    assert len(picked) == n, f"seulement {len(picked)} lignes éwé utilisables"
    return picked


# ---------------------------------------------------------------- helpers
def mojibake(text):
    return text.encode("utf-8").decode("latin-1")


def make_row(rng, transcription, language, speaker, region, src, dur=None, words=None):
    if words is None:
        words = len(str(transcription).split())
    if dur is None:
        wps = rng.uniform(1.8, 3.4)
        dur = max(1.5, min(12.0, words / wps))
    day = date(2025, 9, 1) + timedelta(days=rng.randint(0, 350))
    return {
        "id": None,
        "audio_path": None,
        "duration_s": round(dur, 1),
        "sample_rate": 16000,
        "channels": 1,
        "language": language,
        "transcription": transcription,
        "speaker_id": speaker,
        "region": region,
        "recorded_at": day.isoformat(),
        "source": src,
    }


def main():
    sanity_check()
    rng = random.Random(SEED)
    rows, defects = [], {k: [] for k in [
        "doublon_exact", "doublon_approx", "duree_aberrante", "sample_rate",
        "channels", "langue_incoherente", "transcription_vide", "wps_impossible",
        "mojibake", "speaker_manquant", "date_future"]}

    # --- 60 lignes calibrées, propres, locuteurs spk_041..spk_052
    curated_speakers = [f"spk_{i:03d}" for i in range(41, 53)]
    for i, s in enumerate(SENTENCES):
        spk = curated_speakers[i % 12]
        r = make_row(rng, s["text"], "fr", spk, rng.choice(REGIONS), rng.choice(SOURCES))
        r["_tag"] = f"curated_r{s['round']}"
        rows.append(r)

    # --- 20 lignes éwé légitimes (corpus Babacar, verbatim)
    for l in load_ewe_lines(20):
        spk = f"spk_{rng.randint(53, 60):03d}"
        r = make_row(rng, l, "ee", spk, rng.choice(["Maritime", "Plateaux"]), rng.choice(SOURCES))
        r["_tag"] = "ewe_clean"
        rows.append(r)

    fillers = build_filler_sentences(rng, 140)
    f_iter = iter(fillers)

    def filler_row(**kw):
        return make_row(rng, next(f_iter), "fr",
                        f"spk_{rng.randint(1, 40):03d}", rng.choice(REGIONS),
                        rng.choice(SOURCES), **kw)

    # --- durées aberrantes : 3 × 0,2 s (une seule ...
    # ... syllabe transcrite, wps=5 sous le seuil) et 3 × 47 s
    for i in range(3):
        r = make_row(rng, "Oui.", "fr", f"spk_{rng.randint(1, 40):03d}",
                     rng.choice(REGIONS), rng.choice(SOURCES), dur=0.2)
        r["_tag"] = "duree_courte"; rows.append(r)
    for i in range(3):
        long_txt = next(f_iter) + " " + next(f_iter)
        r = make_row(rng, long_txt, "fr", f"spk_{rng.randint(1, 40):03d}",
                     rng.choice(REGIONS), rng.choice(SOURCES), dur=47.0)
        r["_tag"] = "duree_longue"; rows.append(r)

    # --- sample_rate 8000 : 7 lignes, dont 2 sans speaker_id et 1 transcription vide
    for i in range(7):
        r = filler_row() if i != 6 else make_row(
            rng, "", "fr", f"spk_{rng.randint(1, 40):03d}", rng.choice(REGIONS), rng.choice(SOURCES), dur=rng.uniform(2, 8))
        r["sample_rate"] = 8000
        if i in (0, 1):
            r["speaker_id"] = ""
        r["_tag"] = "sr8000"; rows.append(r)

    # --- channels 2 : 5 lignes, dont 1 sans speaker_id et 1 mojibake
    moji_src = "La cérémonie de remise des diplômes s'est déroulée à l'école préfectorale."
    for i in range(5):
        if i == 4:
            r = make_row(rng, mojibake(moji_src), "fr", f"spk_{rng.randint(1, 40):03d}",
                         rng.choice(REGIONS), rng.choice(SOURCES))
        else:
            r = filler_row()
        r["channels"] = 2
        if i == 3:
            r["speaker_id"] = ""
        r["_tag"] = "stereo"; rows.append(r)

    # --- langue incohérente : 6 lignes marquées ee, texte français
    # le texte doit contenir au moins deux mots outils distincts, sinon
    # l'heuristique de la séquence 3 ne peut pas le signaler
    made = 0
    while made < 6:
        r = filler_row()
        if french_stopword_hits(r["transcription"]) < 2:
            r["_tag"] = "clean_filler_extra"; rows.append(r)
            continue
        r["language"] = "ee"
        r["_tag"] = "lang_ee_fr"; rows.append(r)
        made += 1

    # --- transcription vide : 8 lignes pures (la 9e est déjà dans sr8000)
    for i in range(8):
        r = filler_row()
        r["transcription"] = ""
        r["_tag"] = "vide"; rows.append(r)

    # --- ratio mots/seconde impossible : 6 lignes, dont l'hommage 40 mots / 0,6 s
    base_words = ("alors donc voilà ensuite après demain matin marché village "
                  "école route maison famille travail argent réunion pluie soleil "
                  "moto taxi téléphone radio boutique champ récolte").split()
    wps_specs = [(0.6, 40), (0.8, 12), (1.2, 15), (2.0, 22), (1.5, 14), (0.9, 9)]
    for dur, n_words in wps_specs:
        words = [base_words[rng.randint(0, len(base_words) - 1)] for _ in range(n_words)]
        txt = (" ".join(words)).capitalize() + "."
        assert len(txt.split()) == n_words
        r = make_row(rng, txt, "fr", f"spk_{rng.randint(1, 40):03d}",
                     rng.choice(REGIONS), rng.choice(SOURCES), dur=dur, words=n_words)
        assert n_words / dur > 6.0
        r["_tag"] = "wps"; rows.append(r)

    # --- mojibake : 4 lignes pures (la 5e est déjà dans stereo)
    moji_texts = [
        "Le défilé du quartier a été reporté à cause de l'état de la chaussée.",
        "La cérémonie d'ouverture a réuni les élèves et les aînés du canton.",
        "Le comité a félicité les bénévoles pour leur générosité exemplaire.",
        "Les activités reprendront dès la fête de l'indépendance, a précisé le maire.",
    ]
    for t in moji_texts:
        r = make_row(rng, mojibake(t), "fr", f"spk_{rng.randint(1, 40):03d}",
                     rng.choice(REGIONS), rng.choice(SOURCES))
        r["_tag"] = "moji"; rows.append(r)

    # --- speaker manquant : 11 lignes pures (4 autres vivent dans sr8000, stereo, date)
    for i in range(11):
        r = filler_row()
        r["speaker_id"] = ""
        r["_tag"] = "no_spk"; rows.append(r)

    # --- date future : 4 lignes, dont 1 sans speaker_id
    for i, d in enumerate(["2026-09-30", "2026-12-15", "2027-01-10", "2027-03-05"]):
        r = filler_row()
        r["recorded_at"] = d
        if i == 2:
            r["speaker_id"] = ""
        r["_tag"] = "futur"; rows.append(r)

    # --- lignes propres restantes, complétées jusqu'à 180 lignes uniques
    while len(rows) < 180:
        r = filler_row()
        r["_tag"] = "clean_filler"; rows.append(r)

    assert len(rows) == 180, len(rows)

    # ids attribués après mélange, pour disperser les défauts dans le fichier
    rng.shuffle(rows)
    for i, r in enumerate(rows, start=1):
        r["id"] = f"rec_{i:04d}"
        r["audio_path"] = f"audio/rec_{i:04d}.wav"

    # --- doublons : uniquement des copies de lignes propres
    clean_pool = [r for r in rows if r["_tag"] == "clean_filler"]
    exact_sources = rng.sample(clean_pool, 9)
    exact_copies = []
    for k in range(12):
        src = exact_sources[k % 9]
        exact_copies.append(dict(src))
        defects["doublon_exact"].append(src["id"])

    approx_sources = rng.sample([r for r in clean_pool if r not in exact_sources], 8)
    approx_copies = []
    transforms = ["upper_word", "trailing_space", "double_space", "region_case"]
    for k, src in enumerate(approx_sources):
        c = dict(src)
        t = transforms[k % 4]
        if t == "upper_word":
            w = c["transcription"].split()
            w[1] = w[1].upper()
            c["transcription"] = " ".join(w)
        elif t == "trailing_space":
            c["transcription"] = c["transcription"] + " "
        elif t == "double_space":
            c["transcription"] = c["transcription"].replace(" ", "  ", 1)
        else:
            c["region"] = c["region"].lower()
        approx_copies.append(c)
        defects["doublon_approx"].append(src["id"])

    for c in exact_copies + approx_copies:
        rows.insert(rng.randint(0, len(rows)), c)
    assert len(rows) == 200

    # --- registre des défauts pour le dossier animateur
    tag_map = {
        "duree_courte": "duree_aberrante", "duree_longue": "duree_aberrante",
        "sr8000": "sample_rate", "stereo": "channels", "lang_ee_fr": "langue_incoherente",
        "vide": "transcription_vide", "wps": "wps_impossible", "moji": "mojibake",
        "no_spk": "speaker_manquant", "futur": "date_future",
    }
    seen = set()
    for r in rows:
        key = (r["id"], r["_tag"])
        if key in seen:
            continue
        seen.add(key)
        t = tag_map.get(r["_tag"])
        if t:
            defects[t].append(r["id"])
        if r["_tag"] == "sr8000" and r["speaker_id"] == "":
            defects["speaker_manquant"].append(r["id"])
        if r["_tag"] == "sr8000" and str(r["transcription"]).strip() == "":
            defects["transcription_vide"].append(r["id"])
        if r["_tag"] == "stereo" and r["speaker_id"] == "":
            defects["speaker_manquant"].append(r["id"])
        if r["_tag"] == "stereo" and "Ã" in str(r["transcription"]):
            defects["mojibake"].append(r["id"])
        if r["_tag"] == "futur" and r["speaker_id"] == "":
            defects["speaker_manquant"].append(r["id"])

    df = pd.DataFrame(rows)
    curated_ids = {
        "round1": [r["id"] for r in rows if r["_tag"] == "curated_r1"],
        "round2": [r["id"] for r in rows if r["_tag"] == "curated_r2"],
    }
    df = df.drop(columns=["_tag"])
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")

    OUT_JSON.write_text(json.dumps(
        {"defects": defects, "curated_ids": curated_ids}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"écrit : {OUT_CSV} ({len(df)} lignes)")
    print(f"écrit : {OUT_JSON}")


if __name__ == "__main__":
    main()
