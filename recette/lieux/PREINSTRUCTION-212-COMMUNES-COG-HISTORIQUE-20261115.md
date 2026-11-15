# Lieux — préinstruction temporelle des 212 communes ultramarines actuelles

**15 novembre 2026 · Référentiel Lieux AdlFI · PR #30 · RECETTE NON VALIDANTE**

## Périmètre et méthodes

Reprise de **l'exact lot de 212 candidats** issu du RDF Pactols-Lieux `th17` daté du 22 juillet 2026 (une piste avec URI INSEE de même code pour chaque commune). Contrôle croisé avec les fichiers officiels COG 2026 suivants :

- `v_commune_2026.csv` et `v_commune_depuis_1943.csv` pour les 129 communes des cinq DROM ;
- `v_mvt_commune_2026.csv` pour les mouvements DROM ;
- `v_commune_comer_2026.csv` et `v_commune_outremer_depuis_1943.csv` pour les 83 subdivisions de nature `COM` de Polynésie française, Nouvelle-Calédonie et Saint-Pierre-et-Miquelon.

Toutes les **212 URI INSEE de commune** contenues dans les concepts Pactols concordent avec leur code COG 2026 ; les **212 états COG au 1er janvier 2026** ont un libellé concordant dans les tables historiques ; codes et ARK sont distincts. **Ce contrôle technique ne valide aucune correspondance individuelle AdlFI**.

## Quatre catégories exclusives de préinstruction

| Catégorie | Nombre | Conséquence |
|---|---:|---|
| Homonymies / plusieurs concepts candidats | **5** | Décision entre concepts après désambiguïsation (Trois-Rivières, Le Lamentin, Le Marin, Le Port, Le Mont-Dore) |
| Référent spatial potentiellement différent | **1** | Saint-Pierre `97502` : le concept `26678/pcrtYQmFfwxLq8` est libellé **« île Saint-Pierre (Saint-Pierre-et-Miquelon) »**, tandis que le COG décrit la commune **Saint-Pierre** |
| Historique administratif à instruire | **24** | Première attestation plus tardive, périodes multiples ou mouvement COG après création/entrée du code |
| Contrôle éditorial standard | **182** | Candidature de 2026 techniquement concordante, sans autre signal relevé dans ces sources ; pas encore validée |
| **Total** | **212** | **0 approbation individuelle nouvelle** |

Ainsi, les **207** communes à piste unique précédemment proposées se divisent en **182 contrôles standards + 24 cas historiques + 1 exception sémantique**. L'absence d'alerte temporelle dans le groupe standard n'établit ni l'invariabilité des limites ni une équivalence conceptuelle intemporelle.

### Exemples d'alertes historiques justifiant le tri

- **Guyane, Mana (`97306`)** : mouvements `MOD=31` en 1969 et `MOD=20` en 1989, malgré un seul libellé dans la table des périodes ; même code et même nom ne prouvent donc pas un périmètre stable.
- **Guyane, Régina (`97301`)** : mouvements et changement de libellé en 1969.
- **Guyane, Grand-Santi (`97357`)** : plusieurs épisodes et mouvements en 1969, 1976 et 1993.
- **La Réunion, Saint-Louis (`97414`)** : division en 1965 entraînant notamment la création de Cilaos (`97424`) ; l'origine des deux entités doit être distinguée.
- **Martinique, Le Carbet (`97204`)** et **Case-Pilote (`97205`)** : divisions respectivement en 1949 et 1950 ; les nouveaux codes `97233` et `97234` doivent conserver leurs dates de première attestation.
- **Guadeloupe, Capesterre-Belle-Eau (`97107`)** : ancien libellé « Capesterre-de-Guadeloupe », changement en 1976.

Sur les 212 cibles, la source fournit **225 épisodes code–libellé COG**, répartis entre les deux familles de fichiers historiques. Les 24 cas prioritaires sont des **cibles distinctes**, pas un décompte d'événements.

### Concordances de libellé Pactols / COG

| Forme constatée | Nombre |
|---|---:|
| Libellés identiques après normalisation | 182 |
| Libellé Pactols avec précision territoriale compatible | 28 |
| Article omis dans le concept Pactols (« L'Île-des-Pins » / « Île-des-Pins ») | 1 |
| Referent potentiellement différent (« île Saint-Pierre » / commune) | 1 |

Ces quatre modalités lexicales sont **indépendantes** des quatre catégories d'instruction ci-dessus.

## Provenance et limites de la recette

Empreintes SHA-256 :
- Lot source 212 : `d156e894bdb0a2d8c76b19729b140f76a000a2da98e3461558dde41e3396dcaa`
- COG communes 2026 : `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`
- Historique communes depuis 1943 : `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`
- Mouvements communaux : `8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`
- Zonages COMER 2026 (extraction déjà qualifiée) : `ff6812488f504b63dddfa5216f6f4254c5d1001bcc9e5f5b1305e7ffc559ddc3`
- Historique COMER (extraction déjà qualifiée) : `53c2fe2bf44718f105403b51b232560fc8381de000688f3d3ebbc37dfa99b19d`

Les 83 communes de Polynésie, Nouvelle-Calédonie et Saint-Pierre-et-Miquelon disposent de leurs périodes COG, mais **pas, dans ce lot, d'une table de mouvements aussi détaillée que celle des DROM**. L'absence d'événement relevé pour ces communes ne démontre donc pas qu'aucune transformation territoriale n'a eu lieu.

**Aucune généralisation d'identité Pactols vers les périodes historiques, aucun `skos:exactMatch` nouveau, aucune géométrie historique et aucune modification de `docs/`.**

### Livrable de recette conservé hors Pages

Un classeur éditorial de cinq feuilles (`Vue_ensemble`, `Candidats_212`, `Prioritaires_30`, `Episodes_COG_225`, `Provenance`) et quatre CSV complémentaires ont été produits dans la conversation du 15 novembre 2026 ; le programme de génération est fourni dans la même archive. **Saisir les décisions exclusivement dans la feuille `Candidats_212`** ; l'autre vue est une copie de lecture.

## Suite préconisée

1. **Premier arbitrage : Saint-Pierre `97502`** — l'ARK existant peut désigner l'île sans représenter juridiquement la commune.
2. Examiner les **24 cas temporels** et déterminer explicitement la portée de chaque relation à partir de 2026, sans l'étendre aux états antérieurs.
3. Instruire ensuite les **182 cas standards**, par petits lots régionaux, et traiter séparément les cinq homonymies.
4. Publier uniquement les décisions individuelles approuvées, après un export contrôlé distinct de la recette.
