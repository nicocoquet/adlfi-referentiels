# Polynésie française — chronologie des 48 communes dans le COG 2026

**17 novembre 2026 — chronologie COG des communes, complétée par 48 correspondances Pactols–COG validées pour le seul état du 1er janvier 2026 ; aucune géométrie historique homologuée.**

## Résultat officiel du COG

La [recette GitHub Actions n°44059455597](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44059455597) a contrôlé les **six tables INSEE originales** par SHA-256, extrait deux fois les épisodes et comparé le rapport JSON.

| Niveau COG | Codes | Épisodes code–libellé | Début de leur épisode COG |
|---|---|---:|---|
| Communes | `98711` à `98758` | **48** | **21 mai 1972**, chacun |
| Territoire | `987` Polynésie française | **1** | **21 mai 1972** |
| Ancien code distinct | `98799` Clipperton | **1** | 21 mai 1972 au **23 février 2007** (fin exclusive) |

Les 48 couples actuels sont déjà recensés dans `lieux-outremer/recherche-2026.json`. Aucune modification de libellé ni fin d'épisode n'est inscrite pour ces codes dans la série `v_commune_outremer_depuis_1943.csv` consultée. Cela ne certifie **pas** l'absence de changement de périmètre, de limites physiques ou de fonctionnement institutionnel.

