# -*- coding: utf-8 -*-
"""Simulation de calibration : deux annotateurs synthétiques, guide v1 puis v2.

Objet : vérifier AVANT l'atelier que les phrases et les trous du guide v1
produisent bien la démonstration attendue, une hausse nette du Kappa quand on
passe au guide v2. Si ce script ne montre pas cette hausse, ce sont les
phrases ou le guide qu'il faut reprendre, pas la salle.

Modèle de comportement, volontairement simple :

- Guide v1. Sur les phrases claires, les deux annotateurs suivent l'évidence.
  Sur les cas limites, chacun applique sa politique personnelle, puisque le
  guide ne dit rien : A lit la proposition finale des phrases mixtes, annote
  le contenu des discours rapportés, prend l'ironie au premier degré quand
  des marqueurs positifs dominent, range les faits sans jugement dans neutre.
  B porte un biais de négativité sur les phrases mixtes, refuse d'annoter un
  sentiment rapporté, lit l'intention derrière l'ironie, étiquette les
  mauvaises nouvelles factuelles selon la désirabilité du fait. Ces politiques
  sont encodées phrase par phrase dans sentences_fr.py (champs a_v1, b_v1).
- Guide v2. Les deux annotateurs appliquent les six règles de la référence,
  qui décident chaque cas limite : ils convergent vers gold_v2.
- Bruit résiduel dans les deux conditions : chaque annotateur se trompe sur
  un petit nombre de phrases claires tirées à graine fixe, parce que des
  humains fatigués font des fautes d'inattention même avec un bon guide.

Protocole mesuré, identique à celui de l'atelier : Kappa v1 sur les 40 phrases
du round 1, Kappa v2 sur les 20 phrases du round 2. Les croisements
(v1 sur round 2, v2 sur round 1) sont donnés en contrôle de robustesse.
"""

import random
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "kit_build"))
sys.path.insert(0, str(ROOT / "taiss2026_workshop" / "scripts"))

from sentences_fr import SENTENCES  # noqa: E402
from agreement import kappa, raw_agreement  # noqa: E402

SEED = 90210
NOISE = {"positif": "neutre", "negatif": "neutre", "neutre": "positif"}


def flip(label):
    return NOISE[label]


def simulate(round_no, guide, n_noise_a, n_noise_b, rng):
    rows = [s for s in SENTENCES if s["round"] == round_no]
    a, b = [], []
    for s in rows:
        if guide == "v1":
            a.append(s["a_v1"])
            b.append(s["b_v1"])
        else:
            a.append(s["gold_v2"])
            b.append(s["gold_v2"])
    clear_idx = [i for i, s in enumerate(rows) if s["category"] != "limite"]
    for lst, n in ((a, n_noise_a), (b, n_noise_b)):
        for i in rng.sample(clear_idx, n):
            lst[i] = flip(lst[i])
    # alignement sur l'ordre réel du fichier de round livré aux participants :
    # les CSV de simulation doivent porter les mêmes ids, dans le même ordre,
    # sinon tout usage aval par identifiant serait brouillé
    fichier = ROOT / "taiss2026_workshop" / "data" / f"transcriptions_fr_round{round_no}.csv"
    ordre = pd.read_csv(fichier, encoding="utf-8")
    par_texte = {s["text"]: (la, lb) for s, la, lb in zip(rows, a, b)}
    rows_al, a_al, b_al = [], [], []
    for rid, texte in zip(ordre["id"], ordre["transcription"]):
        la, lb = par_texte[texte]
        rows_al.append({"id": rid, "text": texte})
        a_al.append(la)
        b_al.append(lb)
    return rows_al, a_al, b_al


def main():
    rng = random.Random(SEED)
    out = {}
    runs = {
        ("v1", 1): dict(n_noise_a=2, n_noise_b=1),
        ("v2", 2): dict(n_noise_a=1, n_noise_b=0),
        ("v1", 2): dict(n_noise_a=1, n_noise_b=1),
        ("v2", 1): dict(n_noise_a=2, n_noise_b=1),
    }
    for (guide, rnd), noise in runs.items():
        rows, a, b = simulate(rnd, guide, rng=rng, **noise)
        out[(guide, rnd)] = {
            "kappa": kappa(a, b),
            "accord_brut": raw_agreement(a, b),
            "n": len(rows),
        }
        df = pd.DataFrame({
            "id": [r["id"] for r in rows],
            "transcription": [r["text"] for r in rows],
            "annotateur_A": a,
            "annotateur_B": b,
        })
        df.to_csv(HERE / f"simulation_labels_{guide}_round{rnd}.csv",
                  index=False, encoding="utf-8")

    print(f"{'condition':28} {'accord brut':>12} {'kappa':>8}")
    for (guide, rnd), m in out.items():
        name = f"guide {guide} sur round {rnd} (n={m['n']})"
        print(f"{name:28} {m['accord_brut']:>11.1%} {m['kappa']:>8.3f}")

    k1 = out[("v1", 1)]["kappa"]
    k2 = out[("v2", 2)]["kappa"]
    delta = k2 - k1
    print(f"\nprotocole atelier : v1/round1 = {k1:.3f}, v2/round2 = {k2:.3f}, "
          f"delta = {delta:+.3f}")
    if delta < 0.25:
        print("CALIBRATION INSUFFISANTE : hausse du Kappa trop faible")
        sys.exit(1)
    print("calibration conforme : hausse nette du Kappa")
    return out


if __name__ == "__main__":
    main()
