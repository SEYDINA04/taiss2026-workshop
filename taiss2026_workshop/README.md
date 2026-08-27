# Atelier TAISS 2026 — Data Engineering for AI

De la donnée brute à un dataset de confiance. Jeudi 27 août 2026, 13h30 à
15h30, salle F1. Animateur : Babacar Ndao, Afriklang.

## Démarrage

1. Ouvrir `notebook_atelier.ipynb` dans Google Colab (lien projeté en salle),
   ou dans Jupyter si vous travaillez en local.
2. Exécuter les deux premières cellules : elles mettent les données en place.
   Aucune installation n'est nécessaire, tout tourne avec ce que Colab fournit.
3. Le reste suit le rythme de la séance, section par section. Chaque section
   commence par un encadré qui dit quoi faire et en combien de temps.

## Contenu du dossier

| Chemin | Rôle |
|---|---|
| `notebook_atelier.ipynb` | le fil de la séance, sept sections |
| `data/raw_manifest.csv` | le manifeste à inspecter et nettoyer, 200 lignes |
| `data/transcriptions_*_round*.csv` | les phrases à annoter, par langue et par round |
| `data/model_predictions.csv` | prédictions zéro-shot du modèle, pré-calculées |
| `guides/annotation_guide_v1_*.md` | le guide d'annotation du round 1 |
| `scripts/quality_check.py` | contrôles de qualité, quatre fonctions à écrire |
| `scripts/agreement.py` | mesures d'accord, fourni complet |
| `audio_demo/` | les trois extraits joués en ouverture de la séquence 2 |
| `templates/dataset_card_template.md` | gabarit de la carte du dataset |

## Ce que vous emportez

Le notebook construit au fil de la séance un dossier
`taiss2026_sentiment_ee-fr_v1.0/` : manifeste nettoyé puis annoté, splits sans
fuite de locuteur, guide v2 écrit par la salle, rapport de qualité et carte du
dataset. Il est à vous.

## En cas de problème

La connexion tombe : le notebook fonctionne aussi en local, et l'annotation
peut se faire sur papier, l'animateur a le nécessaire. Une cellule refuse
d'avancer : lisez le message, les cellules disent quoi faire quand il manque
quelque chose ; au pire, sautez la cellule, la suite ne casse pas en chaîne.
