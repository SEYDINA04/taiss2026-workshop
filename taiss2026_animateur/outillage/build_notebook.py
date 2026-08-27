# -*- coding: utf-8 -*-
"""Construit notebook_atelier.ipynb (participant) et notebook_corrige.ipynb
(animateur) à partir des mêmes sources, pour qu'ils ne divergent jamais.

Les squelettes d'exercice sont extraits textuellement de
taiss2026_workshop/scripts/quality_check.py. Les solutions du corrigé
reproduisent kit_build/reference_solutions.py. Les labels de démonstration du
corrigé viennent des CSV de simulation du dossier animateur.
"""

import re
import sys
from pathlib import Path

import nbformat as nbf
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / "taiss2026_workshop"
ANIM = ROOT / "taiss2026_animateur"
QC_SOURCE = (KIT / "scripts" / "quality_check.py").read_text(encoding="utf-8")


def extract_def(name):
    """Extrait le bloc d'une fonction top-level du module quality_check."""
    pattern = rf"^def {name}\(.*?(?=^def |^ALL_CHECKS|^# ---|^TEST_CASES|\Z)"
    m = re.search(pattern, QC_SOURCE, re.DOTALL | re.MULTILINE)
    assert m, f"fonction {name} introuvable dans quality_check.py"
    return m.group(0).rstrip() + "\n"


def md(source):
    return nbf.v4.new_markdown_cell(source)


def code(source):
    return nbf.v4.new_code_cell(source)


# ---------------------------------------------------------------- solutions
SOLUTIONS = {
    "check_channels": '''\
def check_channels(row, expected=EXPECTED_CHANNELS):
    """Contrôle que le nombre de canaux est exactement celui attendu."""
    try:
        return int(row["channels"]) == expected
    except (TypeError, ValueError, KeyError):
        return False


run_tests(check_channels)''',

    "check_words_per_second": '''\
def check_words_per_second(row, max_wps=MAX_WORDS_PER_SECOND):
    """Contrôle que le débit de parole annoncé est physiquement plausible.

    Signale, ne prouve pas : un débit impossible veut dire qu'un humain doit
    écouter ce fichier.
    """
    words = _words(_text(row["transcription"]))
    if not words:
        return True
    try:
        d = float(row["duration_s"])
    except (TypeError, ValueError, KeyError):
        return True
    if d != d or d <= 0:
        return True
    return len(words) / d <= max_wps


run_tests(check_words_per_second)''',

    "check_language_consistency": '''\
def check_language_consistency(row):
    """Heuristique : une ligne « ee » qui contient au moins deux mots outils
    français distincts est suspecte. Approximation assumée, pas une détection
    de langue : elle oriente l'écoute humaine, elle ne prouve rien."""
    if _text(row["language"]) != "ee":
        return True
    tokens = _words(_text(row["transcription"]))
    hits = {t for t in tokens if t in FRENCH_STOPWORDS}
    return len(hits) < 2


run_tests(check_language_consistency)''',

    "check_metadata_complete": '''\
def check_metadata_complete(row):
    """Champs requis non vides et date d'enregistrement antérieure au jour de
    l'atelier. Les dates AAAA-MM-JJ se comparent directement entre chaînes."""
    for field in REQUIRED_METADATA_FIELDS:
        if _text(row[field]) == "":
            return False
    return _text(row["recorded_at"]) <= REFERENCE_DATE


run_tests(check_metadata_complete)''',

    "quality_gate": '''\
def quality_gate(row, checks=None):
    """Agrège les contrôles : accepted vaut True si tout passe, reasons liste
    le nom des contrôles en échec, dans l'ordre de la liste fournie."""
    if checks is None:
        checks = ALL_CHECKS
    reasons = [c.__name__ for c in checks if not c(row)]
    return (len(reasons) == 0, reasons)


run_tests(quality_gate)''',
}


def exercise_cell(name):
    skeleton = extract_def(name)
    return skeleton + "\n\nrun_tests(" + name + ")"


def load_demo_labels():
    """Labels simulés pour le corrigé, injectés par le chemin manuel."""
    out = {}
    for guide, rnd in (("v1", 1), ("v2", 2)):
        df = pd.read_csv(ANIM / "labels_simules" /
                         f"simulation_labels_{guide}_round{rnd}.csv",
                         encoding="utf-8")
        out[(guide, rnd)] = (list(df["annotateur_A"]), list(df["annotateur_B"]))
    return out


