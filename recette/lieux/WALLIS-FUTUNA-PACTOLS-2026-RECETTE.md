# Wallis-et-Futuna — audition du RDF Pactols et des catégories COG 2026

**17 novembre 2026 — audit non validant, sans modification du référentiel publié.**

## Périmètre des autorités

Le [référentiel Lieux publié dans la PR n°67](https://github.com/nicocoquet/adlfi-referentiels/pull/67) distingue **un territoire** (`986` Wallis-et-Futuna), **trois circonscriptions territoriales** (`98611` Alo, `98612` Sigave, `98613` Uvea), et **aucune commune**.

Une première typologie du contrôle Pactols :

| Code INSEE | Type attendu | Interprétation d'un éventuel `skos:exactMatch` |
| --- | --- | --- |
| `986` | Territoire / collectivité d'outre-mer | Candidat territorial à qualifier |
| `98611` | CIR Alo | Candidat de circonscription, ne peut devenir « commune Alo » |
| `98612` | CIR Sigave | Candidat de circonscription, ne peut devenir « commune Sigave » |
| `98613` | CIR Uvea | Candidat de circonscription, ne peut devenir « commune Uvea » |

Le code historique `98609` (Wallis-et-Futuna, épisode du 31 juillet 1961 au 1er janvier 1985) est conservé en **diagnostic uniquement**, tout comme `98607` dont le libellé dans la série COG est **Nouvelle-Calédonie**, et non une identité autonome de Wallis-et-Futuna. Aucune succession historique Pactols n'est inférée.

## Sources de l'audit

- Frantiq, [PACTOLS-Lieux RDF, export du 22 juillet 2026](https://github.com/frantiq/PACTOLS), commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- [INSEE, Code officiel géographique 2026](https://www.insee.fr/fr/information/8740222) : `v_comer_2026.csv` et `v_commune_comer_2026.csv`, chacune vérifiée par empreinte.
- [Légifrance, loi n° 61-814 du 29 juillet 1961, articles 17 et 18](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000684031) : identité institutionnelle et personnalité morale des circonscriptions.

Le workflow lit le RDF XML en flux, identifie les assertions `skos:exactMatch` vers les quatre codes (et les deux codes historiques en diagnostic), conserve la **famille d'URI INSEE** (par exemple `commune`, `collectiviteDOutreMer`, `circonscription`), les libellés français, les dépréciations et les remplacements.

## Réserves de catégorie sémantique

Les expressions « île d'Uvea », « royaume d'Alo » ou « royaume de Sigave » ne peuvent être assimilées d'emblée aux **circonscriptions territoriales de droit public**. Une éventuelle URI `geo/commune/98611` ne prouverait pas une commune. Un code historique `98607` identifié dans le RDF ne serait pas attribué automatiquement à Wallis.

Les simples homonymes « Alo », « Uvea » ou « Sigave » sans contexte géographique explicite restent écartés de toute validation. Seuls les libellés qualifiés territorialement peuvent être listés comme **candidats lexicaux à instruire**, jamais comme correspondances validées.

## Portée de l'audit

La comparaison RDF–COG est **reproductible** et archivée hors des fichiers publics. Elle conserve **zéro validation automatique, zéro nouvel alignement Pactols, zéro géométrie et zéro commune**.

## Résultat réel du RDF Frantiq — 17 novembre 2026

La [CI n°44057523347](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44057523347) a réussi le contrôle des empreintes du RDF et des CSV COG, les tests synthétiques, la double exécution reproductible et l'audit sémantique.

**Un seul concept porte une assertion `skos:exactMatch` vers les quatre codes COG 2026 examinés :**

| Code COG | Type administratif | ARK Pactols trouvé | URI INSEE explicitement citée |
| --- | --- | --- | --- |
| **`986` Wallis-et-Futuna** | Territoire / COMER | **`26678/pcrtwFq5jKHO3k`** | `http://id.insee.fr/geo/collectiviteDOutreMer/986` |
| `98611` Alo | CIR | Aucun | Aucune URI exacte |
| `98612` Sigave | CIR | Aucun | Aucune URI exacte |
| `98613` Uvea | CIR | Aucun | Aucune URI exacte |

Le [concept Pactols `26678/pcrtwFq5jKHO3k`](https://ark.frantiq.fr/ark:/26678/pcrtwFq5jKHO3k) a pour `prefLabel` français « **Wallis et Futuna** » et pour `altLabel` « **Territoire des îles Wallis et Futuna** ». Le concept est **non déprécié, non remplacé** ; son `exactMatch` est typé **`collectiviteDOutreMer`**, de même nature administrative que l'autorité COG actuelle `986`.

Les deux codes historiques `98609` et `98607` ne portent **aucune déclaration exacte** dans l'export RDF contrôlé. **Deux concepts à libellé non suffisamment contextualisé** ont été exclus de la correspondance par homonymie ; aucun candidat purement lexical qualifié n'a été retenu.

### Arbitrage éditorial proposé

Le couple **`986` → `26678/pcrtwFq5jKHO3k`** satisfait les critères documentaires de cohérence entre collectivité COG courante, URI INSEE typée, concept Pactols unique et actif. Il est **proposé pour validation au 1er janvier 2026**, selon le modèle séparé des collectivités d'outre-mer institué dans la [PR n°68](https://github.com/nicocoquet/adlfi-referentiels/pull/68).

Ce statut n'est **pas** celui d'une relation déjà publiée. Aucun `exactMatch` ne sera attribué aux trois circonscriptions à partir de l'ARK du territoire, ni rétroactivement à `98609` ou `98607`. Le compteur public conserve **128 alignements communaux**, distincts des propositions de collectivités.

Le contrôle CI de la PR vérifie désormais **l'ARK précis**, la famille de l'URI INSEE, les libellés Pactols, la non-dépréciation, l'absence de liens CIR et l'absence de correspondances vers les anciens codes.
