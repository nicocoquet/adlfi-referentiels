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

## Résultats effectivement observés — recette initiale

[Première CI spécialisée réussie n°44015852671](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44015852671), [artefact de revue JSON/CSV](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44015852671/artifacts/14298851780).

| Contrôle | Résultat |
| --- | ---: |
| Communes COG au 1er janvier 2026 | **32** |
| Correspondances Pactols `skos:exactMatch` univoques éligibles | **32/32** |
| Concepts dépréciés/remplacés bloquants ou discordances | **0** |
| Codes historiques communaux `971` depuis 1943 | **34** |
| Épisodes code–libellé COG depuis 1943 | **35** |
| Lignes de mouvements impliquant un code 971 | **37** |
| Liens Pactols citant explicitement un code 971 non courant | **0** |
| Contours communaux 2026 topologiquement valides | **32/32** |
| Nouveaux contours historiques adoptés | **0** |

### 32 correspondances approuvées pour le COG 2026

**Les 32 correspondances éligibles ont été validées par application de la politique éditoriale adoptée**, et toutes sont inscrites dans le registre `recette/lieux/GUADELOUPE-VALIDATIONS-PACTOLS-COG-2026.csv`. Les décisions sont fondées exclusivement sur la citation RDF d'une URI INSEE par `skos:exactMatch`, un seul ARK Pactols actif et le libellé cohérent. Les relations sont **limitées au COG du 1er janvier 2026**.

**Sept préfLabels Pactols présentent une précision géographique explicite**, sans divergence d'identité :

| Code | Libellé COG 2026 | préfLabel Pactols |
| --- | --- | --- |
| 97122 | Port-Louis | Port-Louis (Guadeloupe) |
| 97124 | Saint-Claude | Saint-Claude (Guadeloupe) |
| 97125 | Saint-François | Saint-François (Guadeloupe) |
| 97126 | Saint-Louis | Saint-Louis (Guadeloupe) |
| 97128 | Sainte-Anne | Sainte-Anne (Guadeloupe) |
| 97129 | Sainte-Rose | Sainte-Rose (Guadeloupe) |
| 97132 | Trois-Rivières | Trois-Rivières (Guadeloupe) |

### Chronologie et anciens codes

Les **35 épisodes** représentent les 34 codes historiques, avec une seule commune attestant **deux libellés successifs sous le même code** :

- **97107, Capesterre-de-Guadeloupe** du 21 mars 1946 au 4 juin 1976 (fin exclusive), puis **Capesterre-Belle-Eau** à compter du 4 juin 1976. Le COG décrit un mouvement de modalité **MOD 10** à cette date, sans changement de code communal.
- **97123, Saint-Barthélemy** : épisode du 21 mars 1946 au **23 février 2007**, date de fin exclusive.
- **97127, Saint-Martin** : même période documentaire, avec date de fin exclusive au **23 février 2007**.

Les mouvements datés se répartissent entre le **21 mars 1946 (34 lignes, MOD 20)**, le **4 juin 1976 (1 ligne, MOD 10)** et le **23 février 2007 (2 lignes, MOD 30)**.

**Précision sur les deux mouvements de 2007 :** les lignes de modalité **MOD 30** consignent `COM_AV=97123` ou `97127`, mais **`COM_AP` est vide**. Le fichier des mouvements ne code donc **aucune destination communale explicite** de ces deux lignes. L'existence contemporaine des collectivités `977` et `978` ne doit pas être utilisée pour remplir cette lacune comme s'il s'agissait d'une relation attestée par ces mouvements.

La disparition des codes 97123 et 97127 du COG départemental n'entraîne **ni suppression de leurs anciennes autorités historiques**, ni assimilation automatique aux autorités des collectivités 977 et 978, ni attribution d'ARK par simple concordance. Dans l'export RDF Pactols vérifié, **aucun concept ne cite une URI INSEE de commune pour les anciens codes 97123 et 97127**.

**Les 32 géométries 2026 ont passé le contrôle topologique, mais ne constituent pas des limites historiques.** Les relations Pactols validées en 2026 restent contemporaines, sans rétroprojection sur l'histoire du code.

