# Guadeloupe — recette GEOFLA 2015 et contours Etalab 2026

**17 novembre 2026. Audit cartographique non validant, sans publication de polygones.**

## Objet et contexte

Après les PR 54 et 55, la Guadeloupe dispose de **32 alignements Pactols–COG validés pour 2026** et de **35 épisodes historiques documentaires**, dont deux anciens codes `97123` (Saint-Barthélemy) et `97127` (Saint-Martin), terminés en 2007.

La comparaison cartographique porte **exclusivement sur les 32 codes 971 encore courants en 2026**. Il serait erroné d'intégrer les deux anciens codes 97123 et 97127 à un total de 34 communes en 2015 ou 2026 ; ils sont conservés dans les fiches historiques mais exclus de cette comparaison de partitions contemporaines.

## Sources

- Archive candidate **GEOFLA 2015** : `GEOFLA_2-1_COMMUNE_SHP_UTM20W84GUAD_D971_2015-12-01.rar`, localisée dans le [miroir documentaire GitHub justinelliotmeyers](https://github.com/justinelliotmeyers/official_france_administrative_boundary_shapefile). L'empreinte de la copie sera figée après la première acquisition vérifiée. **La présence dans ce dépôt tiers et la nomenclature ne suffisent pas à authentifier le fichier comme un original IGN.**
- [Contours administratifs Etalab 2026, data.gouv.fr](https://www.data.gouv.fr/datasets/contours-administratifs), généralisations 100 m et 50 m, issues des sources administratives nationales. Empreintes SHA-256 déjà figées dans le dépôt : respectivement `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778` et `6db43cd98a7211516da64e91761100504ba3feeddc986ebe0d50f84df624cd38`.
- Documentation produit [GEOFLA, IGN](https://geoservices.ign.fr/sites/default/files/2021-07/DC_GEOFLA_2-2.pdf) : produit cartographique généralisé destiné à des usages proches du 1:1 000 000, dernière édition documentée en 2016 ; ses limites et dates ne sont pas assimilables automatiquement à une délimitation juridique exacte.

## Méthode

1. Inventorier les fichiers SHP/PRJ du RAR et vérifier la projection **déclarée dans le WKT source**, sans la déduire uniquement du nom UTM20W84GUAD.
2. Lire les **codes INSEE attributaires des 32 communes** ; refuser les doublons, les codes hors département ainsi que les anciens 97123 et 97127 si ceux-ci étaient mêlés à la couche de 2015.
3. Vérifier la validité des géométries et l'absence de recouvrement surfacique, projeter les trois partitions dans **EPSG:6933** pour les mesures.
4. Comparer GEOFLA 2015 avec Etalab 2026 à 100 m, puis 50 m ; mesurer aussi la sensibilité au niveau de généralisation entre les deux dessins 2026.
5. Décomposer le cumul des écarts des 32 communes en : **différence d'emprise extérieure + deux fois la différence de répartition interne entre codes** ; vérifier la fermeture de l'équation avant archivage.
6. Localiser les principales divergences de contour par leur **aire, point intérieur représentatif et rectangle approximatif** en WGS84, sans exporter de polygone.
7. Générer deux fois le rapport avec les mêmes sources et comparer les octets ; archiver uniquement les métriques et la provenance dans un artefact de CI.

La CI spécialisée contrôle séparément les sources, les codes, la topologie et les métriques. Les résultats seront ajoutés à cette note une fois obtenus et la source candidate 2015 sera alors épinglée par SHA-256.

## Interprétation strictement limitée

Une différence mesurée entre GEOFLA 2015 et Etalab 2026 peut résulter du **trait de côte représenté, de la généralisation, d'autres méthodes de production ou de véritables transformations** ; l'audit n'est pas en mesure d'en identifier la cause juridique.

**Aucun contour 2015 ou 2026 n'est publié comme limite historique, aucune ancienne commune 971 n'est réintroduite dans le millésime 2026, aucun ARK Pactols ni relation de succession ne sont modifiés.**

Fichiers : `scripts/auditer_geofla_guadeloupe_2015.py`, `tests/test_auditer_geofla_guadeloupe_2015.py`, `.github/workflows/lieux-guadeloupe-geofla-2015.yml`.
