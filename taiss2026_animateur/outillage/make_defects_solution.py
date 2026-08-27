# -*- coding: utf-8 -*-
"""Écrit defauts_manifest_solution.md depuis le registre des défauts plantés.

Généré plutôt que rédigé à la main : les identifiants cités sont garantis
exacts par construction, et le document se régénère si le manifeste change.
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REG = json.loads((Path(__file__).resolve().parent / "manifest_defects.json")
                 .read_text(encoding="utf-8"))
OUT = ROOT / "taiss2026_animateur" / "defauts_manifest_solution.md"
CSV = ROOT / "taiss2026_workshop" / "data" / "raw_manifest.csv"

SECTIONS = [
    ("doublon_exact", "Doublons exacts", 12,
     "12 lignes strictement identiques à une autre, identifiant compris. "
     "`drop_duplicates` les retire ; les identifiants listés sont ceux des "
     "lignes dupliquées, chaque copie partage l'identifiant de son original."),
    ("doublon_approx", "Doublons approximatifs", 8,
     "8 lignes qui ne diffèrent de leur original que par une majuscule, un "
     "espace en fin de texte, un espace doublé ou la casse de la région. "
     "Invisibles pour `drop_duplicates` brut, capturés après normalisation "
     "minuscules + espaces."),
    ("duree_aberrante", "Durées aberrantes", 6,
     "3 lignes à 0,2 s et 3 lignes à 47 s. Les 0,2 s portent une transcription "
     "d'un seul mot : leur débit reste sous le seuil, c'est bien le contrôle "
     "de durée qui doit les attraper, pas celui de débit."),
    ("sample_rate", "Fréquence incohérente", 7,
     "7 lignes à 8000 Hz au lieu de 16000. Deux cumulent un speaker_id "
     "manquant, une cumule une transcription vide."),
    ("channels", "Canaux incohérents", 5,
     "5 lignes en stéréo là où le corpus est mono. Une cumule un speaker_id "
     "manquant, une cumule un encodage cassé."),
    ("langue_incoherente", "Langue mal renseignée", 6,
     "6 lignes marquées `ee` dont la transcription est manifestement du "
     "français, au moins deux mots outils français distincts chacune. Les 20 "
     "vraies lignes éwé du manifeste ne déclenchent pas l'heuristique."),
    ("transcription_vide", "Transcription vide", 9,
     "9 lignes sans texte, dont une cumule la fréquence à 8000 Hz."),
    ("wps_impossible", "Débit impossible", 6,
     "6 lignes au-dessus de 6 mots par seconde, dont l'hommage au plan : "
     "40 mots annoncés sur 0,6 s. Les durées de ces lignes restent dans la "
     "plage normale, seul le rapport mots/durée les trahit."),
    ("mojibake", "Encodage cassé", 5,
     "5 lignes en mojibake réel, UTF-8 relu en latin-1 (« é » devenu « Ã© »), "
     "dont une cumulée avec la stéréo. Détection : présence de « Ã » ou « â€ »."),
    ("speaker_manquant", "Identifiant locuteur manquant", 15,
     "15 lignes sans speaker_id : 11 pures, 2 cumulées avec la fréquence, "
     "1 avec la stéréo, 1 avec une date future."),
    ("date_future", "Date impossible", 4,
     "4 lignes enregistrées après le jour de l'atelier (2026-09-30, "
     "2026-12-15, 2027-01-10, 2027-03-05). Référence de comparaison fixée au "
     "27 août 2026 dans les contrôles, pour rester reproductible."),
]

HEADER = """# Les onze défauts plantés — solution animateur

> Ne pas divulguer avant la restitution de la séquence 2. Ce document liste
> chaque défaut, sa quantité exacte et les identifiants concernés, pour
> compléter au tableau ce que la salle n'a pas trouvé.
>
> Vue d'ensemble : 200 lignes, 123 propres (61,5 %), 77 défectueuses, six
> lignes cumulent deux défauts. Les 60 phrases calibrées de la séquence 4 et
> les 20 vraies lignes éwé sont toutes propres et survivent au nettoyage.

"""


def main():
    defects = REG["defects"]
    df = pd.read_csv(CSV, encoding="utf-8")
    parts = [HEADER]
    for key, title, expected, note in SECTIONS:
        ids = sorted(set(defects[key]))
        n = len(defects[key]) if key != "doublon_exact" else 12
        parts.append(f"## {title} — {expected} lignes\n")
        parts.append(note + "\n")
        parts.append("Identifiants : " + ", ".join(f"`{i}`" for i in ids) + "\n")
    parts.append(
        "## Ce que la barrière de la séquence 3 attrape, et le reste\n\n"
        "Les sept contrôles ligne à ligne attrapent durées, fréquence, canaux, "
        "langue, vides, débit, métadonnées et dates. Les doublons et le mojibake "
        "se traitent au niveau du tableau entier, le notebook fournit ces deux "
        "opérations déjà écrites dans la cellule d'application de la barrière : "
        "personne n'a à les coder, mais la distinction ligne contre tableau vaut "
        "d'être dite à voix haute.\n")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"écrit : {OUT}")


if __name__ == "__main__":
    main()
