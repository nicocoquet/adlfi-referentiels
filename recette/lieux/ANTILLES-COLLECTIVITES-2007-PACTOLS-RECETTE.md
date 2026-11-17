# Saint-Barthélemy et Saint-Martin — audit RDF Pactols des six codes historiques/actuels

**17 novembre 2026 — recette documentaire non validante, aucun alignement public modifié.**

Après la [PR n°65](https://github.com/nicocoquet/adlfi-referentiels/pull/65), le référentiel dispose de deux successions juridiques attestées entre anciennes communes et collectivités de 2007. La présente étape vérifie **la nature des correspondances Pactols disponibles**, sans créer de lien du seul fait du transfert des droits et obligations.

## Périmètre exact

| Identité administrative | Saint-Barthélemy | Saint-Martin |
| --- | --- | --- |
| Ancienne commune (jusqu'au 23 février 2007) | `97123` | `97127` |
| Collectivité actuelle | `977` | `978` |
| Code d'application à cinq positions, non communal | `97701` | `97801` |

Ces six identifiants n'ont **pas la même nature**. En particulier, le fait qu'un export RDF porte un éventuel `skos:exactMatch` vers `http://id.insee.fr/geo/commune/97701` ne prouverait **pas** l'existence d'une commune actuelle Saint-Barthélemy ; le code à cinq chiffres sert à la codification applicative selon [l'Insee](https://www.insee.fr/fr/information/7929495).

## Sources épinglées

- Frantiq, [PACTOLS](https://github.com/frantiq/PACTOLS), export RDF Lieux `Pactols_Lieux_th17_20260722.rdf` au commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- Insee, COG 2026, fichier `v_commune_comer_2026.csv` à l'empreinte `9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8`.

Le workflow récupère le RDF par **Git LFS**, vérifie l'empreinte, lit ses concepts en flux, puis extrait les éventuelles déclarations **`skos:exactMatch`** portant exactement sur l'un des six codes. Il en conserve la famille d'URI, le libellé préféré, les variantes et les indicateurs de dépréciation/remplacement.

Les ressemblances lexicales assorties de précisions géographiques sont recensées **comme candidats non validants** ; les simples homonymes « Saint-Martin » ne sont pas transformés en correspondances.

## Politique de qualification

- `97123`/`97127` : une URI explicite est une **preuve vers une ancienne autorité communale** et ne vaut pas alignement vers la collectivité successeure.
- `977`/`978` : une URI explicite peut documenter une **autorité de collectivité d'outre-mer**, sous réserve de sa nature sémantique.
- `97701`/`97801` : tout `exactMatch`, même étiqueté comme « commune » dans son URI, demande **un examen ontologique** et ne peut être validé comme lien communal courant.
- Aucun `skos:exactMatch` historique n'est rétroprojeté, aucun ARK ne passe automatiquement d'une entité à l'autre.
- Le rapport conserve **zéro alignement publié**, **zéro contour historique**, **zéro validation automatique**, quel que soit le résultat du RDF.

## Résultats RDF Frantiq (17 novembre 2026)

La [CI n°44052876958](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44052876958) a réussi la lecture du RDF officiel épinglé et la double exécution reproductible. **Deux concepts uniques** sont directement liés à **quatre URI INSEE** :

| Collectivité COG | ARK Pactols | `skos:prefLabel` du concept | URI explicites `skos:exactMatch` |
| --- | --- | --- | --- |
| `977` Saint-Barthélemy | `26678/pcrtrGdtY56gmH` | Saint-Barthélemy (Antilles Françaises) | `http://id.insee.fr/geo/collectiviteDOutreMer/977` **et** `http://id.insee.fr/geo/commune/97701` |
| `978` Saint-Martin | `26678/pcrty5LooX8FgU` | Saint-Martin (Antilles Françaises) | `http://id.insee.fr/geo/collectiviteDOutreMer/978` **et** `http://id.insee.fr/geo/commune/97801` |

Le second concept présente également l'**`altLabel` français « Saint-Martin (Guadeloupe) »**, correspondant à une forme historique de localisation et non à une preuve d'identité avec l'ancienne commune `97127`.

Les deux concepts sont **non dépréciés et non remplacés**. L'audit du RDF épinglé ne trouve **aucune URI `exactMatch` vers les anciennes communes `97123` et `97127`**.

**Interprétation :** les URI `collectiviteDOutreMer/977` et `/978` constituent des preuves fortes en faveur de correspondances vers les **collectivités actuelles**. Les URI `commune/97701` et `commune/97801` existent effectivement dans Pactols, mais leurs suffixes sont des **codes applicatifs** selon l'Insee et ne permettent pas de réintroduire des communes inexistantes.

Les correspondances `977` / `978` peuvent être **proposées à l'arbitrage éditorial** avec indication explicite de leur catégorie. Elles ne sont **pas encore homologuées ni publiées** dans cette PR.

### Faux positifs lexicaux

Le premier passage a recensé **18 ressemblances « Saint-Barthélemy »** correspondant à d'autres communes (Villers-Saint-Barthélemy, Saint-Barthélemy-d'Anjou, etc.). Ces résultats **ne sont pas des candidats antillais**. La recette a été corrigée pour les **écarter de la liste des candidats qualifiés** et les dénombrer séparément comme homonymes sans contexte antillais. Ce contrôle limite les alignements par ressemblance et est testé sur le RDF synthétique.


### Recette finale des homonymes (RDF épinglé)

La [CI consolidée n°44053293173](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44053293173) confirme **quatre déclarations exactMatch vers les six codes**, émanant des **deux concepts Pactols décrits ci-dessus**. Aucune ancienne commune `97123` ou `97127` n'est référencée par exactMatch.

Après exclusion des toponymes sans contexte antillais dans leur libellé préféré, le contrôle a écarté **304 concepts contenant « Saint-Martin » ou « Saint-Barthélemy »** au sens lexical (dont les 18 Saint-Barthélemy identifiés lors du premier passage). Ce sont **304 cas non qualifiés géographiquement par leur seul libellé**, pas nécessairement 304 lieux distincts. **Zéro candidat purement lexical suffisamment contextualisé** demeure dans le périmètre de cette recette.

Ce constat ne conduit à **aucune validation automatique**. Les concepts actuels `977` / `978` restent proposés pour examen éditorial en tant qu'autorités territoriales, avec le problème des deux `exactMatch` vers les codes applicatifs `97701` / `97801` conservé dans la note.