def build(with_solutions):
    demo = load_demo_labels() if with_solutions else None
    cells = []

    # ------------------------------------------------------------- en-tête
    title = ("# Data Engineering for AI : de la donnée brute à un dataset de confiance\n"
             "\n"
             "Atelier TAISS 2026 — jeudi 27 août, 13h30 à 15h30, salle F1. "
             "Animateur : Babacar Ndao, Afriklang.\n"
             "\n"
             "Un seul jeu de données traverse les deux heures : le manifeste d'un corpus "
             "vocal, 200 lignes qui décrivent des enregistrements en français et en éwé. "
             "Vous allez l'inspecter, le nettoyer, l'annoter, mesurer la fiabilité de vos "
             "annotations, et repartir avec un dataset documenté :\n"
             "\n"
             "```\n"
             "raw_manifest.csv → clean_manifest.csv → annotated_manifest.csv → dataset final\n"
             "```")
    if with_solutions:
        title = ("# CORRIGÉ ANIMATEUR — ne pas distribuer\n\n"
                 "Version résolue du notebook participant : exercices remplis, labels de "
                 "démonstration injectés par le chemin manuel. Sert de répétition et de "
                 "filet de sécurité pendant la séance.\n\n") + title
    cells.append(md(title))

    # ------------------------------------------------- section 1 + setup
    cells.append(md(
        "## Section 1 — Le pipeline (13h30, 10 min)\n"
        "\n"
        "> **Consigne (10 min)** — Suivre la présentation. Exécuter les deux cellules "
        "ci-dessous pendant la distribution du lien : la première met les données en "
        "place, la seconde vérifie que tout est lisible.\n"
        "\n"
        "```\n"
        "Collecte → Inspection → Nettoyage → Annotation → Contrôle qualité → Dataset\n"
        "```\n"
        "\n"
        "Toutes ces étapes comptent. Une seule échoue en silence, et c'est celle que "
        "cet atelier prend au sérieux.\n"
        "\n"
        "Pourquoi travailler sur un manifeste plutôt que sur les fichiers audio : dans "
        "un pipeline réel, les contrôles automatiques tournent d'abord sur le tableau "
        "qui décrit les enregistrements, et seuls les cas signalés partent en écoute "
        "humaine. Écouter dix mille fichiers n'est pas une option. Filtrer dix mille "
        "lignes puis écouter les deux cents suspectes en est une."))

    cells.append(code(
        '# Mise en place des données. Trois cas, dans cet ordre :\n'
        '# 1. les fichiers sont déjà là (poste local ou session déjà préparée)\n'
        '# 2. téléchargement depuis l\'URL publique communiquée par l\'animateur\n'
        '# 3. repli : téléversement manuel du zip dans Colab\n'
        'import os\n'
        'import zipfile\n'
        'from pathlib import Path\n'
        'from urllib.request import urlretrieve\n'
        '\n'
        'DATA_URL = ""  # communiquée au tableau si le téléchargement est nécessaire\n'
        '\n'
        'if Path("data/raw_manifest.csv").exists():\n'
        '    print("données en place, rien à télécharger")\n'
        'elif Path("taiss2026_workshop/data/raw_manifest.csv").exists():\n'
        '    os.chdir("taiss2026_workshop")\n'
        '    print("données trouvées, dossier de travail :", Path.cwd())\n'
        'elif DATA_URL:\n'
        '    try:\n'
        '        urlretrieve(DATA_URL, "taiss2026_workshop.zip")\n'
        '        with zipfile.ZipFile("taiss2026_workshop.zip") as z:\n'
        '            z.extractall(".")\n'
        '        os.chdir("taiss2026_workshop")\n'
        '        print("données téléchargées, dossier de travail :", Path.cwd())\n'
        '    except Exception as e:\n'
        '        print("téléchargement impossible :", e)\n'
        '        print("repli : menu Fichiers de Colab, téléverser le zip fourni,")\n'
        '        print("puis relancer cette cellule")\n'
        'else:\n'
        '    print("pas de données locales et pas d\'URL : téléverser le zip fourni")\n'
        '    print("dans le menu Fichiers de Colab, puis relancer cette cellule")\n'
        '\n'
        '# le dossier que vous emporterez se construit au fil de la séance\n'
        'DATASET_DIR = Path("taiss2026_sentiment_ee-fr_v1.0")\n'
        'for sub in ["data", "splits", "scripts"]:\n'
        '    (DATASET_DIR / sub).mkdir(parents=True, exist_ok=True)'))

    cells.append(code(
        'import sys\n'
        'import pandas as pd\n'
        '\n'
        'sys.path.insert(0, "scripts")\n'
        '\n'
        'raw = pd.read_csv("data/raw_manifest.csv", encoding="utf-8")\n'
        'print(raw.shape[0], "lignes,", raw.shape[1], "colonnes")\n'
        'raw.head()'))

    # ------------------------------------------------- section 2
    cells.append(md(
        "## Section 2 — Inspecter un manifeste dégradé (13h40, 13 min)\n"
        "\n"
        "> **Consigne (8 min, en binômes)** — Trouvez tout ce qui ne va pas avec ce "
        "manifeste. Notez chaque famille de problème que vous repérez, avec un exemple "
        "de ligne. La restitution se fait au tableau, gardez vos trouvailles pour vous "
        "d'ici là.\n"
        "\n"
        "Vous venez d'entendre trois problèmes au haut-parleur. Il y en a davantage "
        "dans ce tableau, et vous ne pourrez écouter aucun fichier : c'est la situation "
        "normale d'un pipeline de données vocales."))

    cells.append(code(
        '# points de départ, à compléter par vos propres idées\n'
        'raw.describe(include="all").T'))

    cells.append(code(
        'raw[["language", "sample_rate", "channels", "region", "source"]].apply(\n'
        '    lambda col: col.value_counts(dropna=False).to_dict())'))

    cells.append(code(
        'raw.isna().sum()'))

    cells.append(code(
        '# votre exploration\n'))

    cells.append(md(
        "Ce que ce tableau ne montrera jamais, quel que soit le soin de l'inspection : "
        "si les labels d'annotation qu'on posera dessus seront fiables. Les défauts "
        "structurels se voient en dix minutes. Le défaut d'annotation ne se voit "
        "nulle part, et c'est la raison d'être de la séquence 4."))

    # ------------------------------------------------- section 3
    cells.append(md(
        "## Section 3 — Écrire les règles de qualité (13h53, 12 min)\n"
        "\n"
        "> **Consigne (12 min)** — Quatre fonctions de contrôle à écrire, une cellule "
        "chacune, puis la fonction d'agrégation. Chaque cellule contient le contrat, "
        "l'exemple et ses tests : exécutez la cellule pour savoir où vous en êtes. "
        "Ceux qui finissent en avance affinent leurs seuils et regardent ce que ça "
        "change au rapport final.\n"
        "\n"
        "Deux idées gouvernent cette section.\n"
        "\n"
        "Un seuil est une décision, pas une vérité. Fixer la durée maximale à 20 "
        "secondes plutôt qu'à 30 change le dataset, donc le modèle qu'on entraînera "
        "dessus. Ces décisions sont écrites en tête de `scripts/quality_check.py`, "
        "visibles et discutables, jamais enfouies dans le code.\n"
        "\n"
        "Un filtre signale, il ne prouve pas. Le contrôle de débit de parole ne "
        "démontre pas qu'une transcription est fausse : il désigne l'enregistrement "
        "qu'un humain doit écouter, comme le troisième fichier joué en ouverture."))

    cells.append(code(
        'from quality_check import (\n'
        '    check_duration, check_sample_rate, check_transcription_present,\n'
        '    run_tests, TEST_CASES, _text, _words,\n'
        '    FRENCH_STOPWORDS, REQUIRED_METADATA_FIELDS, REFERENCE_DATE,\n'
        '    EXPECTED_CHANNELS, EXPECTED_SAMPLE_RATE, MAX_WORDS_PER_SECOND,\n'
        '    MIN_DURATION_S, MAX_DURATION_S,\n'
        ')\n'
        '\n'
        '# trois contrôles sont déjà écrits, à lire comme des modèles\n'
        'import inspect\n'
        'print(inspect.getsource(check_duration))'))

    exercises = [
        ("check_channels",
         "**Attendu** : True si la ligne est en mono (`channels == 1`), False sinon, "
         "y compris quand la valeur est absente ou illisible.\n\n"
         "**Le test vérifie** : mono accepté, stéréo refusé, valeur non numérique et "
         "valeur absente refusées.\n\n"
         "**Si vous êtes bloqué** : `check_sample_rate` fait exactement le même "
         "travail sur une autre colonne, lisez-la."),
        ("check_words_per_second",
         "**Attendu** : False quand le nombre de mots divisé par la durée dépasse "
         "`max_wps`, True sinon. Une transcription vide ou une durée invalide ne sont "
         "pas le problème de ce contrôle : True dans ces cas, d'autres contrôles s'en "
         "chargent.\n\n"
         "**Le test vérifie** : le cas 40 mots en 0,6 s, les cas vides, la durée "
         "nulle, et un débit juste au-dessus du seuil.\n\n"
         "**Si vous êtes bloqué** : comptez les mots avec `_words(...)`, convertissez "
         "la durée comme le fait `check_duration`, comparez le rapport au seuil. "
         "Attention au sens : True veut dire conforme."),
        ("check_language_consistency",
         "**Attendu** : False pour une ligne marquée `ee` dont le texte contient au "
         "moins deux mots outils français distincts, True pour tout le reste. Les "
         "lignes `fr` sont toujours acceptées : sans lexique éwé, l'inverse n'est pas "
         "contrôlable, et le code l'assume plutôt que de le cacher.\n\n"
         "**Le test vérifie** : une ligne `ee` en français est refusée, une vraie "
         "ligne éwé passe, une ligne vide passe.\n\n"
         "**Si vous êtes bloqué** : `_words(...)` découpe, `FRENCH_STOPWORDS` est un "
         "ensemble, l'intersection de deux ensembles se compte avec `len`."),
        ("check_metadata_complete",
         "**Attendu** : True quand `speaker_id`, `region`, `recorded_at` et `source` "
         "sont tous non vides ET que la date d'enregistrement ne dépasse pas le jour "
         "de l'atelier. Un enregistrement daté du futur est impossible.\n\n"
         "**Le test vérifie** : la ligne complète passe, chaque champ vide ou NaN fait "
         "échouer, une date de 2027 fait échouer.\n\n"
         "**Si vous êtes bloqué** : `_text(...)` rend toute valeur comparable à la "
         "chaîne vide, et deux dates au format AAAA-MM-JJ se comparent directement "
         "entre chaînes."),
    ]
    for name, guidance in exercises:
        cells.append(md(f"### Exercice — `{name}`\n\n{guidance}"))
        cells.append(code(SOLUTIONS[name] if with_solutions else exercise_cell(name)))

    cells.append(md(
        "### Exercice — `quality_gate`\n\n"
        "**Attendu** : la fonction appelle chaque contrôle de la liste et retourne "
        "`(accepted, reasons)` : `accepted` vaut True seulement si tout passe, "
        "`reasons` liste les noms des contrôles en échec, dans l'ordre de la liste.\n\n"
        "**Le test vérifie** : ligne conforme → `(True, [])`, une puis deux pannes → "
        "les bons noms dans le bon ordre.\n\n"
        "**Si vous êtes bloqué** : `fn.__name__` donne le nom d'une fonction, et une "
        "liste en compréhension avec un `if` suffit."))
    cells.append(code(
        ('ALL_CHECKS = [\n'
         '    check_duration, check_sample_rate, check_transcription_present,\n'
         '    check_channels, check_words_per_second, check_language_consistency,\n'
         '    check_metadata_complete,\n'
         ']\n\n\n' + SOLUTIONS["quality_gate"]) if with_solutions else
        ('ALL_CHECKS = [\n'
         '    check_duration, check_sample_rate, check_transcription_present,\n'
         '    check_channels, check_words_per_second, check_language_consistency,\n'
         '    check_metadata_complete,\n'
         ']\n\n\n' + extract_def("quality_gate") + '\n\nrun_tests(quality_gate)')))

    cells.append(md(
        "La cellule suivante applique la barrière de qualité aux 200 lignes. Elle "
        "n'attend pas que tout soit résolu : un contrôle dont les tests ne passent "
        "pas encore est simplement laissé de côté, la séance continue, et le rapport "
        "dit lesquels ont tourné. Revenez remplir les trous quand vous voulez, puis "
        "relancez-la."))

    cells.append(code(
        'import contextlib\n'
        'import io\n'
        'import re\n'
        '\n'
        '\n'
        'def _tests_passent(fn):\n'
        '    with contextlib.redirect_stdout(io.StringIO()):\n'
        '        try:\n'
        '            return run_tests(fn)\n'
        '        except Exception:\n'
        '            return False\n'
        '\n'
        '\n'
        'checks_actifs = [check_duration, check_sample_rate, check_transcription_present]\n'
        'checks_ignores = []\n'
        'for fn in [check_channels, check_words_per_second,\n'
        '           check_language_consistency, check_metadata_complete]:\n'
        '    (checks_actifs if _tests_passent(fn) else checks_ignores).append(fn)\n'
        '\n'
        'erreurs_execution = {}\n'
        '\n'
        '\n'
        'def gate_robuste(row):\n'
        '    reasons = []\n'
        '    for fn in checks_actifs:\n'
        '        try:\n'
        '            if not fn(row):\n'
        '                reasons.append(fn.__name__)\n'
        '        except Exception:\n'
        '            # un contrôle qui plante sur une vraie ligne ne bloque pas la\n'
        '            # séance : on le compte et on continue\n'
        '            erreurs_execution[fn.__name__] = erreurs_execution.get(fn.__name__, 0) + 1\n'
        '    return len(reasons) == 0, reasons\n'
        '\n'
        '\n'
        'verdicts = raw.apply(gate_robuste, axis=1)\n'
        'raw_checked = raw.copy()\n'
        'raw_checked["accepted"] = [v[0] for v in verdicts]\n'
        'raw_checked["reasons"] = [";".join(v[1]) for v in verdicts]\n'
        '\n'
        '# deux opérations niveau tableau complètent les contrôles ligne à ligne :\n'
        '# les doublons et l\'encodage cassé ne se voient pas depuis une ligne seule\n'
        '\n'
        '\n'
        'def _norme(s):\n'
        '    return re.sub(r"\\s+", " ", str(s).strip().lower())\n'
        '\n'
        '\n'
        'doublon = raw.astype(str).apply(lambda c: c.map(_norme)).duplicated(keep="first")\n'
        'moji = raw["transcription"].fillna("").str.contains("Ã|â€", regex=True)\n'
        '\n'
        'garde = raw_checked["accepted"] & ~doublon & ~moji\n'
        'clean = raw[garde].copy()\n'
        'clean.to_csv(DATASET_DIR / "data" / "clean_manifest.csv",\n'
        '             index=False, encoding="utf-8")\n'
        '\n'
        'motifs = {}\n'
        'for _, v in raw_checked[~raw_checked["accepted"]].iterrows():\n'
        '    for m in v["reasons"].split(";"):\n'
        '        motifs[m] = motifs.get(m, 0) + 1\n'
        '\n'
        'lignes_rapport = [\n'
        '    "# Rapport de qualité — raw_manifest.csv", "",\n'
        '    f"Lignes en entrée : {len(raw)}",\n'
        '    f"Lignes conservées : {len(clean)}",\n'
        '    f"Lignes rejetées par les contrôles : {int((~raw_checked.accepted).sum())}",\n'
        '    f"Doublons retirés (exacts et approximatifs) : {int(doublon.sum())}",\n'
        '    f"Encodage cassé (mojibake) : {int(moji.sum())}", "",\n'
        '    "Motifs de rejet :",\n'
        '] + [f"- {k} : {v}" for k, v in sorted(motifs.items())] + [\n'
        '    "",\n'
        '    f"Contrôles actifs : {[f.__name__ for f in checks_actifs]}",\n'
        '    f"Contrôles ignorés (tests non passés) : {[f.__name__ for f in checks_ignores]}",\n'
        '    f"Seuils : durée [{MIN_DURATION_S}, {MAX_DURATION_S}] s, "\n'
        '    f"{EXPECTED_SAMPLE_RATE} Hz, mono, {MAX_WORDS_PER_SECOND} mots/s max",\n'
        ']\n'
        'if erreurs_execution:\n'
        '    lignes_rapport.append(f"Contrôles ayant levé des erreurs en cours de "\n'
        '                          f"route : {erreurs_execution}")\n'
        '(DATASET_DIR / "quality_report.md").write_text(\n'
        '    "\\n".join(lignes_rapport), encoding="utf-8")\n'
        '\n'
        'print(f"{len(raw)} lignes en entrée, {len(clean)} conservées")\n'
        'print(f"contrôles actifs : {[f.__name__ for f in checks_actifs]}")\n'
        'if checks_ignores:\n'
        '    print(f"contrôles ignorés pour l\'instant : "\n'
        '          f"{[f.__name__ for f in checks_ignores]}")\n'
        'print("rapport écrit :", DATASET_DIR / "quality_report.md")'))

    # ------------------------------------------------- section 4
    cells.append(md(
        "## Section 4 — Mesurer la fiabilité des labels (14h05, 45 min)\n"
        "\n"
        "> **Consigne (5 min pour cette page)** — Lire le guide d'annotation v1 "
        "distribué (`guides/annotation_guide_v1_fr.md` ou sa version éwé selon votre "
        "groupe). Pas de questions sur les cas particuliers : le guide est réputé "
        "suffisant, c'est lui votre seule référence pour le round 1.\n"
        "\n"
        "La tâche : trois classes de sentiment, `positif`, `negatif`, `neutre`, sur "
        "la colonne `transcription`. Chaque binôme annote la même série de phrases, "
        "chacun de son côté.\n"
        "\n"
        "Une objection arrive toujours ici : le sentiment est subjectif, le désaccord "
        "serait donc normal. C'est exactement pourquoi il faut un guide. Un guide ne "
        "supprime pas la subjectivité, il la rend reproductible : deux annotateurs "
        "qui appliquent la même règle explicite convergent, même sur une tâche "
        "subjective. C'est ce que le Kappa mesure."))

    cells.append(md(
        "### Round 1 — annotation en aveugle (13 min)\n"
        "\n"
        "> **Consigne (13 min)** — 40 phrases, chacun annote seul, sans se concerter "
        "avec son binôme. Si vous vous alignez, la mesure ne veut plus rien dire. "
        "Saisie dans l'onglet de votre binôme du Google Sheet projeté, colonnes "
        "`annotateur_A` et `annotateur_B`, ou sur papier si la connexion tombe."))

    cells.append(code(
        'LANGUE = "fr"  # passer à "ee" pour le groupe éwé\n'
        '\n'
        'round1 = pd.read_csv(f"data/transcriptions_{LANGUE}_round1.csv",\n'
        '                     encoding="utf-8")\n'
        'if round1["transcription"].str.contains(r"\\[À REMPLIR", na=False).any():\n'
        '    print("le corpus éwé n\'est pas encore chargé dans ce kit ;")\n'
        '    print("le groupe éwé travaille sur la version distribuée en salle")\n'
        'else:\n'
        '    with pd.option_context("display.max_colwidth", None):\n'
        '        display(round1)'))

    cells.append(md(
        "### Mesurer l'accord (9 min)\n"
        "\n"
        "> **Consigne (9 min)** — Récupérer vos labels ci-dessous, par le Sheet ou en "
        "les collant à la main, puis exécuter les cellules de mesure. Reportez votre "
        "Kappa au tableau dans la colonne de votre groupe.\n"
        "\n"
        "L'accord brut ment. Deux annotateurs qui répondent `neutre` partout obtiennent "
        "un accord brut spectaculaire et n'ont rien jugé du tout : le Kappa corrige "
        "l'accord de ce que le hasard produirait compte tenu des habitudes de chacun. "
        "C'est l'écart entre les deux chiffres qui va vous surprendre."))

    manual_r1 = ("labels_A = []  # coller ici vos 40 labels, ex. \"positif\", \"neutre\", ...\n"
                 "labels_B = []")
    if with_solutions:
        a1, b1 = demo[("v1", 1)]
        manual_r1 = f"labels_A = {a1!r}\nlabels_B = {b1!r}"

    cells.append(code(
        '# chemin principal : le Google Sheet de votre binôme, publié au format CSV.\n'
        '# Fichier → Partager → Publier sur le web → votre onglet → CSV, puis coller\n'
        '# l\'URL ici. Colonnes attendues : id, annotateur_A, annotateur_B.\n'
        'SHEET_CSV_URL_R1 = ""\n'
        '\n'
        '# chemin de repli : coller les deux listes à la main, dans l\'ordre du\n'
        '# tableau affiché plus haut\n'
        + manual_r1))

    cells.append(code(
        'from agreement import (normalize_labels, raw_agreement, kappa,\n'
        '                       confusion, disagreements, compare_guides, summary)\n'
        '\n'
        '\n'
        'def recuperer_labels(sheet_url, manuel_a, manuel_b, ids_attendus):\n'
        '    """Choisit le chemin disponible et rend deux listes de labels propres.\n'
        '\n'
        '    Priorité au Sheet s\'il est renseigné et lisible, sinon aux listes\n'
        '    manuelles si elles sont remplies. Retourne (None, None) plutôt que de\n'
        '    lever une erreur : la suite du notebook saute proprement ce qui manque.\n'
        '    """\n'
        '    if sheet_url:\n'
        '        try:\n'
        '            feuille = pd.read_csv(sheet_url)\n'
        '            manquantes = {"id", "annotateur_A", "annotateur_B"} - set(feuille.columns)\n'
        '            if manquantes:\n'
        '                print("colonnes manquantes dans le Sheet :", manquantes)\n'
        '            else:\n'
        '                feuille = feuille.set_index("id").reindex(ids_attendus)\n'
        '                absents = feuille["annotateur_A"].isna() | feuille["annotateur_B"].isna()\n'
        '                if absents.any():\n'
        '                    print(f"{int(absents.sum())} lignes sans label dans le Sheet, "\n'
        '                          f"ids : {list(feuille.index[absents])[:5]}...")\n'
        '                else:\n'
        '                    a, b = list(feuille["annotateur_A"]), list(feuille["annotateur_B"])\n'
        '                    print("labels récupérés depuis le Sheet")\n'
        '                    return _nettoyer(a, b)\n'
        '        except Exception as e:\n'
        '            print("Sheet illisible :", e)\n'
        '    if manuel_a and manuel_b:\n'
        '        if len(manuel_a) != len(ids_attendus) or len(manuel_b) != len(ids_attendus):\n'
        '            print(f"il faut {len(ids_attendus)} labels par annotateur, reçu "\n'
        '                  f"{len(manuel_a)} et {len(manuel_b)}")\n'
        '            return None, None\n'
        '        print("labels récupérés depuis les listes manuelles")\n'
        '        return _nettoyer(manuel_a, manuel_b)\n'
        '    print("pas encore de labels : renseigner SHEET_CSV_URL ou les listes,")\n'
        '    print("puis relancer cette cellule ; la suite du notebook reste utilisable")\n'
        '    return None, None\n'
        '\n'
        '\n'
        'def _nettoyer(a, b):\n'
        '    a, anom_a = normalize_labels(a)\n'
        '    b, anom_b = normalize_labels(b)\n'
        '    for nom, anomalies in (("A", anom_a), ("B", anom_b)):\n'
        '        if anomalies:\n'
        '            print(f"labels illisibles chez {nom} : {anomalies} — corrigez et relancez")\n'
        '            return None, None\n'
        '    return a, b\n'
        '\n'
        '\n'
        'labels_A_r1, labels_B_r1 = recuperer_labels(\n'
        '    SHEET_CSV_URL_R1, labels_A, labels_B, list(round1["id"]))'))

    cells.append(code(
        'if labels_A_r1 is not None:\n'
        '    mesures_r1 = summary(labels_A_r1, labels_B_r1)\n'
        '    print(mesures_r1)\n'
        '    kappa_v1 = mesures_r1["kappa"]\n'
        '    display(confusion(labels_A_r1, labels_B_r1))\n'
        'else:\n'
        '    kappa_v1 = None'))

    cells.append(md(
        "### Diagnostiquer et réécrire le guide (12 min)\n"
        "\n"
        "> **Consigne (12 min, collectif)** — Lire les désaccords ci-dessous à voix "
        "haute, phrase par phrase. Pour chacun : est-ce une faute d'inattention, ou "
        "bien le guide ne disait rien ? Chaque silence du guide identifié au tableau "
        "devient une règle explicite. L'ensemble de ces règles est votre guide v2, à "
        "recopier dans la cellule prévue plus bas."))

    cells.append(code(
        'if labels_A_r1 is not None:\n'
        '    table_desaccords = disagreements(round1, labels_A_r1, labels_B_r1)\n'
        '    with pd.option_context("display.max_colwidth", None):\n'
        '        display(table_desaccords)\n'
        'else:\n'
        '    print("pas de labels round 1, rien à diagnostiquer pour l\'instant")'))

    guide_v2_participant = (
        'GUIDE_V2 = """\n'
        '# Guide d\'annotation — Sentiment (version 2, écrite par la salle)\n'
        '\n'
        'Reprend le guide v1, plus les règles décidées collectivement :\n'
        '\n'
        '## Règle 1 —\n'
        '\n'
        '## Règle 2 —\n'
        '\n'
        '## Règle 3 —\n'
        '\n'
        '## Règle 4 —\n'
        '\n'
        '## Règle 5 —\n'
        '\n'
        '## Règle 6 —\n'
        '"""\n'
        '\n'
        '(DATASET_DIR / "annotation_guide_v2.md").write_text(GUIDE_V2, encoding="utf-8")\n'
        'print("guide v2 sauvegardé dans", DATASET_DIR / "annotation_guide_v2.md")')
    guide_v2_corrige = (
        'GUIDE_V2 = """\n'
        '# Guide d\'annotation — Sentiment (version 2, écrite par la salle)\n'
        '\n'
        'Reprend le guide v1, plus les règles décidées collectivement :\n'
        '\n'
        '## Règle 1 — Sentiment mixte : annoter le jugement final ; à équilibre, neutre\n'
        '\n'
        '## Règle 2 — Neutre : fait sans jugement du locuteur ; les marqueurs\n'
        '## d\'insistance (« toujours pas », « encore ») comptent comme un jugement\n'
        '\n'
        '## Règle 3 — Sentiment rapporté : annoter ce qui est exprimé, même si le\n'
        '## locuteur ne fait que le rapporter\n'
        '\n'
        '## Règle 4 — Ironie : annoter l\'intention, pas la lettre\n'
        '\n'
        '## Règle 5 — Mauvaise nouvelle factuelle sans plainte : neutre\n'
        '\n'
        '## Règle 6 — Questions et impératifs : neutre sauf charge émotionnelle explicite\n'
        '"""\n'
        '\n'
        '(DATASET_DIR / "annotation_guide_v2.md").write_text(GUIDE_V2, encoding="utf-8")\n'
        'print("guide v2 sauvegardé dans", DATASET_DIR / "annotation_guide_v2.md")')
    cells.append(code(guide_v2_corrige if with_solutions else guide_v2_participant))

    cells.append(md(
        "### Round 2 — mêmes annotateurs, nouveau guide (6 min)\n"
        "\n"
        "> **Consigne (6 min)** — 20 nouvelles phrases, mêmes binômes, même interdiction "
        "de se concerter. Une seule chose a changé : vous annotez avec le guide v2. "
        "Saisie dans les colonnes round 2 de votre onglet."))

    manual_r2 = ("labels_A_2 = []  # les 20 labels du round 2\n"
                 "labels_B_2 = []")
    if with_solutions:
        a2, b2 = demo[("v2", 2)]
        manual_r2 = f"labels_A_2 = {a2!r}\nlabels_B_2 = {b2!r}"

    cells.append(code(
        'round2 = pd.read_csv(f"data/transcriptions_{LANGUE}_round2.csv",\n'
        '                     encoding="utf-8")\n'
        'if not round2["transcription"].str.contains(r"\\[À REMPLIR", na=False).any():\n'
        '    with pd.option_context("display.max_colwidth", None):\n'
        '        display(round2)\n'
        '\n'
        'SHEET_CSV_URL_R2 = ""\n'
        + manual_r2 + '\n'
        '\n'
        'labels_A_r2, labels_B_r2 = recuperer_labels(\n'
        '    SHEET_CSV_URL_R2, labels_A_2, labels_B_2, list(round2["id"]))'))

    cells.append(code(
        'if labels_A_r2 is not None:\n'
        '    mesures_r2 = summary(labels_A_r2, labels_B_r2)\n'
        '    print(mesures_r2)\n'
        '    kappa_v2 = mesures_r2["kappa"]\n'
        'else:\n'
        '    kappa_v2 = None\n'
        '\n'
        'if kappa_v1 is not None and kappa_v2 is not None:\n'
        '    compare_guides(kappa_v1, kappa_v2)'))

    cells.append(md(
        "Rien n'a changé dans les annotateurs ni dans le type de phrases, la "
        "proportion de cas difficiles est la même dans les deux rounds. Seul le guide "
        "a changé. Si votre Kappa monte, vous venez de voir la démonstration entière "
        "de l'atelier tenir dans un chiffre. S'il ne monte pas dans votre binôme : "
        "vingt items, c'est un petit échantillon, et cette instabilité est précisément "
        "la raison pour laquelle un jeu d'évaluation de production en compte des "
        "milliers."))

    # ------------------------------------------------- section 5
    cells.append(md(
        "## Section 5 — Pré-annotation IA et validation humaine (14h50, 15 min)\n"
        "\n"
        "> **Consigne (15 min)** — Exécuter les cellules, puis discussion : où le "
        "modèle se trompe-t-il, et sur quelles classes ? La démonstration en direct "
        "se fait depuis le poste de l'animateur, pas sur vos machines.\n"
        "\n"
        "Un modèle a annoté les mêmes phrases que vous, en zéro-shot : trois classes "
        "demandées, aucune règle de cas limite fournie, exactement votre situation du "
        "round 1. Ses prédictions sont livrées pré-calculées dans "
        "`data/model_predictions.csv`."))

    cells.append(code(
        'predictions = pd.read_csv("data/model_predictions.csv", encoding="utf-8")\n'
        'pred_langue = predictions[predictions["language"] == LANGUE]\n'
        'if pred_langue.empty:\n'
        '    print(f"pas encore de prédictions pour la langue {LANGUE!r} ;")\n'
        '    print("la passe éwé tourne dès que le corpus est chargé")\n'
        'else:\n'
        '    print(len(pred_langue), "prédictions du modèle pour", LANGUE)\n'
        '    display(pred_langue["predicted_label"].value_counts())'))

    cells.append(code(
        '# votre référence humaine : les phrases où votre binôme est d\'accord.\n'
        '# En production on utiliserait un gold arbitré par un troisième annotateur ;\n'
        '# en deux heures, le consensus du binôme en tient lieu, et cette\n'
        '# simplification est exactement le genre de choix qu\'une dataset card doit\n'
        '# documenter.\n'
        'consensus = {}\n'
        'for tableau, la, lb in ((round1, labels_A_r1, labels_B_r1),\n'
        '                        (round2, labels_A_r2, labels_B_r2)):\n'
        '    if la is None:\n'
        '        continue\n'
        '    for rid, a, b in zip(tableau["id"], la, lb):\n'
        '        if a == b:\n'
        '            consensus[rid] = a\n'
        '\n'
        'if not consensus or pred_langue.empty:\n'
        '    accord_modele = None\n'
        '    print("comparaison sautée : il faut des labels de binôme et des "\n'
        '          "prédictions dans votre langue")\n'
        'else:\n'
        '    commun = pred_langue[pred_langue["id"].isin(consensus)]\n'
        '    verdicts = [consensus[r.id] == r.predicted_label\n'
        '                for r in commun.itertuples()]\n'
        '    accord_modele = sum(verdicts) / len(verdicts)\n'
        '    print(f"accord du modèle avec votre consensus : {accord_modele:.0%} "\n'
        '          f"sur {len(verdicts)} phrases")\n'
        '    rates = commun[[not v for v in verdicts]].merge(\n'
        '        pd.concat([round1, round2])[["id", "transcription"]], on="id")\n'
        '    rates["votre_label"] = rates["id"].map(consensus)\n'
        '    with pd.option_context("display.max_colwidth", None):\n'
        '        display(rates[["id", "transcription", "votre_label", "predicted_label"]])'))

    cells.append(md(
        "Regardez sur quelles phrases le modèle décroche : ce sont massivement les "
        "cas limites que votre guide v2 vient de trancher. Le modèle applique ses "
        "propres conventions implicites, pas les vôtres, et aucun F1 ne le dira si le "
        "jeu d'évaluation a été construit avec les mêmes conventions implicites.\n"
        "\n"
        "D'où l'architecture qui structure le travail d'Afriklang :\n"
        "\n"
        "```\n"
        "Pré-annotation IA → Validation humaine → Contrôle qualité → Dataset\n"
        "```\n"
        "\n"
        "Sur une tâche d'analyse de sentiment en wolof, avec un protocole documenté, "
        "les annotateurs natifs d'Afriklang atteignent 90 pour cent de F1 macro là où "
        "le meilleur modèle testé en zéro-shot plafonne à 45 pour cent. Cette mesure "
        "porte sur cette tâche et ce corpus. Elle ne dit pas qu'un modèle est "
        "incapable de traiter le wolof."))

    # ------------------------------------------------- section 6
    cells.append(md(
        "## Section 6 — Assembler et documenter (15h05, 15 min)\n"
        "\n"
        "> **Consigne (15 min)** — Exécuter les cellules dans l'ordre : fusion des "
        "annotations, découpage par locuteur, carte du dataset. Puis compléter les "
        "champs marqués à compléter dans la carte, c'est elle qu'on lit dans six "
        "mois.\n"
        "\n"
        "Le nom du dossier est déjà une leçon : `taiss2026_sentiment_ee-fr_v1.0` "
        "porte l'origine, la tâche, les langues et la version. Un dossier nommé "
        "`dataset_final` ou `data2` est irretrouvable dans six mois et impossible à "
        "citer."))

    cells.append(code(
        '# fusion des labels consensuels dans le manifeste nettoyé\n'
        'annotated = clean.copy()\n'
        'annotated["sentiment"] = annotated["id"].map(consensus) if consensus else ""\n'
        'annotated["sentiment"] = annotated["sentiment"].fillna("")\n'
        'annotated.to_csv(DATASET_DIR / "data" / "annotated_manifest.csv",\n'
        '                 index=False, encoding="utf-8")\n'
        'n_annotees = int((annotated["sentiment"] != "").sum())\n'
        'print(f"{n_annotees} lignes portent un label consensuel")\n'
        '\n'
        'import shutil\n'
        'shutil.copy("data/raw_manifest.csv", DATASET_DIR / "data" / "raw_manifest.csv")\n'
        'for script in ["quality_check.py", "agreement.py"]:\n'
        '    shutil.copy(f"scripts/{script}", DATASET_DIR / "scripts" / script)'))

    cells.append(md(
        "Le découpage se fait par locuteur, pas par ligne. Si les enregistrements de "
        "`spk_042` sont à la fois dans train et dans test, le modèle peut reconnaître "
        "la voix ou le style au lieu d'apprendre la tâche : le score de test devient "
        "un mensonge optimiste. C'est la fuite de données, et le manifeste porte "
        "`speaker_id` précisément pour la rendre évitable en trois lignes."))

    cells.append(code(
        'import random\n'
        '\n'
        'rng = random.Random(20260827)\n'
        'source_splits = annotated.copy()\n'
        '# une ligne sans locuteur ne peut pas garantir la règle : on l\'isole dans\n'
        '# train par convention, et la carte le documentera\n'
        'source_splits["speaker_id"] = source_splits["speaker_id"].fillna("spk_inconnu")\n'
        '\n'
        'locuteurs = sorted(source_splits["speaker_id"].unique())\n'
        'rng.shuffle(locuteurs)\n'
        'cible = {"train": 0.70, "validation": 0.15, "test": 0.15}\n'
        'quotas = {k: v * len(source_splits) for k, v in cible.items()}\n'
        'affectation, effectifs = {}, {"train": 0, "validation": 0, "test": 0}\n'
        'for spk in locuteurs:\n'
        '    n = int((source_splits["speaker_id"] == spk).sum())\n'
        '    part = "spk_inconnu" == spk and "train" or min(\n'
        '        effectifs, key=lambda s: (effectifs[s] + n) / quotas[s])\n'
        '    affectation[spk] = part\n'
        '    effectifs[part] += n\n'
        '\n'
        'source_splits["split"] = source_splits["speaker_id"].map(affectation)\n'
        'for part in ["train", "validation", "test"]:\n'
        '    bloc = source_splits[source_splits["split"] == part].drop(columns=["split"])\n'
        '    bloc.to_csv(DATASET_DIR / "splits" / f"{part}.csv",\n'
        '                index=False, encoding="utf-8")\n'
        '    print(f"{part:11} {len(bloc):4} lignes, {bloc.speaker_id.nunique()} locuteurs")\n'
        '\n'
        'recouvrement = (set(source_splits[source_splits.split == "train"].speaker_id)\n'
        '                & set(source_splits[source_splits.split == "test"].speaker_id))\n'
        'print("locuteurs présents dans train et test :", recouvrement or "aucun")'))

    cells.append(code(
        '# la carte du dataset : remplie avec ce qui se mesure, à compléter pour ce\n'
        '# qui se décide (licence, limites que vous connaissez et pas nous)\n'
        'from datetime import date\n'
        '\n'
        'LICENCE = "[À COMPLÉTER : ex. CC-BY-4.0]"\n'
        'AUTEURS = "[À COMPLÉTER : votre binôme]"\n'
        '\n'
        'gabarit = (Path("templates") / "dataset_card_template.md").read_text(encoding="utf-8")\n'
        'carte = (gabarit\n'
        '         .replace("{{origine}}", "Atelier TAISS 2026, Lomé — corpus vocal Afriklang")\n'
        '         .replace("{{langues}}", "français (fr), éwé (ee)")\n'
        '         .replace("{{n_items}}", str(len(annotated)))\n'
        '         .replace("{{n_annotees}}", str(n_annotees))\n'
        '         .replace("{{tache}}", "analyse de sentiment, trois classes")\n'
        '         .replace("{{guide}}", "annotation_guide_v2.md (v1 conservée pour audit)")\n'
        '         .replace("{{n_annotateurs}}", "2 par binôme, consensus simple")\n'
        '         .replace("{{kappa_v1}}", str(kappa_v1) if kappa_v1 is not None else "non mesuré")\n'
        '         .replace("{{kappa_v2}}", str(kappa_v2) if kappa_v2 is not None else "non mesuré")\n'
        '         .replace("{{licence}}", LICENCE)\n'
        '         .replace("{{date}}", date.today().isoformat())\n'
        '         .replace("{{auteurs}}", AUTEURS))\n'
        '(DATASET_DIR / "dataset_card.md").write_text(carte, encoding="utf-8")\n'
        'print(carte)'))

    cells.append(code(
        '# le dossier que vous emportez\n'
        'for f in sorted(DATASET_DIR.rglob("*")):\n'
        '    if f.is_file():\n'
        '        print(f.relative_to(DATASET_DIR.parent))'))

    # ------------------------------------------------- section 7
    cells.append(md(
        "## Section 7 — À l'échelle, et questions (15h20, 10 min)\n"
        "\n"
        "Ce que vous avez fait sur 60 phrases, Afriklang le fait tourner sur 24 "
        "langues avec plus de 200 contributeurs natifs. Ce qui change à l'échelle : "
        "les binômes deviennent des équipes, le consensus simple devient un arbitrage "
        "par un troisième annotateur quand les deux premiers divergent, et le guide "
        "d'annotation devient un document vivant, versionné comme du code, parce que "
        "chaque nouveau lot de données révèle un cas que personne n'avait prévu.\n"
        "\n"
        "Ce qui ne change pas : un modèle ne peut pas être meilleur que la mesure qui "
        "l'évalue. Et cette mesure, quelqu'un l'a construite à la main.\n"
        "\n"
        "Les participants les plus rigoureux d'aujourd'hui peuvent rejoindre le réseau "
        "de contributeurs rémunérés d'Afriklang : la feuille de contacts circule."))

    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python",
                       "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
        "colab": {"provenance": []},
    }
    return nb


def main():
    participant = build(with_solutions=False)
    corrige = build(with_solutions=True)
    p1 = KIT / "notebook_atelier.ipynb"
    p2 = ANIM / "notebook_corrige.ipynb"
    nbf.write(participant, str(p1))
    nbf.write(corrige, str(p2))
    print(f"écrit : {p1} ({len(participant.cells)} cellules)")
    print(f"écrit : {p2} ({len(corrige.cells)} cellules)")


if __name__ == "__main__":
    main()
