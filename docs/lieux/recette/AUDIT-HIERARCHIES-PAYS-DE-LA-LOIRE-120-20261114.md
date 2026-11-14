# Pays de la Loire — instruction des 120 lieux imbriqués (14 novembre 2026)

**PR n°24 — audit de recette non validant.** Les calculs sont réalisés sur les CSV de l'extraction AdlFI v2 et sur l'inventaire de 806 autorités contrôlé par SHA-256 lors de la reconstruction régionale. Une « relation de parent » désigne **uniquement la position dans une chaîne hiérarchique Pactols attestée dans les XML** : elle ne prouve pas, par elle-même, une relation administrative Insee, une commune déléguée ni une succession historique.

## Résultats de la vérification des chaînes

| Mesure | Résultat |
| --- | ---: |
| ARK terminaux imbriqués dans une hiérarchie départementale | **120** |
| ARK avec un parent Pactols unique parmi les chaînes attestées | **120** |
| Parents Pactols distincts | **53** |
| ARK imbriqués dont le parent apparaît aussi dans l'inventaire des 806 ARK terminaux | **96** |
| ARK imbriqués dont le parent n'est pas lui-même terminal dans ce corpus | **24** |
| Parents distincts ne figurant pas comme terminaux | **19** |
| ARK dont le code communal SKOS est partagé avec un autre ARK de l'inventaire | **22** |
| Parmi eux, codes également portés par leur parent Pactols terminal | **22** |
| Autres ARK imbriqués, dont le code n'est pas partagé dans les 806 | **98** |
| Code historique hors département de la hiérarchie Pactols | **1** : Le Puy-Saint-Bonnet, `79224` |

Répartition des **120** : Loire-Atlantique **10**, Maine-et-Loire **90**, Mayenne **4**, Sarthe **7**, Vendée **9**. La surreprésentation du Maine-et-Loire reflète surtout le corpus Pactols documenté, non une mesure exhaustive des restructurations administratives régionales.

## Principaux groupes de parents (structure Pactols, non composition officielle exhaustive)

| Parent dans la hiérarchie | Enfants terminaux attestés |
| --- | ---: |
| Segré-en-Anjou Bleu | 11 |
| Chemillé-en-Anjou | 8 |
| Ombrée d'Anjou | 8 |
| Mauges-sur-Loire | 6 |
| Baugé-en-Anjou | 5 |
| Brissac Loire Aubance | 5 |
| Gennes-Val-de-Loire | 5 |
| Sèvremoine | 5 |
| Doué-en-Anjou | 4 |

**Attention :** il ne faut pas transformer ces effectifs d'enfants Pactols indexés en effectifs de communes déléguées, fusionnées ou disparues. L'inventaire ne contient que les concepts terminaux effectivement attestés dans les XML étudiés.

## Deux catégories d'instruction

**A. Les 22 enfants ayant le même code Insee que leur parent Pactols terminal** : ils recoupent exactement les 22 codes déjà documentés avec `v_mvt_commune_2026.csv` dans `BILAN-22-CODES-PAYS-DE-LA-LOIRE-COG-20261114.md`. La relation conceptuelle doit être rapprochée, épisode par épisode, des événements officiels, avec attention particulière à Baugé-en-Anjou, Orée d'Anjou et Essarts-en-Bocage.

**B. Les 98 autres enfants** : chacun porte une assertion Pactols vers un code communal distinct dans le corpus régional. Pour établir la nature de son rattachement au parent, il faut retrouver les lignes d'événements Insee avec `TYPECOM_AV/AP`, `COM_AV/AP`, `DATE_EFF` et `MOD`. Le simple parent lexical ou une hiérarchie ne suffit pas.

Par ailleurs, pour **24 enfants**, le parent Pactols est présent comme nœud d'une chaîne, mais pas dans la liste des ARK terminaux. Cela ne constitue pas une absence du concept dans Pactols ; il ne faut ni créer un doublon ni inférer une absence de relation administrative.

## Suites et provenance

La conversation contient une archive de recette `AdlFI_PdL_hierarchies_120_20261114.zip` avec :
- `imbriques-120-contextes.csv` : une ligne par enfant avec ARK du parent, libellés, nombre de parents attestés, code déclaré, présence d'un autre ARK partageant ce code ;
- `parents-53-synthese.csv` : regroupement par parent ;
- `rapport-imbriques-120.json` : contrôles de cardinalité ;
- `analyser_imbriques_120.py` : script de reconstruction de la table à partir des CSV de recette locaux.

La **prochaine étape historique** est de croiser ces **98 codes distincts** avec les fichiers officiels Insee 2026 en conservant tous les événements avant/après et leur provenance. Ne pas présumer que les 98 sont toutes des anciennes communes déléguées ; ne pas attribuer automatiquement les géométries contemporaines des parents aux enfants.

**Zéro nouvelle validation Pactols–COG, zéro géométrie historique publiée.**