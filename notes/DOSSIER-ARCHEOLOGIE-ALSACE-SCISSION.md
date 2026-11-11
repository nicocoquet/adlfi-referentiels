# Dossier contrôlé — séparation des deux personnes morales Archéologie Alsace

**État au 11 novembre 2026 :** réconciliation XML complète des **181 occurrences sur 181** ; **maître privé 1.41 consolidé** et contrôlé (voir `CONSOLIDATION-MAITRE-1-41.md`). Le JSON public reste à l'état 1.40, aucune publication GitHub Pages à ce stade. Source du dossier : maître `AdlFI_referentiel_1-40_20261110_secteur_historique_DRASM_CNRAS.xlsx`.

## 1. Deux identités attestées

| | Établissement historique | Structure actuelle |
|---|---|---|
| Identifiant AdlFI | `ORG-0093` **à conserver** | `ORG-0675` **créé dans le maître privé 1.41** |
| Nom éditorial retenu | Archéologie Alsace (depuis 2016) | Archéologie Alsace (depuis 2020) |
| Autre dénomination | Pôle d’archéologie interdépartemental rhénan (Pair), 2006–2016 | — |
| SIREN | `200006336` | `200094746` |
| Début | 2006-09-01 | 2020-12-11 |
| Fin / activité | Activité terminée le 2020-12-11 (date de fin exclusive pour le raisonnement temporel) | Actif |
| Type ORG proposé | `etablissement_public` | `syndicat_mixte` |
| Forme détaillée à documenter | Établissement public de coopération interdépartementale | Syndicat mixte ouvert (SMO) |
| Secteur | `public` | `public` |
| Catégorie BSR | `COL` | `COL` |
| Échelon territorial | **À déterminer** ; l’actuel `regional` décrit le territoire d'activité et non un niveau juridique | **À déterminer** : structure regroupant des collectivités de niveaux différents |
| Site actuel | URL actuelle transférée à `ORG-0675` dans le maître 1.41 | https://www.archeologie.alsace/ |
| Visuel | Rechercher la version historique appropriée | Éventuelle réaffectation contrôlée du logo `ORG-0093-logo.webp` vers le nouvel ID |

### Chronologie documentaire

- **2006-09-01** : création du Pôle d’archéologie interdépartemental rhénan, personne morale SIREN 200006336.
- **2016-10-15** : changement de dénomination en Archéologie Alsace sans changement de personne morale ; l’historique actuel `HIS-0003` porte à tort une date de fin `2015`. La date de fin **inclusive** à proposer est `2016-10-14`, et la date de début `2006-09-01`.
- **2020-12-11** : création du syndicat mixte ouvert SIREN 200094746 ; rupture de personne morale et succession institutionnelle à représenter, et non changement d'état de la même ORG.

Références :
- https://www.archeologie.alsace/fr/actualites-archivees (annonce de 2016 et de 2020)
- https://www.banatic.interieur.gouv.fr/intercommunalite/200094746-smo-archeologie-alsace-aa
- https://www.alsace.eu/delib-cd68/Rapports_Annexes/67adec56-870e-4203-8ee5-e23753dbe5c0.pdf (statuts de la personne morale historique)
- https://www.pappers.fr/entreprise/pair-archeologie-alsace-200006336

## 2. Correspondances d'affiliation : réconciliation XML exhaustive (11 novembre 2026)

Quatre fichiers XML distincts ont été analysés ; deux doublons présents dans une archive complémentaire ont été écartés. **Toutes les mentions du maître 1.40 ont été retrouvées dans les balises TEI `<affiliation>`**.

| Source | Libellé | Années d'opération des notices | Occurrences XML | COR existante | Attribution chronologique |
|---|---|---|---:|---|---|
| `AdlFI_Alsace_2015.xml` | Pair | 2014–2015 | 57 | `COR-0054` / `AFF-0047` | `ORG-0093` historique |
| `AdlFI_Grand-Est_2016.xml` | Archéologie Alsace | 2016 | 48 | `COR-0055` / `AFF-0048` | `ORG-0093` historique |
| `AdlFI_Grand-Est_2017_part1.xml` | — | — | 0 | — | Sans objet |
| `AdlFI_Grand-Est_2017_part2.xml` | Archéologie Alsace | 2017 | 76 | `COR-0055` / `AFF-0048` | `ORG-0093` historique |
| **Total** | | | **181** | 57 + 124 | **181 à conserver sur l'ancienne ORG** |

