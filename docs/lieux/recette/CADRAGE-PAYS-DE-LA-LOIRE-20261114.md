# Lieux — Pays de la Loire : premier cadrage historique documenté (14 novembre 2026)

**Statut : instruction non validante, PR n°24 en brouillon.** Aucun changement de `docs/data/lieux.json`, des géométries ou des assertions validées AdlFI.

## Périmètre

L'extraction XML AdlFI v2 comprend **806 ARK terminaux**, **3 007 occurrences**, **2 108 notices distinctes** et **55 fichiers XML**, selon `rapport-priorites-regionales.json`. Sur les 806 autorités, **797** portent une assertion Pactols `skos:exactMatch` vers une URI Insee de commune à code lisible et **9** n'en portent pas. **Ces 797 liens sont des assertions Pactols et non des validations AdlFI.** Un premier échantillon de 25 ARK est dans `lot-01-pays-de-la-loire.csv`.

Ventilation hiérarchique : Loire-Atlantique 153, Maine-et-Loire 194, Mayenne 101, Sarthe 190, Vendée 167, autorité non départementale 1. Les valeurs sont des ARK de la hiérarchie Pactols, **pas** des nombres de communes administratives.

Le référentiel officiel est le COG au 1er janvier 2026 : https://www.insee.fr/fr/information/8740222. Les sources nationales employées en Corse (`v_commune_2026.csv`, `v_commune_depuis_1943.csv`, `v_mvt_commune_2026.csv`) doivent être reprises, avec les mêmes empreintes vérifiées ; conserver le type `TYPECOM` lors des jointures.

## Premières preuves ponctuelles (contrôle des autorités du lot 25)

| Concept Pactols | ARK | Identifiant / état officiel | Preuve et conséquence |
| --- | --- | --- | --- |
| Cherré-Au | `26678/pcrtk5xjv8vgwk9w8fmrz9z3` | `COM 72080`, créée le **2019-01-01** | Nouvelle commune regroupant **Cherré (72080)** et **Cherreau (72081)**, devenues communes déléguées. Le même code `72080` ne signifie pas que Cherré avant 2019 et Cherré-Au depuis 2019 sont des entités administratives interchangeables. https://www.insee.fr/fr/statistiques/2011101?geo=COM-72080 |
| Thouarsais-Bouildroux | `26678/pcrtRm3hz8YCOM` | `COMD 85292` au COG 2026 ; `COMPARENT 85292` | Commune déléguée de **Rives-du-Fougerais (COM 85292)** depuis **2024-01-01** ; antérieurement commune. La même chaîne numérique correspond à deux types d'entités : `TYPECOM` est indispensable. L'URI `communeDeleguee/ef312e8c-b172-40ed-b169-8bf72e16ba8b` de Pactols doit être conservée en provenance. https://www.insee.fr/fr/metadonnees/geographie/commune-deleguee/85292-thouarsais-bouildroux ; https://www.insee.fr/fr/statistiques/2011101?geo=COM-85292 |
| Grandchamp-des-Fontaines | `26678/pcrt99dzcmxdhR` | `COM 44066` | **Changement de nom** au **2023-01-01** : `Grandchamps-des-Fontaines` → `Grandchamp-des-Fontaines`. La « date de création » affichée dans la fiche du nom courant ne doit **pas** être interprétée comme preuve d'une fusion ou d'un changement de contour. L'URI Pactols UUID `commune/493ed29c-e150-4c2e-9880-f94d7002f1f5` reste une assertion distincte du code `44066`, à vérifier par le COG. https://www.insee.fr/fr/statistiques/2011101?geo=COM-44066 |
| Le Puy-Saint-Bonnet | `26678/pcrtthzSDyCh4Z` | `COMA 79224`, commune associée à **Cholet (COM 49099)** depuis **1973-09-01** | Code ancien du département des Deux-Sèvres conservé officiellement : **ne pas le transformer en code de Maine-et-Loire**. https://www.insee.fr/fr/metadonnees/geographie/commune-associee/79224-le-puy-saint-bonnet |

## Contrôles documentaires distincts

- **Béthon** est bien une autorité Pactols distincte (`26678/pcrtGHlbdiOta1`), assertion `72036`. L'hypothèse de confusion **Bethon/Béthon** dans la notice *Autoroute A28* doit être vérifiée au niveau TEI avant correction documentaire.
- **Brain/Brains** relève d'une autre notice, *Pays de Retz* (2008), qui comporte 35 autres localisations en Loire-Atlantique. Le signalement est documenté dans `ANOMALIE-BRAIN-PAYS-DE-RETZ-2008.md`. Ne pas modifier l'autorité `Brain` (Côte-d'Or) au seul motif de cette occurrence.
- La **date de l'opération archéologique ne date pas la commune** ; elle décrit l'attestation documentaire.
- Un `skos:exactMatch` déclaré par Frantiq ne certifie ni le type historique ni la géométrie au moment de l'opération.

## Plan d'audit reproductible du lot régional entier

1. Constituer et figer un **inventaire des 806 ARK** à partir des trois CSV de l'extraction v2 dont les empreintes sont dans `rapport-priorites-regionales.json` ; ne pas prendre le lot pilote de 25 comme s'il s'agissait de tout le corpus.
2. Joindre l'assertion Insee Pactols à `v_commune_2026.csv` sur **code ET `TYPECOM`**, puis aux périodes `v_commune_depuis_1943.csv` et aux mouvements `v_mvt_commune_2026.csv`. En cas d'URI UUID, rechercher la preuve et conserver l'URI source ; ne pas déduire un identifiant à partir du libellé seul.
3. Produire une ligne par ARK et **des épisodes temporels distincts par (TYPECOM, COM, libellé, période)**, en conservant le code parent `COMPARENT` lorsqu'il est défini. Les mouvements de fusion/succession sont des relations explicites et non de simples variantes lexicales.
4. Sortir des tableaux séparés : correspondances contemporaines, événements administratifs, épisodes code–libellé, cas non communaux, divergences de noms, conflits d'identité et dossiers TEI à relire. Dédupliquer les opérations avant toute statistique de fusions.
5. Ajouter tests automatisés : même code COM/COMD ; changement de dénomination sans fusion ; ancienne commune associée hors département ; commune nouvelle et prédécesseur partageant un code ; URI UUID non résolue ; anti-écrasement des validations et des géométries.
6. Exécuter en GitHub Actions comme pour la Corse, **archives de recette uniquement**, puis instruire les exceptions avant toute publication.

**Point de dépendance :** à ce stade, la branche contient l'inventaire régional de **25 ARK** et les **compteurs** des 806, mais pas l'inventaire régional intégral des 806 en tant que CSV. Le calcul des résultats exhaustifs régionaux doit attendre la reconstruction de ce fichier à partir des sources v2, ou leur disponibilité effective dans un workflow. Ne pas extrapoler les résultats du pilote à la population complète.

## Sources internes

- `docs/lieux/recette/PRIORITES-REGIONALES-20261114.md`
- `docs/lieux/recette/rapport-priorites-regionales.json`
- `docs/lieux/recette/lot-01-pays-de-la-loire.csv`
- `docs/lieux/recette/ANOMALIE-BRAIN-PAYS-DE-RETZ-2008.md`
- `docs/lieux/recette/BILAN-CORSE-200-COMMUNES-20261114.md`
