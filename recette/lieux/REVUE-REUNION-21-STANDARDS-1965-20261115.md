# Lieux AdlFI — revue des 21 communes standards et de l'événement Saint-Louis/Cilaos

**15 novembre 2026 — recette non publiée — annexe à la PR #30.**

## Bilan

| Catégorie | Cibles | Nombre | Avis documentaire |
|---|---|---:|---|
| Standard | Tous les codes sauf 97407, 97414, 97424 | **21** | Favorable à une validation individuelle au millésime COG 2026 |
| Division | Saint-Louis 97414 et Cilaos 97424 | **2** | Favorable pour 2026 seulement, événement de 1965 explicitement documenté |
| ARK confirmé par l'éditeur | Le Port 97407 | **1** | Choix du concept fixé, lien communal restant à approuver |
| **Total** | | **24** | **Zéro nouvelle validation éditoriale** |

Le tableau exhaustif, avec les 24 couples ARK Pactols / code COG, figure dans **recette/lieux/REVUE-REUNION-24-COG2026-20261115.csv**.

## Contrôle des 21 candidats standards

Les données inspectées sont les sources officielles Insee du COG 2026 :
- v_commune_2026.csv : exactement 24 communes TYPECOM=COM dans le département 974.
- v_commune_depuis_1943.csv : 24 périodes code–libellé TYPECOM=COM ; 23 commencent le 21 mars 1946, une (Cilaos) commence le 5 février 1965.
- v_mvt_commune_2026.csv : **25 lignes** associées au département 974, dont **23 lignes d'entrée dans la série** au 21 mars 1946 (code antérieur vide) et **2 lignes liées à la division du 5 février 1965**.
- Pactols-Lieux th17 2026-07-22 : chacun des 24 codes possède un ARK candidat distinct avec URI INSEE de même valeur et concept non déprécié ; 12 libellés français sont identiques au COG et 12 sont qualifiés « (La Réunion) ».

**Pour les 21 codes standards, aucun mouvement postérieur au 21 mars 1946 n'est signalé dans le COG 2026 examiné.** Cette conclusion ne permet pas d'attester que les limites ont été géométriquement identiques depuis 1946.

**Il serait erroné d'interpréter les 23 lignes de 1946 comme 23 créations juridiques de communes.** Elles marquent ici l'entrée des codes dans la série COG documentée.

## Événement de 1965 : deux lignes, une seule division

Le **5 février 1965**, deux mouvements MOD=20 décrivent une division unique :

| Avant | Après | Interprétation |
|---|---|---|
| 97414 Saint-Louis | 97414 Saint-Louis | Code et nom conservés, emprise réduite |
| 97414 Saint-Louis | 97424 Cilaos | Nouvelle commune issue du territoire ancien |

Les fiches Insee actuelles indiquent le 5 février 1965 comme date de création de **Saint-Louis dans sa configuration actuelle** et de **Cilaos** :
- https://www.insee.fr/fr/metadonnees/geographie/commune/97414-saint-louis
- https://www.insee.fr/fr/metadonnees/geographie/commune/97424-cilaos

**Proposition :** correspondance documentaire possible au millésime 2026 pour chacun, mais aucun alignement concept–géométrie historique automatique et aucune assimilation du périmètre actuel de Saint-Louis à l'état 1946–1965.

## Le Port : dossier séparé

Le concept Pactols **26678/pcrtIKvRT9vwUl**, Le Port (La Réunion), avec l'URI INSEE 97407, a été confirmé explicitement par l'éditeur. Les concepts « Port » et « Le Port (Ariège) » sont exclus pour cette cible. La validation du **lien communal** de 2026 reste une décision distincte de celle sur l'identifiant.

## Décisions et limites

Les **21 avis standards** et les **deux avis historiques** sont des recommandations, pas une homologation. Les colonnes decision_editoriale du registre originel restent **A_INSTRUIRE** pour ces 23 communes. Le Port reste **ARK_CONFIRME_CORRESPONDANCE_A_VALIDER**. La revue ne publie aucun nouvel ARK, aucun skos:exactMatch, aucune géométrie ancienne, ni aucun fichier dans docs/.

La date de début d'un couple code–libellé COG ne doit jamais être interprétée automatiquement comme date de création juridique ou date d'entrée en vigueur d'une géométrie précise.

## Sources et empreintes SHA-256

Source COG : https://www.insee.fr/fr/information/8740222

- v_commune_2026.csv : 7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3
- v_commune_depuis_1943.csv : 08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee
- v_mvt_commune_2026.csv : 8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1
- Pactols_Lieux_th17_20260722.rdf : 3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7

La revue conclut à **21 candidats standards solides pour 2026**, **2 candidats historiques solides pour 2026 avec précaution temporelle** et **1 ARK Le Port confirmé**. **Aucune nouvelle correspondance publiée ou validée pendant cette revue.**
