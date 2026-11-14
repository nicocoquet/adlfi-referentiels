# Bourgogne-Franche-Comté — qualification des relations historiques candidates entre ARK Pactols

**14 novembre 2026 — PR n°24 — recette non validante, non publiée.**

## Sources et portée

La procédure `scripts/qualifier_relations_ark_bfc.py` croise :
1. l'inventaire régional des **736 ARK terminaux** (`inventaire-bourgogne-franche-comte.csv`) ;
2. les **25 anciens codes** et leurs **42 lignes de mouvements avant/après**, produits dans `instruction-exceptions/` ;
3. les deux cas de **code réutilisé pour deux ARK** (`25368` Marchaux/Marchaux-Chaudefontaine ; `25529` Sancey-le-Grand/Sancey) ;
4. les deux communes associées **Antorpe** (`39012`) et **Frettes** (`52210`), avec leur `COMPARENT` au COG 2026.

Les **cinq sources sont contrôlées par SHA-256**, et les sorties ont été générées deux fois puis comparées octet par octet dans [GitHub Actions — audit BFC du 14 novembre](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43629844760).

**La concordance d'un code n'est pas une identité historique. La concordance d'un libellé n'est pas une validation éditoriale.** Cette procédure est un outil de *candidature* pour l'éditeur, non un générateur d'alignements définitifs.

## Résultat : 29 propositions de relations administratives

| Famille | Dossiers | ARK cible proposé | Sans ARK cible proposé |
| --- | ---: | ---: | ---: |
| Réceptions administratives immédiates des 25 anciens codes (`MOD 31/32/33`) | **25** | **11** | **14** |
| Réutilisation d'un code pour deux concepts distincts de commune (`MOD 32`) | **2** | **2** | 0 |
| Rattachement de commune associée au COG 2026 (`COMA`/`COMPARENT`) | **2** | **2** | 0 |
| **Total** | **29** | **15 candidats** | **14 à instruire** |

Les **14** sans cible univoque parmi les 25 anciens codes se décomposent en **neuf** codes correspondant à un ARK du corpus mais avec un **libellé différent**, et **cinq** destinations absentes de la liste des 736 concepts *terminaux*. Cette absence ne prouve pas leur absence du thésaurus Pactols.

### Onze réceptions avec cible ARK lexicalement concordante

| Ancien concept | Commune immédiatement réceptrice selon Insee | Signal documentaire |
| --- | --- | --- |
| Arcier | Vaire-Arcier | Code présent, libellé correspondant à l'état historique |
| Arguel (Doubs) | Fontain | Code + libellé |
| Champvans-les-Baume | Baume-les-Dames | Code + libellé |
| Châtillon-sur-Lison | Cussey-sur-Lison | Code + libellé |
| Chaudefontaine | Marchaux-Chaudefontaine | Code + libellé ; le même code porte aussi Marchaux |
| Droitfontaine | Belleherbe | Code + libellé |
| Sancey-le-Long | Sancey | Code + libellé ; le même code porte aussi Sancey-le-Grand |
| Vauchamps | Bouclans | Code + libellé ; statut `COMD` supprimé plus tard |
| Chisséria | Arinthod | Code + libellé |
| Sézéria | Orgelet | Code + libellé |
| Gonvillars | Saulnot | Code + libellé ; statut `COMA` intermédiaire |

**Précaution :** le libellé `Vaire-Arcier` est celui du récepteur *au moment du mouvement*, pas nécessairement du `COM` actuel : le code `25575` porte aujourd'hui un libellé différent (`Vaire`). Les candidats sont donc **datés**, même lorsque le code demeure identique.

### Neuf réceptions : code présent mais libellé non concordant

| Ancien concept | Récepteur Insee | Libellé Pactols actuellement observé sur ce code |
| --- | --- | --- |
| Vaux-les-Prés | Chemaudin et Vaux (`25147`) | Chemaudin |
| Cézia | Saint-Hymetière-sur-Valouse (`39137`) | Chemilla |
| Chatonnay | Valzin en Petite Montagne (`39290`) | Légna |
| Coisia | Thoirette-Coisia (`39530`) | Thoirette |
| Fétigny | Valzin en Petite Montagne (`39290`) | Légna |
| Lavans-sur-Valouse | Saint-Hymetière-sur-Valouse (`39137`) | Chemilla |
| Mirebel | Hauteroche (`39177`) | Crançot |
| Saint-Hymetière | Saint-Hymetière-sur-Valouse (`39137`) | Chemilla |
| Savigna | Valzin en Petite Montagne (`39290`) | Légna |

