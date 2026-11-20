# Normandie — lot 02, validation prudente des correspondances Pactols–COG 2026

**20 novembre 2026.** Suivi [#152](https://github.com/nicocoquet/adlfi-referentiels/issues/152), préflight [#154](https://github.com/nicocoquet/adlfi-referentiels/pull/154), premier lot [#155](https://github.com/nicocoquet/adlfi-referentiels/pull/155) et validation [#156](https://github.com/nicocoquet/adlfi-referentiels/pull/156), deuxième lot de qualification RDF [#158](https://github.com/nicocoquet/adlfi-referentiels/pull/158).

## Décision sur les dix dossiers

Le préflight du lot 02 a étudié **10 codes COG 2026 / 20 ARK concurrents**, concernant **49 occurrences AdlFI agrégées**. L'examen des identités, des définitions et de l'historique officiel conduit à valider **7 correspondances 2026**, et non les 10 proposées par leur seul libellé.

| Code actuel | Commune | Date de création vérifiée | Décision | Concept Pactols contemporain |
|---|---|---|---|---|
| [14035](https://www.insee.fr/fr/statistiques/2011101?geo=COM-14035) | Balleroy-sur-Drôme | 2016-01-01 | Validé pour 2026 | `26678/crts1h2V4fgZ4` |
| [14654](https://www.insee.fr/fr/statistiques/2011101?geo=COM-14654) | Saint-Pierre-en-Auge | 2017-01-01 | Validé pour 2026 | `26678/pcrtf4lulrxUo6` |
| [27471](https://www.insee.fr/fr/statistiques/2011101?geo=COM-27471) | Porte-de-Seine | 2018-01-01 | Validé pour 2026 | `26678/pcrtTVZxjfH4A1` |
| [50239](https://www.insee.fr/fr/statistiques/2011101?geo=COM-50239) | Thèreval | 2016-01-01 | Validé pour 2026 | `26678/pcrtPvLbdZBmws` |
| [61211](https://www.insee.fr/fr/statistiques/2011101?geo=COM-61211) | Juvigny Val d'Andaine | 2016-01-01 | Validé pour 2026 | `26678/pcrtQPOvb7fsR5` |
| [61341](https://www.insee.fr/fr/statistiques/2011101?geo=COM-61341) | Écouves | 2016-01-01 | Validé pour 2026 | `26678/pcrtsZJYVKHuCr` |
| [76258](https://www.insee.fr/fr/statistiques/2011101?geo=COM-76258) | Terres-de-Caux | 2017-01-01 | Validé pour 2026 | `26678/pcrt9wS8mfBRqs` |

Pour chaque code, `skos:exactMatch` du concept contemporain renvoie au code INSEE actuel, `skos:historyNote` atteste explicitement la **création de la commune nouvelle** à la date confirmée par l'Insee, et un ARK distinct désigne l'ancienne commune ou la commune déléguée. Aucune identité ancienne n'est promue. **Saint-Pierre-en-Auge** impose un contrôle particulier : la note de création du RDF se situe au-delà des 1 600 caractères conservés par l'audit exploratoire ; le nouveau validateur relit la note source intégralement et en conserve son empreinte SHA-256.

## Trois exceptions maintenues

1. **Isigny-sur-Mer (`14342`)**. L'ARK candidat `26678/pcrtJiEVVL4S0d` possède une note historique sur la création de 2017, **mais sa définition décrit aussi une ancienne commune**, et des `exactMatch` documentent la commune déléguée. Le concept concurrent `26678/pcrtOlN1ZN3BqW` est explicitement intitulé « Isigny-sur-Mer (commune déléguée) ». L'identité de la commune nouvelle ne peut être validée sur le seul nom et code conservés ; vérifier les réemplois de Wikidata/DBpedia, puis arbitrer.
2. **Breteuil (`27112`)**. L'ARK candidat contemporain `26678/pcrtwD0OalOHGK` et l'ARK de la commune déléguée `26678/pcrtKa9QelswXe` ont un `skos:exactMatch` commun vers **Wikidata Q467162**, alors que leurs définitions et la création au **1er janvier 2016** les distinguent. Il faut réconcilier les références externes avant publication, malgré le `exactMatch` INSEE partagé.
3. **Bourgvallées (`50546`)**. Le concept courant `26678/pcrtgtbpJSZPKx` décrit la création initiale au **1er janvier 2016**, mais le dossier Insee du COG 2026 enregistre une **nouvelle création au 1er janvier 2019** (Bourgvallées, Le Mesnil-Herman et Soulles). Le maintien du code `50546` ne prouve pas que l'ARK décrivant l'identité 2016 couvre sans réserve l'identité administrative issue de 2019. Distinguer les états et les relations avant d'approuver 2026.

Sources Insee : [Isigny-sur-Mer, 14342](https://www.insee.fr/fr/statistiques/2011101?geo=COM-14342), [Breteuil, 27112](https://www.insee.fr/fr/statistiques/2011101?geo=COM-27112), [Bourgvallées, 50546](https://www.insee.fr/fr/statistiques/2011101?geo=COM-50546). Les autres dates ont été comparées aux dossiers officiels de chaque commune (liens par ligne ci-dessus).

## Registre et recette

- Registre : `docs/data/lieux-chronologie/pactols-normandie-lot02-2026.json`, schéma `adlfi.lieux.pactols.normandie.lot02.2026.public.v1`, **7 alignements** et **3 exceptions documentées**.
- Source : RDF Frantiq/PACTOLS du 22 juillet 2026, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- Générateur `scripts/valider_normandie_lot02_pactols_2026.py`, tests `tests/test_valider_normandie_lot02_pactols_2026.py`. Contrôles bloquants : changement des vingt candidats, divergence d'ARK et de note, mauvaise empreinte RDF, absence de note complète de Saint-Pierre-en-Auge, suppression des contradictions non réexaminées et chevauchement du registre du lot 01.
- Deux exécutions du script sont comparées octet par octet, puis comparées au registre publié. Source publique seulement : aucun fichier AdlFI contenant des identifiants de notices n'est versé au dépôt.

## Limites impératives

**Cumul des deux premiers lots : 16 correspondances 2026 validées**, et 4 dossiers suspendus, dont Port-Bail-sur-Mer au lot 01. Il ne s'agit pas de 16 alignements territoriaux pour toutes les années : aucun ARK ancien n'est converti en alias, aucun lien historique n'est inféré, aucun contour n'est créé dans cette PR.

Les nouveaux alignements demeurent **non activés dans le moteur cartographique** (`active_dans_interface=false`), le temps que les contours normands officiels 2026 et les états COG correspondants soient disponibles. Cette séparation interdit à une fiche de montrer un alignement contemporain comme identité historique d'une opération ancienne.

Pour la suite, priorités : (a) résoudre les quatre exceptions suspendues sur preuves RDF et COG, (b) préparer l'acquisition vérifiable des géométries 2026 de Normandie et leur découpage par région pour le chargeur progressif introduit dans [#157](https://github.com/nicocoquet/adlfi-referentiels/pull/157).
