# Lot 001 — Instruction des mouvements COG historiques (14 novembre 2026)

**Nature : preuve administrative contrôlée — aucune validation nouvelle Pactols–COG.**

## Sources et périmètre

Les trois sorties de l'auditeur `scripts/auditer_evenements_cog_lot.py` sont archivées
dans `docs/lieux/recette/lot-001-preuves-cog/`. Elles portent sur le lot de
100 autorités Pactols, et ont été transmises après interrogation du fichier
officiel Insee `v_mvt_commune_2026.csv` (13 734 lignes dans cette source).

Empreintes SHA-256 des **entrées originales sur le Mac de l'éditeur**, relevées
par le programme et conservées dans le rapport :

- `lot_editorial_prioritaire_001.csv` :
  `57a60d513eb91f2ea0f6a03c9e838047a3ecac3fb8b59f8125f8248391fc1f46`
- `v_mvt_commune_2026.csv` :
  `8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`

La sémantique des variables `MOD`, `DATE_EFF`,
`TYPECOM_AV/AP`, `COM_AV/AP` est documentée par l'Insee :
https://www.insee.fr/fr/information/8740222

Les fichiers joints sont les **sorties d'audit**, et non une copie
intégrale du fichier Insee. L'audit reste reproductible à partir de
la source originale identifiée par son empreinte.

## A — Huit mutations de code directement attestées

Le CSV `transitions_code_a_verifier.csv` contient huit lignes et, pour
chacune, **une ligne source COG directe exacte**, conservée dans la colonne
`preuve_lignes_cog` : concordance des codes, date d'effet, type COM et
libellé avant/après, avec `MOD=41` (changement de code lié à un changement
de département).

| ARK Pactols (suffixe) | Commune | Code avant | Code après | Date d'effet |
| --- | --- | --- | --- | --- |
| `pcrtgs2LLPYow2` | Afa | 20001 | 2A001 | 1976-01-01 |
| `pcrtGx0ke7aJM6` | Aghione | 20002 | 2B002 | 1976-01-01 |
| `pcrtKhAshygTwg` | Colombier-Saugnieu | 38119 | 69299 | 1971-04-01 |
| `pcrtjtHmRcuVFO` | Abbéville-la-Rivière | 78001 | 91001 | 1968-01-01 |
| `pcrtLVhssZPxil` | Antony | 75002 | 92002 | 1968-01-01 |
| `pcrtPmgdjRPDeg` | Aulnay-sous-Bois | 78032 | 93005 | 1968-01-01 |
| `pcrtTr682PPh7b` | Alfortville | 75001 | 94002 | 1968-01-01 |
| `pcrt66HzrNZZ4l` | Argenteuil | 78018 | 95018 | 1968-01-01 |

**Arbitrage de l'événement administratif : confirmé.** Il ne s'agit pas
de deux communes homonymes simultanées, mais de deux états de codification
successifs d'une commune dans le COG. Conserver les deux codes et les dates
de la transition sous une même candidature d'ARK, sans créer de seconde
autorité Pactols ni déduire une stabilité du contour.

**Alignement ARK → identité COG : à valider éditorialement** ; les huit
lignes demeurent `statut_validation_pactols=non_valide`.

## B — Allaines-Mervilliers (ARK 26678/pcrtwrbovhYGLl)

**Six lignes de mouvement** au 2019-01-01 avec `MOD=32`
(création de commune nouvelle), dans le même ensemble de mouvements
administratifs :

- `COM 28002 Allaines-Mervilliers` →
  `COMD 28002 Allaines-Mervilliers` : changement de statut.
- `COM 28002 Allaines-Mervilliers` →
  `COM 28199 Janville-en-Beauce` : intégration territoriale.
- La source documente aussi `COM 28199 Janville` →
  `COM 28199 Janville-en-Beauce`, `COM 28199 Janville` →
  `COMD 28199 Janville`, et les contributions de Le Puiset
  (`28311`) et de Mervilliers (`COMA 28244`).

