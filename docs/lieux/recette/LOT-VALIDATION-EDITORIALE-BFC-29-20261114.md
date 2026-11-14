# Bourgogne-Franche-Comté — lot de validation éditoriale des 29 relations administratives

**14 novembre 2026 — PR n°24 — RECETTE, AUCUNE VALIDATION.**

## Objet et périmètre

Consolider, sans fusion d'ARK ni publication, les **29 relations administratives** préparées par les audits Insee COG 2026 et le contrôle du thésaurus **Pactols-Lieux th17 du 22 juillet 2026**.

| Famille de relation administrative | Dossiers | ARK cible candidat | Sans ARK cible |
| --- | ---: | ---: | ---: |
| Réception d'une ancienne commune (MOD 31, 32 ou 33) | **25** | **24** | **1** |
| Code Insee réutilisé par une commune nouvelle, deux ARK distincts | **2** | **2** | 0 |
| Commune associée COMA rattachée à son COMPARENT actuel | **2** | **2** | 0 |
| **Total** | **29** | **28** | **1** |

Les **28 ARK cibles** sont des propositions documentaires, non des correspondances ni des relations de succession validées. Les deux rattachements `COMA` (Antorpe–Saint-Vit et Frettes–Champlitte) **ne sont pas des successions communales**. Les deux cas de code réutilisé (Marchaux et Sancey) ne justifient aucune fusion des autorités Pactols.

## Priorités de relecture

| Priorité | Dossiers | Instruction |
| --- | ---: | --- |
| **P1** — absence d'ARK cible ou concept sans URI Insee numérique | **4** | **Ciel → Verdun-Ciel** reste sans ARK ; **Cézia, Lavans-sur-Valouse et Saint-Hymetière** pointent vers le concept *Saint-Hymetière-sur-Valouse*, dont le `prefLabel` est concordant mais l'`exactMatch` Insee numérique absent dans le RDF examiné |
| **P2** — qualification de la relation ou homonymie | **5** | Quatre dossiers de rattachement COMA / code réutilisé ; **Mirebel → Hauteroche (Jura)**, à distinguer de l'homonyme Côte-d'Or |
| **P3** — concordance documentaire déjà établie | **20** | Examiner les portées temporelles et géographiques des concepts, puis décider la nature précise de la relation |

Ces priorités ne constituent pas des décisions éditoriales et n'affectent pas le degré de validité juridique des événements Insee.

## Vérification supplémentaire de Verdun-Ciel dans le Pactols vivant

Le **14 novembre 2026**, une [CI dédiée](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43632808104) a interrogé l'API publique Opentheso, thésaurus `th17` :

- `q=Verdun-Ciel&format=json` : HTTP 200, objet JSON vide `{}` ;
- `q=Verdun-Ciel&format=jsonld` : HTTP 200, tableau vide `[]` ;
- `q=Verdun&format=jsonld` : HTTP 200, concepts trouvés, notamment **Verdun-sur-le-Doubs** ;
- `q=71566&format=jsonld` : HTTP 200, tableau vide `[]`.

Cette interrogation **n'a identifié aucun concept sous le nom Verdun-Ciel**, mais une recherche négative par l'API **ne prouve pas une absence absolue dans le thésaurus vivant**. Ne créer aucun ARK ni remplacer Verdun-Ciel par le concept ancien Verdun-sur-le-Doubs.

**Preuve administrative indépendante** : l'Insee atteste la commune nouvelle **Verdun-Ciel (`71566`) au 1er janvier 2025**, réunissant **Ciel (`71131`)** et **Verdun-sur-le-Doubs (`71566`)**. Source : https://www.insee.fr/fr/metadonnees/geographie/commune/71566-verdun-ciel. L'identité documentaire de Pactols reste une question distincte.

Le rapport exact de consultation est dans l'artefact GitHub Actions `verdun-ciel-pactols-vivant-recette`. Le script reproductible (consultation publique, sans écriture) est `scripts/verifier_verdun_ciel_pactols_vivant.py`.

## Tableau de recette autonome fourni dans la conversation

Une archive de travail **`AdlFI_BFC_lot_validation_editoriale_29_relations_20261114.zip`** est livrée dans la conversation. Elle contient, de manière autonome :

- `lot-validation-relations-bfc-29.csv` : les 29 dossiers et leurs colonnes de validation **vides** ;
- `candidatures-cibles-ark-bfc-28.csv` : les 28 propositions de cibles, non validées ;
- `dossier-verdun-ciel-ouvert.csv` : le dossier ouvert ;
- `source-candidatures-29.csv` : source issue de l'audit des mouvements et des ARK du corpus XML ;
- `source-rapprochement-14.csv` : complément issu des 50 691 concepts du Pactols intégral ;
- `controle-verdun-ciel-pactols-vivant-20261114.json` : réponses de la consultation publique contemporaine ;
- `construire_lot_validation_bfc.py` : reconstruction locale déterministe à partir des deux CSV source, vérifiée par deux exécutions identiques ;
- `rapport-validation-bfc-29.json`, `GUIDE-ARBITRAGE-BFC.md`, `MANIFESTE-SHA256.json`.

Les artefacts antérieurs et le code de recherche initial sont versionnés ou archivés dans :
- `QUALIFICATION-RELATIONS-ARK-BFC-20261114.md` (15 cibles initiales et 14 dossiers non résolus) ;
- `RECHERCHE-INTEGRALE-PACTOLS-8-CIBLES-BFC-20261114.md` (13 nouvelles propositions, sept cibles nominales dans le thésaurus complet) ;
- [CI de recherche intégrale](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43632056202) et [CI de vérification de l'API vivante](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43632808104).

## Arbitrages éditoriaux à conduire

1. Vérifier si l'objet documentaire de chaque ARK décrit une **ancienne commune, une commune nouvelle, une commune déléguée, un lieu habité ou un toponyme indépendant**.
2. Pour les fusions, modéliser les **événements administratifs datés** et les participations, sans déclarer l'ancienne et la nouvelle commune `skos:exactMatch`.
3. Pour les communes associées, enregistrer un **rattachement administratif daté**, non une succession, et conserver le code historique de l'associée.
4. Pour les trois dossiers Saint-Hymetière-sur-Valouse, proposer une vérification de l'assertion Insee du concept existant **sans la modifier automatiquement**.
5. Pour Verdun-Ciel, faire une vérification humaine dans l'interface Pactols ou demander à Frantiq si un concept distinct doit être ajouté ; ne pas inventer d'ARK.
6. Ne renseigner les colonnes de décision qu'après examen éditorial explicite ; conserver auteur, date, source et justification de chaque arbitrage.

**PR n°24 maintenue en brouillon. Zéro relation éditoriale approuvée et zéro géométrie historique attribuée.**
