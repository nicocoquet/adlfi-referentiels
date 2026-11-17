# Polynésie française — jointures ISPF et validité géométrique (PR 80)

**17 novembre 2026 — recette non validante, suite aux PR 75, 77, 78 et 79.**

## Sources figées

- Nomenclature ISPF : `Codes_geographiques_ce46ed21ee.xlsx`, SHA-256 `d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6`.
- Archive ISPF GeoJSON : `Com.GeoJSON`, `Comas.GeoJSON`, `Ile.GeoJSON`, SHA-256 `6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62`.

## Contrôles

Le script `auditer_jointures_topologie_ispf.py` lit les feuilles institutionnelles `Commune`, `Commune associée`, `Ile` et confronte les **codes**, sans rapprochement lexical, aux propriétés géométriques `IDCom`, `IDComas` et `IDIle`. Les identifiants numériques entiers (`11.0`) sont normalisés en chaînes canoniques ; les valeurs fractionnaires, ambiguës ou non numériques sont refusées.

Pour chaque couche : couverture exacte, codes absents/supplémentaires, doublons, variations de libellé et incohérences `IDCom`/`IDSub`. La concordance des libellés est un contrôle complémentaire, **pas la clé de correspondance**. Le cas `Faa'a`/`Faaa` peut rester une variante éditoriale.

Les géométries sont passées dans **Shapely 2.1.2 / GEOS** pour le test topologique OGC `is_valid`, sans nettoyage ni `make_valid`. La liste des codes dont la géométrie est vide ou invalide et la raison `explain_validity` est conservée dans l'artefact de CI. Ce premier contrôle **n'homologue ni la précision ni les limites administratives** : comparaisons de superposition, intersections entre couches, surfaces et conformité géodésique sont à mener ensuite.

## Garde-fous éditoriaux

- **48** communes COG, **116** unités fines ISPF (98 associées + 18 conventionnelles), **119** îles attendues comme cardinalités de contrôle, jamais comme 116 communes associées nouvelles.
- **Maria, Raiatea, Tahiti** : aucune hypothèse de hiérarchie univoque île→commune ; les relations multi-communes déjà sourcées restent préservées.
- **Tahaa** : son contour COG 2026 précédemment signalé invalide n'est pas réputé réparé par la seule présence d'un contour ISPF.
- **Épisodes historiques** : aucune rétroprojection vers 1972, 1974, ni assimilation de la date de dépôt du ZIP à une date d'effet réglementaire.
- **Statuts distincts** : correspondance d'identifiant, validité GEOS et validation éditoriale de publication sont trois conditions indépendantes.

Rapport produit **hors `docs/`**, double génération vérifiée octet par octet, aucun contour ni nouvel ARK publié.

**Décision avant fusion :** lire les résultats de CI, recenser toutes les discordances et les géométries invalides et déterminer si la recette doit évoluer. Aucune fusion sur la seule réussite technique des tests.
