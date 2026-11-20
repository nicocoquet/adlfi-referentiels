# Normandie — lot 01, dix identités communales à code INSEE réemployé

**20 novembre 2026 — instruction RDF–COG, sans publication de nouveaux ARK ni géométries.**

Suivi : [#152](https://github.com/nicocoquet/adlfi-referentiels/issues/152).  
Préflight régional : [PR #154](https://github.com/nicocoquet/adlfi-referentiels/pull/154), 2 644 communes COG 2026, 2 496 candidatures univoques, 148 exceptions.

## Principe et provenance

L'export des notices AdlFI permet de prioriser les dix codes d'après la fréquence **agrégée** des ARK concurrents ; **aucune ligne de notice, ARK issu de la source privée ou chemin XML n'est versé ici**. Les ARK indiqués dans le tableau ci-dessous sont exclusivement des **preuves déjà présentes dans le RDF Pactols public épinglé**.

- Source RDF : `frantiq/PACTOLS`, commit `69bf9697e24cefd645a69465bbd271702786285a`, `Pactols_Lieux_th17_20260722.rdf`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- COG actuel : recensement exhaustif 2026 vérifié dans le préflight #154 (`REG=28`, `TYPECOM=COM`). SHA-256 de `v_commune_2026.csv` : `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`.
- Histoire administrative des dix codes : dossiers officiels INSEE 2026, liés ci-dessous ; **la date de création n'est pas inférée du seul `exactMatch`**.
- `scripts/auditer_normandie_lot01_identites_2026.py` recalcule sur le RDF épinglé le nombre d'ARK par code, leurs `prefLabel`, `altLabel`, `exactMatch`, notes (`skos:historyNote`, `skos:definition`, etc.), dépréciation et relations de remplacement. Deux générations binaires identiques sont exigées en CI. Le rapport JSON est conservé comme artefact GitHub Actions, **hors de `docs/`**.

## Dossiers prioritaires

| Code COG 2026 | Commune actuelle (création) | ARK candidat *actuel* dans le RDF | ARK de l'ancienne commune / particularité |
|---|---|---|---|
| [50129](https://www.insee.fr/fr/statistiques/2011101?geo=COM-50129) | **Cherbourg-en-Cotentin** (2016-01-01) | `26678/pcrt4Ft3j507NA` | Cherbourg-Octeville : `26678/pcrtKpjSHTRIyK` |
| [50412](https://www.insee.fr/fr/statistiques/2011101?geo=COM-50412) | **Port-Bail-sur-Mer** (2019-01-01) | **Aucun `exactMatch` propre au nouveau libellé dans ce lot** | Portbail : `26678/pcrtouI45wMnJl`, **ne pas promouvoir** |
| [14456](https://www.insee.fr/fr/statistiques/2011101?geo=COM-14456) | **Moult-Chicheboville** (2017-01-01) | `26678/pcrtNAhK2vpwPa` | Moult : `26678/pcrtetxgQaGZ5H` |
| [61194](https://www.insee.fr/fr/statistiques/2011101?geo=COM-61194) | **Monts-sur-Orne** (2018-01-01) | `26678/pcrtZtrHp1bjSL` | Goulet : `26678/pcrtinAdI9l885` |
| [14762](https://www.insee.fr/fr/statistiques/2011101?geo=COM-14762) | **Vire Normandie** (2016-01-01) | `26678/pcrt78ZZg0wMbU` | Vire : `26678/pcrtkeqj9I3nbw` |
| [27467](https://www.insee.fr/fr/statistiques/2011101?geo=COM-27467) | **Pont-Audemer** (2018-01-01) | `26678/pcrttaqrTGrSS9` : concept contemporain différencié par définition et [Wikidata Q47067820](https://www.wikidata.org/wiki/Q47067820) | `26678/pcrtFmM1SUxsz6` : ancienne commune déléguée, définition distincte et [Wikidata Q367667](https://www.wikidata.org/wiki/Q367667) |
| [27022](https://www.insee.fr/fr/statistiques/2011101?geo=COM-27022) | **Le Val d’Hazey** (2016-01-01) | `26678/pcrt5SNyKsPv04` | Aubevoye : `26678/pcrtABogj7gxSP` |
| [14098](https://www.insee.fr/fr/statistiques/2011101?geo=COM-14098) | **Thue et Mue** (2017-01-01) | `26678/pcrt32xA0aWOKZ` | Bretteville-l’Orgueilleuse : `26678/pcrt37IBobgENS` |
| [14014](https://www.insee.fr/fr/statistiques/2011101?geo=COM-14014) | **Colomby-Anguerny** (2016-01-01) | `26678/pcrtAHatdH8M5h` | Anguerny : `26678/pcrtqhCH2knMXr` |
| [14200](https://www.insee.fr/fr/statistiques/2011101?geo=COM-14200) | **Creully sur Seulles** (2017-01-01) | `26678/pcrtEU57VjwLxi` | Creully : `26678/crtHlZfEWxn98` |

### Statuts éditoriaux

- **Neuf codes avec un candidat de commune nouvelle distinct de l'ancienne identité**, à instruire avant toute décision d'alignement. Huit sont différenciés par le libellé et leurs notes RDF ; le neuvième, Pont-Audemer, nécessite deux preuves supplémentaires : les `skos:definition` (« commune » contre « ancienne commune ») et les `exactMatch` vers **deux éléments Wikidata distincts** (Q47067820 contre Q367667), corroborés par la création au 1er janvier 2018 dans l'Insee.
- **Un code reste non résolu** : Port-Bail-sur-Mer (le seul ARK à `exactMatch` vers 50412 porte le libellé et l'identité de Portbail).
- **Dix anciennes identités ne sont jamais assimilées automatiquement aux communes nouvelles**. Certaines anciennes communes conservent des codes identiques au COG 2026 ; l'événement administratif ne crée pas une relation `skos:exactMatch` entre leurs ARK.
- **Aucun nouvel alignement, aucune nouvelle géométrie ni chronologie rétroprojetée** par ce dossier.

## Particularité des années d'opération

Les notices AdlFI sont indexées par le thésaurus disponible au moment du traitement éditorial ; le libellé géographique peut avoir été normalisé *après* l'opération archéologique. Dans l'export documentaire de travail, l'ARK actuel de Cherbourg-en-Cotentin est ainsi présent dans des notices dont l'opération précède la création de 2016. Inversement, certains ARK d'anciennes communes sont employés pour des opérations postérieures aux fusions. **L'année d'opération ne constitue donc ni une preuve d'identité administrative, ni une licence pour rétroprojeter un contour.** Le portail doit distinguer date d'opération, état COG et période d'identité du concept.

## Suite

1. Analyser le rapport enrichi du RDF et ses `skos:historyNote` / `skos:definition`, puis décider un premier lot de correspondances **2026 seulement**, séparément de la présente PR.
2. Rechercher, si elle existe, l'autorité de **Port-Bail-sur-Mer** hors des seuls `exactMatch` vers `50412` ; ne pas créer un ARK fictif.
3. Conserver **Pont-Audemer** comme candidat contemporain sur la convergence entre définition RDF, deux URI Wikidata distinctes et COG 2018 : ne pas attribuer ces deux ARK à une même autorité historique ni déduire une relation de succession ontologique par simple conservation du code.
4. Préserver les 148 exceptions de la Normandie et le classement par poids documentaire ; la publication de la couche cartographique 2026 de Normandie sera une opération distincte.
