# -*- coding: utf-8 -*-
"""Pré-annotation zéro-shot des transcriptions, à lancer depuis le poste de
l'animateur uniquement. Jamais sur les machines des participants.

Deux passes prévues :
    python generate_predictions.py --language fr
    python generate_predictions.py --language ee     # quand le corpus éwé est là

Chaque passe lit les fichiers de round de la langue, interroge le modèle en
zéro-shot avec le prompt PROMPT_ZERO_SHOT ci-dessous, et met à jour
model_predictions.csv sans toucher aux lignes de l'autre langue. Le fichier
livré dans le kit contient déjà la passe française, exécutée le 26 août 2026
avec claude-fable-5 ; relancer la passe fr écrase ces valeurs, ce qui est le
comportement voulu pour la démonstration live.

La clé d'API est lue dans la variable d'environnement ANTHROPIC_API_KEY.
Elle n'apparaît nulle part dans les fichiers, et ce script refuse de démarrer
sans elle. Dépendances : pandas et la bibliothèque standard, rien d'autre.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

KIT = Path(__file__).resolve().parent.parent.parent / "taiss2026_workshop"
DATA = KIT / "data"
PREDICTIONS = DATA / "model_predictions.csv"

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-fable-5"
VALID = {"positif", "negatif", "neutre"}

# Le prompt reproduit volontairement le niveau d'information du guide v1 :
# trois classes, pas de règle de cas limite. C'est la condition de la
# comparaison de la séquence 5 : le modèle et les annotateurs du round 1
# travaillent avec la même (absence de) consigne.
PROMPT_ZERO_SHOT = """Classe le sentiment de la phrase suivante en exactement \
un mot parmi : positif, negatif, neutre.

Phrase : {sentence}

Réponds uniquement par le mot choisi, en minuscules, sans accent."""


def ask_model(api_key, sentence, retries=3):
    payload = {
        "model": MODEL,
        "max_tokens": 8,
        "messages": [{"role": "user",
                      "content": PROMPT_ZERO_SHOT.format(sentence=sentence)}],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"x-api-key": api_key,
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            label = body["content"][0]["text"].strip().lower()
            if label in VALID:
                return label
            print(f"  réponse hors format ({label!r}), nouvel essai")
        except Exception as e:
            print(f"  tentative {attempt + 1} : {e}")
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"pas de label valide pour : {sentence[:60]}...")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", choices=["fr", "ee"], required=True)
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY absente de l'environnement. "
                 "Exporter la clé avant de lancer, ne jamais l'écrire ici.")

    frames = []
    for rnd in (1, 2):
        f = DATA / f"transcriptions_{args.language}_round{rnd}.csv"
        frames.append(pd.read_csv(f, encoding="utf-8"))
    sentences = pd.concat(frames, ignore_index=True)

    pending = sentences["transcription"].str.contains(r"\[À REMPLIR", na=False)
    if pending.any():
        sys.exit(f"{pending.sum()} lignes encore marquées [À REMPLIR PAR "
                 f"BABACAR] dans les fichiers {args.language}. Compléter le "
                 f"corpus avant de lancer cette passe.")

    rows = []
    for _, r in sentences.iterrows():
        label = ask_model(api_key, r["transcription"])
        rows.append({"id": r["id"], "language": args.language,
                     "predicted_label": label})
        print(f"{r['id']}: {label}")

    new = pd.DataFrame(rows)
    if PREDICTIONS.exists():
        old = pd.read_csv(PREDICTIONS, encoding="utf-8")
        old = old[old["language"] != args.language]
        new = pd.concat([old, new], ignore_index=True)
    new.to_csv(PREDICTIONS, index=False, encoding="utf-8")
    print(f"\nécrit : {PREDICTIONS} ({len(new)} lignes)")


if __name__ == "__main__":
    main()