Le total de **124** mentions « Archéologie Alsace » est intégralement constitué des **48** mentions d'opérations de 2016 et des **76** mentions d'opérations de 2017. Ces opérations sont antérieures au 11 décembre 2020. Le maintien des correspondances `AFF-0047 → ORG-0093` et `AFF-0048 → ORG-0093` est donc documenté ; **aucune des 181 occurrences ne doit être transférée automatiquement au syndicat mixte successeur**.

**Précaution historiographique :** le titre du corpus renvoie à l'année **d'opération**, pas nécessairement à la date d'édition ou de publication des notices. Certaines notices ont été publiées ou révisées après 2020. Le libellé rétrospectif « Archéologie Alsace », y compris pour les opérations de 2016 antérieures au changement de nom du 15 octobre 2016, **n'atteste pas le nom juridique en usage à la date exacte de l'opération**. Il permet néanmoins de rattacher l'opération à la personne morale historique déjà créée en 2006, non au successeur de 2020.

Contrôle de provenance SHA-256 du fichier `AdlFI_Grand-Est_2016.xml` : `55af34c7a7a8fc7733e4ffa237584e1f7a482c665cfac2d4dcee5a6ba8e69333`. La copie dans le ZIP transmis est **octet pour octet identique**.

Les preuves par occurrence (nom du fichier, numéro de notice, intitulé, identifiant XML `aff...`, année d'opération) sont conservées dans un rapport CSV/JSON de travail remis à l'éditeur, sans verser les fichiers XML au dépôt public. Reproduction avec `scripts/audit_alsace_xml.py` : l'audit échoue si les effectifs ne correspondent plus à 57 + 124 ou si une opération associée dépasse l'année 2019.


## 3. Relations

- `REL-0054` : relation `ORG-0093 → ORG-0092` de type `rattachement_administratif`, statut `a_verifier` et date absente. Ne pas la transférer automatiquement à la nouvelle ORG : la Collectivité européenne d'Alsace est **membre** du syndicat mixte (BANATIC), ce qui n'est pas une tutelle administrative au sens de cette relation.
- `REL-0305` : identifiant **candidat**, proposé pour `succession_institutionnelle` `ORG-0093 → ORG-0675`, date d'effet `2020-12-11`. Créé et validé dans le maître privé 1.41 sur la base des SIREN et de BANATIC ; sa publication est conditionnée aux contrôles de l'export JSON.
- Ne pas rabattre une `succession_institutionnelle` sur un `rattachement_administratif`.

## 4. Préconditions de migration dans le maître

1. **Appliqué au maître 1.41** : `ORG-0093` conservée pour la personne morale **200006336**, activité, forme juridique, chronologie et dénomination historique corrigées.
2. **Appliqué** : `ORG-0675` créée pour **200094746** et URL actuelle transférée ; attribution du logo **encore à vérifier**.
3. **Appliqué** : relation de succession `REL-0305` créée et datée 2020-12-11.
4. **Résolu le 11 novembre 2026 :** les 181 affiliations sont retrouvées et datées par année d'opération dans les quatre XML. Maintenir `COR-0054` et `COR-0055` vers `ORG-0093` ; ne pas créer de correspondance avec `ORG-0675` pour les notices anciennes. Conserver le rapport d'audit comme preuve de désambiguïsation.
5. Ne corriger le champ `echelon_territorial` ni sur l’ancienne autorité ni sur le successeur par simple déduction de leur nom ou de leur zone d'activité.
6. Vérifier que les modifications d'identité se répercutent sur `Historique`, `Correspondances_affiliations`, `Relations`, puis sur le JSON de publication, ses tests et les liens entre fiches.
7. Réévaluer si un `identifiant_siren` optionnel dans `Organismes` devient nécessaire pour l'identification juridique des ORG françaises.

## 5. Exécution de l'audit

```bash
python3 -m scripts.audit_alsace_xml AdlFI_Alsace_2015.xml AdlFI_Grand-Est_2016.xml AdlFI_Grand-Est_2017_part1.xml AdlFI_Grand-Est_2017_part2.xml --output-dir /tmp/audit-alsace
python3 -m scripts.audit_alsace_identity /chemin/vers/AdlFI_referentiel_1-40_20261110_secteur_historique_DRASM_CNRAS.xlsx --xml-corpus AdlFI_Alsace_2015.xml AdlFI_Grand-Est_2016.xml AdlFI_Grand-Est_2017_part1.xml AdlFI_Grand-Est_2017_part2.xml --output-dir /tmp/audit-alsace
```

Sorties : `audit-alsace-xml.json`, `affiliations-alsace-xml.csv`, `dossier-identites-alsace.json`, avec les 181 attestations, les identifiants candidats, les dates, les correspondances et les seules décisions institutionnelles encore à traiter. Ce script est **en lecture seule** et n'effectue jamais de migration de données.