**Décision automatique : aucune cible ARK attribuée.** Ces neuf cas montrent le risque d'appliquer un même code communal à un concept qui représente en réalité une ancienne commune différente. Pour chacun, l'éditeur devra rechercher le concept de commune nouvelle dans Pactols (hors corpus XML terminal si nécessaire), sans remplacer l'ARK historique.

### Cinq récepteurs sans ARK terminal dans le corpus BFC

| Ancien concept | Récepteur identifié par le COG | Code récepteur |
| --- | --- | --- |
| Essia | La Chailleuse | `39021` |
| Saint-Laurent-la-Roche | La Chailleuse | `39021` |
| Varessia | La Chailleuse | `39021` |
| Villechantria | Val Suran | `39485` |
| Ciel | Verdun-Ciel | `71566` |

Il ne faut **ni créer un ARK fictif ni déduire de ce tableau que Pactols ne contient pas ces concepts**. Il décrit seulement les concepts terminaux des XML AdlFI convertis à ce stade.

## Les quatre autres candidatures

**Deux codes réutilisés (suite historique à instruire entre deux concepts)** :
- `25368` : Marchaux → Marchaux-Chaudefontaine, **2018-01-01** ;
- `25529` : Sancey-le-Grand → Sancey, **2016-01-01**.

**Deux rattachements administratifs, qui ne sont pas des relations de succession entre concepts** :
- `39012` Antorpe : `COMA`, `COMPARENT=25527` Saint-Vit au COG 2026, fusion-association initiale **1974-06-01** ;
- `52210` Frettes : `COMA`, `COMPARENT=70122` Champlitte au COG 2026, fusion-association initiale **1974-07-01**.

Ces deux liens documentent un **rattachement**, pas une équivalence entre Antorpe et Saint-Vit ou entre Frettes et Champlitte.

## Données livrées et garde-fous

Le nouveau sous-dossier `relations-candidates/` de l'artefact GitHub Actions `audit-lieux-bfc-736-cog2026` comprend :

- `candidatures-relations-bfc-29.csv` : 29 dossiers, date et modalité COG, codes avant/après, preuve de mouvement et liste des ARK présents sur le code cible ;
- `candidatures-ark-ark-bfc-15.csv` : 15 **propositions** de cible ARK, aucune validée ;
- `dossiers-sans-cible-univoque-bfc-14.csv` : 14 dossiers à documenter sans création automatique de relation ;
- `rapport-relations-bfc.json` : cardinalités, empreintes et limites.

Le script conserve la preuve `identifiant_ligne_cog` pour les réceptions des 25 anciens codes. Il ne transforme **pas** les `MOD=35` (suppression de commune déléguée), `MOD=10` (changement de nom) ni les `COM → COMD/COMA` simultanés en nouvelles successions entre ARK ; ces **42 lignes originales** restent disponibles séparément.

Les relations candidates sont définies par une **égalité lexicale normalisée** (accents, espaces, apostrophes, traits d'union), jamais par une égalité sémantique présumée. Même les 15 cibles proposées nécessitent examen de la portée de chaque concept Pactols et de l'historicité du lieu dans le corpus.

**Résultat : 0 nouvel alignement AdlFI validé, 0 géométrie historique créée, 0 modification des données GitHub Pages.**

## Mise à jour : vérification dans le Pactols-Lieux intégral du 22 juillet 2026

La recherche exhaustive dans **50 691 concepts**, validée par SHA-256 et GitHub Actions, a identifié **sept communes réceptrices distinctes possédant un ARK au libellé concordant**. Cela permet de proposer **13 nouvelles cibles ARK** pour les **14 réceptions précédemment laissées sans ARK univoque** ; les **trois** dossiers de Saint-Hymetière-sur-Valouse demandent notamment un contrôle supplémentaire, le concept retrouvé ne déclarant pas l'URI Insee numérique.

**Verdun-Ciel (`71566`)** reste ouvert dans le snapshot 2026-07-22 : le code est déclaré sur le concept historique Verdun-sur-le-Doubs, pas sur un concept de ce nouveau nom. Ne pas conclure à une absence dans le thésaurus vivant sans vérification ultérieure.

Le rapport complet, ses ARK, ses signaux lexical/INSEE et sa provenance sont dans `RECHERCHE-INTEGRALE-PACTOLS-8-CIBLES-BFC-20261114.md`. **Aucun de ces 13 candidats n'est éditorialement validé.**

## Étape éditoriale conseillée

La priorité est de vérifier, dans le thésaurus Pactols complet, les **neuf récepteurs à code partagé mais libellé discordant** et les **trois communes nouvelles distinctes absentes de notre corpus terminal** (La Chailleuse, Val Suran, Verdun-Ciel). Ce travail doit précéder toute validation de relations historiques dans le module Lieux.

La branche reste en recette ; PR n°24 non fusionnée.
