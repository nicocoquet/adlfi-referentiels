# Référentiel Lieux — contrôle national des ARK et libellés Pactols (14 novembre 2026)

**État : audit national reproductible, non validant pour le lien Pactols–COG et pour les géométries.**

## Sources et exécution vérifiées

- **Extraction XML AdlFI nationale v2** : 9 928 ARK terminaux distincts et leurs libellés documentaires.
- **Instantané minimal du corpus** : `docs/lieux/recette/autorites-minimales-9928.json`, dérivé de
  `AdlFI-audit-lieux-v2/autorites_lieux.csv` (SHA-256 de ce CSV :
  `878aa70f32d43313ea5bd36bbb30bbd6b57b4872ba2f68a5117ac6c35b6380b6`).
- **Source SKOS officielle CNRS-Frantiq** : `Pactols_Lieux_th17_20260722.rdf`,
  93 418 191 octets, issue du dépôt `frantiq/PACTOLS`, sous licence ODbL.
  SHA-256 vérifié par GitHub Actions :
  `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- **Code reproductible** : `scripts/auditer_export_pactols_lieux.py`,
  tests `tests/test_auditer_export_pactols_lieux.py`, workflow indépendant
  `.github/workflows/audit-pactols-lieux.yml`.

[GitHub Actions — exécution réussie et artefact ZIP du contrôle national](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43587570258).
L'artefact `audit-pactols-lieux-national-20260722` contient
`rapport_concepts_pactols.json` et **9 928 lignes** dans
`controle_concepts_pactols.csv`. L'artefact est une pièce de recette,
**non un jeu de données publiées sur GitHub Pages**.

## Résultats sur 9 928 concepts

| Catégorie de contrôle | ARK |
|---|---:|
| Présents dans l'export RDF du 22/07/2026 | **9 928** |
| `skos:prefLabel` français concordant avec le libellé XML, après normalisation | **9 886** |
| Libellé XML attesté comme `skos:altLabel` français | **9** |
| Libellé XML non retrouvé parmi prefLabel/altLabel/hiddenLabel français | **32** |
| Concept marqué `owl:deprecated` | **1** |
| ARK absent de l'export daté | **0** |
| **Total des ARK** | **9 928** |

Ce rapport classe le concept déprécié en priorité ; il dispose néanmoins
d'un libellé préféré concordant. Les catégories sont **disjointes selon
l'ordre de qualification de l'auditeur** ; elles ne mesurent pas les
identifiants COG ni une éventuelle équivalence SKOS.

**Lot 001 : 100/100 ARK ont un `skos:prefLabel` français concordant.**
Cela corrobore l'identité lexicale du concept Pactols à la date de
l'export, sans valider le code communal COG pressenti.

## Les 42 cas particuliers : interprétation

### 26 anciennes abréviations documentaires

Dans **26 des 32 libellés non retrouvés**, le libellé XML comporte une
abréviation typologique de la géographie physique : `R` (cours d'eau),
`L` (lac), `Mer`, `Causse`, etc. Exemples :

- `Rhône R` → libellé SKOS **Rhône (fleuve)** ;
- `Loire R` → **Loire (fleuve)** ;
- `Annecy L` → **lac d'Annecy** ;
- `Bourget L` → **lac du Bourget** ;
- `Paladru L` → **lac Paladru** ;
- `Manche Mer` → **Manche**.

L'ARK identique prouve que cette divergence ne correspond pas à deux
concepts. La correction est une **mise à jour du libellé documentaire**
et de son affichage, non un changement d'identifiant ou une
correspondance au COG. Conserver les formes XML comme traces
d'attestation et utiliser les `prefLabel` Pactols à l'affichage.

### Six cas non hydrographiques : priorité historique ou typologique

| ARK (suffixe) | Libellé XML → préf. Pactols | Contrôle externe | Traitement |
|---|---|---|---|
| `pcrtBXhVhHIr4F` | Jugon-les-Lacs → Jugon-les-Lacs (commune déléguée) | Insee : commune nouvelle en **2016**, modification de dénomination en **2024**, code **22084** | Distinguer `COM`, `COMD` et épisodes historiques ; ne pas attribuer le contour 2026 à l'ancienne commune |
| `pcrtRNBicOhFjL` | Osmery → Osmery (ancienne commune) | Insee : commune nouvelle au **01/01/2024**, code **18173**, intégrant Lugny-Bourbonnais | Préserver l'ancienne identité et la relation avec la commune nouvelle |
| `pcrtV597Kj16Ap` | Ports (Indre-et-Loire) → Ports-sur-Vienne | Insee : changement de nom au **29/02/2020**, code **37187** | Enregistrer la variante et ses périodes, **sans inférer un changement de contour** |
| `pcrtYQmFfwxLq8` | Saint-Pierre (Saint-Pierre-Et-Miquelon) → île Saint-Pierre (Saint-Pierre-et-Miquelon) | L'Insee distingue la commune **Saint-Pierre 97502** ; le concept Pactols est explicitement une **île** | Classer comme géographie insulaire, hors alignement communal automatique |
| `pcrtlhwJPMkYwg` | Bazeilles → Bazeilles (commune déléguée) | Insee : créations de commune nouvelle en **2017** et **2024**, code **08053** | Épisodes administratifs distincts malgré le même code |
| `pcrtzYbHiu1Bx5` | Commeny → Commeny (ancienne commune) | Insee : commune nouvelle au **01/01/2024**, code **95169**, avec Gouzangrez | Préserver l'identité de l'ancienne commune, ne pas rétrodater le contour 2026 |

Sources :
- Insee Jugon-les-Lacs : https://www.insee.fr/fr/statistiques/2011101?geo=COM-22084
- Insee Osmery : https://www.insee.fr/fr/statistiques/8643952?geo=COM-18173
- Insee Ports-sur-Vienne : https://www.insee.fr/fr/statistiques/2011101?geo=COM-37187
- Insee Saint-Pierre-et-Miquelon : https://www.insee.fr/fr/information/7929495
- Insee Bazeilles : https://www.insee.fr/fr/statistiques/2011101?geo=COM-08053
- Insee Commeny : https://www.insee.fr/fr/statistiques/2011101?geo=COM-95169
- Arrêté créant la commune nouvelle de Commeny : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000048728215

**Alerte sur un `altLabel` Pactols :** l'unique `skos:altLabel`
français purement numérique retrouvé parmi les 9 928 concepts est
`08140`, associé à l'ARK **Bazeilles (commune déléguée)**. Or le COG
2026 attribue **08140 à Dom-le-Mesnil**, et **08053 à Bazeilles**.
Il est interdit de convertir mécaniquement un `altLabel` numérique en
code INSEE sans vérifier sa sémantique. Cette entrée doit être
**signalée à Frantiq pour examen**, sans correction automatique du
thésaurus : https://www.insee.fr/fr/metadonnees/geographie/commune/08140-dom-le-mesnil

### Neuf libellés XML attestés en variante

Les neuf cas à `skos:altLabel` français concordant sont :

- **Exideuil** → Exideuil-sur-Vienne ;
- **Montreuil (Pas-de-Calais)** → Montreuil-sur-Mer ;
- **Cadillac** → Cadillac-sur-Garonne ;
- **Pommiers (Loire)** → Pommiers-en-Forez ;
- **Loire Bassin** → bassin de la Loire ;
- **Caraïbes Mer** → mer des Caraïbes ;
- **Vercors** → massif du Vercors ;
- **Quissac (Lot)** → Quissac-en-Quercy ;
- **Lazaret** → grotte du Lazaret.

Ce sont des **variantes documentées par Pactols**. La mise à jour
de la forme d'affichage peut donc être proposée, sans remplacer l'ARK
ni inférer que toutes les variantes ont la même période de validité.

### Un concept déprécié

- ARK `26678/pcrtYl5BQ48ldd`, libellé **Oisans Massif**.
- L'export indique `owl:deprecated = true`.
- Aucun `skos:exactMatch` n'est présent sur ce concept dans le
  résultat extrait. **Aucun successeur n'est déduit**.

À instruire dans le Pactols vivant auprès de Frantiq avant
toute modification des index XML. Le concept garde son identité
documentaire d'attestation dans les anciennes notices.

## Décisions d'intégration (proposées, non validées)

1. Dans la future fiche Lieux, afficher le `skos:prefLabel` français
   officiel de Pactols **avec la provenance et la date d'export** ;
   conserver les libellés XML et `altLabel` comme variantes.
2. Ne jamais prendre une variante lexicale pour une identité administrative.
3. Résoudre les **épisodes COG** à partir des mouvements Insee ; les
   créations de communes nouvelles et les fusions peuvent réutiliser
   un code tout en changeant d'emprise.
4. Le lien vers un contour data.gouv/IGN doit inclure son millésime,
   niveau de généralisation et preuve de raccordement, et ne pas
   prétendre représenter un contour historique sans source historique.
5. **Conserver les 103 correspondances PACA validées** et les
   données de production indépendamment de cet audit national.

Ce bilan ne signifie pas « 9 928 communes validées » : une partie
des concepts sont des cours d'eau, lacs, régions, sites, lieux
historiques ou lieux hors champ du COG communal.
