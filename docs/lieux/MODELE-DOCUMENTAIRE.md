# Modèle documentaire des lieux — jalon lexical

## Invariants du pilote

L'autorité Pactols, identifiée par son ARK, est l'unité principale du référentiel.
Le code INSEE et le libellé COG sont rattachés à une **correspondance éditoriale
datée**, non substitués à l'ARK. La géométrie reste celle d'un millésime
administratif contemporain et ne représente pas des limites historiques.

Les 103 couples PACA validés au 18 octobre 2026 restent inchangés. Les
115 lignes exclues ne sont pas automatiquement réintroduites. Il n'existe
pas de `skos:exactMatch` automatique Pactols–COG.

## Extension lexicale facultative

Chaque élément de `autorites[]` peut recevoir un tableau
`variantes_pactols[]` comprenant :

| Champ | Sémantique | Obligation |
| --- | --- | --- |
| `libelle` | Valeur exacte du `skos:altLabel` issu de Pactols | non vide |
| `langue` | Langue BCP 47 fournie par la source (ex. `fr`) | obligatoire |
| `type` | Valeur fixe `skos:altLabel` | obligatoire |
| `uri_source` | URI de l'autorité Pactols porteuse du libellé | ARK identique à la fiche |

Les variantes ne remplacent pas `libelle_pactols` et ne sont pas déduites
des libellés COG. Elles sont indexées dans l'autocomplétion à partir du
fichier JSON statique et, si elles sont présentes, affichées dans la fiche
d'autorité. Les noms canoniques, codes INSEE et ARK conservent leur
priorité de classement.

Ce champ est optionnel pour préserver la compatibilité du schéma 0.1.0 ;
le fichier `docs/data/lieux.json` actuel **ne contient aucune variante**.
Il faudra effectuer une montée de version du schéma et de l'exporteur lors
de la première alimentation réelle, avec un manifeste d'extraction Pactols.

## Préconditions à toute importation réelle

1. Identifier un export SKOS officiel du thésaurus **Pactols Lieux**
   et en figer l'URL, la date, le format et l'empreinte du fichier.
2. Faire la jointure **uniquement par ARK** avec les 103 autorités validées.
3. Distinguer strictement `skos:prefLabel`, `skos:altLabel`, traductions,
   labels dépréciés et désignations historiques, sans les confondre.
4. Vérifier la provenance, les langues, l'unicité et la normalisation
   des données ; générer un rapport des divergences et anomalies.
5. Tester et relire un échantillon avant tout ajout aux données publiques.

Un libellé historique n'est pas en soi une entité administrative historique ;
le rattachement temporel Pactols–COG relève d'un autre modèle et d'une
validation éditoriale spécifique.

## Audit effectif du 12 novembre 2026 : source Pactols Lieux de juillet

Le script `scripts/audit_variantes_pactols.py` lit en streaming le RDF/XML
officiel du thésaurus **Pactols Lieux (th17)**, téléchargé par le workflow
`.github/workflows/audit-lieux-pactols.yml` à partir de Git LFS.

- Dépôt : `frantiq/PACTOLS`, commit immuable
  `69bf9697e24cefd645a69465bbd271702786285a`.
- Chemin :
  `pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf`.
- SHA-256 des **93 418 191 octets réels** :
  `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- Licence : ODbL ; attribution : CNRS-Frantiq.
- Cette version datée **22 juillet 2026** est antérieure à l'état du
  thésaurus en ligne (modification affichée le 28 octobre 2026).

Résultat du contrôle reproductible (workflow GitHub Actions n° 43194175957,
réussi) :

| Indicateur | Nombre |
| --- | ---: |
| ARK du pilote | 103 |
| ARK présents dans l'export | 103 |
| `skos:prefLabel@fr` égaux aux libellés éditoriaux | 103 |
| Autorités avec au moins un `skos:altLabel` | 24 |
| Occurrences de variantes avec étiquette de langue | 145 |
| **Formes lexicales distinctes par autorité** | **31** |
| Anomalies signalées | 0 |

Répartition des occurrences : français 31 ; allemand 23 ; anglais 23 ;
espagnol 23 ; italien 23 ; néerlandais 22.

**Attention à l'interprétation** : il ne s'agit pas de 145 noms différents.
La majorité des formes est répétée à l'identique dans plusieurs langues
SKOS. Les fiches les regroupent donc par chaîne lexicale, tout en
conservant la liste des langues dans lesquelles Pactols les atteste.

L'export comporte par exemple des formes telles que *Aquae Sextiae*
(Aix-en-Provence), *Antipolis* (Antibes), *Arelate* (Arles), *Digne*
(Digne-les-Bains). Certaines pourraient relever de la toponymie historique,
d'autres de l'orthotypographie : leur **qualification reste éditoriale** et
n'est pas inférée automatiquement à partir de `skos:altLabel`.
Même une forme ancienne attestée ne constitue pas un contour historique.

Les sorties du workflow sont archivées comme artefacts **hors `docs/data`** :
`rapport-pactols-lieux.json`,
`candidats-variantes-pactols.json` et
`revue-variantes-pactols.csv`. Elles ne sont pas injectées dans le module
public tant que la revue des 31 formes n'est pas achevée.

Lien de recette :
https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43194175957
