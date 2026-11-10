# Dossier contrôlé — séparation des deux personnes morales Archéologie Alsace

**État au 10 novembre 2026 :** proposition de migration, **aucune modification du maître ni du JSON public**. Source du dossier : maître `AdlFI_referentiel_1-40_20261110_secteur_historique_DRASM_CNRAS.xlsx`.

## 1. Deux identités attestées

| | Établissement historique | Structure actuelle |
|---|---|---|
| Identifiant AdlFI | `ORG-0093` **à conserver** | `ORG-0675` **proposé** (prochain ID libre au maître 1.40) |
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
| Site actuel | À ne pas attribuer rétrospectivement à l'établissement disparu sans réserve | https://www.archeologie.alsace/ |
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

## 2. Correspondances d'affiliation (maître 1.40)

| Source | Libellé XML | Occurrences | COR existante | Rattachement actuel | Décision de traitement |
|---|---|---:|---|---|---|
| `AFF-0047` | Pair | 57 | `COR-0054` | `ORG-0093` validée | Conserver provisoirement sur l'ORG historique ; vérifier les emplois rétrospectifs éventuels |
| `AFF-0048` | Archéologie Alsace | 124 | `COR-0055` | `ORG-0093` validée | **Bloquer la distribution**, et contrôler les notices XML individuellement (année d'opération/publication, signature et contexte) |

**Point crucial :** le maître donne seulement un nombre agrégé d'occurrences par libellé. Il ne fournit ni identifiant de notice ni date pour chacune de ces occurrences. On ne peut pas déduire combien des 124 appartiennent à l'établissement de 2016–2020 ou au syndicat créé en décembre 2020. Ne pas créer de lien doublement validé, ne pas attribuer toutes ces occurrences au successeur, et ne pas interpréter les années de publication comme années d'affiliation.

En cas d'homonymie historique dans les XML, une correspondance simple `AFF-0048 → ORG` est insuffisante. Il faudra maintenir l'entrée source brute `AFF-0048`, préserver son nombre de 124, et documenter des résolutions **par notice ou par occurrence**, avec date et provenance. Cela peut requérir une table de désambiguïsation, à concevoir après examen du corpus.

## 3. Relations

- `REL-0054` : relation `ORG-0093 → ORG-0092` de type `rattachement_administratif`, statut `a_verifier` et date absente. Ne pas la transférer automatiquement à la nouvelle ORG : la Collectivité européenne d'Alsace est **membre** du syndicat mixte (BANATIC), ce qui n'est pas une tutelle administrative au sens de cette relation.
- `REL-0305` : identifiant **candidat**, proposé pour `succession_institutionnelle` `ORG-0093 → ORG-0675`, date d'effet `2020-12-11`. À créer seulement après création de `ORG-0675` et validation de la provenance.
- Ne pas rabattre une `succession_institutionnelle` sur un `rattachement_administratif`.

## 4. Préconditions de migration dans le maître

1. Conserver `ORG-0093` sur la personne morale **200006336** ; corriger son statut actif, sa forme, sa chronologie et sa dénomination historique.
2. Créer `ORG-0675` pour **200094746** ; réexaminer le site web et le média actuel pour ne pas l'attribuer au mauvais organisme.
3. Créer et dater la relation de succession `REL-0305`.
4. **Avant de rendre la migration publique**, récupérer les notices XML concernées, dater chaque mention `AFF-0048` puis modéliser les éventuelles ambigüités.
5. Ne corriger le champ `echelon_territorial` ni sur l’ancienne autorité ni sur le successeur par simple déduction de leur nom ou de leur zone d'activité.
6. Vérifier que les modifications d'identité se répercutent sur `Historique`, `Correspondances_affiliations`, `Relations`, puis sur le JSON de publication, ses tests et les liens entre fiches.
7. Réévaluer si un `identifiant_siren` optionnel dans `Organismes` devient nécessaire pour l'identification juridique des ORG françaises.

## 5. Exécution de l'audit

```bash
python3 -m scripts.audit_alsace_identity /chemin/vers/AdlFI_referentiel_1-40_20261110_secteur_historique_DRASM_CNRAS.xlsx --output-dir /tmp/audit-alsace
```

Sortie : `dossier-identites-alsace.json`, avec identifiants candidats, dates, correspondances, enjeux et décisions bloquantes. Ce script est **en lecture seule** et n'effectue jamais de migration de données.
