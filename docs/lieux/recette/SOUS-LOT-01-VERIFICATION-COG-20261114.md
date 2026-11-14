# Référentiel Lieux — sous-lot éditorial 01 : vérification COG 2026

**Statut : dix candidats administrativement corroborés, zéro alignement Pactols–COG nouvellement validé.**

Ce contrôle porte sur les dix premières autorités du groupe des 83 candidatures
ordinaires sans contradiction documentaire détectée, dans la revue de
`REVUE-CONTEXTES-LOT-001.md`. Il ne préjuge ni du vocabulaire d'autorité
Pactols ni de la géométrie historique.

Les **dix fiches officielles Insee (COG au 1er janvier 2026)** ont été
retrouvées ; toutes présentent le code, le libellé et le département
attendus :

| ARK Pactols (suffixe) | Libellé | Département | Code COG 2026 |
| --- | --- | --- | --- |
| `pcrtTT6sGvSKno` | Ambronay | 01 | `01007` |
| `pcrtCc5628YFYt` | Crouy | 02 | `02243` |
| `pcrtMiDUaETsXu` | Abrest | 03 | `03001` |
| `pcrteT1TEHXSQh` | Annot | 04 | `04008` |
| `pcrtDiUQvNk5nJ` | Arvieux | 05 | `05007` |
| `pcrtklDRrrzDMy` | Andon | 06 | `06003` |
| `pcrtiRFQp99noq` | Lavilledieu | 07 | `07138` |
| `pcrtWkrwOcwsGf` | Annelles | 08 | `08014` |
| `pcrtvoSud5XqM5` | Artigat | 09 | `09019` |
| `pcrte33QlrWu7z` | Sainte-Maure | 10 | `10352` |

Les liens vers les **dix fiches Insee et les dix ARK** sont conservés
ligne par ligne dans `sous-lot-01-cog2026-controle.csv`. À ce stade,
les identités administratives contemporaines sont corroborées.

**Réserve éditoriale :** les ARK Pactols n'ont pas pu être
interrogés directement dans le serveur d'autorités lors de ce
contrôle ; leurs libellés et hiérarchies viennent de notre extraction
XML, et non d'un contrôle SKOS indépendant. Les dix correspondances
demeurent donc `non_valide`.

Le cas **Annelles** ne comporte pas d'attestation dans un titre
de notice ; l'indexation dans le corps du XML étant valide dans
AdlFI, cette absence ne constitue pas une anomalie à elle seule.

## Passage ultérieur à l'intégration

1. Vérifier les fiches Pactols vivantes, variantes et éventuels
   changements conceptuels ; accepter ou refuser éditorialement les
   couples ARK–COG un par un.
2. Distinguer épisode COG historique et commune actuelle ;
   confronter le cas échéant les événements Insee.
3. Attribuer uniquement les **géométries du millésime et du produit
   cartographique retenus**, comme données contemporaines datées ;
   sans inférer un contour historique.
4. Ajouter les couples validés au référentiel national, en
   conservant le pilote PACA, son historique de validation et
   toutes les correspondances non validées hors production.

**Aucune modification de `docs/data/lieux.json` ou de
`docs/data/lieux-communes.geojson`.**
