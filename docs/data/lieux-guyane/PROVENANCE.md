# Guyane — historique communal publié sans géométries

**16 novembre 2026 · Extension documentaire de la page Lieux**

Le fichier `chronologie-cog-2026.json` expose **41 épisodes code–libellé de 26 codes historiques de Guyane**, dont les **22 communes actuelles du COG 2026** et les **quatre anciens codes 97351, 97354, 97355, 97359**. Les périodes sont exprimées en dates de **début inclusif et fin exclusive**.

## Chaîne de provenance

1. Source officielle : **Insee COG 2026, `v_commune_depuis_1943.csv`** et `v_mvt_commune_2026.csv`, contrôlés par empreinte dans le script `scripts/auditer_guyane_2026.py`.
2. Reconstruction documentaire : **PR 45**, `scripts/construire_chronologie_guyane.py` ; 41 épisodes, 52 lignes de mouvement, 84 états au 1er janvier, sans polygones. [Exécution de recette 43931916896](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43931916896).
3. Empreinte SHA-256 du fichier `guyane-etats-1943-2026.json` dans l’artefact : `83409c5923f31c80ad265c9b9196646ee5b2afcbcaf82ab0a213c67a3387e2e2`.
4. Projection publique compacte : épisodes uniques, sans 84 répétitions annuelles ; moteurs de lecture et de recherche dans `docs/assets/lieux-guyane-historique.js`, validé par les tests Node et Chromium. Les quatre fusions MOD31 du 27 mars 1969 ont été contrôlées séparément dans la CI de la PR 45.

Les intervalles ne sont pas reconstruits à partir des seuls libellés : leurs dates proviennent des épisodes officiels INSEE. Les codes 97351, 97354, 97355, 97359 possèdent chacun un concept Pactols avec URI INSEE explicitement citée dans l’export daté de juillet 2026, mais **l’équivalence sémantique de ces concepts et d’un successeur contemporain n’est pas approuvée**.

## Interprétation dans l’interface

- Le curseur sélectionne **l’état au 1er janvier**. Un mouvement du 27 mars 1969 ne modifie donc pas la fiche du **1er janvier 1969** ; l’état postérieur apparaît au **1er janvier 1970**.
- Dans une fiche communale **COG 2026** de Guyane, le code et le Pactols approuvé pour 2026 demeurent affichés comme référence contemporaine ; un **encart historique distinct** décrit le nom associé à ce même code à la date sélectionnée.
- Les **quatre anciens codes** sont retrouvables par recherche, y compris sous leurs anciennes dénominations. La fiche rappelle le mouvement de fusion COG 1969 et le **statut non arbitré du concept Pactols historique**. Elle ne redirige pas automatiquement vers un ARK actuel.
- **1943** et le **1er janvier 1946** sont dépourvus d’état actif dans les périodes COG utilisées ; cela signifie **non documenté dans cette source**, nullement inexistence d’une commune.
- **Aucun contour historique** de Guyane n’est introduit. Les seuls contours communaux 2026 cartographiquement publiés restent ceux des quatre régions pilotes ; les références cartographiques contemporaines sont explicitement identifiées comme telles.

## Invariants

Le registre contient **41 épisodes, 26 codes différents, quatre anciens codes**, 22 communes pour l’état COG 2026 et 84 années possibles. Les tests vérifient les changements de libellé de Régina en 1969, de Grand-Santi en 1976, et l’apparition d’Awala-Yalimapo (1989) et de Papaichton (1993), ainsi que les bornes temporelles et l’absence de géométrie.

**Les 22 correspondances Pactols–COG actuelles sont inchangées, les quatre correspondances anciennes restent non validées pour 2026, aucune géométrie historique n’est publiée et aucun nouvel échelon territorial n’est ajouté.**
