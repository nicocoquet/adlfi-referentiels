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
