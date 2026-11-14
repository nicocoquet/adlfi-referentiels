# Référentiel Lieux AdlFI — graphe historique transversal BFC

**14 novembre 2026 — modèle de recette v1 ; PR n°24 en brouillon.**

## Objet et unités de comptage

Le générateur **scripts/consolider_evenements_bfc_p1_p2_p3.py** harmonise les préinstructions de P1, P2 et P3 en conservant leurs 29 candidatures initiales. Le validateur indépendant **scripts/valider_graphe_historique_bfc.py** vérifie les références de bout en bout.

| Objet | Nombre |
| --- | ---: |
| Candidatures P1 / P2 / P3 | 4 / 5 / 20 |
| Candidatures avec ARK cible proposé | **28** |
| Sans ARK cible (Verdun-Ciel) | **1** |
| Groupes d'événements initiaux | **21** |
| Groupes d'événements ultérieurs | **7** |
| **Groupes administratifs distincts** | **28** |
| **Lignes COG distinctes** | **86** |
| États type–code–libellé observés | **83** |
| Références historiques d'événements conservées | **30** |
| Chevauchements P2/P3 dédoublonnés | **2** |
| Candidatures liées à un événement ultérieur | **9** |

Un groupe est identifié par la date d'effet, la modalité MOD et le code de la commune réceptrice. Il s'agit d'une **unité technique de regroupement des lignes COG, non nécessairement d'un acte juridique distinct**.

Les deux chevauchements P2/P3 correspondent à Sancey (2016-01-01) et Marchaux-Chaudefontaine (2018-01-01). Les quatre lignes de mouvements communes à ces deux dossiers sont dédoublonnées.

## Collections et identifiants du JSON

| Collection | Identifiant | Description |
| --- | --- | --- |
| **relations_candidates** | Identifiant de candidature d'origine | Source et cible ARK éventuelle, nature de relation proposée, preuves et décisions vides |
| **evenements** | BFC-COG-AAAA-MM-JJ-MOD-CODE | Groupe daté de mouvements, commune réceptrice, modalité et phase initiale/ultérieure |
| **mouvements** | Empreinte dérivée des 14 champs COG | Transition officielle avant/après, associée à un événement et deux états |
| **etats** | Empreinte du triplet TYPECOM, code et libellé | Observation administrative ; **ni une autorité pérenne ni une période géographique complète** |
| **alias_identifiants_evenements** | Couple lot et ancien identifiant | Correspondance vers l'identifiant canonique, avec référence juridique P1 lorsqu'elle est disponible |

Deux listes **nouvelles_validations** et **geometries_historiques** sont explicitement vides. Les 83 états observés ne constituent pas 83 communes et n'attestent aucune géométrie : c'est la transition officielle qui porte la date.

Les 30 alias d'anciens événements sont conservés, y compris ceux qui renvoient deux fois au même événement partagé par P2 et P3.

## Typologie proposée pour le référentiel

Les types ci-dessous sont des **valeurs de recette**, non des propriétés SKOS :

| MOD | Catégorie proposée | Sens |
| --- | --- | --- |
| 31 | participation_fusion_simple | Participation à une fusion simple, sans équivalence d'identité |
| 32 | participation_mouvement_commune_nouvelle | Création ou extension de commune nouvelle ; le code peut être conservé |
| 33 | rattachement_par_fusion_association | Commune associée, parent administratif et historique distincts |
| 34 | transformation_fusion_association_en_fusion_simple | Évolution de statut postérieure à l'événement initial |
| 35 | suppression_statut_commune_deleguee | Suppression du seul statut administratif délégué |

Les valeurs MOD 34 et 35 figurent dans **les événements ultérieurs**, et non comme nouvelles équivalences entre ARK.

Les neuf dossiers à suivi sont : **Mirebel, Gonvillars, Arcier, Essia, Saint-Laurent-la-Roche, Varessia, Coisia, Villechantria et Vauchamps**.

## Cas qui structurent le modèle

**Saint-Hymetière-sur-Valouse** (2019, code 39137) : trois candidatures P1 concernent un événement unique ; l'ancienne commune Chemilla et la commune nouvelle possèdent des ARK distincts. L'alignement Insee numérique de la nouvelle commune demeure à instruire.

**Verdun-Ciel** (2025, code 71566) : événement Insee établi, mais ARK propre non identifié dans les recherches du thésaurus Pactols du 14 novembre 2026 ; cible vide, sans création locale.

**Marchaux et Sancey** : deux événements partagés par les lots P2 et P3, avec réutilisation du code de l'ancienne commune et conservation d'ARK distincts.

**Mirebel et Hauteroche (Jura)** : création en 2016, puis suppression des statuts délégués en 2020 ; Hauteroche (Côte-d'Or) est un autre concept et porte un autre code.

**Antorpe et Frettes** : rattachements de communes associées depuis 1974, attestés aussi par COMPARENT au millésime 2026. Le parent actuel ne doit pas être considéré comme intemporel.

**Arcier → Vaire-Arcier → Vaire** : deux épisodes (1974, puis 2016) malgré la continuité du code 25575 ; le libellé administratif n'est pas rétroprojeté.

## Sources, reproductibilité et garde-fous

Entrées versionnées dans le dossier de recette : les quatre candidatures P1, les deux événements P1, leurs six transitions, les cinq candidatures P2 et les vingt candidatures P3.

Sources officielles : [COG 2026 de l'Insee](https://www.insee.fr/fr/information/8740222). Empreintes SHA-256 exigées :

- v_commune_2026.csv : 7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3
- v_commune_depuis_1943.csv : 08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee
- v_mvt_commune_2026.csv : 8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1

Le générateur contrôle les six transitions P1 sur la source officielle complète ; chaque candidature reçoit une preuve de participation, son événement initial et, le cas échéant, l'événement de suivi. Les sorties sont générées deux fois puis comparées **octet par octet** par GitHub Actions.

Le validateur contrôle tous les renvois entre candidatures, événements, mouvements et états. Il rejette une décision éditoriale préremplie, une preuve introuvable et un état manquant lors de trois essais négatifs. [Exécution GitHub Actions réussie](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43642293571).

## Condition d'intégration au module public Lieux

Ce JSON est un **modèle de recette**, non un export de publication. Son intégration future demandera une décision explicite et sourcée pour chaque relation, avec la distinction des participations et rattachements. Aucun nouvel alignement SKOS exactMatch ne peut être déduit d'un code réutilisé ou d'une ressemblance de libellé.

Les géométries communales 2026 ne doivent **jamais** être rétroprojetées sur les états historiques. Toute géométrie datée future nécessitera une provenance indépendante.

**Bilan : 29/29 préinstructions achevées, 0/29 relations validées, aucune géométrie historique, aucune modification des données publiques. PR n°24 maintenue en brouillon.**
