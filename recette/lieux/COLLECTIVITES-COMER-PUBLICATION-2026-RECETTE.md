# Alignements Pactols–COG des collectivités ultramarines (millésime 2026)

**17 novembre 2026 — registre de validation institutionnelle distinct de la table des communes.**

## Décisions

La validation porte sur le couple d'**identifiants de collectivité dans le COG 2026**, et non sur une relation d'identité historique ou une limite cartographique. Les propositions documentées dans les PR [68](https://github.com/nicocoquet/adlfi-referentiels/pull/68) et [69](https://github.com/nicocoquet/adlfi-referentiels/pull/69), ainsi que le concept territorial `987` isolé dans la PR [71](https://github.com/nicocoquet/adlfi-referentiels/pull/71), sont retenus dans le [registre de quatre décisions](COLLECTIVITES-COMER-VALIDATIONS-PACTOLS-COG-2026.csv).

| Nature | Code COG 2026 | Collectivité | ARK Pactols (preuve explicite) |
| --- | --- | --- | --- |
| Collectivité d'outre-mer | **`977`** | Saint-Barthélemy | **`26678/pcrtrGdtY56gmH`** |
| Collectivité d'outre-mer | **`978`** | Saint-Martin | **`26678/pcrty5LooX8FgU`** |
| Territoire / COMER | **`986`** | Wallis-et-Futuna | **`26678/pcrtwFq5jKHO3k`** |
| Collectivité d'outre-mer | **`987`** | Polynésie française | **`26678/pcrt4K8nLVxWOP`** |

La déclaration RDF retenue pour chacun est `skos:exactMatch` vers `http://id.insee.fr/geo/collectiviteDOutreMer/{code}`. Les quatre concepts sont actifs, non dépréciés, non remplacés ; la décision `VALIDE_ADLFI_2026` porte sur l'état **`2026-01-01`**.

## Six URI, quatre décisions : distinction ontologique obligatoire

Le [RDF Pactols-Lieux Frantiq](https://github.com/frantiq/PACTOLS), export `Pactols_Lieux_th17_20260722.rdf`, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`, contient **six URI INSEE explicitement citées** par les quatre concepts :

- Pour **`977` et `978`**, chaque concept possède **deux** URI `skos:exactMatch` : une de type `collectiviteDOutreMer` (retenue pour la collectivité) **et** une de type `commune/97701` ou `commune/97801` (conservée comme preuve **non publiée** à cet autre échelon).
- Pour **`986` et `987`**, chaque concept possède une URI `collectiviteDOutreMer`, sans lien individuel vers une circonscription wallisienne ou une commune polynésienne.

La [notice de codification INSEE](https://www.insee.fr/fr/information/7929495) décrit **`97701` et `97801` comme des codes à cinq positions de la collectivité utilisés pour certaines applications** ; ils ne prouvent pas la création de communes indépendantes en 2007. Les codes `97123` et `97127` restent les identifiants des **anciennes communes de Guadeloupe** dont l'existence COG se termine le 23 février 2007. La [loi organique n° 2007-223](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000735132) atteste une succession des droits et obligations, **pas un transfert automatique de l'ARK** vers ces anciennes communes.

**Wallis-et-Futuna** comporte trois circonscriptions territoriales `98611`, `98612` et `98613` (type `CIR`), **aucune commune**. Elles ne reçoivent pas l'ARK de `986` ; il n'est pas non plus attribué aux anciens codes `98609` et `98607`.

**Polynésie française** conserve ses **48 correspondances communales 2026 déjà validées** et **98 communes associées de nomenclature ISPF non encore instruites** : le concept de collectivité `987` est une autorité distincte de celles-ci. Le code historique `98799` Clipperton n'est pas aligné.

## Format et reproductibilité

L'index public `docs/data/lieux-outremer/recherche-2026.json` expose deux espaces :

- `pactols_valides` : **176 alignements communaux** (inchangés).
- `pactols_collectivites_valides` : **4 alignements de collectivités** (`977`, `978`, `986`, `987`).

Les quatre ARK sont recherchables directement dans le module Lieux et conduisent **uniquement** aux fiches `COMER:TERRITOIRE:{code}`. Les codes à cinq positions `97701` et `97801`, les trois circonscriptions `CIR`, les anciennes communes et les entités historiquement documentées ne sont pas assimilés aux collectivités actuelles.

Le générateur `scripts/extraire_index_public_outremer_2026.py` dispose de l'option `--validations-collectivites`. La CI spécialisée `lieux-collectivites-pactols-publication-2026.yml` reconfronte **les 4 décisions et leurs 6 URI** au RDF Frantiq et à **deux CSV INSEE COG 2026 SHA-256 épinglés**, puis reconstitue **octet par octet** l'index public depuis l'état à 176 correspondances communales (fusion PR [72](https://github.com/nicocoquet/adlfi-referentiels/pull/72)).

**Aucune géométrie nouvelle, aucune rétroprojection au-delà de 2026, aucune nouvelle commune, aucune altération de Tahaa `98745`** (contour 2026 toujours invalide topologiquement). Les **212 communes** et les **21 autres entités COG** présentes dans le moteur restent inchangées.

Les registres préliminaires des PR 68–69 conservent leur valeur de **documents d'instruction à la date de ces PR** ; le présent registre `VALIDE_ADLFI_2026` constitue la **décision éditoriale désormais applicable**.
