# Normandie — lot 02 : deuxième série de dix collisions Pactols–COG

**20 novembre 2026 — recette de qualification, sans validation ni publication de nouvelles correspondances.**

Suivi national : [#152](https://github.com/nicocoquet/adlfi-referentiels/issues/152) ; premier lot [#155](https://github.com/nicocoquet/adlfi-referentiels/pull/155) et ses neuf validations 2026 [#156](https://github.com/nicocoquet/adlfi-referentiels/pull/156).

## Périmètre issu des notices AdlFI

Les dix dossiers suivants correspondent aux rangs 11 à 20 du tableau local des **148 exceptions normandes** ; ils totalisent **49 occurrences** sur les ARK concurrents dans les notices. Ce total ne signifie pas 49 notices différentes : une notice peut comporter plusieurs occurrences ou plusieurs autorités.

Les ARK présentés sont ceux du **RDF Pactols public** ; les fichiers privés `autorites_lieux.csv` et `occurrences_lieux.csv` ne sont pas déposés ici. Les identifiants des notices n'entrent pas dans le rapport publié.

| Code COG 2026 | Commune actuelle | Occurrences AdlFI des ARK candidats | ARK au libellé contemporain (candidat) | ARK concurrent, identité ancienne ou déléguée à distinguer |
|---|---|---:|---|---|
| `27112` | Breteuil | 6 | `26678/pcrtwD0OalOHGK` — Breteuil (Eure) | `26678/pcrtKa9QelswXe` — Breteuil (commune déléguée) |
| `61341` | Écouves | 6 | `26678/pcrtsZJYVKHuCr` | `26678/pcrtfjO3sQkDv7` — Radon |
| `27471` | Porte-de-Seine | 5 | `26678/pcrtTVZxjfH4A1` | `26678/pcrtQB6XrQQ9LZ` — Porte-Joie |
| `50239` | Thèreval | 5 | `26678/pcrtPvLbdZBmws` | `26678/pcrtkp7pbzeyjj` — Hébécrevon |
| `61211` | Juvigny Val d'Andaine | 5 | `26678/pcrtQPOvb7fsR5` | `26678/pcrtV19FHEOsRO` — Juvigny-sous-Andaine |
| `76258` | Terres-de-Caux | 5 | `26678/pcrt9wS8mfBRqs` | `26678/pcrtHyxyLS19S7` — Fauville-en-Caux |
| `50546` | Bourgvallées | 5 | `26678/pcrtgtbpJSZPKx` | `26678/pcrtiPrPGO44Zc` — Saint-Samson-de-Bonfossé |
| `14035` | Balleroy-sur-Drôme | 4 | `26678/crts1h2V4fgZ4` | `26678/pcrtBZN8Mc6oeC` — Balleroy |
| `14342` | Isigny-sur-Mer | 4 | `26678/pcrtJiEVVL4S0d` | `26678/pcrtOlN1ZN3BqW` — Isigny-sur-Mer (commune déléguée) |
| `14654` | Saint-Pierre-en-Auge | 4 | `26678/pcrtf4lulrxUo6` | `26678/pcrt5RPJFgGgvO` — Saint-Pierre-sur-Dives |

## Vérification et statut

Le script `scripts/auditer_normandie_lot02_rdf_2026.py` :

1. Relit le RDF Frantiq/PACTOLS du 22 juillet 2026, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
2. Contrôle l'existence des vingt ARK exacts, les deux `skos:exactMatch` vers chaque code du COG 2026 et les libellés du rapport régional [#154](https://github.com/nicocoquet/adlfi-referentiels/pull/154).
3. Extrait leurs `skos:historyNote`, `skos:definition`, autres `exactMatch`, liens de remplacement et dépréciation.
4. Émet une **recette non validante** (statut `NON_PRISE` pour chaque décision éditoriale), deux fois à l'identique, en artefact de CI, jamais dans `docs/`.

**Les dix ARK aux libellés contemporains restent des candidats**, et non des identités officiellement validées. Pour décider, il faudra vérifier les créations et les codes conservés dans les mouvements historiques de l'Insee, puis distinguer les concepts anciens même lorsque leur `exactMatch` utilise le même code courant.

Le bilan attendu de cette tranche est de **10 codes / 20 ARK qualifiés / 0 validation / 0 géométrie / 0 inférence historique**. La publication des alignements 2026, si les preuves convergent, sera une PR indépendante.

## Limite cartographique

Le module Lieux ne publie pas encore les géométries communales de Normandie. Le dossier n'affiche donc pas de nouveau contour et ne modifie ni l'échelon Commune ni les alignements régionaux existants. La montée en charge de la carte est instruite séparément dans la [PR #157](https://github.com/nicocoquet/adlfi-referentiels/pull/157).
