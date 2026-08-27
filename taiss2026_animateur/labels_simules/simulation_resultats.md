# Simulation de calibration — résultats

> Dossier animateur. Produit par `simulate_annotators.py` avant l'atelier,
> valeurs mesurées le 26 août 2026, graine fixe 90210. Les labels simulés
> sont dans les quatre CSV de ce dossier.

## Ce qui a été simulé

Deux annotateurs synthétiques annotent les phrases françaises. Sous guide v1,
chacun applique sa politique personnelle sur les cas limites, puisque le guide
ne dit rien : lecture de la proposition finale contre biais de négativité,
annotation du contenu rapporté contre refus du discours rapporté, premier
degré contre intention sur l'ironie, neutre contre désirabilité du fait sur
les mauvaises nouvelles. Sous guide v2, tous deux appliquent les six règles de
la référence. Dans les deux conditions, un bruit d'inattention à graine fixe
touche quelques phrases claires, parce qu'un bon guide n'empêche pas les
fautes de fatigue.

## Valeurs mesurées

| Condition | n | Accord brut | Kappa |
|---|---|---|---|
| **guide v1 sur round 1** (protocole atelier) | 40 | **77,5 %** | **0,661** |
| **guide v2 sur round 2** (protocole atelier) | 20 | **95,0 %** | **0,924** |
| guide v1 sur round 2 (contrôle) | 20 | 70,0 % | 0,535 |
| guide v2 sur round 1 (contrôle) | 40 | 92,5 % | 0,885 |

**Delta du protocole atelier : +0,264.**

## Lecture

- La hausse tient dans les deux sens de contrôle : sur les mêmes 40 phrases,
  v1 donne 0,661 et v2 donne 0,885 ; sur les mêmes 20 phrases, v1 donne 0,535
  et v2 donne 0,924. L'effet vient du guide, pas du choix des phrases.
- L'accord brut v1 (77,5 %) tombe dans la fourchette annoncée en séquence 4c,
  « souvent 70 à 80 pour cent », avec un Kappa nettement plus bas : le
  contraste qui motive le Kappa est bien au rendez-vous.
- Le round 2 porte la même proportion de cas limites que le round 1 (5 sur 20
  contre 10 sur 40) et des mêmes types : la difficulté est constante, la
  hausse n'est pas un artefact de sélection.

## Si la salle obtient autre chose

Les binômes réels seront plus bruyants que la simulation. Un Kappa v1 entre
0,3 et 0,7 et une hausse au round 2 dans la majorité des groupes suffisent à
la démonstration. Un groupe qui ne monte pas est traité comme prévu en
séquence 4e : vingt items, c'est petit, et c'est exactement pourquoi les jeux
d'évaluation réels en comptent des milliers.
