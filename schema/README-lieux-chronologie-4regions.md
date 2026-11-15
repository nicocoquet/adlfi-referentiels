# Lieux AdlFI — aperçu chronologique de quatre régions (PR de recette)

## Objet

Préparer un **site de recette autonome**, non diffusé dans le GitHub Pages de production, avec :
- sélecteur PACA / Corse / Pays de la Loire / Bourgogne-Franche-Comté ;
- recherche des noms historiques et des codes COG, indépendante de l'année ;
- un seul curseur **1943–2026**, chaque valeur représentant **le 1er janvier** ;
- fonds Leaflet et limites des communes **au seul millésime 2026** ;
- fiches à la date consultée, mouvements Insee, statuts COMA/COMD **uniquement observés en 2026** ;
- les **103 correspondances Pactols–COG de PACA déjà validées**, sans ajouter de lien ailleurs.

## Délimitation scientifique

Le nom d'une commune en 1943 ne prouve ni sa géométrie en 1943 ni son identité avec un concept Pactols. Un préfixe de code INSEE ne prouve pas un rattachement régional historique : il sert seulement à constituer un ensemble de codes à consulter. Le COG actuel sert à identifier les communes de 2026 et les statuts de communes associées/déléguées du même millésime.

Les événements sont **des lignes de mouvements**, non des actes administratifs uniques. Les correspondances non validées des 61 dossiers du registre restent **exclues du navigateur**, comme les 194 recodifications corses en tant qu'alignements individuels AdlFI.

Le curseur ne modifie **jamais la géométrie** : dès que l'année sélectionnée diffère de 2026, les contours 2026 sont masqués. Une option permet de les réafficher explicitement comme **repère actuel**, sans faire croire qu'il s'agit de contours historiques.

Les arrondissements municipaux ne sont pas traités par cette PR (voir PR #23) ; une commune comme Marseille peut ne pas avoir de contour communal autonome dans le jeu contenant ses arrondissements.

## Sources et reproductibilité

- Insee, COG au 1er janvier 2026 : les trois CSV (états actuels, historiques depuis 1943, mouvements), contrôlés par SHA-256 dans scripts/recuperer_cog_2026.py.
- Data.gouv.fr, **Contours administratifs / 2026 / communes-100m.geojson.gz** : contours 2026, généralisation 100 m, licence ODbL. Leur SHA-256 réel est conservé dans le manifeste d'export.
- Pilote PACA déjà publié : docs/data/lieux.json, les 103 alignements datés du 18 octobre 2026.

Aucun XLSX, CSV de décision, candidature non validée, URI suggérée ni journal éditorial n'est joint à la PR.

## Exécution

La CI dédiée acquiert les sources COG officielles, récupère les contours de 2026, génère **quatre paires** de fichiers (COG temporel + GeoJSON 2026) et effectue la recette automatique. Elle archive le résultat sous le nom :

**adlfi-lieux-quatre-regions-chronologie-recette**

Le ZIP de l'artefact contient un répertoire docs/. Depuis ce répertoire :

~~~sh
python3 -m http.server 8000
~~~

Puis ouvrir : http://localhost:8000/lieux/chronologie/

Exemples de vérification : Marchaux 2017/2018 ; Chemilla/Saint-Hymetière-sur-Valouse 2018/2019 ; Verdun-sur-le-Doubs/Verdun-Ciel 2024/2025 ; Champtoceaux et Orée d'Anjou 2024/2026 ; une commune corse avant/après 1976 ; et une correspondance PACA sélectionnée en 2026 puis consultée avant 2026.

## État de publication

**Ne pas fusionner cette PR de recette avant que les quatre paires de données aient été examinées et intégrées dans une PR de publication distincte.** Sinon, la page chronologie de docs/ ferait référence à des fichiers qui ne sont pas encore dans le dépôt.

La PR #24, et ses tables de candidatures, reste séparée. La PR #28 concerne le schéma relationnel de recette et n'est pas nécessaire à l'affichage des faits administratifs officiels.

Avant déploiement Pages :
1. examiner les bilans, empreintes et cardinalités des quatre régions ;
2. vérifier visuellement le rendu Leaflet, la recherche, le curseur et le statut des contours ;
3. décider si les fichiers générés et contrôlés sont aptes à une publication autonome ;
4. créer une PR finale modifiant le module Lieux existant avec des **données publiques approuvées**, sans fusionner en bloc les recettes.
