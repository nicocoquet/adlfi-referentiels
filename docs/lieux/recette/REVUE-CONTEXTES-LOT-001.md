# Lieux — Lot 001 : instruction documentaire des 89 candidatures ordinaires

**Statut : travail en recette, aucune correspondance Pactols–COG nouvelle validée.**

## Contrat de vérification

Ce contrôle relit les **occurrences géographiques indexées dans toute la notice TEI**, leurs chemins Pactols et les titres des notices issus de l’extraction nationale v2. Il ne vérifie pas le contenu intégral du paragraphe de chaque notice et ne remplace ni l’autorité Pactols, ni les mouvements du COG, ni la validation éditoriale.

- **89** candidatures ordinaires du lot initial de 100 autorités, toutes déclarées présentes dans le COG 2026 par la qualification nationale.
- **0** discordance entre départements dans les chaînes Pactols du même ARK.
- **0** divergence territoriale entre chemins Pactols une fois ignoré le préfixe facultatif « entités actuelles » (17 ARK concernés par ce seul préfixe).
- **22** ARK ne figurent dans aucun titre de notice associé : ce n’est **pas** une anomalie, puisque l’indexation peut se trouver dans le corps.
- **6** ARK apparaissent dans des notices indexant majoritairement d’autres départements : signal de contexte, pas anomalie avérée.

## Trois priorités de relecture contextuelle

