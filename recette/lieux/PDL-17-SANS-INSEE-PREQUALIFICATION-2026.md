# Pays de la Loire — préqualification des 17 concepts Pactols contemporains sans URI INSEE

**Recette de qualification non validante — 18 novembre 2026.** Point de départ publié : **1 195 / 1 228** correspondances Pactols–COG 2026 ; **33 exceptions**. Après la PR 142, la PR 141 documente 17 communes pour lesquelles il existe un ARK Pactols au libellé actuel, mais **aucun lien INSEE explicite**, y compris au format UUID. Les 5 communes sans ARK lexical, Les Hauts-d’Anjou (identité créée en 2019 distincte du concept 2016), les 9 collisions historiques et Rives-du-Fougerais restent hors de cette recette.

## Ce que la recette vérifie

Le script `scripts/prequalifier_pdl_17_sans_insee_2026.py` repart :

- du [registre nominatif des 24 divergences](PDL-24-DIVERGENCES-NOMINATIF-2026.json) et **des six index publiés** (1 140 + 3 + 5 + 1 + 45 + 1 = 1 195), pour exclure tout code ou ARK déjà validé ;
- du RDF Pactols `Pactols_Lieux_th17_20260722.rdf`, commit Frantiq `69bf9697e24cefd645a69465bbd271702786285a` et SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7` ;
- du COG PDL historique 2026 **déjà versionné et validé** : `docs/data/lieux-chronologie/cog-pdl.json`, sans prétendre à une nouvelle acquisition des CSV de l’Insee.

Pour **chacun des 17 concepts**, une relecture indépendante du RDF collecte les libellés, les `exactMatch` et `closeMatch`, les `broader` et `related`, le schéma d’appartenance, les définitions et notes, les dépréciations et les remplacements. Elle compte **tous les concepts Pactols portant le même `prefLabel` normalisé**, même lorsqu’ils sont liés à une autre URI INSEE : la sélection initiale par libellé ne prouve pas leur unicité nationale.

Le contrôle COG liste la période actuelle `COM`, le mouvement de création `MOD32` à la même date, l’épisode antérieur du code conservé et les communes qui ont participé à la création. Un événement MOD32 est une preuve de l’**identité administrative COG**, **pas** une preuve qu’un concept Pactols lexicalement proche la représente.

### Critères de classement

Les cas avec des identifiants d’autres référentiels ou des relations descriptives dans Pactols sont isolés pour **vérification externe de ces preuves**, jamais validés automatiquement. Les concepts ne disposant d’aucune preuve non lexicale restent en instruction. Les homonymies de `prefLabel`, incohérences de création ou reprises d’ARK historiques font l’objet d’une alerte.

**Aucune publication, aucune géométrie, aucune inférence historique.** La CI doit générer deux rapports JSON bit à bit identiques et vérifier que les 17 lignes conservent `decision_editoriale=NON_PRISE` et `publication=NON_PUBLIE`. Le rapport est publié uniquement comme artefact de recette et consigne les critères de preuve à demander avant une PR de validation.

## Sources indépendantes de contrôle

- [Insee, description du COG et de l’historique des communes](https://www.insee.fr/fr/information/2560452).
- [Ancenis-Saint-Géréon : dossier Insee 2026](https://www.insee.fr/fr/statistiques/2011101?geo=COM-44003) (création le 1er janvier 2019).
- [Bellevigne-les-Châteaux : dossier Insee 2026](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49060) (création le 1er janvier 2019).

La concordance géographique et chronologique établie par les sources institutionnelles sera intégrée à chaque décision. **Le but est un ensemble d’alignements défendables, pas une couverture artificielle de 100 %.**

Après les 17 dossiers, restent notamment les 5 autorités courantes non retrouvées, les 9 collisions historiques et Rives-du-Fougerais. La reprise de l’interface graphique du module Lieux est prévue après cette phase de consolidation régionale, selon les propositions de l’éditeur.

## Première recette réussie : triangulation Pactols–Wikidata–COG

La [première exécution spécialisée](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44355246615) a réussi la double génération et constaté que **chacun des 17 concepts Pactols possède un `skos:exactMatch` vers un élément Wikidata distinct**, ainsi qu'un `skos:broader` territorial et, dans 16 cas, une description textuelle de la commune nouvelle (les notes sont souvent créditées Wikipédia, elles sont donc seulement informatives et non des sources administratives autonomes).

Chacun des 17 candidats est **le seul concept Pactols possédant ce `prefLabel` normalisé** dans le RDF épinglé, et chacun est confronté à une création COG `MOD32` datée exactement comme son épisode communal actuel.

La [page Wikidata d'Ancenis-Saint-Géréon (Q57208924)](https://www.wikidata.org/wiki/Q57208924), par exemple, indique le code INSEE `44003`, et celle de [Bellevigne-les-Châteaux (Q58839998)](https://www.wikidata.org/wiki/Q58839998) le code `49060`. Les fiches [Wikidata de Vimartin-sur-Orthe (Q104586158)](https://www.wikidata.org/wiki/Q104586158) et [Insee de la commune](https://www.insee.fr/fr/metadonnees/geographie/commune/53249-vimartin-sur-orthe) permettent le même rapprochement `53249`.

**Nouvelle étape nécessaire :** extraire et qualifier **les 17 valeurs de la propriété Wikidata `P374` (code de commune INSEE)**. Le script `scripts/croiser_pdl_17_wikidata_p374_2026.py` interroge l'API Wikidata pour les QID explicitement cités dans Pactols, tient compte des qualificatifs de dates (`P580`/`P582`) et des déclarations dépréciées, puis consigne les `lastrevid` de provenance. Une **seule acquisition** alimente deux générations locales comparées octet à octet. Un résultat absent ou contradictoire ne sera pas promu en publication.

Ce recoupement constitue une **chaîne probatoire indirecte** : `Pactols skos:exactMatch Wikidata → Wikidata P374 code INSEE → COG 2026`. Il **ne crée ni ne prétend découvrir dans Pactols un exactMatch direct vers l'Insee**. Même lorsque toutes les propriétés concordent, la décision éditoriale et la publication devront intervenir dans une PR séparée.

## Recoupement Wikidata P374 achevé — preuves révisionnelles

La [CI spécialisée 44356761491](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44356761491) a acquis par l'API publique Wikidata les 17 éléments explicitement cités par les 17 `skos:exactMatch` Pactols. Les **17 codes INSEE actuels `P374`** concordent avec le COG 2026. Les **17 instances `P31` sont de type commune française (`Q484170`)**, et les **17 dates de création `P571` coïncident** avec le début de l'épisode `COM` 2026. Les déclarations `P374` dépréciées, historiques ou concurrencées sont exclues par la règle temporelle ; aucune contradiction active n'a été relevée.

Le [registre de preuve Wikidata](PDL-17-WIKIDATA-P374-2026.json) consigne, pour chaque code, le QID, le `lastrevid` de Wikidata, un lien `oldid` vers sa version figée, les valeurs `P374`, `P31` et `P571`, et la concordance COG. La CI reproduit le croisement deux fois depuis **un seul instantané brut**, puis compare le résultat aux données versionnées dans Git. Une révision future de Wikidata demandera un réexamen du registre plutôt qu'un changement silencieux.

**Proposition éditoriale après audit, sans publication dans cette PR :** les 17 concordances satisfont un faisceau de preuves explicites et permettent la préparation d'une PR distincte d'alignements pour le **millésime COG 2026 uniquement**. La chaîne de provenance doit rester affichée comme `skos:exactMatch Pactols→Wikidata` et `P374 Wikidata→INSEE`, **jamais comme un exactMatch INSEE présent dans Pactols**. Les ARK des communes antérieures restent différents. Couverture actuelle : **1 195 / 1 228** ; couverture *attendue après une éventuelle publication validée* : **1 212 / 1 228**, 16 exceptions.
