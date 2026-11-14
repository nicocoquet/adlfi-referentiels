# Pays de la Loire — vérification des 120 parentages et instruction des sept cas atypiques

**14 novembre 2026 — PR n°24 — recette non validante.**

Ce contrôle fait suite à :
- `AUDIT-HIERARCHIES-PAYS-DE-LA-LOIRE-120-20261114.md` ;
- `BILAN-22-CODES-PAYS-DE-LA-LOIRE-COG-20261114.md` ;
- `BILAN-120-LIEUX-IMBRIQUES-PDL-COG-20261114.md`.

La méthode compare les **parents présents dans les chaînes XML Pactols** avec le champ **`COMPARENT` des communes déléguées et associées du COG 2026**. Le contrôle des `skos:exactMatch` Pactols porte seulement sur les **9 928 ARK terminaux attestés dans les XML nationaux** ; un parent qui n'en fait pas partie peut néanmoins être une autorité valide du thésaurus Frantiq.

## Contrôle des 120 enfants

| Catégorie de recette | ARK | Sens exact |
| --- | ---: | --- |
| Concordance numérique du code du parent Pactols avec `COMPARENT` 2026 | **67** | Cohérence des assertions à ce millésime ; aucune équivalence historique validée |
| Parent absent des 9 928 **concepts terminaux** du contrôle SKOS | **21** | Code du parent non vérifiable dans le périmètre d'extraction, pas absence dans Pactols |
| Décalage entre l'assertion du code parent Pactols et le `COMPARENT` 2026 | **3** | Épisodes administratifs intermédiaires à documenter |
| Aucun `COMPARENT` en 2026 (codes sortis du fichier ou désormais `COM` seuls) | **7** | Instruction par les mouvements avant/après |
| Code partagé avec le parent Pactols, traité dans le lot des 22 collisions | **22** | L'extraction du lot 22 ne fournit pas le `COMPARENT` brut ; contrôle direct complémentaire requis |
| **Total** | **120** | |

Les 120 ARK sont uniques. Les catégories sont disjointes et complètes. Aucun `COMPARENT` n'a été extrapolé pour les 22 collisions.

### Les trois écarts temporels

| ARK enfant / libellé | Code enfant | Parent Pactols | Code parent déclaré par Pactols | `COMPARENT` 2026 |
| --- | --- | --- | --- | --- |
| Bouzillé | `49040` | Orée d'Anjou | `49069` | **`49126`** |
| Brissarthe | `49051` | Les Hauts d'Anjou | `49065` | **`49080`** |
| Marigné | `49189` | Les Hauts d'Anjou | `49065` | **`49080`** |

La divergence s'explique par un changement administratif documenté, mais **n'autorise pas à réécrire l'assertion `exactMatch` de Frantiq**, qui correspond à un état antérieur. Le dossier Insee d'Orée d'Anjou documente le passage à **49126** à compter de **2025**. Celui des Hauts-d'Anjou documente la création de la commune actuelle **49080** au **1er janvier 2019** en lieu et place de la précédente commune **49065** et de Châteauneuf-sur-Sarthe.

- Insee Orée d'Anjou : https://www.insee.fr/fr/statistiques/2011101?geo=COM-49126
- Insee Les Hauts-d'Anjou : https://www.insee.fr/fr/statistiques/2011101?geo=COM-49080
- Référentiel des modalités `MOD` : https://www.insee.fr/fr/information/8377252
- Dictionnaire du COG 2026 (`COMPARENT`) : https://www.insee.fr/fr/information/8740222

## Sept cas atypiques : transitions confirmées par le fichier des mouvements

| Concept Pactols | Transitions observées |
| --- | --- |
| **Trèves-Cunault (`49357`)** | `COM → COMA` au **1974-01-01** (`MOD=33`), puis `COMA → COM 49149 Gennes-Val de Loire` au **2016-01-01** (`MOD=32`) |
| **Bazouges (`53024`)** | `COM → COMA` au **1990-01-01** (`MOD=33`), puis `COMA → COM 53062 Château-Gontier` au **2006-05-01** (`MOD=34`) |
| **Saint-Mars-sous-Ballon (`72301`)** | `COM → COMD` au **2016-01-01** (`MOD=32`), puis suppression de `COMD` le **2020-05-28** (`MOD=35`) |
| **Tuffé (`72363`)** | `COM → COMD` au **2016-01-01** (`MOD=32`), puis suppression de `COMD` le **2021-12-31** (`MOD=35`) ; `COM 72363 Tuffé Val de la Chéronne` persiste |
| **La Chapelle-Achard (`85052`)** | `COM → COMD` au **2017-01-01** (`MOD=32`), puis suppression de `COMD` au **2024-01-01** (`MOD=35`) |
| **Doix (`85080`)** | `COM → COMD` au **2016-01-01** (`MOD=32`), puis suppression de `COMD` au **2026-01-01** (`MOD=35`) ; `COM 85080 Doix lès Fontaines` persiste |
| **Fontaines (`85091`)** | `COM → COMD` au **2016-01-01** (`MOD=32`), puis suppression de `COMD` au **2026-01-01** (`MOD=35`) |

Le fichier de recette conserve **25 lignes de transitions avant/après rattachées aux sept codes**. Certaines opérations produisent plusieurs lignes et sont représentées sous plusieurs codes ; ne pas assimiler 25 lignes à 25 opérations indépendantes.

La suppression d'une commune déléguée est celle d'un **statut administratif**, pas la disparition du toponyme ni de l'ARK documentaire.

## Reproductibilité et limites

Script versionné : `scripts/auditer_parentages_pdl_120.py`. Il exploite :

1. `imbriques-120-contextes.csv` (hiérarchies Pactols extraites des XML nationaux) ;
2. `controle_concepts_pactols.csv` (audit SKOS Frantiq du 22 juillet 2026) ;
3. `synthese-codes-98.csv`, `evenements-codes-98.csv` et `periodes-codes-98.csv` (artefacts de la CI COG 2026).

Les **cinq empreintes SHA-256 des fichiers d'entrée sont exigées**, les 120 ARK et les cinq catégories sont vérifiés, et les résultats sont reproductibles octet pour octet. Les tableaux de sortie (`parentages-pdl-120.csv`, `sept-cas-atypiques.csv`, `transitions-sept-cas.csv`, `rapport-parentages-120.json`) restent en recette et sont fournis dans l'archive associée.

### Réserve de méthode

- `COMPARENT` documente un rattachement administratif **au 1er janvier 2026**, pas un lien historique intemporel.
- La table `v_commune_depuis_1943.csv` documente des couples code–libellé, **pas les contours historiques**.
- Les **22 enfants partageant le code du parent** doivent encore être confrontés à la colonne `COMPARENT` brute du COG 2026.
- Les **21 parents hors corpus terminal** doivent être vérifiés dans le thésaurus Pactols complet, sans inventer de nouvel ARK.
- Aucun résultat ne crée automatiquement de `skos:exactMatch`, de succession historique validée ni de géométrie attribuée.

**Aucune donnée du référentiel public n'a été modifiée.**
