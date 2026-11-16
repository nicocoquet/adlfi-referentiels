# Lieux — contrôle de couverture des géométries ultramarines 2026

**16 novembre 2026 · PR #30 · recette seule, aucune publication.**

## Décision d'interface

Le sélecteur public « Échelon territorial » est limité à **Région / Département / Commune** (PR #41, fusionnée le 16 novembre 2026). Cette simplification ne supprime aucune entité administrative des données.

Les collectivités et subdivisions ultramarines restent indexées sous leurs types d'origine ; la présence d'un objet COG dans le fichier géographique « communes » ne permet pas à elle seule de lui attribuer le statut de commune de droit commun.

## Données et provenance

- **États administratifs au 1er janvier 2026 :** [Insee, COG 2026](https://www.insee.fr/fr/information/8740222), fichiers v_commune_2026.csv, v_commune_comer_2026.csv, v_comer_2026.csv.
- **Contours datés du 4 mai 2026 :** [data.gouv.fr, Contours administratifs](https://www.data.gouv.fr/datasets/contours-administratifs), fichier communes-100m.geojson.gz (GeoJSON WGS84, généralisation 100 m, licence ODbL).
- La provenance des contours est **mixte** : produits IGN, OSM pour des COM, données géographiques spécifiques à la Polynésie française et à la Nouvelle-Calédonie. Il est inexact d'étiqueter tous les contours comme « IGN ».

L'audit compare **233 identités typées** : 129 DROM:COM, 85 COMER:COM, 5 COMER:DIS, 3 COMER:CIR, 1 COMER:CPT, 1 COMER:CDM et 9 COMER:TERRITOIRE.

Les **212 communes** constituant le lot éditorial prioritaire sont un sous-ensemble : 129 DROM, 48 Polynésie française, 33 Nouvelle-Calédonie et 2 Saint-Pierre-et-Miquelon. Les zonages COM de Saint-Martin et Saint-Barthélemy sont volontairement instruits à part ; ils ne sont pas ajoutés artificiellement aux 212.

## Contrôle mis en place

Le script scripts/auditer_contours_outremer_2026.py croise les identifiants exacts des tables 2026 avec la couche « communes » ; il ne rapproche aucun ARK Pactols. Pour chaque entité :

1. présence ou absence du code dans la source cartographique ;
2. doublons de codes éventuels ;
3. type géométrique Polygon / MultiPolygon et validité topologique Shapely, **sans réparation automatique** ;
4. emprise longitudinale supérieure à 180° comme **alerte de contrôle**, non comme erreur certaine, pour l'antiméridien ;
5. nature de zonage COG et territoire de rattachement, sans attribuer un statut de commune à DIS, CIR, CPT ou CDM.

Les 9 collectivités COMER:TERRITOIRE sont **non évaluées** dans cette couche de communes : même si toutes leurs subdivisions avaient une géométrie, leur union ne serait pas une frontière institutionnelle officiellement attestée.

La comparaison aboutit aux statuts descriptifs PRESENTE_VALIDE_A_QUALIFIER, PRESENTE_INVALIDE, ABSENTE_DU_FICHIER_COMMUNES, DOUBLON_CODE_DANS_SOURCE ou NON_EVALUE_TERRITOIRE_SANS_COUCHE_DEDIEE. Le premier signifie seulement que le polygone lu est structurellement et topologiquement utilisable ; **il ne valide ni son identité juridique, ni sa source locale, ni ses limites historiques**.

## Reproduction

CI : .github/workflows/audit-lieux-contours-outremer-2026.yml.

1. Télécharger les deux sources officielles ; contrôler SHA-256, dont les empreintes COG déjà établies en PR #30.
2. Exécuter les tests synthétiques, avec Shapely.
3. Générer deux fois, de manière strictement identique, controle_233_cibles.csv et rapport_couverture_2026.json dans un dossier temporaire.
4. Conserver un artefact **de recette** dans GitHub Actions pendant 30 jours ; aucune image vectorielle source et aucun CSV candidat ne sont ajoutés sous docs/.

## Résultats constatés — CI réussie du 16 novembre 2026

[Audit spécialisé n°43894284872](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43894284872) : tests synthétiques, acquisition des sources, contrôle des 233 cibles, double génération identique et artefact de recette réussis.

| Nature COG | Entités | Présentes et topologiquement valides | Invalides | Absentes | Non évaluées comme territoire |
|---|---:|---:|---:|---:|---:|
| DROM:COM | 129 | 129 | 0 | 0 | 0 |
| COMER:COM | 85 | 83 | **2** | 0 | 0 |
| COMER:DIS (TAAF) | 5 | 5 | 0 | 0 | 0 |
| COMER:CIR (Wallis-et-Futuna) | 3 | 3 | 0 | 0 | 0 |
| COMER:CPT (Clipperton) | 1 | 1 | 0 | 0 | 0 |
| COMER:CDM (Île des Faisans) | 1 | 0 | 0 | **1** | 0 |
| COMER:TERRITOIRE | 9 | 0 | 0 | 0 | **9** |
| **Total** | **233** | **221** | **2** | **1** | **9** |

**Cas à instruire individuellement :**

- **Tahaa**, code COMER:COM:98745 (Polynésie française) : MultiPolygon présent, mais topologiquement invalide dans la source 2026.
- **Dumbéa**, code COMER:COM:98805 (Nouvelle-Calédonie) : MultiPolygon présent, mais topologiquement invalide dans la source 2026.
- **Île des Faisans**, code COMER:CDM:98101 : pas de Feature correspondante dans le GeoJSON de communes. L'absence n'est pas une preuve d'inexistence de géométrie dans une autre source.

**Empreintes SHA-256 contrôlées :**

- communes-100m.geojson.gz : 4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778
- v_commune_2026.csv : 7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3
- v_commune_comer_2026.csv : 9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8
- v_comer_2026.csv : d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed

## Diagnostic ciblé des deux multipolygones invalides

[Exécution spécialisée n°43895384451](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43895384451), réussie sur l'extension du diagnostic.

| Code | Motif Shapely dans la source | Type après make_valid sur copie | Écart de surface planaire |
|---|---|---|---:|
| 98745 — Tahaa | Self-intersection[-151.447423287671 -16.5649232876712] | MultiPolygon | 0,001741883 % |
| 98805 — Dumbéa | Self-intersection[166.4384 -22.1726] | MultiPolygon | 0,0 % à la précision affichée |

L'écart est un **ratio de surfaces planaires en coordonnées géographiques**, non une mesure géodésique. Un écart faible ne suffit pas à approuver un contour ou son appartenance territoriale. Aucune sortie réparée n'a été introduite dans les fichiers géographiques publiés.

Une vérification explicite de la validité des multipolygones issus de make_valid est désormais testée ; cette opération reste **strictement diagnostique et non publiable**.

## Étapes avant publication cartographique

- Examiner les géométries absentes, invalides ou traversant potentiellement l'antiméridien ; identifier des sources alternatives, notamment pour TAAF, Wallis-et-Futuna, Clipperton et Île des Faisans.
- Vérifier les contours des 212 communes prioritaires au millésime précis, puis les 2 zonages COMER particuliers de Saint-Martin/Saint-Barthélemy.
- Définir la sélection dans la recherche textuelle pour les territoires COMER:TERRITOIRE et les zonages non communaux **sans ajout de quatrième échelon au sélecteur**.
- Introduire les seuls alignements Pactols–COG décidés éditorialement, sans extrapolation temporelle.
- Ne jamais afficher une géométrie 2026 comme celle d'une situation antérieure.

Aucune correction des sources, aucune géométrie publiée, aucun alignement créé par cette tranche.