**Attention :** ne pas réduire ces six lignes à six créations de communes,
ni déduire que Mervilliers est devenue une commune déléguée :
la ligne disponible indique `COMA 28244 → COM 28199`.

Conserver l'état historique `(COM, 28002)` jusqu'à la transition de
2019, le nouveau statut `(COMD, 28002)` et la relation administrative
vers la commune nouvelle `(COM, 28199)`. La durée de maintien
de la commune déléguée dans les millésimes ultérieurs devra être
contrôlée séparément. **Aucune géométrie 2026 de Janville-en-Beauce
ne remplace le contour historique d'Allaines-Mervilliers.**

## C — Aigondigné (ARK 26678/pcrtfw73wt5vbcj28pg6g6pd)

**Neuf lignes de mouvement** réparties en deux opérations datées :

- **2017-01-01 : quatre lignes `MOD=32`.**
  `COM 79185 Mougon` devient `COM 79185 Mougon-Thorigné`
  et `COMD 79185 Mougon` ; la commune `COM 79327 Thorigné`
  contribue à la commune nouvelle et devient `COMD 79327`.
- **2019-01-01 : cinq lignes `MOD=32`.**
  `COM 79185 Mougon-Thorigné` devient `COM 79185 Aigondigné` ;
  `COM 79004 Aigonnay` et `COM 79240 Sainte-Blandine`
  y contribuent, avec des changements de statut délégué indiqués
  par les lignes COG correspondantes.

**Arbitrage de l'événement administratif : confirmé.** Les trois
états `Mougon → Mougon-Thorigné → Aigondigné` ne doivent pas
être traités comme une identité inchangée au seul motif du code
invariant `79185`. Les deux opérations de création de commune
nouvelle imposent de distinguer **les épisodes d'identité
administrative** et leurs emprises temporelles.

La source Insee confirme les changements de contour de 2017 et 2019 :
https://www.insee.fr/fr/statistiques/2011101?geo=COM-79185

## D — Distinction indispensable pour le référentiel Lieux

**15 lignes de mouvement dans les deux dossiers B et C** correspondent
à **trois opérations de création de commune nouvelle** (Allaines 2019,
Aigondigné 2017, Aigondigné 2019), et non à quinze événements
indépendants.

Modélisation préconisée :

1. **Autorité documentaire Pactols** : ARK, libellé, hiérarchie(s)
   et attestation(s) dans les XML.
2. **Épisode administratif COG** : clé interne distincte,
   `TYPECOM`, `COM`, `LIBELLE`, `date_debut`, `date_fin` ;
   ne jamais faire du seul code `COM` une identité historique.
3. **Relations d'événements** : `MOD`, `DATE_EFF`,
   état avant et état après, source et statut de preuve.
4. **Géométrie** : clé propre, producteur, millésime, résolution,
   licence, emprise temporelle attestée ou explicitement inconnue.

Les 8 changements de code ont un statut `evenement_cog_confirme`,
et les 2 dossiers ont un statut `mouvements_cog_confirmes` :
**ces statuts décrivent la preuve COG, pas l'alignement Pactols**.

## E — Suite de l'instruction

- Vérifier dans le COG 2026 la durée d'activité actuelle des entités
  `COMD` et les autres périodes administratives pertinentes.
- Contrôler le cas **Brain / Pays de Retz** dans le XML source ;
  cette anomalie ne peut pas être levée par les seuls événements COG.
- Présenter ensuite les 89 dossiers ordinaires à validation éditoriale
  par sous-lots, en maintenant le statut `non_valide` par défaut.
- Seulement après cette étape, raccorder les géométries data.gouv/IGN
  selon le **millésime** et l'**épisode administratif**. Pour un
  ancien territoire, une géométrie moderne du successeur n'est pas
  une géométrie historique de l'entité disparue.
