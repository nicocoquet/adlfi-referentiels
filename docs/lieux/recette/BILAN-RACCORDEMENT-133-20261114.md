# Lieux — Recette nationale : 42 exceptions SKOS et 133 contours COG 2026

**Date : 14 novembre 2026 — État : recette non validante, PR n°24 en brouillon.**

## 1. Contrôle des autorités Pactols

Le contrôle national indépendant de l'extraction XML AdlFI contre l'export
officiel Frantiq `Pactols_Lieux_th17_20260722.rdf`, SHA-256
`3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`,
a retrouvé **9 928 ARK sur 9 928**.

Le programme `scripts/qualifier_exceptions_skos_lieux.py` a qualifié les
**42 cas hors concordance de `prefLabel`** :
26 formes documentaires abrégées de géographie physique,
9 variantes `altLabel` attestées,
6 différences historiques ou typologiques,
et 1 concept déprécié (Oisans Massif).
Une alerte particulière demeure : `08140` comme `altLabel` numérique
du concept Bazeilles — à vérifier auprès de Frantiq ; aucune transformation
automatique en code INSEE.

**Pièces :**
- `docs/lieux/recette/qualifications-skos-exceptions-42.csv`
- `docs/lieux/recette/rapport-qualifications-skos-42.json`
- `docs/lieux/recette/QUALIFICATION-42-SKOS-ET-GEOMETRIES-2026.md`

Le workflow Pactols Lieux a été enrichi pour produire ces mêmes résultats
depuis **l'export RDF complet réellement téléchargé** :
https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43590529851

## 2. Audit des 30 candidatures des sous-lots 01 à 03

Les 30 couples ARK–COG proposés, **non validés**, ont été contrôlés contre
`communes-100m.geojson.gz` du jeu officiel **Contours administratifs 2026**
de data.gouv.fr. Résultat de l'exécution :
- **30 codes COG distincts présents** ;
- **30 libellés de contour concordants** ;
- **0** code manquant, **0** conflit de code entre ces 30 candidatures.

Empreinte SHA-256 du fichier géographique source :
`4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778`.

## 3. Réconciliation contrôlée avec le pilote existant de Lieux

Le script `scripts/assembler_recette_lieux_133.py` a également été exécuté
sur **la même source géographique 2026 à 100 m** avec les 103 correspondances
PACA du pilote (déjà validées le 18 octobre 2026) et les 30 candidatures
nationales non validées :

| Indicateur | Résultat |
| --- | ---: |
| Correspondances PACA déjà validées, inchangées | **103** |
| Nouvelles candidatures, non validées | **30** |
| Codes et contours 2026 distincts, présents | **133** |
| Collisions de code ou d'ARK | **0** |
| Codes géographiques sans contour source | **0** |

L'audit est **réel et réussi** :
https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43590529927

L'artefact GitHub Actions contient :
- `carte-lieux-recette-133-communes-2026-100m.geojson` :
  133 géométries contemporaines homogènes et statut documentaire par fiche ;
- `liens-cog-geometries-recette-133.json` :
  provenance et statut des 103 validations / 30 propositions ;
- `rapport-carte-lieux-recette-133.json` :
  effectifs, contrôles et empreintes des entrées ;
- les trois livrables initiaux des 30 candidatures géométriques.

### Cohérence avec les travaux sur les arrondissements municipaux

Le GeoJSON des **45 arrondissements** de la PR n°23 porte la **même empreinte
source `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778`** :
les deux chantiers utilisent le même produit cartographique **2026 / 100 m**,
et non deux fonds de provenance indéterminée.

Le **pilote Lieux actuellement exposé** est toujours généré à partir
du fichier amont de l'atlas nommé `communes-1000m.geojson`. Toutefois,
l'audit topologique complémentaire du 14 novembre 2026 démontre que
**les 103 polygones déjà exposés sont topologiquement identiques**
à ceux de la source nationale 2026 à 100 m : **103/103 équivalents,
différence symétrique maximale = 0 m², distance de Hausdorff maximale = 0 m**
(après reprojection Lambert-93). Voir
[`INSTRUCTION-TOPOLOGIE-133-ET-EPISODES-20261114.md`](INSTRUCTION-TOPOLOGIE-133-ET-EPISODES-20261114.md).

**Conséquence : aucune migration de ces 103 géométries n'est requise
pour le raccordement au fonds 2026 à 100 m.** Le nom de fichier
`1000m` n'est pas une preuve de la généralisation effectivement
présente ; les étapes de production dans l'atlas restent à éclaircir
pour documenter correctement la provenance. Les données publiques
du pilote ne sont pas modifiées.

**Important :** l'identité de source et de généralisation favorise une
cartographie sans rupture de résolution ; elle **ne constitue pas à elle
seule un audit topologique** de toutes les frontières adjacentes.
La validité/continuité de cette couche complète devra être mesurée
et contrôlée avant intégration publique.

## 4. Contrat de non-anachronisme et d'identité

1. **Concept Pactols** : ARK, `prefLabel`, variantes et attestations XML.
2. **Relation éditoriale Pactols–COG** : une décision vérifiable distincte
   de la seule concordance lexicale ou départementale.
3. **Épisode administratif historique** : `TYPECOM`, code `COM`,
   intervalle code–libellé et événements de succession. Un code stable
   n'implique pas une emprise stable (Bazeilles, Aigondigné, etc.).
4. **Géométrie** : producteur, millésime, résolution, empreinte et
   licence ; en l'absence de preuve, **les contours 2026 ne représentent
   pas les limites des communes anciennes**.

## 5. Étapes restant à instruire avant publication

- Recette topologique sur les 133 contours et les arrondissements
  concernés, en comparant leurs bordures sans mélange de généralisation.
- Qualification historique des six concepts SKOS non physiques et du
  concept déprécié ; confronter aux épisodes COG et statuts COM/COMD.
- Révision des autres sous-lots éditoriaux, puis décision explicite
  sur les couples Pactols–COG (sans déduction de `skos:exactMatch`).
- Si la carte doit intégrer de nouvelles communes : conserver le
  même jeu source 2026 à 100 m et les propriétés de provenance.
  Les **103 géométries existantes sont déjà identiques** ; ajouter les
  nouveaux contours après validation, sans migration géométrique inutile
  ni modification des validations existantes.

**Publication :** 0 nouveau couple validé dans ce chantier.
`docs/data/lieux.json`, `docs/data/lieux-communes.geojson`,
`docs/lieux/index.html` restent inchangés.

**CI :** les deux workflows spécialisés réussissent. La CI générale
du dépôt reste en échec sur `assets/organismes/ORG-0023-logo.svg`
(média Organismes manquant), sans rapport avec le nouveau chantier Lieux.
