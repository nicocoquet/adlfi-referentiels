# Polynésie française — préinstruction des 98 communes associées

**17 novembre 2026 — contrôle de nomenclature avant mise en production du nouvel échelon.**

## Deux niveaux non interchangeables

La [nomenclature officielle ISPF](https://www.ispf.pf/ispf/referentiels) distingue les **48 communes** COG, les **98 communes associées** regroupées dans **30 communes**, les **18 communes sans association** et **cinq subdivisions administratives**. La nomenclature statistique fine compte **116 unités**, car les 18 communes non subdivisées sont repérées par leur propre code communal à deux positions suivi de `0`. Ce code ISPF à trois chiffres n’est **pas** une commune COG à cinq chiffres.

La documentation ISPF souligne que le code géographique `CODGEO` comporte les **trois positions de la commune associée ou de l’unité non subdivisée**, suivies d’un **code île rattachée à deux positions**. **On ne doit pas inventer un identifiant INSEE** par concaténation.

Un piège d’homonymie est explicitement recensé par l'ISPF : `Avera` apparaît à `441` (Rurutu) et `501` (Taputapuatea). Ces deux entités doivent être préservées distinctement.

La loi française publie un inventaire auxiliaire : le [décret n° 2022-1592 du 20 décembre 2022](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000046768003/2026-04-17), **annexe tableau II**, donne les codes à trois chiffres et les communes de rattachement avec le recensement 2022. Ce texte authentifie des populations et la nomenclature utilisée au recensement ; **il ne date pas l’apparition juridique de chaque commune associée**.

## Contrôles de source

Le [fichier `Codes_geographiques_ce46ed21ee.xlsx`](https://www.ispf.pf/content/uploads/Codes_geographiques_ce46ed21ee.xlsx), distribué par l’ISPF, contient la nomenclature institutionnelle. Le premier workflow d'inspection relève **SHA-256, feuilles, colonnes et structure réelle** de ce fichier ; ensuite l’extraction sera écrite sur ses colonnes effectivement présentes, et non sur une structure supposée.

### Écart interne de la feuille géographique « Geo »

L'inspection a confirmé les cinq feuilles **Geo (179 lignes), Subdivision (5), Commune (48), Commune associée (116) et Ile (119)**. La feuille « Commune associée » est la **source d'autorité administrative** ; la feuille « Geo » concerne le découpage des îles rattachées et ne la remplace pas.

Une particularité contrôlée concerne la commune **Gambier** : l'unité non subdivisée **`190`** figure bien dans la feuille administrative, mais la feuille « Geo » ne comporte **aucune ligne de base `19000`** ; elle y présente seulement **16 enregistrements `19001` à `19016`** signalés « île rattachée ». Ainsi la feuille Geo contient **98 lignes de communes associées, 17 lignes de communes non subdivisées et 64 lignes d'îles rattachées**, quand la notice ISPF annonce **63 îles rattachées**. Cette différence descriptive est **consignée explicitement**, sans retirer Gambier des 18 unités non subdivisées, sans reclassifier une ligne `Geo` et sans fabriquer de contours.

Les deux « Avera » y conservent leurs **libellés exacts du classeur, qualificatifs de contexte compris**, leurs codes `441` et `501` et deux parents différents. L'égalité des noms n'est jamais employée comme clé de rattachement.

Pour la publication, les vérifications prévues sont : **98 unités véritablement associées**, **30 communes parentes distinctes**, **18 codes de communes non subdivisées**, **116 unités ISPF au total** et **48 parents COG** déjà publiés. L’officialité des codes et des rattachements doit être établie avant d’ajouter une fiche ou un index.

## Interdits éditoriaux

Zéro ARK attribué par homonymie, zéro contour inventé, zéro création de communes COG, zéro rétroprojection du registre statistique 2022 sur les périodes historiques, et conservation de **176 alignements communaux + 4 alignements de collectivités** déjà validés.

Les communes associées polynésiennes ont un régime spécifique, qui ne doit pas être assimilé à une fusion de communes indépendantes du régime métropolitain : [Haut-commissariat](https://www.polynesie-francaise.gouv.fr/Actions-de-l-Etat/Accompagnement-des-communes/Presentation).
