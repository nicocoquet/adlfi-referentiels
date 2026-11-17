# Polynésie française — audit Pactols-Lieux des 48 communes COG 2026

**17 novembre 2026 — préinstruction RDF, aucune validation ni publication automatique.**

## Une question distincte de la chronologie COG

La [PR n°70](https://github.com/nicocoquet/adlfi-referentiels/pull/70) a publié **48 épisodes COG communaux**, débutant chacun le **21 mai 1972** dans la série historique, et isolé **Clipperton `98799`**, code terminé en 2007.

L'objectif du présent lot est différent : examiner, dans l'export officiel **Pactols-Lieux**, les `skos:exactMatch` vers les URI des **48 communes principales `98711`–`98758`** et évaluer chaque preuve.

## Sources et traçabilité

- [Frantiq/PACTOLS](https://github.com/frantiq/PACTOLS), `Pactols_Lieux_th17_20260722.rdf`, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 **`3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`**.
- [INSEE, COG 2026](https://www.insee.fr/fr/information/8740222), les mêmes **six CSV contrôlés SHA-256** que la recette n°70, vérification directe des 48 codes et libellés.
- [ISPF, nomenclatures géographiques](https://www.ispf.pf/ispf/referentiels) pour la distinction de **98 communes associées** et cinq subdivisions administratives, qui ne sont **pas** des communes COG principales.

## Règle de préqualification

Pour chacun des 48 codes, un lien est uniquement **éligible à un arbitrage éditorial** si :

1. Le concept porte explicitement `skos:exactMatch` vers une URI `http(s)://id.insee.fr/geo/commune/987XX` correspondant au code et à la famille de communes COG courante.
2. Il existe un seul concept candidat pour ce code et son concept ne cite **aucun autre identifiant INSEE** incompatible ; un même ARK ne doit pas désigner plusieurs communes différentes dans le lot.
3. Le concept n'est ni `owl:deprecated` ni remplacé, et son `prefLabel` est compatible avec le libellé communal.
4. Un libellé commençant par « île », « îlot », « atoll », « archipel », « royaume » ou « district » entraîne **instruction sémantique spécifique** même en présence d'un `exactMatch`.

Tout cas différent est **à instruire**, sans invention de correspondance à partir d'une homonymie ou d'une variante lexicale. Les libellés seuls sont recensés comme **candidats non validants**.

La voie URI et les identifiants `987` (collectivité territoriale) et `98799` (Clipperton historique) sont contrôlés **séparément**, jamais reversés automatiquement vers l'une des 48 communes.

**Le concept géographique d'une île n'est pas nécessairement identique à la commune qui la contient**, et une même commune peut couvrir plusieurs îles ou atolls. La décision doit donc respecter la catégorie de l'entité et les données de provenance.

## Livrables et bornes

Le script `scripts/auditer_pactols_polynesie_2026.py`, ses tests synthétiques et le workflow `lieux-polynesie-pactols-2026.yml` garantissent une double production JSON identique ; le rapport exhaustif est archivé comme artefact de CI, **hors `docs/`**.

Le rapport distingue les 48 codes, les candidats explicites, les candidats seulement lexicaux, les problèmes d'unicité, les libellés incompatibles, les concepts dépréciés et les catégories d'URI.

**0 correspondance validée par le script, 0 contour historique, 0 commune associée construite ou rétroprojetée.** Les 128 relations Pactols communales publiées jusqu'à présent sont inchangées.

Le résultat chiffré et les ARK de la source seront consignés **après exécution effective du workflow sur le RDF épinglé**, et non inférés des noms.
