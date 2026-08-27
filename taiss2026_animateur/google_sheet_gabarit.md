# Google Sheet de collecte des labels — gabarit

À créer avant l'atelier depuis le compte de l'animateur, puis projeter l'URL.

## Structure

Un classeur unique, **un onglet par binôme**, nommés `binome_01` à
`binome_15`. Chaque onglet porte quatre colonnes, ligne d'en-tête comprise :

| id | annotateur_A | annotateur_B | round |
|---|---|---|---|
| rec_0086 | | | 1 |
| ... | | | 1 |
| rec_0102 | | | 2 |

- Colonne `id` : pré-remplie en copiant la colonne id de
  `transcriptions_fr_round1.csv` puis, à la suite, celle de
  `transcriptions_fr_round2.csv` (pareil pour les onglets éwé avec les
  fichiers `ee`). L'ordre doit rester celui des fichiers.
- Colonnes `annotateur_A` et `annotateur_B` : saisie par les participants,
  valeurs `positif`, `negatif`, `neutre`, sans majuscule ni accent.
- Colonne `round` : 1 ou 2, pré-remplie, sert de séparation visuelle.

Onglets 1 à 10 pré-remplis avec les ids français, 11 à 15 avec les ids éwé,
à ajuster selon la salle le jour J.

## Publication au format CSV

Pour chaque onglet : Fichier → Partager → Publier sur le web → choisir
l'onglet → format CSV → publier, et noter l'URL. Chaque binôme colle l'URL de
SON onglet dans la variable `SHEET_CSV_URL_R1` du notebook (et `_R2` au round
2 ; c'est la même URL, le notebook filtre par les ids attendus).

Vérifier la veille que la publication est active : le lien doit se télécharger
depuis une fenêtre de navigation privée, sans connexion à un compte.

## Si le Sheet tombe pendant la séance

Le notebook a un chemin de repli intégré : chaque binôme colle ses deux listes
de labels directement dans la cellule prévue. L'annotation elle-même peut se
faire sur papier, la saisie ne prend qu'une minute. Ne pas passer plus de
deux minutes à déboguer le Sheet en séance, basculer.
