# Guadeloupe — lot 01, audit COG/Pactols/historique et géométries

**17 novembre 2026 — recette documentaire, aucune nouvelle géométrie adoptée.**

## Périmètre

L'index public Lieux répertorie **32 communes du département 971**. Les codes sont **non contigus** : les anciennes entrées **97123 (Saint-Barthélemy)** et **97127 (Saint-Martin)** n'appartiennent pas au périmètre départemental du COG 2026. Ces codes doivent être étudiés comme **autorités historiques distinctes**, et non recréés comme communes de Guadeloupe en 2026 ni déduits des libellés.

Le script `scripts/auditer_guadeloupe_2026.py` reprend le protocole éprouvé pour la Martinique, en gardant séparés :

- les **32 communes COG 2026**, avec code, libellé et géométrie de cette édition ;
- les **épisodes administratifs historiques** extraits des lignes `TYPECOM=COM` du COG depuis 1943, y compris les anciens codes s'ils sont documentés ;
- les **mouvements datés** ayant un code 971 avant ou après le mouvement, sans génération automatique de relations de succession entre autorités Pactols ;
- les **liens URI INSEE explicitement cités** dans les concepts Pactols, distincts des concordances lexicales.

## Sources et vérifications

- [INSEE, Code officiel géographique 2026](https://www.insee.fr/fr/information/2560452) : `v_commune_2026.csv`, `v_commune_depuis_1943.csv`, `v_mvt_commune_2026.csv` ; contrôlés par leurs trois SHA-256 déjà retenus dans le dépôt.
- [Frantiq PACTOLS](https://github.com/frantiq/PACTOLS) : export RDF Lieux du 22 juillet 2026 au commit `69bf9697e24cefd645a69465bbd271702786285a` ; SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- [Etalab, contours administratifs 2026](https://www.data.gouv.fr/datasets/contours-administratifs) : GeoJSON des communes à 100 m, SHA-256 `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778`.

La validité topologique d'un contour 2026 ne constitue pas une preuve de la géométrie de 1946, 2007 ou d'une autre date passée.

## Critère de qualification Pactols

Chaque relation est classée **ÉLIGIBLE SELON RÈGLE** lorsque le RDF atteste un `skos:exactMatch` univoque vers le code INSEE de la commune **active au 1er janvier 2026**, sans autre code contradictoire cité, sans dépréciation ou remplacement, et avec préfLabel français compatible. À défaut, la ligne est **À INSTRUIRE** et comporte un motif explicite.

Les anciennes autorités, notamment 97123 et 97127 si elles sont explicitement attestées dans l'historique COG et/ou dans Pactols, sont consignées dans une revue séparée. **Elles ne doivent pas être automatiquement alignées sur les autorités actuelles 97701 et 97801** : les relations de succession COG, la continuité territoriale et l'identité des concepts Pactols sont trois questions distinctes.

## Exécution

La CI `.github/workflows/lieux-guadeloupe-audit-2026.yml` contrôle les sources épinglées, les tests de lecture RDF et de conflits, les 32 géométries de 2026, puis produit deux exécutions identiques de l'audit ; les JSON et CSV sont archivés comme **artefacts de recette**. Le nombre d'épisodes anciens, les modalités des mouvements et le nombre d'alignements éligibles **ne sont pas postulés à l'avance**.

**Aucun fichier `docs/` n'est modifié pendant cette première instruction**, aucune géométrie historique n'est publiée et aucune succession juridique ou équivalence Pactols n'est inférée de la ressemblance d'un nom.

Les résultats chiffrés et les arbitrages seront consignés ici à partir de la CI.