Le code `98799` ne fait pas partie des communes actuelles. Le [COG historique](https://www.insee.fr/fr/information/7929495) et la loi de 2007 sur le rattachement de Clipperton doivent être mobilisés séparément avant toute cartographie de la période antérieure à 2007.

## Date de codification et existence juridique

La **date COG du 21 mai 1972** correspond à la première attestation des 48 couples code–libellé dans la série retenue, **pas à une création juridique simultanée**. Le [rapport officiel du 4 juin 2026](https://www.legifrance.gouv.fr/jorf/id/JORFARTI000054191111) rappelle que la [loi n° 71-1028 du 24 décembre 1971](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000693681/) et son application ont ajouté **44 communes à quatre communes préexistantes**. Sans instruction individuelle de ces quatre communes, le module ne projette pas rétrospectivement les codes 2026 en 1943–1971.

La frise indique l'**état au 1er janvier** : pour 1972, l'épisode COG de mai n'est pas encore actif ; au 1er janvier 1973, les 48 codes sont documentés.

## Nomenclature fine ISPF à instruire séparément

L'[ISPF](https://www.ispf.pf/ispf/referentiels) et le [Haut-commissariat](https://www.polynesie-francaise.gouv.fr/Actions-de-l-Etat/Accompagnement-des-communes/Presentation) distinguent :

- **98 communes associées** dans **30 communes principales** ;
- **18 communes** sans commune associée, soit **116 entités** dans la nomenclature fine de l'ISPF ;
- **5 subdivisions administratives** et un découpage *subdivision > île* qui ne correspond pas directement au découpage *subdivision > commune > commune associée*.

**Aucun de ces 98 codes associés n'est inventé** à partir des 48 codes COG. La qualification de ces sous-entités requiert le fichier géographique ISPF, les relations de rattachement et les règles d'homonymie propres à la Polynésie. Selon le [Sénat](https://www.senat.fr/rap/r24-017/r24-0178.html), ces communes associées **ne sont pas issues de fusions de communes indépendantes** au sens métropolitain : cette différence doit guider la modélisation historique.

## Publication et garde-fous

Le moteur du module Lieux utilise le fichier `chronologie-cog-2026.json` pour les fiches des **48 communes principales** et celle du territoire `987`. Le document inclut les dates COG et distingue les 98 communes associées et les cinq subdivisions sans prétendre les cartographier. Les contours contemporains ou anciens de ces sous-entités ne sont pas qualifiés ici.

Le script `scripts/verifier_index_public_polynesie_2026.py` reconfronte les 48 épisodes publiés **aux six tables INSEE originales** et vérifie Clipperton. Les tests Python, Node.js et Chromium empêchent une rétroprojection des codes ou une assimilation des associations au COG.

## Validation des correspondances Pactols–COG au millésime 2026

La [PR n°71](https://github.com/nicocoquet/adlfi-referentiels/pull/71) a établi **48 `skos:exactMatch` univoques** entre les 48 communes du COG 2026 et 48 concepts actifs distincts dans le [RDF Frantiq-Lieux du 22 juillet 2026](https://github.com/frantiq/PACTOLS), commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.

La publication des décisions éditoriales est documentée dans [`POLYNESIE-VALIDATIONS-PACTOLS-COG-2026.csv`](../../../recette/lieux/POLYNESIE-VALIDATIONS-PACTOLS-COG-2026.csv) : chaque ligne comprend code et libellé de commune COG, ARK, URI INSEE `geo/commune`, prédicat `skos:exactMatch`, statut non déprécié et `VALIDE_ADLFI_2026`, portée **`2026-01-01`**.

**Le module Lieux publie 176 alignements communaux ultramarins**, dont **48 pour la Polynésie française**. Le concept correspondant au territoire **`987`** (`26678/pcrt4K8nLVxWOP`, URI `collectiviteDOutreMer/987`) est **distinct** et ne figure pas dans ces 48 décisions. Il figure désormais dans le [registre séparé des quatre collectivités d’outre-mer](../../../recette/lieux/COLLECTIVITES-COMER-VALIDATIONS-PACTOLS-COG-2026.csv), validé **pour la collectivité au 1er janvier 2026**, sans modifier le total des 176 alignements communaux. Le code historique **`98799` Clipperton** ne reçoit aucun ARK par cette publication.

L'alignement `98745` Tahaa → `26678/pcrteZcqWgVUaT` est **validé pour les identifiants seulement**. L'anomalie topologique du contour 2026 de Tahaa demeure signalée, sans contour adopté. Les **98 communes associées ISPF** n'ont reçu aucun identifiant de commune principale ni alignement déduit.

**0 contour historique, 0 commune associée créée, 0 succession automatique.** Les 212 communes et 21 autres entités COG de l'index demeurent inchangées.

## Nomenclature ISPF — les 98 communes associées

La [nomenclature officielle `Codes_geographiques_ce46ed21ee.xlsx`](https://www.ispf.pf/content/uploads/Codes_geographiques_ce46ed21ee.xlsx), SHA-256 `d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6`, **consultée le 17 novembre 2026**, apporte une source supplémentaire qui **n'est pas millésimée juridiquement** comme le COG.

Le fichier public [`communes-associees-ispf-2026.json`](communes-associees-ispf-2026.json) contient **98 communes associées distinctes** identifiées par leur code **ISPF à trois positions**, rattachées univoquement à **30 des 48 communes principales COG**. Le fichier contient aussi les **18 unités statistiques des communes non subdivisées** (codes ISPF terminés par `0`), sans créer de nouvelles autorités. La partition ISPF compte ainsi **116 unités**, contre **48 communes principales COG**, plus les cinq subdivisions administratives.

Les **48 libellés de communes parentes** du classeur ont été contrôlés contre le COG 2026 : **aucun écart après normalisation typographique**. Les deux homonymes sont distingués par la source : **`441` Avera (Rurutu) → `98744` Rurutu** et **`501` Avera (Taputapuatea) → `98750` Taputapuatea**.

Une précaution documentaire s'impose : la feuille `Geo` du même classeur contient **179 enregistrements**, dont **98 marqués `isComas`**, **17 `isCom`** et **64 `isIleRattachee`**. L'unité **`190` Gambier**, bien présente dans la feuille administrative des 116 unités, **n'a pas de ligne de base `19000`** dans la feuille géographique ; seules ses **16 îles rattachées `19001` à `19016`** y figurent. La [notice de l'ISPF](https://www.ispf.pf/ispf/referentiels) annonce pour sa part **63 îles rattachées**. **Nous conservons ce décalage comme anomalie de provenance**, sans inventer ni supprimer d'enregistrement et sans déduire de limite cartographique.

Le module Lieux permet la recherche des **98 fiches de communes associées ISPF**, et propose le retour à la commune COG principale. Les 18 unités statistiques non subdivisées sont indiquées sur leurs fiches parentales, **sans être présentées comme communes associées**. La [nomenclature et son contrôle](../../../recette/lieux/POLYNESIE-ASSOCIEES-ISPF-2022-RECETTE.md) demeurent séparés de l'[arrêté sur le recensement 2022](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000046768003/2026-04-17), qui ne suffit pas à établir les dates de création de chaque commune associée.

**Aucun nouvel ARK, aucune nouvelle commune COG, aucun contour, aucune période historique créée ou extrapolée.** Les **176 liens communaux** et **4 liens de collectivités** déjà validés demeurent inchangés.
