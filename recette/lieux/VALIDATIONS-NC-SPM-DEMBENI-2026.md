# Arbitrages AdlFI — Nouvelle-Calédonie, Saint-Pierre-et-Miquelon et Dembeni

**17 novembre 2026 — 36 ARK examinés dans ce registre, mais deux niveaux de preuve distincts.**

L'éditeur a explicitement confirmé trois ARK supplémentaires :
- **`98809` L'Île-des-Pins** ↔ `26678/pcrti4LqTHByEs` ;
- **`97501` Miquelon-Langlade** ↔ `26678/pcrtQAMzeGHldU` ;
- **`97607` Dembeni** ↔ `26678/crtZcuFSJVYZU`.

L'arbitrage de **`97502` Saint-Pierre** ↔ `26678/pcrtYQmFfwxLq8` est déjà consigné dans la PR 93. Les **32 autres communes de Nouvelle-Calédonie** ont une preuve RDF `skos:exactMatch` univoque, sans dépréciation, classée éligible par [l'audit PR 94](NOUVELLE-CALEDONIE-PACTOLS-33-2026.md).

## Distinction obligatoire entre identifiant confirmé et équivalence RDF

Le registre [VALIDATIONS-NC-SPM-DEMBENI-2026.csv](VALIDATIONS-NC-SPM-DEMBENI-2026.csv) conserve **35 décisions `VALIDE_ADLFI_2026`** appuyées par une assertion `skos:exactMatch` en RDF : **33 en Nouvelle-Calédonie, 2 à Saint-Pierre-et-Miquelon**. Parmi ces 35, deux exceptions sont assumées éditorialement :

- Saint-Pierre, `97502`, `prefLabel` actuel **« île Saint-Pierre (Saint-Pierre-et-Miquelon) »**, correction à demander à Pactols ;
- L'Île-des-Pins, `98809`, `prefLabel` **« Île-des-Pins »**, `altLabel` **« L'Île-des-Pins »**, malgré la possible divergence entre objet insulaire et commune administrative.

Ces deux exceptions sont **nominatives** et ne justifient pas de généraliser une correspondance île/commune.

**Dembeni `97607` :** l'éditeur valide formellement l'ARK `26678/crtZcuFSJVYZU`, qui était déjà présent en `ark_confirmes_non_valides`. À la date de cette décision, la présence d'un `skos:exactMatch` pour l'URI `http://id.insee.fr/geo/commune/97607` **n'était pas certifiée**. Le statut est donc `VALIDE_ARK_EDITORIAL` jusqu'au contrôle du RDF. L'ARK ne doit pas être promu automatiquement en équivalence COG par simple confirmation éditoriale.

La CI `lieux-decisions-nc-spm-mayotte.yml` vérifie la source RDF originale SHA-256, confronte les 36 lignes et **affiche explicitement le résultat du contrôle Dembeni**. Toute absence ou contradiction exige une instruction complémentaire.

## Publication

Cette PR est une **recette préalable non publiante** : l'index public contient encore **176 correspondances communales validées**, les quatre collectivités sont séparées. Une PR de publication devra gérer les garde-fous de l'interface, le manifeste, les tests et les scripts de reconstitution, sans modifier les géométries ni attribuer rétroactivement des ARK. Si le RDF atteste aussi `97607` sans ambiguïté, les 36 nouvelles correspondances pourront être publiées ensemble ; sinon, seules les **35 équivalences fondées sur `exactMatch`** pourront l'être dans ce lot.
