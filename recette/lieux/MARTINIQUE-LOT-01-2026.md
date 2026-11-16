# Martinique — lot 01 : audit COG / Pactols / contours

**16 novembre 2026. Recette non publiée, préparée après le lot Guyane.**

## Méthode

Le référentiel public contient actuellement **34 communes COG 2026 de Martinique** (codes 97201 à 97234) et **aucun lien Pactols–COG déjà approuvé** pour ces codes. Les données de la page Lieux restent inchangées pendant l'audit.

Le script scripts/auditer_martinique_2026.py reprend les contrôles de la Guyane et réexamine exclusivement :

- [Insee COG 2026](https://www.insee.fr/fr/information/2560452) : v_commune_2026.csv, v_commune_depuis_1943.csv et v_mvt_commune_2026.csv, téléchargés et vérifiés par SHA-256 ;
- [Frantiq / Pactols Lieux](https://github.com/frantiq/PACTOLS), export RDF daté du **22 juillet 2026**, commit 69bf9697e24cefd645a69465bbd271702786285a, SHA-256 3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7 ;
- [Contours administratifs nationaux 2026](https://www.data.gouv.fr/datasets/contours-administratifs), GeoJSON 100 m, SHA-256 4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778.

Le rapport distingue **34 communes actuelles**, **toutes les périodes et mouvements communaux impliquant le département 972**, les concepts Pactols dont l'URI INSEE est explicitement citée et les simples homonymies lexicales. Les géométries 2026 sont contrôlées sans être publiées.

## Alignements : application prudente de la décision éditoriale

La [politique Pactols–COG du référentiel](POLITIQUE-ALIGNEMENT-PACTOLS-COG.md) autorise la validation automatique contrôlée lorsque l'on observe un **skos:exactMatch explicite** d'un concept actif vers un **unique code de commune INSEE 2026**, sans autre code contradictoire, sans dépréciation ou remplacement et avec libellé français compatible.

Le rapport classe chaque commune :

- **ELIGIBLE_SELON_REGLE** : toutes les preuves vérifiées ; la fiche peut être qualifiée en appliquant la politique, après validation de la recette ;
- **A_INSTRUIRE** : absence d'URI, prédicat non exact, libellé incompatible, concept déprécié ou autres ambiguïtés, avec motif explicite.

Les autorités associées à **d'anciens codes communaux** sont consignées séparément, **sans les fusionner automatiquement** avec les communes actuelles. Le nombre d'anciennes autorités, de périodes, de mouvements et de concepts Pactols sera constaté par l'exécution, sans cardinalités postulées à l'avance.

**Aucune correspondance nouvelle n'est injectée sous docs/ pendant cette première recette**, aucune géométrie 2026 n'est attribuée à un état historique et aucune succession administrative n'est inférée d'une homonymie.

## Contrôles

La CI spécialisée lieux-martinique-audit-2026.yml effectue deux exécutions du lot avec les mêmes sources et contrôle leur identité octet à octet. Elle archive une table de revue complète, une table de qualification des 34 liens, les états et mouvements COG, un bilan des 34 géométries et les empreintes des sources/sorties.

## Résultats contrôlés — 16 novembre 2026

Les recettes spécialisées ont exécuté deux fois le traitement sur le COG et le RDF Pactols **SHA-256 épinglés**, avec résultats identiques. [Première exécution réussie](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43952745257) ; [seconde recette détaillée RDF et historique](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43953166729).

| Contrôle | Résultat |
| --- | ---: |
| Communes COG actives le 1er janvier 2026 | **34** |
| Codes communaux distincts dans l'historique COG depuis 1943 | **34** |
| Épisodes code–libellé depuis 1943 | **34** |
| Lignes de mouvements communaux impliquant un code 972 | **36** |
| Codes INSEE courants explicitement cités dans Pactols | **34/34** |
| skos:exactMatch univoques, non dépréciés, non remplacés | **34/34** |
| Liens nécessitant un arbitrage particulier | **0** |
| Anciennes autorités Pactols liées à un code disparu | **0** |
| Géométries communales 2026 topologiquement valides | **34/34** |
| Nouveaux contours adoptés | **0** |

### Validation éditoriale par règle

La règle adoptée avec la Guyane a été appliquée aux **34 couples Pactols–COG 2026** ; le registre versionné des décisions est **recette/lieux/MARTINIQUE-VALIDATIONS-PACTOLS-COG-2026.csv**. Il consigne l'URI INSEE, l'ARK, le préfLabel Pactols, le prédicat exactMatch, l'absence de dépréciation, la portée temporelle et le statut VALIDE_ADLFI_2026.

**Sept différences de libellé sont des désambiguïsations explicitement présentes dans Pactols**, non des cas problématiques :

| Code | Libellé du COG | préfLabel Pactols |
| --- | --- | --- |
| 97224 | Saint-Joseph | Saint-Joseph (Martinique) |
| 97225 | Saint-Pierre | Saint-Pierre (Martinique) |
| 97226 | Sainte-Anne | Sainte-Anne (Martinique) |
| 97227 | Sainte-Luce | Sainte-Luce (Martinique) |
| 97228 | Sainte-Marie | Sainte-Marie (Martinique) |
| 97230 | La Trinité | La Trinité (Martinique) |
| 97234 | Bellefontaine | Bellefontaine (Martinique) |

### Chronologie attestée, distincte des géométries

La version COG étudiée comporte **34 épisodes** (un par code communal), sans réattribution d'ancien code à une autre commune. Les 36 lignes de mouvements se répartissent ainsi :

| Date d'effet dans le COG | Modalité (MOD) | Nombre de lignes | Lecture documentaire |
| --- | --- | ---: | --- |
| 21 mars 1946 | 20 (création) | 32 | Première série d'états présents dans le fichier COG |
| 25 mars 1949 | 20 (création) | 2 | Épisode du code 97233, Le Morne-Vert |
| 26 août 1950 | 20 (création) | 2 | Épisode du code 97234, Bellefontaine |

Les **deux lignes** des événements de 1949 et de 1950 ne signifient pas deux nouvelles communes à chaque date : un démembrement documenté peut comporter une ligne relative à la commune source et une autre à la commune nouvellement créée.

Les épisodes eux-mêmes attestent la présence de **32 codes au 1er janvier 1947**, **33 au 1er janvier 1950** et **34 au 1er janvier 1951**. Au 1er janvier 1946, aucune période n'est encore active dans le fichier : cela indique une limite de couverture documentaire, pas l'inexistence des communes martiniquaises. La [fiche Insee de Bellefontaine](https://www.insee.fr/fr/metadonnees/geographie/commune/97234-bellefontaine) confirme la date de création du 26 août 1950.

**Décisions de publication :** les 34 alignements sont approuvés pour **2026 uniquement**. Aucun contour 2026 n'est adopté, aucun ancien contour n'est reconstruit, les 36 lignes de mouvements n'engendrent pas automatiquement de relation de succession et aucun concept Pactols n'est étendu rétroactivement à une période antérieure.

