# Consolidation du maître 1.41 — Archéologie Alsace et échelons (11 novembre 2026)

**Statut au 11 novembre 2026 : maître privé 1.41 consolidé ; JSON 1.41 publié par la [PR n° 12](https://github.com/nicocoquet/adlfi-referentiels/pull/12), fusionnée en `main` (`2f5473b1`) ; CI et déploiement GitHub Pages réussis.**

## Traçabilité des artefacts éditoriaux

- **Maître source 1.40** : `AdlFI_referentiel_1-40_20261110_secteur_historique_DRASM_CNRAS.xlsx`, SHA-256 `c0e401ad4c5fa1af46be0f58ec0a989d8bfcb04ada403a2a925e2dce13d2c7ca`.
- **Maître 1.41** : `AdlFI_referentiel_1-41_20261111_Archeologie_Alsace_echelons.xlsx`, SHA-256 `d9ec168c72871e5a5c712aa36f79547d9bf0431bcde8c7c6529cd1e5aa257f07`.
- **JSON de prépublication** (archive de contrôle) : `AdlFI_organismes_1-41_JSON_prepublication_20261111.json`, SHA-256 `c3a0994b0cee722ab2ca065166e66776b16b1cdd37a1b7337c2cf03a211b6173`.
- **JSON publié** (`docs/data/organismes.json`) : SHA-256 `8d145029382db1aec68976d5b2c76396b29f622887ed31d7f6b44d0f2eb221d8`, blob Git `13956635ecf9cb146fafa636d07e88d6247e8405`.
- **Identité visuelle** : renommage du fichier `ORG-0093-logo.webp` en `ORG-0675-logo.webp`, blob inchangé `5fb96d11ff1b26e9df35471816b2ab6e92b94c8f`.

Le **maître privé** et le **JSON de prépublication** restent hors du dépôt public. Seul le fichier `docs/data/organismes.json` final y est publié. Ce JSON a été obtenu par transformation contrôlée du JSON officiel 1.40 avec les modifications du maître 1.41 ; ses champs ont été **vérifiés indépendamment, ligne par ligne**, contre les feuilles du XLSX (y compris les conversions des dates Excel). La réexécution complète de l'exporteur officiel reste une vérification supplémentaire reproductible, sans mettre le maître en dépôt.

## Identités et correspondances

- `ORG-0093` : personne morale SIREN 200006336, établissement public interdépartemental, créé 2006-09-01, clos 2020-12-11 ; activité `non`, type `etablissement_public`, échelon non attribué, ancien site actuel retiré.
- `ORG-0675` : personne morale SIREN 200094746, syndicat mixte ouvert, créé 2020-12-11, actif, type `syndicat_mixte`, secteur `public`, BSR `COL`, Sélestat, site officiel actuel, catalogue inclus.
- `REL-0305` : `ORG-0093 → ORG-0675`, `succession_institutionnelle`, 2020-12-11, `valide`.
- `REL-0054` : conserve `a_verifier` (relation historique avec la CeA temporellement problématique). Pas de migration vers le successeur ; à instruire.
- `HIS-0003` : ancienne dénomination Pair, 2006-09-01 à 2016-10-14 inclus.
- `STH-0003` et `STH-0004` : périodes et formes juridiques des deux personnes morales, avec les sources.
- `AFF-0047` (57 « Pair ») et `AFF-0048` (124 « Archéologie Alsace »), avec `COR-0054` et `COR-0055` : **conservées sur ORG-0093**, zéro occurrence sur ORG-0675. Audit XML : 57 (2014–2015) + 48 (2016) + 76 (2017) = 181.

**Attention** : années d'opération des notices, pas nécessairement dates d'affiliation des auteurs à la publication.

## Lot 01 — échelons institutionnels

- `ORG-0249` Valenciennes Métropole : `type_organisme=epci`, `echelon_territorial=intercommunal`. `STH-0005` : `communaute_agglomeration` (2000-12-31).
- `ORG-0429` Commune de Port-Vendres : `echelon_territorial=communal`.
- `ORG-0650` Métropole de Lyon : `type_organisme=collectivite_territoriale`, `echelon_territorial=metropolitain` conservé provisoirement ; `STH-0006` : `collectivite_statut_particulier`, depuis 2015-01-01.
- `Vocabulaire` : définition des quatre formes juridiques utilisées.

## Contrôles d'intégrité

Classeur : **17 feuilles**, **8 tables Excel** (même nombre et mêmes noms), **40 composants OOXML** (aucune perte/ajout), CRC ZIP et parsabilité XML intégrale correctes. Comparaison cellule à cellule avec 1.40 : seules les feuilles et lignes documentées ci-dessus, ainsi que les journaux/synthèses, évoluent.

Synthèse vérifiée : **654 ORG**, 166 SER, 1580 AFF, 2140 COR, 303 relations ORG, 219 relations SER, 110 autorités inactives, 155 activités non renseignées, 702 villes de référence renseignées. Les anciennes valeurs du tableau de bord (104 / 181 / 696) étaient obsolètes et ont été recalculées.

JSON publié et vérifié : **820 autorités** (654 ORG + 166 SER), **615 visibles**, 205 exclues, **522 relations** au total. Les 164 SER publics et 2 privés ne changent pas.

## Reproductibilité

Depuis la racine du dépôt et sur la machine ayant accès au maître privé :

```bash
python3 -m scripts.controle_maitre_1_41 "/chemin/vers/AdlFI_referentiel_1-41_20261111_Archeologie_Alsace_echelons.xlsx" \
  --report /tmp/controle-maitre-1-41.json \
  --preview-json /tmp/organismes-1-41.json
python3 -m unittest discover -s tests -v
```

Le contrôle de migration échoue en présence de doublons, affiliation réaffectée à la mauvaise personne morale, succession mal datée, lien non validé ou contradiction des statuts juridiques. Les sorties sont écrites dans `/tmp` et ne modifient pas `docs/data/organismes.json`.

**Après publication** : la CI et GitHub Pages ont réussi, le logo actuel est attribué seulement à `ORG-0675`, et les relations de succession sont vérifiées dans le JSON. **Reste à instruire : `REL-0054`**, qui demeure `a_verifier` et n'est pas affichée comme rattachement validé ; ne pas confondre l'adhésion de la CeA au SMO et une tutelle historique. La refonte de la facette « Échelon institutionnel » reste un chantier distinct.

## Sources

- BANATIC (SMO actuel, SIREN, création, composition) : https://www.banatic.interieur.gouv.fr/intercommunalite/200094746-smo-archeologie-alsace-aa
- Personne morale historique : https://www.pappers.fr/entreprise/pair-archeologie-alsace-200006336
- Annonce institutionnelle décembre 2020 : https://www.archeologie.alsace/fr/actualites/actualite?cHash=9e5ed42a8371c6403457d8a378449e67&tx_news_pi1%5Baction%5D=detail&tx_news_pi1%5Bcontroller%5D=News&tx_news_pi1%5Bnews%5D=137
- Valenciennes Métropole : https://www.banatic.interieur.gouv.fr/intercommunalite/245901160-ca-valenciennes-metropole
- Métropole de Lyon : https://www.insee.fr/fr/information/7929497
