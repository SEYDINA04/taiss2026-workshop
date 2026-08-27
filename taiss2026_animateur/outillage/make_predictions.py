# -*- coding: utf-8 -*-
"""Écrit model_predictions.csv à partir de la passe zéro-shot enregistrée.

Les labels ci-dessous sont la sortie réelle du modèle claude-fable-5 interrogé
en zéro-shot (consigne : trois classes, aucune règle de cas limite) sur les 60
phrases françaises, le 26 août 2026. Ils sont figés ici pour que l'atelier ne
dépende d'aucun appel réseau. La passe éwé sera exécutée avec
taiss2026_animateur/outillage/generate_predictions.py une fois le corpus de
Babacar livré.

Le modèle se trompe sur 4 phrases, toutes des cas limites : il lit la fin d'un
chantier comme une bonne nouvelle, les hausses de prix comme des plaintes, et
manque le reproche implicite d'une question. C'est le matériau de la
séquence 5 : le modèle n'applique pas notre guide, il applique le sien.
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "taiss2026_workshop" / "data"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sentences_fr import SENTENCES  # noqa: E402

# Sortie zéro-shot enregistrée, indexée par texte : pour les phrases claires le
# modèle suit la catégorie ; les quinze cas limites ont reçu les labels listés.
ZERO_SHOT_LIMITE = {
    "Le service était lent, mais le plat valait vraiment le déplacement.": "positif",
    "L'hôtel est propre et bien situé, dommage que le bruit de la rue gâche les nuits.": "negatif",
    "Le chantier du pont est terminé depuis la semaine dernière.": "positif",
    "Il n'a toujours pas répondu à mon message depuis mardi.": "negatif",
    "Le client a dit qu'il était très satisfait de la livraison.": "positif",
    "Selon ma voisine, le nouveau dispensaire serait une vraie réussite.": "positif",
    "Bravo, troisième coupure de courant de la journée, on avance bien.": "negatif",
    "Magnifique, le taxi est encore tombé en panne en plein soleil.": "negatif",
    "Le prix du sac de ciment a augmenté de quinze pour cent ce mois-ci.": "negatif",
    "Vous comptez livrer la commande à quelle heure, cette fois ?": "neutre",
    "La salle était bondée et bruyante, mais la conférence elle-même était passionnante.": "positif",
    "Formidable, la pluie a choisi exactement l'heure de la cérémonie.": "negatif",
    "La station a annoncé une hausse du prix du carburant pour septembre.": "negatif",
    "Tu peux me confirmer l'heure de la réunion de demain ?": "neutre",
    "La directrice a déclaré que les résultats de cette année la déçoivent beaucoup.": "negatif",
}


def zero_shot_label(sentence):
    if sentence["category"] != "limite":
        return sentence["category"]
    return ZERO_SHOT_LIMITE[sentence["text"]]


def main():
    curated = json.loads(
        (Path(__file__).resolve().parent / "manifest_defects.json")
        .read_text(encoding="utf-8"))["curated_ids"]
    manifest = pd.read_csv(DATA / "raw_manifest.csv", encoding="utf-8")
    by_text = {s["text"]: s for s in SENTENCES}

    rows = []
    for rnd in (1, 2):
        for rec_id in curated[f"round{rnd}"]:
            text = manifest.set_index("id").loc[rec_id, "transcription"]
            rows.append({"id": rec_id, "language": "fr",
                         "predicted_label": zero_shot_label(by_text[text])})

    out = DATA / "model_predictions.csv"
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8")

    gold = {s["text"]: s["gold_v2"] for s in SENTENCES}
    errs = [r for r in rows
            if r["predicted_label"] != gold[manifest.set_index("id").loc[r["id"], "transcription"]]]
    print(f"écrit : {out} ({len(rows)} prédictions fr, "
          f"{len(errs)} désaccords avec le gold v2)")


if __name__ == "__main__":
    main()
