# Lieux — clôture TAAF et priorité à 212 communes ultramarines actuelles

**15 novembre 2026 · Instruction éditoriale de la PR #30 · Aucune correspondance nouvelle approuvée.**

## Décision de périmètre

Sur indication éditoriale, **cesser la recherche de nouveaux alignements Pactols pour les districts des TAAF** : le thésaurus comporte un concept global TAAF `26678/pcrtqYLoVxtxFl` et le concept géographique Kerguelen `26678/pcrtiLVIezAOXD`. La prospection complémentaire TAAF est close pour le **présent chantier**, sans affirmer une absence absolue de tout autre concept géographique dans les versions futures du thésaurus. La hiérarchie `skos:broader` Kerguelen → TAAF est conservée comme fait du vocabulaire. **Ne pas créer automatiquement d'équivalence entre Kerguelen et le district administratif COG `98412`.**

Les cinq districts COG TAAF demeurent dans les tables administratives et seront visualisables avec une géométrie sourcée, indépendamment de la couverture Pactols.

## Couverture exhaustive en termes d'indices préexistants pour les communes actuelles

Comparaison des **233 cibles COG 2026** et du snapshot intégral Pactols-Lieux du 22 juillet 2026, avec lecture des `skos:exactMatch` vers les URI INSEE déclarées dans Pactols.

| Territoire | Communes au COG 2026 | Communes avec un concept Pactols déclarant le même code INSEE |
| --- | ---: | ---: |
| Guadeloupe | 32 | 32 |
| Martinique | 34 | 34 |
| Guyane | 22 | 22 |
| La Réunion | 24 | 24 |
| Mayotte | 17 | 17 |
| Polynésie française | 48 | 48 |
| Nouvelle-Calédonie | 33 | 33 |
| Saint-Pierre-et-Miquelon | 2 | 2 |
| **Total** | **212** | **212** |

La totalité des **212 communes** possède **exactement une piste portant l'identifiant INSEE de même code dans notre audit**. Cela démontre la **couverture documentaire sur les codes courants**, et **non** la validité historique des liens, ni leur approbation par AdlFI. Il n'y a aucune nouvelle équivalence validée dans ce lot.

**Délimitation :** 129 communes DROM + 48 de Polynésie + 33 de Nouvelle-Calédonie + 2 de Saint-Pierre-et-Miquelon. Les deux zonages COG `COM` de Saint-Martin et Saint-Barthélemy, dont le statut institutionnel est spécifique, ne sont pas inclus dans ce lot de **212 communes** ; ils restent documentés à part parmi les 233 cibles COG du premier audit. Les deux circonscriptions de Wallis-et-Futuna sans signal direct restent à instruire selon leur nature `CIR`, pas comme des communes.

## Cinq exceptions lexicales à désambiguïser

Toutes les cinq ont un candidat portant une URI INSEE de même code, **et** un autre concept Pactols lexicalement proche sans preuve INSEE de même code.

| Cible COG | Code | ARK avec code INSEE | Autre concept lexical à contrôler |
| --- | --- | --- | --- |
| Trois-Rivières (Guadeloupe) | `97132` | `26678/pcrtqsY0nwgvdx` | `26678/pcrttHxJaRXn0R` |
| Le Lamentin (Martinique) | `97213` | `26678/pcrt2TaUhAoZiH` | `26678/pcrtQuhfj4EN92` |
| Le Marin (Martinique) | `97217` | `26678/pcrtAlOUMlIYXC` | `26678/pcrt3Zc89S6hLT` |
| Le Port (La Réunion) | `97407` | `26678/pcrtIKvRT9vwUl` | `26678/pcrtaVzq2EWV3x` |
| Le Mont-Dore (Nouvelle-Calédonie) | `98817` | `26678/pcrtCvyXBTi1lL` | `26678/pcrtoWwsSu2Kg4` |

**207** communes ont une seule piste pertinente selon le filtre conservateur ; **5** nécessitent cette désambiguïsation complémentaire. Aucune décision n'a été remplie à la place de l'éditeur.

## Proposition de séquence

1. **Valider éditorialement un lot des 207 communes à piste unique**, avec contrôles de l'URI exacte (niveau territorial, code 2026, libellé, statut du concept et historique du code). Validation humaine, pas en bloc automatique.
2. **Résoudre les cinq homonymies** en conservant les deux ARK sources et les justifications.
3. **Traiter séparément** les deux COMER de Saint-Martin et Saint-Barthélemy et les zonages non communaux (`CIR`, `CPT`, `CDM`), avec contrôle des épisodes historiques 2007 et autres.
4. Préparer un **export public des seuls rapprochements approuvés** et la géométrie des territoires à millésime explicite pour la future carte mondiale. Aucune restitution historique de limites par défaut.

**Sources :** artefact GitHub Actions de la PR #30, workflow `43737165911`, et audit contextuel `synthese_233_apres_filtre_contextuel.csv` / `qualification_pistes_Pactols_ultramarines.csv` ; corpus COG 2026 (Insee) et Pactols-Lieux RDF `th17` 2026-07-22 vérifié par SHA-256. Le tableau nominatif des 212 candidats reste dans les artefacts éditoriaux de recette, **hors `docs/` et hors données publiées**.
