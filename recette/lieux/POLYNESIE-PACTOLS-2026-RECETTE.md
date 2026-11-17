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

## Résultat vérifié sur le RDF Frantiq : 48 sur 48

La [CI officielle n°44061695614](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44061695614) a réussi le contrôle SHA-256, les tests RDF et la double extraction reproductible.

| Catégorie | Résultat réel |
| --- | ---: |
| Communes COG 2026 examinées | **48** |
| Codes portant un `skos:exactMatch` explicite | **48** |
| Concepts Pactols distincts | **48** |
| Libellés compatibles et concepts actifs | **48** |
| Conflits de code, concepts multiples ou dépréciations | **0** |
| Alertes automatiques île/atoll/royaume dans les libellés préférés | **0** |
| Candidats exclusivement lexicaux sans URI INSEE | **0** |
| Correspondances nouvelles publiées par cette recette | **0** |

Les 48 URI INSEE ont exactement la forme `http://id.insee.fr/geo/commune/987XX` et chaque concept n'a qu'une seule URI INSEE, vers son code communal courant. Parmi les preuves : **Anaa `98711` → `26678/pcrtwSlYRcWVFw`**, **Bora-Bora `98714` → `26678/pcrtlbU8ne9i3P`**, **Gambier `98719` → `26678/pcrtvKcE6DTLi5`**, **Papeete `98735` → `26678/pcrtr90gKcAXiG`**, **Tahaa `98745` → `26678/pcrteZcqWgVUaT`**, **Uturoa `98758` → `26678/pcrtRw9F7i5M8l`**.

Le RDF contient aussi un **concept distinct pour la collectivité `987`**, ARK **`26678/pcrt4K8nLVxWOP`**, avec `exactMatch` vers `http://id.insee.fr/geo/collectiviteDOutreMer/987`. Il ne porte aucun lien communal à transférer vers les 48 communes.

**Aucun `exactMatch` vers le code historique `98799` Clipperton** n'a été retrouvé dans cet export.

### Décision de méthode

Les **48 couples communaux** satisfont toutes les conditions de la [politique d'alignement Pactols–COG du 16 novembre 2026](POLITIQUE-ALIGNEMENT-PACTOLS-COG.md) et sont **éligibles à validation éditoriale par règle pour l'état du 1er janvier 2026**. Leur publication requerra un **registre CSV versionné** et une PR de publication séparée pour ne pas confondre diagnostic RDF et décision. Cette validation portera sur les **identifiants**, sans homologuer automatiquement la géométrie, les communes associées ISPF ou les périodes historiques.

Le **concept de territoire `987`** sera instruit suivant la politique distincte des collectivités d'outre-mer (cf. [PR n°68](https://github.com/nicocoquet/adlfi-referentiels/pull/68)). Il ne peut être versé dans le registre des communes.
