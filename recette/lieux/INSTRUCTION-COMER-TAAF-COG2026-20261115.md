# Lieux AdlFI — instruction des tables COMER du COG 2026 et des TAAF

**15 novembre 2026 · PR #30 · audit de données officielles, non validant, sans publication.**

## 1. Corpus réellement instruit

Les quatre fichiers CSV de l'[Insee — COG au 1er janvier 2026](https://www.insee.fr/fr/information/8740222) ont été extraits de l'archive officielle et contrôlés intégralement en GitHub Actions, [exécution n°43732674763](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43732674763).

| Rôle | Fichier | SHA-256 |
|---|---|---|
| Collectivités et territoires actuels | `v_comer_2026.csv` | `d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed` |
| Historique des collectivités/territoires | `v_tom_depuis_1943.csv` | `6814a3ddedfa186557f5f7a10ff0f4c521f72fd388bdd430318d3d0d59b426bd` |
| Zonages contemporains | `v_commune_comer_2026.csv` | `9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8` |
| Historique des zonages | `v_commune_outremer_depuis_1943.csv` | `d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748` |

Contrôles : 9 collectivités ou territoires actuels, 95 lignes de zonages contemporains, 61 périodes COMER et 830 périodes de zonages historiques. La [nomenclature officielle](https://www.insee.fr/fr/information/8740218) distingue `COM` (85 lignes), `DIS` (5), `CIR` (3), `CPT` (1), `CDM` (1). **Ces 85 lignes `COM` sont une nature de zonage du fichier COMER, et ne prouvent pas, à elles seules, que les 85 territoires sont des communes juridiquement de droit commun** (notamment Saint-Barthélemy et Saint-Martin).

## 2. Répartition 2026

| Code COMER | Territoire | Type de zonage | Nombre |
|---|---|---|---:|
| 975 | Saint-Pierre-et-Miquelon | COM | 2 |
| 977 | Saint-Barthélemy | COM | 1 |
| 978 | Saint-Martin | COM | 1 |
| 981 | Île des Faisans | CDM | 1 |
| 984 | Terres australes et antarctiques françaises | DIS | 5 |
| 986 | Wallis-et-Futuna | CIR | 3 |
| 987 | Polynésie française | COM | 48 |
| 988 | Nouvelle-Calédonie | COM | 33 |
| 989 | La Passion-Clipperton | CPT | 1 |
| **Total** | | | **95** |

**Attention :** ces 9 entrées sont les collectivités et territoires du fichier COMER, **pas** les 5 DROM. Les 129 communes des DROM recensées dans le premier audit sont documentées par d'autres fichiers COG et ne sont pas à ajouter comme subdivisions COMER.

## 3. Cinq districts des TAAF (COG 2026)

| Code | Nature | Libellé exact INSEE |
|---|---|---|
| 98411 | DIS | Îles Saint-Paul et Amsterdam |
| 98412 | DIS | Archipel des Kerguelen |
| 98413 | DIS | Archipel des Crozet |
| 98414 | DIS | Terre-Adélie |
| 98415 | DIS | Îles Éparses de l'océan Indien |

Les cinq périodes de district présentes dans `v_commune_outremer_depuis_1943.csv` commencent au **23 février 2007** ; aucune limite géométrique ancienne n'a été attribuée.

Le fichier des collectivités historiques établit :
- `98404`, « Terres australes et antarctiques françaises », **10 août 1955 – 23 février 2007** ;
- `98403`, « Îles Éparses de l’océan Indien », **26 juin 1960 – 23 février 2007** ;
- `984`, « Terres australes et antarctiques françaises », **depuis le 23 février 2007**.

**Le préfixe `984` n'est donc pas une preuve de continuité d'identité administrative.** Le regroupement de 2007 devra être représenté comme un événement/épisode sourcé ; aucune équivalence ARK n'en est déduite.

## 4. Autres transitions historiques à instruire

### Saint-Barthélemy et Saint-Martin

- Dans le COG communal de la Guadeloupe : fin des états `COM 97123` et `COM 97127` par événements `MOD=30` du **23 février 2007** (premier audit DROM).
- Dans les tables COMER : apparition des collectivités `977` et `978` au **23 février 2007**, avec zonages actuels `COM 97701` et `COM 97801`.
- **La juxtaposition de ces faits administratifs n'est ni une assertion `skos:exactMatch` ni une relation documentaire entre ARK.**

### Mayotte

Le fichier `v_tom_depuis_1943.csv` contient les épisodes nommés Mayotte :
- `98402` : **6 juillet 1975 – 20 mai 1977** ;
- `985` : **20 mai 1977 – 23 février 2007** ;
- `976` : **23 février 2007 – 31 mars 2011**.

À compter du **31 mars 2011**, la liste des communes de Mayotte relève du fichier des DROM. Au **1er janvier 2026**, le code de la collectivité territoriale à compétences départementales devient `976R`, **d'un niveau administratif différent**. Aucun rapprochement conceptuel automatique n'est autorisé.

### Clipperton et l'Île des Faisans

- `98901`, nature `CPT` : « Clipperton » du **23 février 2007 au 21 février 2022**, puis « La Passion-Clipperton » ; ne pas le qualifier de commune.
- `98101`, nature `CDM` : « Île des Faisans » ; le code renvoie au condominium, pas à une commune française.

### Archives historiques étrangères au périmètre actuel

Parmi les **830** lignes historiques figurent d'anciennes subdivisions administratives du Maroc, de la Tunisie et d'Algérie. Leurs codes ne doivent pas être projetés sur la carte des territoires français d'outre-mer de 2026. Les tables historiques sont conservées, mais **aucune liaison automatique par préfixe n'est permise**.

## 5. Conséquences pour le futur module Lieux mondial

1. Séparer les niveaux `collectivite`, `commune_ou_zonage`, `evenement_administratif`, `concept_pactols`, `geometrie_millesimee`.
2. Conserver `NATURE_ZONAGE` dans l'identifiant typé de chaque subdivision ; ne pas assimiler les 5 districts TAAF à 5 communes.
3. Conserver les périodes `[DATE_DEBUT,DATE_FIN[` avec les codes tels qu'attestés, sans créer de relations historiques par simple réutilisation de code ou de nom.
4. Indexer les DROM et les COMER dans des familles de sources séparées, avec provenance.
5. Avant toute interface cartographique mondiale, qualifier les emprises non contiguës et la gestion de l'antiméridien (Polynésie, Pacifique), des îles dispersées (TAAF) et de l'Antarctique ; ne jamais attribuer un contour 2026 à une date ancienne.
6. Introduire ensuite les concepts Pactols comme autorités documentaires indépendantes, selon le même protocole d'instruction éditoriale qu'en Corse, PDL et BFC.

## 6. Reproductibilité

Code : `scripts/auditer_cog_comer_2026.py`, tests synthétiques dans `tests/test_auditer_cog_comer_2026.py`, workflow `.github/workflows/audit-lieux-comer-cog2026.yml`.

L'exécution CI a conservé un artefact `adlfi-lieux-comer-cog2026-instruction` comprenant les quatre tables de contrôle, la répartition actuelle, les cinq districts TAAF, les alertes lexicales et le rapport avec empreintes. Deux générations intégrales ont été comparées octet par octet.

**Statut : 0 nouvel alignement Pactols–COG validé, 0 géométrie ancienne attribuée, 0 changement dans `docs/`. PR #30 maintenue en brouillon.**


## 7. Premier criblage des libellés du corpus XML AdlFI

En contrôle complémentaire, les **19 libellés de référence** des neuf entrées COMER, des cinq districts TAAF et des cinq DROM ont été confrontés par égalité normalisée (accents et séparateurs ignorés) aux **9 928 ARK terminaux attestés dans les XML AdlFI** du 13 novembre 2026, conservés dans la PR #24 : `recette/lieux/autorites-minimales-9928.json` (source initiale `autorites_lieux.csv`, empreinte `878aa70f32d43313ea5bd36bbb30bbd6b57b4872ba2f68a5117ac6c35b6380b6`).

Deux correspondances de **libellé documentaire exact** seulement :

| Libellé COG 2026 | ARK du corpus XML |
|---|---|
| Saint-Pierre-et-Miquelon | `26678/pcrtJTMXr1ruLl` |
| Terres australes et antarctiques françaises | `26678/pcrtqYLoVxtxFl` |

Les dix-sept autres libellés n'ont pas d'égalité de forme dans **cet index limité aux XML AdlFI**. Cela ne démontre ni l'absence du lieu dans Pactols, ni l'absence de variantes, ni même l'absence d'un ARK documentaire non cité dans les XML : le thesaurus intégral `th17` comptait **50 691 concepts** au 22 juillet 2026 dans la recette nationale de la PR #24.

**Les deux égalités de libellé ne sont pas des alignements Pactols–COG validés** ; aucun code Insee ou zonage COMER n'est transféré aux ARK. La prochaine étape sera une interrogation des concepts dans le RDF intégral et, si nécessaire, le thésaurus vivant, avec désambiguïsation territoriale et temporelle.
