# Audit Pactols–COG 2026 — Corse, Pays de la Loire, Bourgogne-Franche-Comté

**17 novembre 2026 · Recette préliminaire non validante**

## Périmètre et priorité

Après la [publication des 212 correspondances communales ultramarines](PUBLICATION-212-PACTOLS-COG-2026.md), nous abordons les **communes actuelles** des trois régions métropolitaines déjà prioritaires pour les contrôles de géographie historique :

| Code région COG 2026 | Territoire | Contrôle |
| --- | --- | --- |
| `94` | Corse | Codes communaux alphanumériques `2Axxx`, `2Bxxx` ; homonymies |
| `52` | Pays de la Loire | Communes nouvelles et évolutions historiques à séparer de l'identité 2026 |
| `27` | Bourgogne-Franche-Comté | Idem ; contours et ancien découpage régional indépendants des liens |

Le choix d'appartenance à la région utilise **`TYPECOM=COM` et `REG` du fichier officiel `v_commune_2026.csv`** ; il n'est pas déduit du préfixe du code INSEE. Les communes déléguées (`COMD`), associées (`COMA`) et arrondissements (`ARM`) ne sont pas considérés comme communes autonomes dans cette passe.

## Sources et méthode

- RDF Pactols Lieux (`frantiq/PACTOLS`) : `Pactols_Lieux_th17_20260722.rdf`, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- COG Insee : `v_commune_2026.csv`, version 2026 épinglée SHA-256 `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`, acquise par `scripts/recuperer_cog_2026.py`.
- Traitement en flux : `scripts/auditer_pactols_cog_regions_prioritaires_2026.py`, réutilisant le parseur RDF du lot polynésien. **Correction préalable fondamentale :** accepter les codes INSEE alphanumériques `2A` et `2B` dans l'URI `id.insee.fr/geo/commune`.

La sortie rassemble, **pour chaque commune COG 2026**, les assertions `skos:exactMatch` du RDF, ARK, `prefLabel`, `altLabel`, statut de dépréciation/remplacement, éventuels autres liens INSEE, candidats lexicaux *non validants* et état de triage :

1. `ELIGIBLE_SELON_REGLE` : assertion explicite univoque, non dépréciée, vers l'URI de la commune 2026, sans autre URI INSEE contradictoire et libellé principal compatible.
2. `A_INSTRUIRE_*` : ARK concurrents, code multiple, libellé ou catégorie géographique non concordant, concept remplacé/déprécié.
3. `SANS_EXACTMATCH` : aucun lien explicite observé dans le RDF épinglé pour ce code ; une homonymie ne constitue pas une preuve.

Les résultats quantitatifs ci-dessous proviennent de la première exécution vérifiée. La CI génère deux rapports identiques octet à octet, avec un artefact JSON non exposé au public.

## Résultats de la première exécution réelle (GitHub Actions)

L'[exécution de recette 44160348311](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44160348311) a réussi, avec acquisition vérifiée du RDF et du COG, et **deux exports JSON identiques octet à octet**.

| Région | Communes COG 2026 | Codes avec exactMatch | Éligibles selon la règle | Plusieurs ARK | Divergence de libellé, statut ou URI | Sans exactMatch |
|---|---:|---:|---:|---:|---:|---:|
| Corse (94) | 360 | 360 | **360** | 0 | 0 | 0 |
| Pays de la Loire (52) | 1 228 | 1 224 | **1 140** | 60 | 24 | 4 |
| Bourgogne-Franche-Comté (27) | 3 685 | 3 684 | **3 614** | 44 | 26 | 1 |
| **Total** | **5 273** | **5 268** | **5 114** | **104** | **50** | **5** |

Le RDF contient **50 556 concepts ARK examinés** par le parseur. L'audit a également trouvé **66 rapprochements lexicaux candidats non validants** (nombre de candidatures, non nécessairement nombre de communes). Les **154 codes avec une assertion mais un statut à instruire** (104 + 50) et les **5 sans `exactMatch`** sont distincts des **5 114 liens admissibles en première lecture**.

**Ne pas interpréter ces résultats comme une couverture documentaire AdlFI** : ce calcul compare toutes les communes de ces trois régions au RDF Pactols, pas les occurrences extraites du corpus des notices. **Aucune des 5 114 associations n'est encore publiée par cet audit.**

La **Corse** constitue un lot favorable pour une validation éditoriale datée (360/360 liens admissibles). La **Bourgogne-Franche-Comté** et les **Pays de la Loire** demandent une instruction séparée des 104 codes avec plusieurs ARK, en priorité les communes nouvelles et les fusions : l'assertion `exactMatch` de deux concepts distincts vers un même code actuel ne suffit pas à les assimiler. Exemples rencontrés dans les résultats : **Source-Seine (21084)**, **Cormot-Vauchignon (21195)**, **Étalans (25222)**. Les divergences de libellé, parmi lesquelles **Valforêt (21178)** et **Collonges-et-Premières (21183)**, sont également conservées en instruction.

## Priorités opérationnelles

1. **Corse** : générer un registre daté des 360 liens dont les conditions RDF sont réunies, avec contrôle systématique des ARK, libellés et URI, puis produire une publication autonome non géométrique.
2. **Pays de la Loire / BFC** : regrouper les 154 dossiers à instruire par type de difficulté (multiplicité d'ARK, labels et URI divergents). Les éventuelles communes nouvelles seront rapprochées de leurs mouvements COG, sans en déduire une succession de concepts.
3. **Croisement documentaire** : récupérer l'export des 9 928 autorités effectivement utilisées dans les notices pour relier les audits d'identifiants aux besoins éditoriaux prioritaires.

## Limite : corpus documentaire des 9 928 autorités

Le résultat concerne les **communes administratives du COG 2026**, non les seules autorités géographiques effectivement **utilisées dans les notices AdlFI**. Les `9 928` autorités du corpus historique déjà extraites dans l'autre chantier ne sont pas déposées ici sous forme d'entrée utilisable : il faudra réintroduire `autorites_nationales.json` ou l'export d'autorités documentaire validé pour croiser les deux univers, établir une priorisation fondée sur les occurrences des notices, et éviter de rechercher indistinctement toutes les communes de France.

## Prochaine étape : histoire territoriale

Après l'analyse des `exactMatch` communaux actuels, instruire les cas de changements de code, de fusion/division, de `COMA`/`COMD`, de nom ancien ou de territoire non communal à partir des mouvements historiques COG. **Aucune succession, rétroprojection spatiale ou validation éditoriale n'est autorisée par cet audit.**

Les géométries GEOFLA/ADMIN EXPRESS et les anciens périmètres régionaux appartiennent à un contrôle cartographique indépendant. Cette PR n'ajoute **aucune nouvelle association validée** à GitHub Pages.
