# Publication des 212 correspondances communales Pactols–COG (2026)

**17 novembre 2026 — mise à jour de l'index public du référentiel Lieux.**

## Décision

Après la [PR 95](https://github.com/nicocoquet/adlfi-referentiels/pull/95) (36 décisions éditoriales et 36 assertions RDF vérifiées), la publication ajoute **36 associations Pactols–COG 2026** aux **176** déjà en ligne. Les 212 communes du sous-index ultramarin disposent désormais d'un identifiant Pactols validé pour l'état du **1er janvier 2026**.

| Territoire | Communes 2026 | Liens Pactols validés |
| --- | ---: | ---: |
| Guadeloupe (971) | 32 | 32 |
| Martinique (972) | 34 | 34 |
| Guyane (973) | 22 | 22 |
| La Réunion (974) | 24 | 24 |
| Saint-Pierre-et-Miquelon (975) | 2 | 2 |
| Mayotte (976) | 17 | 17 |
| Polynésie française (987) | 48 | 48 |
| Nouvelle-Calédonie (988) | 33 | 33 |
| **Total** | **212** | **212** |

Les **quatre alignements de collectivités** `977`, `978`, `986`, `987` restent dans `pactols_collectivites_valides` et **ne s'ajoutent pas aux 212 communes**. Le total des autres entités COMER de l'index reste de **21**.

## Traçabilité et reproductibilité

- **Source originale** : RDF Frantiq `Pactols_Lieux_th17_20260722.rdf`, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- **Registre des décisions 2026** : [VALIDATIONS-NC-SPM-DEMBENI-2026.csv](VALIDATIONS-NC-SPM-DEMBENI-2026.csv), qui distingue **33 communes NC, 2 SPM et Dembeni**.
- **Instantané de référence historique** : [SOCLE-PACTOLS-COG-OUTREMER-176-2026.json](SOCLE-PACTOLS-COG-OUTREMER-176-2026.json).
- **Index courant** : `docs/data/lieux-outremer/recherche-2026.json`, généré à partir de cet instantané par `scripts/publier_alignements_212_outremer_2026.py`.
- **CI dédiée** : `lieux-publication-212-alignements-2026.yml` : vérification SHA-256 du RDF, confrontation **individuelle des 36 liens** au RDF, régénération du JSON public **octet à octet**, tests d'unicité et du moteur de recherche.

Le script de publication refuse une décision sans URI `id.insee.fr/geo/commune/{code}` conforme, prédicat autre que `skos:exactMatch`, décision éditoriale non validée, doublon ARK ou code absent du COG 2026. La vérification **effective des 36 assertions RDF** est indépendante et obligatoire dans la CI.

## Exceptions et limites

- **Saint-Pierre (97502)**, ARK `26678/pcrtYQmFfwxLq8` : `prefLabel` Pactols d'origine « île Saint-Pierre (Saint-Pierre-et-Miquelon) ». L'éditeur a validé explicitement l'alignement ; une demande de correction du libellé auprès de Pactols reste à faire.
- **L'Île-des-Pins (98809)**, ARK `26678/pcrti4LqTHByEs` : `prefLabel` « Île-des-Pins », `altLabel` « L'Île-des-Pins ». Alignement validé nommément par l'éditeur, sans faire des îles et des communes des catégories automatiquement équivalentes.
- **Dembeni (97607)**, ARK `26678/crtZcuFSJVYZU` : précédemment enregistré sous `ark_confirmes_non_valides`, puis validé après confirmation de `skos:exactMatch` explicite, univoque et non déprécié dans le RDF de référence. Le champ `ark_confirmes_non_valides` est maintenant vide.

Les **212 correspondances d'identifiants ne constituent pas 212 géométries homologuées**. Les contours `98745` (Tahaa) et `98805` (Dumbéa) demeurent signalés comme invalides topologiquement ; aucune géométrie historique, succession communale, alignement de commune associée ISPF, circonscription wallisienne ou transfert vers les anciennes communes de Guadeloupe n'est créé.

## Recettes historiques conservées

Les anciennes CI de La Réunion, de la Polynésie, de Wallis-et-Futuna, etc. font parfois référence à des compteurs de validation antérieurs. Les audits de **publication de 176 liens** restent reproductibles sur le **socle 176** et un manifeste historique épinglé ; les contrôles courants exigent **212/212**. Cette séparation permet de vérifier l'évolution sans réécrire rétroactivement les résultats d'audits précédents.

**Suite du chantier :** basculer sur le référencement métropolitain et les correspondances historiques Pactols–COG, en maintenant les cas géométriques exceptionnels dans leur registre propre.
