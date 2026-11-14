# Lieux — Pays de la Loire, graphe provisoire COG historique des 120 lieux imbriqués

**14 novembre 2026 — PR n°24 — recette non validante.**

## Exécution reproductible

[Workflow officiel GitHub Actions : audit du 14 novembre 2026](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43609855164) — **succès**. Les sources sont les trois fichiers Insee COG 2026 dont les empreintes sont contrôlées dans le workflow ; les éléments Pactols sont ceux de l'extraction XML AdlFI nationale v2 et de l'export Frantiq du 22 juillet 2026.

Les scripts ajoutés à la branche sont :
- `scripts/qualifier_comparent_22_pdl.py`, basé sur `docs/lieux/recette/parentages-pdl-22-a-controler.csv` ;
- `scripts/construire_graphe_mouvements_pdl_120.py`, basé sur les quatre CSV de périodes/mouvements déjà vérifiés pour les lots de 22 et 98 codes ;
- les tests `tests/test_qualifier_comparent_22_pdl.py` et `tests/test_construire_graphe_mouvements_pdl_120.py`.

## Vérification définitive de COMPARENT pour les 22 codes partagés (COG 2026)

| Résultat | ARK |
| --- | ---: |
| Code historique partagé entre une `COM` et une `COMD` au COG 2026 ; `COMPARENT` de la `COMD` égal au code commun | **21** |
| Code historique ne portant plus qu'une `COMD` ; `COMPARENT` différent | **1** |
| **Total** | **22** |

Le cas divergent est **Champtoceaux** : `COMD 49069` renvoie par `COMPARENT` à `COM 49126 Orée d'Anjou`. Il n'est donc pas correct de présenter `49069` comme le code de la commune actuelle Orée d'Anjou. Le code `49069` demeure pertinent comme assertion Pactols documentant l'entité déléguée et certains épisodes précédents.

**Ce contrôle ne crée pas automatiquement de relations de succession validées** entre les ARK Pactols ; il prouve seulement la nature des entrées Insee au millésime 2026.

## Structure du graphe provisoire

Le graphe construit par le script comprend quatre familles distinctes, toutes conservées avec leur provenance :

| Objet | Identifiant | Sémantique et limites |
| --- | --- | --- |
| **État observé** | Empreinte stable de `TYPECOM, COM, LIBELLE` | Triplet attesté dans une source ; **pas une identité institutionnelle intemporelle** |
| **Ligne de mouvement** | Empreinte des huit champs `MOD, DATE_EFF, TYPECOM_AV, COM_AV, LIBELLE_AV, TYPECOM_AP, COM_AP, LIBELLE_AP` | Transition avant/après correspondant à une **ligne** du COG |
| **Période de libellé** | Empreinte de `COM, TYPECOM, LIBELLE, DATE_DEBUT, DATE_FIN` | Validité du couple code–libellé ; **pas du contour géographique** |
| **Groupe candidat** | Empreinte des identifiants des lignes connexes d'une même date et d'une même modalité | Construction algorithmique ; **pas nécessairement un acte administratif unique** |

Les champs `codes_suivis` et `sources_recette` conservent le rattachement documentaire des événements. Un même mouvement mentionné par deux codes étudiés n'est exporté qu'une fois, tout en conservant ces deux provenances.

### Mesures sur les 120 codes

| Mesure | Résultat |
| --- | ---: |
| Codes Pactols étudiés | **120** |
| Lignes de mouvements initiales associées aux codes | **461** |
| Répétitions exactes retirées | **65** |
| Lignes de mouvements distinctes | **396** |
| Périodes code–libellé | **167** |
| États distincts observés (`TYPECOM,COM,LIBELLE`) | **417** |
| Groupes connexes candidats (date, modalité et liens entre codes+types) | **77** |
| Alignements Pactols–COG nouvellement validés | **0** |
| Géométries historiques attribuées | **0** |

**Important :** les 77 groupes ne sont pas 77 arrêtés ou 77 événements juridiques indépendants. La méthode regroupe des transitions observées ; elle doit encore être comparée aux textes de création, de fusion et aux éventuelles situations de recomposition multiples sur une même date.

### Livrables

L'artefact du workflow `audit-lieux-pays-de-la-loire-lot25` (son nom historique fait référence au premier audit, mais il contient désormais aussi les lots de 22 et 98 codes) conserve :

- `comparent-22/comparent-22-codes-partages.csv` et son rapport JSON ;
- `graphe-120/graphe-mouvements-pdl-120.json` (états, mouvements, périodes, groupes) ;
- `graphe-120/lignes-mouvements-distinctes.csv` ;
- `graphe-120/groupes-evenements-candidats.csv` ;
- `graphe-120/rapport-graphe-120.json` ;
- les CSV officiels dérivés de chaque lot de 22 et 98 codes, déjà utilisés précédemment.

## Décisions de modélisation proposées à la validation éditoriale

1. **ARK Pactols :** clé primaire d'un concept documentaire, jamais dédoublonné à partir d'un code Insee.
2. **Entité administrative :** représentation distincte d'une observation `TYPECOM/COM/libellé` ; il faudra un identifiant d'épisode administratif explicitement défini lors de l'étape suivante, ne reposant pas sur le code seul.
3. **Événement Insee :** stocker toutes les lignes avant/après et leurs modalités, sans attribuer d'emblée une identité unique à un groupe connexe.
4. **Rattachement administratif :** `COMPARENT` lié à la date de référence du COG ; jamais confondu avec le parent dans la hiérarchie Pactols.
5. **Géométrie :** identifiant du jeu géospatial et millésime obligatoire, sans rétroprojection du contour 2026 sur les communes précédentes.
6. **Publication :** les 103 alignements PACA antérieurement validés restent les seuls acquis du pilote national ; aucune candidature issue de cet audit n'est diffusée comme validation supplémentaire.

## Étape suivante

L'élargissement aux **806 autorités des Pays de la Loire** nécessite d'appliquer un rapprochement COG exhaustif sur `inventaire-pays-de-la-loire.csv` (construit localement depuis les trois sources nationales), et pas seulement sur les 120 codes sélectionnés. Il faut ensuite qualifier les 686 autres autorités : **toutes ne relèvent pas d'un état communal** (les objets supra-communaux ou les URI non numériques sont à traiter séparément). Le même protocole pourra ensuite être décliné sur la Bourgogne-Franche-Comté.

La PR doit rester en brouillon jusqu'à validation du modèle d'identité et de succession par l'éditeur. Aucun fichier public `docs/data/lieux*` n'est modifié.
