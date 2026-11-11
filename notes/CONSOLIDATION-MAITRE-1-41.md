# Consolidation du maître 1.41 — Archéologie Alsace et échelons (11 novembre 2026)

**Statut : classeur privé 1.41 produit et contrôlé ; JSON de prépublication préparé ; aucune migration publiée sur GitHub Pages.**

## Traçabilité des artefacts éditoriaux

- **Maître source 1.40** : `AdlFI_referentiel_1-40_20261110_secteur_historique_DRASM_CNRAS.xlsx`, SHA-256 `c0e401ad4c5fa1af46be0f58ec0a989d8bfcb04ada403a2a925e2dce13d2c7ca`.
- **Maître 1.41** : `AdlFI_referentiel_1-41_20261111_Archeologie_Alsace_echelons.xlsx`, SHA-256 `d9ec168c72871e5a5c712aa36f79547d9bf0431bcde8c7c6529cd1e5aa257f07`.
- **JSON de prépublication** : `AdlFI_organismes_1-41_JSON_prepublication_20261111.json`, SHA-256 `c3a0994b0cee722ab2ca065166e66776b16b1cdd37a1b7337c2cf03a211b6173`.

Ces fichiers restent **hors du dépôt public**. Le JSON de prépublication est une transformation contrôlée du JSON 1.40 documentée par comparaison de structure ; **avant publication, régénérer le JSON avec le script officiel du dépôt** sur ce maître 1.41 et comparer les fichiers.

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

JSON attendu après export officiel : **820 autorités** (654 ORG + 166 SER), **615 visibles**, 205 exclues, **522 relations** au total. Les 164 SER publics et 2 privés ne changent pas.

## Reproductibilité

Depuis la racine du dépôt et sur la machine ayant accès au maître privé :

```bash
python3 -m scripts.controle_maitre_1_41 "/chemin/vers/AdlFI_referentiel_1-41_20261111_Archeologie_Alsace_echelons.xlsx" \
  --report /tmp/controle-maitre-1-41.json \
  --preview-json /tmp/organismes-1-41.json
python3 -m unittest discover -s tests -v
```

Le contrôle de migration échoue en présence de doublons, affiliation réaffectée à la mauvaise personne morale, succession mal datée, lien non validé ou contradiction des statuts juridiques. Les sorties sont écrites dans `/tmp` et ne modifient pas `docs/data/organismes.json`.

**Avant fusion d'une PR de publication** : régénérer le JSON par l'exporteur natif (ce contrôle fait appel à `scripts.export_organismes.build`), vérifier les CI, vérifier le logo `ORG-0093-logo.webp` pour éviter son affichage anachronique sur la fiche historique, et arbitrer la relation `REL-0054` sans la confondre avec l'adhésion de la CeA au syndicat.

## Sources

- BANATIC (SMO actuel, SIREN, création, composition) : https://www.banatic.interieur.gouv.fr/intercommunalite/200094746-smo-archeologie-alsace-aa
- Personne morale historique : https://www.pappers.fr/entreprise/pair-archeologie-alsace-200006336
- Annonce institutionnelle décembre 2020 : https://www.archeologie.alsace/fr/actualites/actualite?cHash=9e5ed42a8371c6403457d8a378449e67&tx_news_pi1%5Baction%5D=detail&tx_news_pi1%5Bcontroller%5D=News&tx_news_pi1%5Bnews%5D=137
- Valenciennes Métropole : https://www.banatic.interieur.gouv.fr/intercommunalite/245901160-ca-valenciennes-metropole
- Métropole de Lyon : https://www.insee.fr/fr/information/7929497
