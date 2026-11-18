# Pays de la Loire — Baugé-en-Anjou et Montsûrs : états administratifs homonymes

**18 novembre 2026 — instruction documentaire non validante.** Complément de la PR #149 ; aucune modification de `docs/data`, aucune validation d'ARK supplémentaire. Couverture publique : **1 217 / 1 228**.

## Baugé-en-Anjou (49018)

L'Insee établit une commune actuelle créée **le 1er janvier 2016** ; les séries COG versionnées signalent également une création de Baugé-en-Anjou le **1er janvier 2013**, suivie de l'extension/création de 2016. Le **même code** et le **même libellé** ne constituent donc pas des preuves de continuité territoriale.

- Candidat Pactols au libellé courant dans l'audit existant : `26678/crtw3s8jkTOZ8` (Baugé-en-Anjou).
- Concept distinct : `26678/pcrthdy1gGxlIV` (Baugé ancienne commune).
- L'audit antérieur constate une définition Pactols faisant référence à 2013, mais **ne démontrant pas à elle seule la portée 2016**. La présence du concept Loterre « Baugé-en-Anjou » avec une définition mentionnant la création au 01/01/2016 est un indice externe pertinent : [Loterre D63, Baugé-en-Anjou](https://loterre.istex.fr/D63/fr/page/-WPLH5T42-D). En l'absence d'une équivalence RDF explicite contrôlée entre ce concept et l'ARK Pactols candidat, il ne justifie pas sa promotion.
- Sources Insee : [fiche géographique, création 2016](https://www.insee.fr/fr/metadonnees/geographie/commune/49018-bauge-en-anjou), [dossier communal](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49018).

**Décision provisoire :** conserver l'exception 49018, ne pas attribuer automatiquement `26678/crtw3s8jkTOZ8` à l'état territorial de 2016–2026.

## Montsûrs (53161)

L'Insee confirme la création au **1er janvier 2019**, par réunion de **Deux-Évailles (53092), Montourtier (53159), Montsûrs-Saint-Céneré (53161) et Saint-Ouën-des-Vallons (53244)**. Avant cela, l'ancienne Montsûrs devient commune déléguée de Montsûrs-Saint-Céneré au **1er janvier 2017**.

- Ancienne commune Montsûrs : `26678/pcrt2VftxEe5uH`.
- Commune de Montsûrs-Saint-Céneré (2017–2018) : `26678/pcrtzZXdqdUiXm`.
- Aucun ARK **qualifié** pour Montsûrs nouvelle commune de 2019 dans les audits versés au dépôt. Il serait erroné de réutiliser l'ARK de la commune avant 2017 par simple identité de nom.
- Sources Insee : [fiche géographique, création 2019](https://www.insee.fr/fr/metadonnees/geographie/commune/53161-montsurs), [dossier communal et compositions](https://www.insee.fr/fr/statistiques/2011101?geo=COM-53161).

**Décision provisoire :** aucune promotion ; maintien de l'exception 53161 et recherche explicite d'une autorité contemporaine distincte.

## Règle de modélisation confirmée

Une ligne `periodes_com` exprimant un **intervalle de dénomination** n'est pas un identifiant pérenne pour chaque **état administratif et territorial**. La carte historique devra distinguer source d'autorité, épisode de commune, événement COG et disponibilité de la géométrie correspondante. Les contours contemporains ne devront pas être présentés comme restitutions historiques.

## Pour lever les exceptions

1. Contrôler dans `Pactols_Lieux_th17_20260722.rdf` (SHA256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`) tous les liens (`exactMatch`, tiers, UUID), notes et définitions des ARK cités.
2. Établir une équivalence explicite et vérifiée si Loterre/Wikidata fournit une identité actuelle qualifiée ; dater et figer la provenance.
3. Vérifier les épisodes et mouvements du `cog-pdl.json` versionné ; ne pas inférer la continuité du seul code.
4. Ne publier dans l'index 2026 qu'après registre nominatif, régénération déterministe, tests d'unicité, CI et navigation Chromium.

**Limite de la présente instruction :** sources Insee consultées et audits GitHub antérieurs exploités ; extraction RDF spécialisée et CI **non exécutées ici**.

**Suite :** décision sur les sept autres exceptions restantes, puis clôture documentaire PDL avec reliquat motivé et reprise de l'interface web Lieux.
