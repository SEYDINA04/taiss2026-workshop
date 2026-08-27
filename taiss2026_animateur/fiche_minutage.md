# Fiche de minutage — atelier TAISS 2026

Jeudi 27 août, 13h30–15h30, salle F1. Une page, à imprimer.

| # | Séquence | Début | Fin | Durée |
|---|---|---|---|---|
| 1 | The Pipeline | 13h30 | 13h40 | 10 min |
| 2 | Data Inspection | 13h40 | 13h53 | 13 min |
| 3 | Quality Gates | 13h53 | 14h05 | 12 min |
| 4 | Measuring Label Reliability | 14h05 | 14h50 | 45 min |
| 5 | AI Pre-Annotation and Human-in-the-Loop | 14h50 | 15h05 | 15 min |
| 6 | Packaging and Documentation | 15h05 | 15h20 | 15 min |
| 7 | At Scale, and Q&A | 15h20 | 15h30 | 10 min |

## Points de compression en cas de retard

- Séquence 6 compressible à 8 minutes : montrer la fusion et les splits,
  laisser la carte se finir hors séance.
- Séquence 3 compressible à 10 minutes : fournir une quatrième fonction au
  tableau (`check_channels`, la plus courte) et ne faire écrire que les trois
  restantes.
- **Ne jamais rogner sur la séquence 4.** C'est elle qui justifie l'atelier.

## Détail de la séquence 4 (45 min)

| Étape | Durée | Contenu |
|---|---|---|
| 4a | 5 min | tâche, guide v1 lu à voix haute, aucune question sur les cas limites |
| 4b | 13 min | round 1, 40 phrases, annotation en aveugle, saisie Sheet |
| 4c | 9 min | mesures, Kappa au tableau, chaque groupe dans sa colonne, sans mise en regard |
| 4d | 12 min | lecture des désaccords, réécriture collective, guide v2 |
| 4e | 6 min | round 2, 20 phrases, recalcul, comparaison v1/v2 dans chaque groupe |

## Les trois formulations sensibles, mot pour mot

**Réponse à la question d'ouverture** (« Laquelle de ces étapes, si elle
échoue, ne se voit pas ? »), après avoir laissé la salle proposer :

> Un défaut de collecte se voit. Il manque des locuteurs, des accents, des
> registres, et cela se constate en regardant la distribution.
>
> Un défaut de nettoyage se voit et se corrige. On relance le script sur les
> données brutes.
>
> Un défaut d'annotation ne se voit nulle part. Une fois que les labels sont
> traités comme vérité de référence, tout ce qu'on mesure contre eux hérite de
> leurs erreurs, et aucune étape ultérieure ne les révèle. Le modèle affichera
> un F1 excellent contre des labels faux.

Puis : « Toutes ces étapes comptent. Une seule échoue en silence. »

**Réponse à l'objection sur la subjectivité** (séquence 4a) :

> Le sentiment est effectivement subjectif. C'est exactement pourquoi il faut
> un guide. Un guide ne supprime pas la subjectivité, il la rend
> reproductible. Deux annotateurs qui appliquent la même règle explicite
> convergent, même sur une tâche subjective. C'est ce que le Kappa mesure.

**Commentaire conditionnel sur l'écart entre langues** (séquence 4d) — à ne
prononcer QUE si les nombres du tableau le soutiennent, et sous cette seule
formulation :

> Le guide v1 en éwé est une traduction littérale du guide français. S'il
> produit un accord plus faible, cela ne dit rien sur la langue. Cela dit
> qu'un guide d'annotation doit être construit dans la langue, pas traduit
> vers elle.

## Rappels de conduite

- Aucune comparaison affichée entre le Kappa français et le Kappa éwé : chaque
  groupe suit son propre v1 contre v2.
- Un Kappa qui ne monte pas au round 2 : leçon de taille d'échantillon, voir
  la formulation de la séquence 4e du plan, jamais un échec.
- Si un participant conteste le protocole à deux annotateurs : assumer, c'est
  un protocole simplifié pour deux heures ; en production, trois annotateurs
  et un arbitre, c'est dit en séquence 7.
- Citation wolof, séquence 5, formulation exacte : 90 % de F1 macro pour les
  annotateurs natifs contre 45 % pour le meilleur modèle testé en zéro-shot,
  sur cette tâche et ce corpus, et cela ne dit pas qu'un modèle est incapable
  de traiter le wolof.
