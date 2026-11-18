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
