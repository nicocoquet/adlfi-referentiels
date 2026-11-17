# Arbitrage éditorial proposé — collectivités d'outre-mer 977 et 978

**17 novembre 2026 — propositions, pas encore décisions de validation.**

Cette note complète la [politique communale AdlFI](POLITIQUE-ALIGNEMENT-PACTOLS-COG.md) **sans en élargir silencieusement le périmètre**. La politique du 16 novembre visait les *communes COG 2026*. Saint-Barthélemy et Saint-Martin doivent faire l'objet d'une règle **distincte pour les collectivités d'outre-mer**.

## Deux propositions pour le millésime du 1er janvier 2026

| Collectivité COG 2026 | ARK Pactols | URI INSEE de collectivité attestée par `skos:exactMatch` | Avis |
| --- | --- | --- | --- |
| `977` — Saint-Barthélemy | `26678/pcrtrGdtY56gmH` | `http://id.insee.fr/geo/collectiviteDOutreMer/977` | **Proposer validation COLLECTIVITE 2026** |
| `978` — Saint-Martin | `26678/pcrty5LooX8FgU` | `http://id.insee.fr/geo/collectiviteDOutreMer/978` | **Proposer validation COLLECTIVITE 2026** |

Sources : [COG 2026 Insee](https://www.insee.fr/fr/information/8740222), [RDF Frantiq Pactols Lieux, commit `69bf9697…`](https://github.com/frantiq/PACTOLS), [audit PR n°66](https://github.com/nicocoquet/adlfi-referentiels/pull/66) et son [rapport CI](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44053293173).

L'extraction RDF a identifié **deux concepts uniques**, tous deux non dépréciés et sans remplacement, avec libellés antillais explicites. Chacun cite deux URI sous `skos:exactMatch` : la première désigne explicitement la **collectivité** ; la seconde utilise une voie `/geo/commune/` et le code d'application à cinq chiffres (`97701`, `97801`). Il faut **conserver ces deux déclarations brutes comme données de provenance** et **ne valider que le lien vers la collectivité**.

## Distinctions ontologiques indispensables

La loi organique n° 2007-223 du 21 février 2007 atteste la succession juridique de `977` à l'ancienne commune `97123` et de `978` à `97127`, dans les droits et obligations. Cette relation juridique n'est **pas** une équivalence de concepts ou une instruction de transfert des ARK.

Les codes `97701` et `97801` sont **des variantes de codification à cinq positions**, selon l'[Insee, codification des collectivités d'outre-mer](https://www.insee.fr/fr/information/7929495) ; ils ne créent aucune commune. Leurs URI `commune/` dans Pactols sont une **anomalie de modélisation ou de vocabulaire d'URI à contextualiser**, mais ne rendent pas fausse l'autre déclaration explicite `collectiviteDOutreMer/` du même concept.

L'absence d'URI historiques `97123` et `97127` dans le RDF contrôlé interdit de reporter les ARK sur les anciennes communes.

## Conditions proposées pour l'état `VALIDE_ADLFI_COMER_2026`

1. L'autorité cible figure dans le COG au **1er janvier 2026** avec le type **collectivité d'outre-mer** et code `977` ou `978`.
2. Le concept Pactols **non déprécié et non remplacé** cite sous `skos:exactMatch` la voie typée `http://id.insee.fr/geo/collectiviteDOutreMer/{code}`.
3. Le couple **collectivité–ARK est unique** et son libellé est cohérent, avec précision « Antilles Françaises » admissible comme désambiguïsation.
4. Les correspondances vers `commune/97701`, `commune/97801` sont documentées **uniquement comme déclarations RDF secondaires ambiguës** et ne produisent aucune fiche communale ni nouvelle relation approuvée.
5. La validation de chaque couple s'applique exclusivement au **COG 2026**. Elle ne produit **aucune rétroprojection, géométrie, succession d'autorité ou relation vers `97123`/`97127`**.
6. Après une décision éditoriale explicite, un script de publication séparé pourra créer une **table d'alignements des collectivités**, distincte de `pactols_valides` du module communal, avec contrôles de provenance et mise à jour des effectifs **par type d'autorité**.

## Statut de la présente proposition

Les deux lignes du fichier [`ANTILLES-COLLECTIVITES-977-978-ALIGNEMENTS-PROPOSES-2026.csv`](ANTILLES-COLLECTIVITES-977-978-ALIGNEMENTS-PROPOSES-2026.csv) portent le statut **`PROPOSITION_A_VALIDER`** et **`validation_site_publiee=non`**. Il ne s'agit **pas** de `VALIDE_ADLFI_2026`.

Le compteur public reste **128 alignements *communaux*** pour les territoires ultramarins couverts, et non « 130 alignements communaux ». Les **deux propositions de collectivités** doivent être comptabilisées à part si elles sont ultérieurement validées.
