# Arbitrages AdlFI — Nouvelle-Calédonie, Saint-Pierre-et-Miquelon et Dembeni

**17 novembre 2026 — 36 correspondances communales 2026 étayées par exactMatch et validation éditoriale.**

L'éditeur a explicitement confirmé trois ARK supplémentaires :
- **`98809` L'Île-des-Pins** ↔ `26678/pcrti4LqTHByEs` ;
- **`97501` Miquelon-Langlade** ↔ `26678/pcrtQAMzeGHldU` ;
- **`97607` Dembeni** ↔ `26678/crtZcuFSJVYZU`.

L'arbitrage de **`97502` Saint-Pierre** ↔ `26678/pcrtYQmFfwxLq8` est déjà consigné dans la PR 93. Les **32 autres communes de Nouvelle-Calédonie** ont une preuve RDF `skos:exactMatch` univoque, sans dépréciation, classée éligible par [l'audit PR 94](NOUVELLE-CALEDONIE-PACTOLS-33-2026.md).

## Décisions et vérifications RDF

L'audit [GitHub Actions n°44152306293](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44152306293) a confronté les **36 ARK** à l'export RDF Frantiq du 22 juillet 2026 (SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`). Il trouve **36 assertions `skos:exactMatch` uniques** vers les codes de commune INSEE respectifs, sans dépréciation, remplacement ou autre URI INSEE concurrente.

Le registre [VALIDATIONS-NC-SPM-DEMBENI-2026.csv](VALIDATIONS-NC-SPM-DEMBENI-2026.csv) conserve **36 décisions `VALIDE_ADLFI_2026`**, dont **33 en Nouvelle-Calédonie, 2 à Saint-Pierre-et-Miquelon et 1 à Mayotte (Dembeni)**.

Deux exceptions nominatives de libellé restent documentées :
- **Saint-Pierre `97502`** : `prefLabel` actuellement « île Saint-Pierre (Saint-Pierre-et-Miquelon) » ; correction à demander à Pactols ;
- **L'Île-des-Pins `98809`** : `prefLabel` « Île-des-Pins », `altLabel` « L'Île-des-Pins » ; distinction ontologique à surveiller.

Elles n'autorisent pas de généraliser l'équivalence entre îles et communes.

**Dembeni `97607`** : l'ARK `26678/crtZcuFSJVYZU` était initialement `ark_confirmes_non_valides`. L'audit en conditions réelles a désormais observé son **`skos:exactMatch` explicite vers `http://id.insee.fr/geo/commune/97607`**, avec `prefLabel` « Dembeni », sans dépréciation ni remplacement. Le lien peut donc être validé **à la fois sur décision éditoriale et preuve RDF indépendante**, sans créer d'exception au critère général.

## Publication

Cette PR est une **recette préalable non publiante** : l'index public contient encore **176 correspondances communales validées**, les quatre collectivités sont séparées. Une PR de publication devra gérer les garde-fous de l'interface, le manifeste, les tests et les scripts de reconstitution, sans modifier les géométries ni attribuer rétroactivement des ARK. Le RDF ayant attesté `97607` sans ambiguïté, les **36 nouvelles correspondances** peuvent désormais être publiées ensemble, sous réserve d'une recette de publication adaptée.
