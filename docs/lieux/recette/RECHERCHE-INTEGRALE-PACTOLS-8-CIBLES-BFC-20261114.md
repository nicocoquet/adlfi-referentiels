# Bourgogne-Franche-Comté — résolution documentaire des 14 réceptions sans ARK cible dans le corpus XML

**14 novembre 2026 — PR n°24 — recette non validante.**

## Source officielle retrouvée et contrôlée

Le référentiel Pactols-Lieux **intégral**, et non les seuls 9 928 ARK terminaux indexés dans les XML AdlFI, est disponible en RDF/XML dans le dépôt public officiel Frantiq :

`frantiq/PACTOLS/pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf`

- Export : **22 juillet 2026**, thésaurus `th17`.
- Git LFS, empreinte SHA-256 du **contenu RDF complet** : `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- L'exécution [GitHub Actions n°43631692743](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43631692743) a vérifié l'empreinte et parcouru **50 691 concepts**.
- **Huit codes Insee**, correspondant aux **14 événements de réception** à qualifier. La recherche par `skos:prefLabel@fr`, `skos:altLabel@fr` et `skos:exactMatch` a retourné **16 concepts candidats**.
- Code de recherche : `scripts/rechercher_8_cibles_bfc_pactols_th17.py`; code de rapprochement : `scripts/rapprocher_relations_bfc_pactols_integral.py`. Le rapprochement est exécuté deux fois puis comparé octet pour octet en CI.

Ce millésime commun aux audits nationaux initiaux est un choix de **reproductibilité**. Le thésaurus en ligne est actualisé depuis : **l'absence d'un concept de cet export ne permet pas de conclure à son absence actuelle**.

## Huit communes réceptrices : résultats

| Code Insee | Nom de la commune réceptrice dans le mouvement COG | ARK retrouvé dans le RDF intégral | Preuve sur cet ARK | Dossiers concernés |
| --- | --- | --- | --- | ---: |
| `25147` | Chemaudin et Vaux | `26678/pcrt9z3xOVhDld` | `prefLabel` concordant et `exactMatch` Insee `25147` | 1 |
| `39021` | La Chailleuse | `26678/pcrt9DowIYo99D` | `prefLabel` + `exactMatch` `39021` | 3 |
| `39137` | Saint-Hymetière-sur-Valouse | `26678/pcrt80xbz0p4vht8kdd4mtdx` | **`prefLabel` concordant, mais pas d'URI Insee numérique sur ce concept** | 3 |
| `39177` | Hauteroche | `26678/pcrtdDWDTOLZXu` | `prefLabel` **« Hauteroche (Jura) »** + `exactMatch` `39177` | 1 |
| `39290` | Valzin en Petite Montagne | `26678/pcrtdFtNcN7Gnz` | `prefLabel` + `exactMatch` `39290` | 3 |
| `39485` | Val Suran | `26678/pcrtWvk9K2hoR8` | `prefLabel` + `exactMatch` `39485` | 1 |
| `39530` | Thoirette-Coisia | `26678/pcrtDZOBLPOlUP` | `prefLabel` + `exactMatch` `39530` | 1 |
| `71566` | Verdun-Ciel | **Aucun concept portant ce nom retrouvé dans le snapshot** | `71566` demeure un `exactMatch` du concept historique **Verdun-sur-le-Doubs** (`26678/pcrtoFlfDwt01N`) | 1 |
| | **Total** | **7 cibles nominales identifiées** | | **14** |

### Une séparation indispensable entre code Insee et nom du concept

Outre les sept cibles nominales, l'export contient plusieurs concepts historiques partageant le code Insee de la commune nouvelle :

- `25147` : **Chemaudin**, outre Chemaudin et Vaux ;
- `39021` : **Arthenas**, outre La Chailleuse ;
- `39137` : **Chemilla** porte le code ; Saint-Hymetière-sur-Valouse a un ARK distinct **sans assertion de code numérique** ;
- `39177` : **Crançot** porte le code, outre Hauteroche (Jura) ; **Hauteroche (Côte-d'Or)** est une homonymie supplémentaire avec le code **`21314`** ;
- `39290` : **Légna**, outre Valzin en Petite Montagne ;
- `39485` : **Saint-Julien (Val Suran)**, outre Val Suran ;
- `39530` : **Thoirette**, outre Thoirette-Coisia ;
- `71566` : **Verdun-sur-le-Doubs** ; **aucun concept « Verdun-Ciel » identifié par nom** dans le RDF du 22 juillet 2026.

Un algorithme qui prendrait le **premier ARK associé au code** créerait des relations historiques incorrectes. Le rapprochement exige une correspondance de libellé en plus du contexte COG. Une concordance de nom ne représente toutefois **qu'une candidature**, jamais une validation.

## Rapprochement des 14 dossiers

| Niveau de preuve documentaire | Dossiers | Décision automatisée |
| --- | ---: | --- |
| `prefLabel` exact et code `exactMatch` concordant | **9** | ARK cible candidat conservé, non validé |
| `prefLabel` qualifié « Jura » et code concordant | **1** | ARK cible candidat conservé, homonymie « Côte-d'Or » exclue |
| `prefLabel` exact mais aucun code `exactMatch` sur cet ARK | **3** | ARK cible candidat **à vérifier prioritairement** ; cas Saint-Hymetière-sur-Valouse |
| Code `exactMatch` porté par une commune historique de libellé différent | **1** | **Aucune cible ARK proposée** : Ciel → Verdun-Ciel |
| **Total** | **14** | **13 propositions**, **1 dossier ouvert** |

Les 13 propositions couvrent **sept communes réceptrices**. La correspondance avec des concepts non terminaux du corpus AdlFI explique pourquoi le rapprochement précédent n'avait identifié aucune cible pour ces 14 dossiers.

### Cas ouvert : Ciel → Verdun-Ciel

Le mouvement officiel `MOD=32` du **1er janvier 2025** relie Ciel (`71131`) à **Verdun-Ciel (`71566`)**. Dans le RDF du **22 juillet 2026**, le code `71566` apparaît sur l'ARK de **Verdun-sur-le-Doubs**, ancienne commune, et le nom **Verdun-Ciel** n'apparaît ni comme libellé préféré ni comme variante dans les résultats de recherche.

Il serait méthodologiquement incorrect de remplacer automatiquement le concept de commune nouvelle par celui de Verdun-sur-le-Doubs. **Action éditoriale à envisager :** vérifier d'abord le thésaurus Pactols en ligne à la date de l'instruction, puis, seulement si le concept manque effectivement, signaler le besoin d'une autorité distincte à Frantiq. Aucun ARK ne doit être inventé par AdlFI.

## Livrables et provenance

La [CI spécialisée](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43631692743) (réussie) conserve un artefact `audit-bfc-8-cibles-pactols-th17-20260722` :

- `candidats-pactols-th17-bfc.csv` : **16 entrées** avec les ARK, les libellés, les URI `exactMatch`, les parents SKOS et le statut de dépréciation détecté ;
- `synthese-8-cibles.csv` : bilan par commune réceptrice ;
- `rapprochement-14/rapprochement-bfc-14-th17.csv` : les **14 autorités sources**, les codes et dates des mouvements, la preuve COG et la cible ARK éventuelle ;
- rapports JSON et synthèse de recette.

Toutes les sources et sorties sont vérifiées par empreinte ou par cardinalités, et le rapprochement a été généré deux fois de manière identique.

**Statut : 0 alignement éditorial nouvellement validé, 0 géométrie historique attribuée, 0 modification des fichiers publics du module Lieux.** La PR n°24 reste en brouillon.
