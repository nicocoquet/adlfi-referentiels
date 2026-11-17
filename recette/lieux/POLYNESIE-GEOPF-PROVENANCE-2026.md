# Polynésie française — GEO PF, provenance et structure de la source de comparaison

**17 novembre 2026.** Première tranche de la PR 83 : inventaire de l'archive institutionnelle avant toute comparaison spatiale.

## Sources recensées

Le catalogue [Géographie administrative de la Polynésie-française — GEO PF](https://www.data.gouv.fr/datasets/geographie-administrative-de-la-polynesie-francaise), fourni par la **Section Cadastre-Topographie de la Polynésie française**, annonce trois ressources ZIP (localisation des îles, des groupes d'îles et des communes associées) datées du **28 février 2022**. Licence de catalogue : **Creative Commons Attribution**.

Archive ciblée : `loc-commune-associee.zip` (14,6 Mo annoncés), identifiant de ressource `89d202c3-4f04-4168-842d-4c50036125c7`, URL `https://www.data.gouv.fr/api/1/datasets/r/89d202c3-4f04-4168-842d-4c50036125c7`.

La ressource GEO PF **n'est pas confondue** avec l'archive ISPF (SHA-256 `6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62`). Les détails temporels, la précision de levé et l'origine des contours doivent être vérifiés avant de l'employer comme preuve indépendante.

Deux sources complémentaires :

- [Service ArcGIS Découpage_administratif](https://services.arcgis.com/L4H4rU26VyhEF588/ArcGIS/rest/services/D%C3%A9coupage_administratif/FeatureServer/0), EPSG:4326, présentant les champs `com_id`, `ca_id`, `nature_administrative`, ainsi que des catégories distinctes `commune_associee`, `commune`, `commune_300m`, etc. La date d'édition technique observée est postérieure à la date des données : ne pas les assimiler.
- [Métadonnées ISO-19139 de la couche « Communes associées (Tefenua) »](https://www.arcgis.com/sharing/rest/content/items/624bb9320a26424787723a50411a9eba/info/metadata/metadata.xml?format=default&output=html), publication 13 octobre 2022, dernière métadonnée 3 avril 2023. Le producteur y note expressément : **« La source et la précision de cette donnée originale ne sont pas connues. »** Le seul statut institutionnel ne démontre donc pas l'indépendance de ce fond.

## Méthode PR 83

`scripts/inventorier_geopf_polynesie.py` inventorie les composants SHP/SHX/DBF/PRJ, empreintes SHA-256, champs, types de géométries, nombre d'entités et projection déclarée, avec trois échantillons attributaires. Les tests synthétiques vérifient les archives complètes et le rejet de chemins ZIP malveillants. La CI télécharge l'archive par son identifiant immuable de ressource, l'inspecte et archive deux sorties comparées pour reproductibilité.

**Aucune comparaison ISPF–GEO PF n'est présumée** avant confirmation des clés d'alignement et de la projection. Sont en particulier proscrits les appariements par simple homonymie, la création de nouvelles autorités, la rétroprojection historique et le téléchargement d'un fond dont l'origine serait indéterminée pour « corriger » des limites officielles.

Le rapport, contenant l'empreinte complète du ZIP, reste en artefact CI hors `docs/`. **Statut `RECETTE_NON_VALIDANTE`** ; pas de publication cartographique.

## Suite conditionnelle

Si l'archive est exploitable et les identifiants comparables, préparer une deuxième tranche de la PR pour vérifier les couples ISPF `311/312`, `120/250`, `312/313`, `471/482` et `120/360`. Dans le cas contraire, conserver les limites de la preuve et instruire prioritairement les attributs de la couche ArcGIS, sans prétendre qu'elle est indépendante.


## Résultats effectifs — archive GEO PF figée

Le workflow de préflight [n°44102888857](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44102888857) confirme une archive de **15 310 967 octets** (SHA-256 **`29230c18487385f84ca480e9b2c921ea389f848663a4a9574e77b9cbbf40db7b`**), avec une couche `loc_commune_associee` de **179 polygones** (type SHP 5), en coordonnées **RGPF/GRS 1980**. Champs structurants : `code_geogr`, `code_com_1`, `code_commu`, `code_subdi`, `id_ile`, `code_com_i`, `nom_geogra`. Le champ `mode_acq` décrit le mode d'acquisition, dont une valeur effectivement observée est `TERRAIN_TOPO`, avec `org_acq=CADASTRE`. Il faut qualifier ces métadonnées à l'échelle des 179 enregistrements et ne pas en inférer un levé direct de toutes les limites.

Le workflow de comparaison [n°44103354104](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44103354104), lui aussi **réussi**, a rapproché cette couche des **179 lignes de la feuille ISPF `Geo`** par `IDGeo` / `code_geogr` et comparé les clés hiérarchiques par codes :

| Contrôle | Résultat |
| --- | --- |
| Géographies avec code identique | **177/179** |
| Codes présents dans ISPF mais pas GEO PF | **`43001`, `44001`** |
| Codes présents dans GEO PF mais pas ISPF | **`43101`, `44301`** |
| Autres écarts de hiérarchie pour les 177 codes communs | **2 codes d'île** |
| Code `IDGeo=28001` | ISPF `IDIle=53` ; GEO PF `id_ile=54` |
| Code `IDGeo=55001` | ISPF `IDIle=20` ; GEO PF `id_ile=113` |

**Aucun rapprochement automatique** des codes `43001`/`43101` ou `44001`/`44301` : les îlots Maria et leurs rattachements appellent une instruction séparée, en tenant compte des attributs et des actes. Les différences d'îles pour `28001` et `55001` seront vérifiées par leur libellé dans les deux sources ; le code partagé n'efface pas le désaccord hiérarchique.

Une première comparaison textuelle exploratoire a généré des divergences nombreuses parce que les colonnes `nom`, `nom_commun` et `nom_geogra` ne désignent pas systématiquement les mêmes niveaux ; **ce comptage lexical est retiré de la recette comme non probant**. Seules les correspondances de clés explicitement documentées sont retenues.

**Conclusion :** le géoréférencement GEO PF est bien exploitable pour une comparaison ultérieure, mais la concordance étroite des schémas et la divergence de quelques codes ne suffisent ni à prouver ni à infirmer l'indépendance des géométries. Il reste à comparer leurs contours sans réparer ni attribuer des identifiants non vérifiés.