| ARK / libellé | Code COG proposé | Notice témoin | Motif |
|---|---|---|---|
| [Bethon](https://ark.frantiq.fr/ark:/26678/pcrt5YI2zQtodM) | `51056` | Autoroute A28 | Nom non présent dans les titres et notice à plusieurs départements |
| [Usson](https://ark.frantiq.fr/ark:/26678/pcrtavZRJRD9Uf) | `63439` | Habitats agglomérés en pays ségusiave : les formes du fait urbain dans la cité ségusiave du ier s. au iiie s. apr. J.‑C. | Nom non présent dans les titres et notice à plusieurs départements |
| [Marsangy](https://ark.frantiq.fr/ark:/26678/pcrttMIHapwXmV) | `89245` | Habitats et peuplements du Tardiglaciaire dans le Bassin parisien | Nom non présent dans les titres et notice à plusieurs départements |

**Bethon** apparaît dans une notice « Autoroute A28 » indexant des communes de la Sarthe, tandis que son ARK est situé dans la Marne. **Usson** apparaît dans une synthèse sur le pays ségusiave (Loire), tandis que son ARK renvoie au Puy-de-Dôme. **Marsangy** est indexé dans une recherche interrégionale sur le Tardiglaciaire : le contexte est compatible avec un corpus transversal. Ces trois cas doivent être relus au niveau du passage XML, sans correction automatique.

## Trois notices transdépartementales sans contradiction directe

| ARK / libellé | Code COG proposé | Contexte |
|---|---|---|
| [Agen](https://ark.frantiq.fr/ark:/26678/pcrtYQrGrlUtyP) | `47001` | 1 occurrence(s) de contexte transversal ; libellé attesté dans au moins un titre |
| [Angers](https://ark.frantiq.fr/ark:/26678/pcrtHSt4S6U0IG) | `49007` | 1 occurrence(s) de contexte transversal ; libellé attesté dans au moins un titre |
| [Paris](https://ark.frantiq.fr/ark:/26678/pcrtKWS6It1qMw) | `75056` | 2 occurrence(s) de contexte transversal ; libellé attesté dans au moins un titre |

Ces trois ARK ne sont pas classés comme erreurs : **Agen, Angers et Paris** peuvent figurer légitimement dans des synthèses interrégionales.

## Les 83 candidatures sans conflit détecté — pour validation éditoriale

La table suivante n’est **pas** une validation collective. Chaque entrée a déjà : un ARK terminal Pactols observé, un département Pactols cohérent, un nom rapproché du COG historique par le pipeline et un code candidat déclaré présent en 2026. **Un examen conceptuel de l’ARK et de la dénomination officielle demeure requis.**

### Sous-lot éditorial 01 — 10 autorités

| N° source | Lieu Pactols | Département | Code COG candidat | Attestation dans un titre |
|---:|---|---|---|---|
| 1 | [Ambronay](https://ark.frantiq.fr/ark:/26678/pcrtTT6sGvSKno) | 01 | `01007` | oui |
| 2 | [Crouy](https://ark.frantiq.fr/ark:/26678/pcrtCc5628YFYt) | 02 | `02243` | oui |
| 3 | [Abrest](https://ark.frantiq.fr/ark:/26678/pcrtMiDUaETsXu) | 03 | `03001` | oui |
| 4 | [Annot](https://ark.frantiq.fr/ark:/26678/pcrteT1TEHXSQh) | 04 | `04008` | oui |
| 5 | [Arvieux](https://ark.frantiq.fr/ark:/26678/pcrtDiUQvNk5nJ) | 05 | `05007` | oui |
| 6 | [Andon](https://ark.frantiq.fr/ark:/26678/pcrtklDRrrzDMy) | 06 | `06003` | oui |
| 7 | [Lavilledieu](https://ark.frantiq.fr/ark:/26678/pcrtiRFQp99noq) | 07 | `07138` | oui |
| 8 | [Annelles](https://ark.frantiq.fr/ark:/26678/pcrtWkrwOcwsGf) | 08 | `08014` | non (sans conséquence automatique) |
| 9 | [Artigat](https://ark.frantiq.fr/ark:/26678/pcrtvoSud5XqM5) | 09 | `09019` | oui |
| 10 | [Sainte-Maure](https://ark.frantiq.fr/ark:/26678/pcrte33QlrWu7z) | 10 | `10352` | oui |

### Sous-lot éditorial 02 — 10 autorités

| N° source | Lieu Pactols | Département | Code COG candidat | Attestation dans un titre |
|---:|---|---|---|---|
| 11 | [Ajac](https://ark.frantiq.fr/ark:/26678/pcrtFfkm57S1lx) | 11 | `11003` | oui |
| 12 | [Baraqueville](https://ark.frantiq.fr/ark:/26678/pcrt4I6Zc2M4t3) | 12 | `12056` | oui |
| 13 | [Tarascon](https://ark.frantiq.fr/ark:/26678/pcrtPj5N1U4mq0) | 13 | `13108` | oui |
| 14 | [Avenay](https://ark.frantiq.fr/ark:/26678/pcrtH7C0WTQYKe) | 14 | `14034` | non (sans conséquence automatique) |
| 15 | [Dienne](https://ark.frantiq.fr/ark:/26678/pcrt7FhDrovXpO) | 15 | `15061` | oui |
| 16 | [Fontenille](https://ark.frantiq.fr/ark:/26678/pcrtMrVaPpiOEO) | 16 | `16141` | non (sans conséquence automatique) |
| 17 | [Arces](https://ark.frantiq.fr/ark:/26678/pcrtmfWfCtYbAp) | 17 | `17015` | oui |
| 18 | [Vinon](https://ark.frantiq.fr/ark:/26678/pcrtHwhtjGtYRd) | 18 | `18287` | non (sans conséquence automatique) |
| 19 | [Forgès](https://ark.frantiq.fr/ark:/26678/pcrtjM8uRzncP7) | 19 | `19084` | non (sans conséquence automatique) |
| 21 | [Belle-Isle-en-Terre](https://ark.frantiq.fr/ark:/26678/pcrtWd1O5YLHBu) | 22 | `22005` | non (sans conséquence automatique) |

### Sous-lot éditorial 03 — 10 autorités

| N° source | Lieu Pactols | Département | Code COG candidat | Attestation dans un titre |
|---:|---|---|---|---|
| 22 | [Chéniers](https://ark.frantiq.fr/ark:/26678/pcrtL6Gk5EJWiP) | 23 | `23062` | oui |
| 23 | [Bussac](https://ark.frantiq.fr/ark:/26678/pcrt64zW3NexyH) | 24 | `24069` | non (sans conséquence automatique) |
| 24 | [Blamont](https://ark.frantiq.fr/ark:/26678/pcrtUB6r9H3T98) | 25 | `25063` | non (sans conséquence automatique) |
| 25 | [Aleyrac](https://ark.frantiq.fr/ark:/26678/pcrtxOrcEIhzkl) | 26 | `26003` | oui |
| 26 | [Bernay](https://ark.frantiq.fr/ark:/26678/pcrt0x8LXL0n1o) | 27 | `27056` | oui |
| 28 | [Pont-l'Abbé](https://ark.frantiq.fr/ark:/26678/pcrtG4dwNJsgks) | 29 | `29220` | oui |
| 31 | [Belvézet](https://ark.frantiq.fr/ark:/26678/pcrtzJx1TkibCd) | 30 | `30035` | oui |
| 32 | [Baziège](https://ark.frantiq.fr/ark:/26678/pcrtu9pXE0pbU0) | 31 | `31048` | oui |
| 33 | [Aignan](https://ark.frantiq.fr/ark:/26678/pcrtpLof2LddIc) | 32 | `32001` | oui |
| 34 | [Ambarès-et-Lagrave](https://ark.frantiq.fr/ark:/26678/pcrts44hSg1ubX) | 33 | `33003` | oui |

### Sous-lot éditorial 04 — 10 autorités

| N° source | Lieu Pactols | Département | Code COG candidat | Attestation dans un titre |
|---:|---|---|---|---|
| 35 | [Agde](https://ark.frantiq.fr/ark:/26678/pcrt3SAD6LErSm) | 34 | `34003` | oui |
| 36 | [Romagné](https://ark.frantiq.fr/ark:/26678/pcrtepDiashlKX) | 35 | `35243` | oui |
| 37 | [Châteauroux](https://ark.frantiq.fr/ark:/26678/pcrtVZdnBjW66u) | 36 | `36044` | oui |
| 38 | [Abilly](https://ark.frantiq.fr/ark:/26678/pcrtfD8T660S4l) | 37 | `37001` | oui |
| 39 | [Châtonnay](https://ark.frantiq.fr/ark:/26678/pcrtxNn64DrZnI) | 38 | `38094` | oui |
| 40 | [Frontenay](https://ark.frantiq.fr/ark:/26678/pcrtQaN9NA0g9s) | 39 | `39244` | oui |
| 41 | [Saint-Sever](https://ark.frantiq.fr/ark:/26678/pcrtvbVvDDMpIL) | 40 | `40282` | oui |
| 42 | [Angé](https://ark.frantiq.fr/ark:/26678/pcrtdgjeXUw2C2) | 41 | `41002` | oui |
| 43 | [Malleval](https://ark.frantiq.fr/ark:/26678/pcrtQXoHojO7Fn) | 42 | `42132` | oui |
| 44 | [Aiguilhe](https://ark.frantiq.fr/ark:/26678/pcrtbsR8epj2JF) | 43 | `43002` | oui |

### Sous-lot éditorial 05 — 10 autorités

| N° source | Lieu Pactols | Département | Code COG candidat | Attestation dans un titre |
|---:|---|---|---|---|
| 45 | [Legé](https://ark.frantiq.fr/ark:/26678/pcrtJMCDDYbQRv) | 44 | `44081` | non (sans conséquence automatique) |
| 46 | [Guigneville](https://ark.frantiq.fr/ark:/26678/pcrtKFPxueU3lT) | 45 | `45162` | non (sans conséquence automatique) |
| 47 | [Blars](https://ark.frantiq.fr/ark:/26678/pcrterqjXno7RS) | 46 | `46031` | non (sans conséquence automatique) |
| 49 | [Hures-la-Parade](https://ark.frantiq.fr/ark:/26678/pcrt6vISOPzjjL) | 48 | `48074` | oui |
| 51 | [Agon-Coutainville](https://ark.frantiq.fr/ark:/26678/pcrtOJmHh6rsPW) | 50 | `50003` | oui |
| 53 | [Ageville](https://ark.frantiq.fr/ark:/26678/pcrtnHV6CVTECv) | 52 | `52001` | non (sans conséquence automatique) |
| 54 | [Ménil](https://ark.frantiq.fr/ark:/26678/pcrtN7qB9oCXum) | 53 | `53150` | oui |
| 55 | [Allain](https://ark.frantiq.fr/ark:/26678/pcrtN8A40qP95H) | 54 | `54008` | oui |
| 56 | [Bure](https://ark.frantiq.fr/ark:/26678/pcrtXvS55XdMG7) | 55 | `55087` | oui |
| 57 | [Locmaria](https://ark.frantiq.fr/ark:/26678/pcrtAxZ5feDA6j) | 56 | `56114` | oui |

### Sous-lot éditorial 06 — 10 autorités

| N° source | Lieu Pactols | Département | Code COG candidat | Attestation dans un titre |
|---:|---|---|---|---|
| 58 | [Abreschviller](https://ark.frantiq.fr/ark:/26678/pcrtxKiOms72tf) | 57 | `57003` | oui |
| 59 | [Entrains-sur-Nohain](https://ark.frantiq.fr/ark:/26678/pcrt1GKycVqkFj) | 58 | `58109` | oui |
| 60 | [Bierne](https://ark.frantiq.fr/ark:/26678/pcrtf81WrAjFlX) | 59 | `59082` | oui |
| 61 | [Lagny](https://ark.frantiq.fr/ark:/26678/pcrtIrWRDneMrM) | 60 | `60340` | oui |
| 62 | [Alençon](https://ark.frantiq.fr/ark:/26678/pcrtczVoj3JANO) | 61 | `61001` | oui |
| 63 | [Ablain-Saint-Nazaire](https://ark.frantiq.fr/ark:/26678/pcrtEbNjiP9etS) | 62 | `62001` | oui |
| 65 | [Abidos](https://ark.frantiq.fr/ark:/26678/pcrtuDG7aEXWwg) | 64 | `64003` | oui |
| 66 | [Argelès-Gazost](https://ark.frantiq.fr/ark:/26678/pcrtG4UxkC1pfE) | 65 | `65025` | oui |
| 67 | [Alénya](https://ark.frantiq.fr/ark:/26678/pcrtVg6jEjXcSF) | 66 | `66002` | oui |
| 68 | [Achenheim](https://ark.frantiq.fr/ark:/26678/pcrtE3js68aPwp) | 67 | `67001` | oui |

### Sous-lot éditorial 07 — 10 autorités

| N° source | Lieu Pactols | Département | Code COG candidat | Attestation dans un titre |
|---:|---|---|---|---|
| 69 | [Altkirch](https://ark.frantiq.fr/ark:/26678/pcrttESRWnN4kD) | 68 | `68004` | non (sans conséquence automatique) |
| 71 | [Lure](https://ark.frantiq.fr/ark:/26678/pcrtBI3qNVNjJq) | 70 | `70310` | oui |
| 72 | [Allériot](https://ark.frantiq.fr/ark:/26678/pcrtOTNsIQIIXk) | 71 | `71004` | non (sans conséquence automatique) |
| 73 | [Aigné](https://ark.frantiq.fr/ark:/26678/pcrtFQDClxWaiv) | 72 | `72001` | non (sans conséquence automatique) |
| 74 | [Aiguebelette-le-Lac](https://ark.frantiq.fr/ark:/26678/pcrtOo0Qs0peY5) | 73 | `73001` | oui |
| 75 | [Le Sappey](https://ark.frantiq.fr/ark:/26678/pcrtazSTqVVZSu) | 74 | `74259` | non (sans conséquence automatique) |
| 77 | [Néville](https://ark.frantiq.fr/ark:/26678/pcrtkTli0l8mwB) | 76 | `76467` | oui |
| 78 | [Gironville](https://ark.frantiq.fr/ark:/26678/pcrtTNWFIlbILA) | 77 | `77207` | oui |
| 79 | [Ablis](https://ark.frantiq.fr/ark:/26678/pcrt0RHu3a9rJP) | 78 | `78003` | oui |
| 81 | [Allaines](https://ark.frantiq.fr/ark:/26678/pcrthoBeVXnDEP) | 80 | `80017` | oui |

### Sous-lot éditorial 08 — 10 autorités

| N° source | Lieu Pactols | Département | Code COG candidat | Attestation dans un titre |
|---:|---|---|---|---|
| 82 | [Albi](https://ark.frantiq.fr/ark:/26678/pcrtjrLK9Gj1Hf) | 81 | `81004` | oui |
| 83 | [Moissac](https://ark.frantiq.fr/ark:/26678/pcrt5aD7IVl17S) | 82 | `82112` | oui |
| 84 | [Bagnols-en-Forêt](https://ark.frantiq.fr/ark:/26678/pcrtWPMc6cEiPw) | 83 | `83008` | oui |
| 85 | [Mazan](https://ark.frantiq.fr/ark:/26678/pcrto4i3DAb9kr) | 84 | `84072` | non (sans conséquence automatique) |
| 86 | [Saint-Mathurin](https://ark.frantiq.fr/ark:/26678/pcrtsX02FSWJI6) | 85 | `85250` | oui |
| 87 | [Dienné](https://ark.frantiq.fr/ark:/26678/pcrtZTVRR6ec7w) | 86 | `86094` | non (sans conséquence automatique) |
| 88 | [Châlus](https://ark.frantiq.fr/ark:/26678/pcrtf09FoSufrV) | 87 | `87032` | oui |
| 89 | [Escles](https://ark.frantiq.fr/ark:/26678/pcrtSvDZ5FlbSN) | 88 | `88161` | oui |
| 96 | [Ambutrix](https://ark.frantiq.fr/ark:/26678/pcrtuwpXdP1G1g) | 01 | `01008` | oui |
| 97 | [Ribemont](https://ark.frantiq.fr/ark:/26678/pcrtzXc4L7n9Xl) | 02 | `02648` | oui |

### Sous-lot éditorial 09 — 3 autorités

| N° source | Lieu Pactols | Département | Code COG candidat | Attestation dans un titre |
|---:|---|---|---|---|
| 98 | [Arpheuilles-Saint-Priest](https://ark.frantiq.fr/ark:/26678/pcrtvwJKaFrKRk) | 03 | `03007` | non (sans conséquence automatique) |
| 99 | [Aubignosc](https://ark.frantiq.fr/ark:/26678/pcrt7Tbs38Xh58) | 04 | `04013` | oui |
| 100 | [Aspres-sur-Buëch](https://ark.frantiq.fr/ark:/26678/pcrtR6sbwreH7k) | 05 | `05010` | oui |

## Conservation du référentiel maître et critères de publication

Pour chaque ARK, conserver son identifiant, tous ses chemins hiérarchiques observés, son statut documentaire et ses attestations. La candidature de code INSEE est une **relation proposée** jusqu’à validation ; une année d’opération archéologique n’est pas une date de validité du nom ou du contour. Aucun des 89 candidats n’a encore reçu une géométrie certifiée.

**Audit reproductible** : `scripts/auditer_contextes_lieux_lot001.py` et tests `tests/test_auditer_contextes_lieux_lot001.py`. Sources locales originales identifiées par leurs SHA-256 dans `bilan_contextes_lot001.json`.

**Dossiers exclus de cette revue** : huit transitions de code MOD 41, Allaines-Mervilliers, Aigondigné, Brain/Pays de Retz. Ils font l’objet de l’instruction dédiée déjà conservée dans cette branche.
