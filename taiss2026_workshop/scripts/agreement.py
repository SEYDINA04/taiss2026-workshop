# -*- coding: utf-8 -*-
"""Mesure d'accord entre deux annotateurs, séquence 4 de l'atelier.

Tout est fourni : ce fichier n'est pas un exercice. Il donne quatre mesures,
de la plus naïve à la plus honnête :

- accord brut : pourcentage de labels identiques. Trompeur, car deux
  annotateurs qui répondent « neutre » partout obtiennent un excellent accord
  brut sans avoir jugé quoi que ce soit.
- Kappa de Cohen : accord corrigé de ce que le hasard produirait compte tenu
  des habitudes de chaque annotateur. C'est la mesure à retenir.
- matrice de confusion : où les deux annotateurs divergent, classe par classe.
- liste des désaccords : les phrases elles-mêmes, car c'est en les relisant
  qu'on découvre les trous du guide, pas dans les chiffres.

Dépendances : pandas, scikit-learn. Disponibles dans Colab sans installation.
"""

import unicodedata

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

VALID_LABELS = ["positif", "negatif", "neutre"]


def normalize_labels(labels):
    """Nettoie une liste de labels saisis à la main.

    Minuscules, espaces retirés, accents supprimés (« négatif » → « negatif »).
    Retourne (labels_propres, anomalies) où anomalies liste les positions dont
    la valeur, même nettoyée, n'appartient pas à VALID_LABELS. Ces positions
    sont conservées telles quelles dans la sortie : c'est à l'appelant de
    décider, la fonction ne jette silencieusement aucune donnée.
    """
    cleaned, anomalies = [], []
    for i, lab in enumerate(labels):
        s = str(lab).strip().lower()
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        if s not in VALID_LABELS:
            anomalies.append((i, lab))
        cleaned.append(s)
    return cleaned, anomalies


def _check_pair(labels_a, labels_b):
    if len(labels_a) != len(labels_b):
        raise ValueError(
            f"listes de tailles différentes : {len(labels_a)} contre "
            f"{len(labels_b)}. Vérifiez qu'aucune ligne n'a été sautée.")
    if len(labels_a) == 0:
        raise ValueError("listes vides, rien à mesurer")


def raw_agreement(labels_a, labels_b):
    """Pourcentage de labels identiques entre deux annotateurs, entre 0 et 1."""
    _check_pair(labels_a, labels_b)
    same = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    return same / len(labels_a)


def kappa(labels_a, labels_b):
    """Kappa de Cohen entre deux annotateurs.

    1.0 : accord parfait. 0.0 : rien de plus que le hasard. Négatif : pire
    que le hasard, ce qui arrive sur de petits échantillons. Si les deux
    annotateurs ont mis exactement les mêmes labels partout, scikit-learn
    renvoie NaN quand une seule classe est présente ; on renvoie 1.0 dans ce
    cas précis, l'accord étant parfait par construction.
    """
    _check_pair(labels_a, labels_b)
    if labels_a == labels_b and len(set(labels_a)) == 1:
        return 1.0
    return float(cohen_kappa_score(labels_a, labels_b, labels=VALID_LABELS))


def confusion(labels_a, labels_b):
    """Matrice de confusion entre annotateurs, lignes = A, colonnes = B."""
    _check_pair(labels_a, labels_b)
    m = confusion_matrix(labels_a, labels_b, labels=VALID_LABELS)
    return pd.DataFrame(m,
                        index=[f"A:{l}" for l in VALID_LABELS],
                        columns=[f"B:{l}" for l in VALID_LABELS])


def disagreements(sentences_df, labels_a, labels_b):
    """Table des désaccords, avec le texte des phrases concernées.

    Entrée : un DataFrame portant les colonnes id et transcription, dans le
    même ordre que les listes de labels, et les deux listes de labels.
    Sortie : DataFrame [id, transcription, annotateur_A, annotateur_B] réduit
    aux lignes où les labels diffèrent, prêt à projeter tel quel.

    C'est cette table qui alimente la discussion : elle doit se lire sans
    manipulation supplémentaire.
    """
    _check_pair(labels_a, labels_b)
    if len(sentences_df) != len(labels_a):
        raise ValueError(
            f"le tableau de phrases a {len(sentences_df)} lignes, les labels "
            f"en ont {len(labels_a)}. L'ordre des lignes a probablement bougé.")
    table = sentences_df[["id", "transcription"]].copy().reset_index(drop=True)
    table["annotateur_A"] = list(labels_a)
    table["annotateur_B"] = list(labels_b)
    mask = table["annotateur_A"] != table["annotateur_B"]
    return table[mask].reset_index(drop=True)


def compare_guides(kappa_v1, kappa_v2):
    """Affiche les deux Kappa côte à côte et rend le verdict lisible.

    Retourne le DataFrame affiché, pour que la cellule du notebook montre le
    tableau même quand l'affichage standard est capturé.
    """
    table = pd.DataFrame({
        "guide": ["v1", "v2"],
        "kappa": [round(kappa_v1, 3), round(kappa_v2, 3)],
    })
    delta = kappa_v2 - kappa_v1
    print(table.to_string(index=False))
    if delta > 0.05:
        print(f"\nDelta = +{delta:.3f}. Mêmes annotateurs, mêmes types de "
              f"phrases : seul le guide a changé.")
    elif delta < -0.05:
        print(f"\nDelta = {delta:.3f}. Le Kappa descend : sur 20 items, "
              f"l'échantillon est petit et instable. C'est exactement la "
              f"raison pour laquelle un jeu d'évaluation réel compte des "
              f"milliers d'items.")
    else:
        print(f"\nDelta = {delta:+.3f}, quasi nul. Sur un échantillon de 20 "
              f"items, un écart de cette taille ne conclut rien.")
    return table


def summary(labels_a, labels_b):
    """Les quatre mesures d'un coup, pour la cellule de la séquence 4c."""
    return {
        "accord_brut": round(raw_agreement(labels_a, labels_b), 3),
        "kappa": round(kappa(labels_a, labels_b), 3),
        "n_items": len(labels_a),
        "n_desaccords": sum(1 for a, b in zip(labels_a, labels_b) if a != b),
    }
