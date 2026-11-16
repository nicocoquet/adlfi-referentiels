# Lieux — contrôle de couverture des géométries ultramarines 2026

**16 novembre 2026 · PR #30 · recette seule, aucune publication.**

## Décision d'interface

Le sélecteur public « Échelon territorial » est limité à **Région / Département / Commune** (PR #41). Cette simplification ne supprime aucune entité administrative des données.

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

**Résultats de couverture effective et SHA-256 de l'archive géographique : non encore établis au moment de la rédaction.** Ne pas reprendre les nombres théoriques de candidats pour affirmer qu'ils sont tous dessinables.

## Étapes avant publication cartographique

- Examiner les géométries absentes, invalides ou traversant potentiellement l'antiméridien ; identifier des sources alternatives, notamment pour TAAF, Wallis-et-Futuna, Clipperton et Île des Faisans.
- Vérifier les contours des 212 communes prioritaires au millésime précis, puis les 2 zonages COMER particuliers de Saint-Martin/Saint-Barthélemy.
- Définir la sélection dans la recherche textuelle pour les territoires COMER:TERRITOIRE et les zonages non communaux **sans ajout de quatrième échelon au sélecteur**.
- Introduire les seuls alignements Pactols–COG décidés éditorialement, sans extrapolation temporelle.
- Ne jamais afficher une géométrie 2026 comme celle d'une situation antérieure.

Aucune correction des sources, aucune géométrie publiée, aucun alignement créé par cette tranche.
