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
