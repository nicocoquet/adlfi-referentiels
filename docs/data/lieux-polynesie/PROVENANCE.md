# Polynésie française — chronologie des 48 communes dans le COG 2026

**17 novembre 2026 — édition documentaire des couples code–libellé, sans géométries historiques ni alignements Pactols.**

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

**0 alignement Pactols nouveau, 0 contour historique, 0 commune associée créée, 0 succession automatique**. Les **128 correspondances communales ultramarines déjà validées** et les **212 communes existantes dans l'index public** demeurent inchangées.
