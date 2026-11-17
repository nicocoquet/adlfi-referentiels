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

Les ARK et les volumes exacts resteront **non affirmés tant que le RDF officiel n'aura pas été lu par la CI**.
