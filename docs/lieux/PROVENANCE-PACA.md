# Pilote Lieux AdlFI — PACA / Pactols–COG 2026

## Objet

Premier jeu de consultation du module **Lieux** pour le site Référentiels AdlFI.
L'unité principale est **l'autorité géographique Pactols**, identifiée par son ARK.
Un lien éditorial validé vers une commune COG 2026 permet de retrouver sa géométrie.
Le pilote ne publie **aucune équivalence SKOS inférée** : une correspondance validée
dans notre table éditoriale n'est pas automatiquement un `skos:exactMatch` de Pactols.

Ce lot contient uniquement les correspondances éditoriales PACA validées le
**18 octobre 2026**. Aucune commune n'est résolue par homonymie ou concordance
automatique de libellés.

## Livrables du pilote publié

- `docs/data/lieux.json` : **103 autorités Pactols** et **103 correspondances
  COG validées**, avec statut éditorial, date, source et millésime 2026.
- `docs/data/lieux-communes.geojson` : **103 géométries** sélectionnées
  exclusivement au moyen des codes INSEE validés. Il s'agit de contours du
  fichier cartographique de l'atlas, **pas de contours historiques**.
- `scripts/export_lieux_paca.py` : producteur déterministe en lecture seule.
  Il vérifie le contenu des sources par leur SHA-1 Git et refuse toute divergence.
- `tests/test_export_lieux_paca.py` : invariants métier, contrôles de provenance
  et tests négatifs.

Le pilote a été validé en local et fusionné dans `main` le 12 novembre 2026
(PR n°19, commit `25f83e80d6cf6b7d0d86e79b27cb006499dff014`).
L'état du déploiement GitHub Pages doit être contrôlé séparément.

## Interface de consultation

- `docs/lieux/index.html` : grande carte Leaflet, recherche avec autocomplétion,
  fiche latérale de l'autorité Pactols et correspondance COG.
- `docs/assets/lieux-search.js` : recherche client, indépendante du réseau,
  sur les libellés Pactols, les noms COG, les codes INSEE et les ARK.
  Comparaison insensible à la casse, aux accents et à la ponctuation.
- `docs/assets/lieux.js` : lecture des deux jeux statiques, validation de leur
  alignement par code et ARK, sélection et mise en évidence des contours.
  Une URL de type `/lieux/#ark=26678%2Fpcrt...` désigne une fiche consultable.
- `docs/assets/lieux.css` : adaptation graphique au site, présentation
  sur ordinateur et mobile.
- `tests/test_lieux_search.js` et `tests/test_lieux_ui.py` : recherche,
  exclusions, liaison des 103 géométries et contrat d'interface.
- `docs/data/manifest.json` : module déclaré en « prototype » publié ;
  la carte d'accueil Lieux est activée.

### Fond de carte et dépendances

Leaflet est chargé en version **1.9.4**, via un CDN HTTPS et une empreinte
SRI vérifiable. Les tuiles de fond sont demandées à
`https://tile.openstreetmap.org/{z}/{x}/{y}.png` uniquement pour la
fenêtre cartographique affichée, avec attribution OpenStreetMap visible
et sans préchargement ni collecte de données utilisateur.

Les fiches et la recherche fonctionnent sans requête à Pactols ou à l'Insee.
Si Leaflet est indisponible, les fiches restent consultables par recherche.
Les contours (source ODbL) ont une attribution visible et explicite.

La recherche ne couvre pour l'instant **ni les variantes SKOS altLabel
non exportées ni les autorités historiques non validées**.
Les contours du pilote ne représentent pas les limites anciennes.

## Corpus et exclusions

| Statut dans la table éditoriale | Nombre | Traitement |
| --- | ---: | --- |
| `VALIDE_EDITEUR_2026_10_18` | 103 | Exporté |
| `REVU_EDITEUR_A_DOCUMENTER` | 110 | Non exporté |
| `HORS_COG_CONFIRME` | 3 | Non exporté dans le pilote communal |
| `A_COMPLETER_SOURCE` | 2 | Non exporté |
| **Total** | **218** | **103 fiches publiables** |

Le fichier géométrique source comporte **106 entités**.
Les 103 correspondances validées ont chacune une géométrie et un code distinct.
Les trois géométries supplémentaires sont celles de **Nice (06088),
Marseille (13055) et Hyères (83069)** ; elles ne sont pas exportées ici.
Leur exclusion ne signifie pas que ces villes n'existent pas dans le COG :
**c'est leur alignement éditorial Pactols–COG qui reste à instruire**.

## Sources figées

Les données sources ont été lues dans le dépôt privé
`nicocoquet/atlas-documentaire`, branche
`feat/referentiel-pactols-cog-2026`, commit
`bc0455c7d1dbf65f579e9b25a01eb7928a8054d5`.

| Source | Chemin source | SHA du blob Git |
| --- | --- | --- |
| Table éditoriale | `experimentation/donnees/autorite_pactols_insee.csv` | `8d039fe574413df89524b39540ba962ce89ca0a0` |
| Géométries | `cartographie/geometries/communes-1000m.geojson` | `0525607f277ec4c915a3e3273e716a5b1f1108d5` |

### Origine cartographique et licence

Le script de l'atlas `cartographie/telecharger_geometries.py` déclare la
source **Contours administratifs 2026** de data.gouv.fr :

- Fiche producteur : https://www.data.gouv.fr/datasets/contours-administratifs
- Jeu diffusé sous licence **Open Database License (ODbL)**.
- Origine indiquée par le producteur : IGN Admin Express, avec OpenStreetMap
  et des sources territoriales complémentaires selon les zones.
- Attribution retenue dans le GeoJSON : « Contours administratifs —
  data.gouv.fr / IGN et contributeurs OpenStreetMap ».

Ces données sont limitées ici à 103 communes PACA et à la géométrie fournie
par la copie source épinglée dans le dépôt atlas. Le **niveau de généralisation
exact de ce sous-ensemble** reste à attester indépendamment des noms des
fichiers ; les deux fichiers géographiques 100m et 1000m présents dans la
branche atlas portent le même contenu Git.

Les fichiers éditoriaux non filtrés **ne sont pas copiés** dans le dépôt public.
Leurs empreintes sont consignées afin de pouvoir reproduire l'export sans
dépendre de l'état ultérieur des branches. Le référentiel historique COG
national dispose de scripts distincts et n'est pas intégré par cette livraison.

## Regénérer sans publier

Depuis la racine de `adlfi-referentiels`, en ayant accès aux deux fichiers
sources au commit indiqué :

```bash
SORTIE="$(mktemp -d "${TMPDIR:-/tmp}adlfi-lieux-recette.XXXXXX")"

python3 scripts/export_lieux_paca.py \
  /chemin/vers/autorite_pactols_insee.csv \
  /chemin/vers/communes-1000m.geojson \
  --output-dir "$SORTIE"

python3 -m unittest discover -s tests -v
```

L'exporteur bloque si une source a été modifiée, même de manière
apparemment anodine. Il refuse notamment les nouveaux codes non validés,
les doublons d'ARK/code, une géométrie absente ou une autre région.

L'option `--output-dir` est obligatoire et l'écriture directe dans
`docs/data` est interdite par le script pendant cette recette.

## Contrat de données provisoire (`schema_version: 0.1.0`)

Une autorité contient :

- `ark_pactols` et `libelle_pactols` : identité documentaire ;
- `type_entite` : `commune` dans ce seul pilote ;
- `correspondances[]` : relation éditoriale validée vers un code INSEE,
  libellé COG, millésime, département et provenance de la validation.

Le tableau `correspondances[]` est volontairement extensible à plusieurs
relations futures ; la cardinalité **1:1** du pilote n'est pas une règle
ontologique générale.

Le GeoJSON inclut le code INSEE et l'ARK Pactols correspondant pour permettre
la sélection cartographique. Les variantes de noms Pactols (`altLabel`)
ne figurent pas dans la table éditoriale de cette version : elles devront
être enrichies à partir d'un export SKOS Pactols contrôlé, **sans être inventées**.

## Conditions préalables à la mise en ligne

1. Contrôler localement la recherche au clavier et les liens ARK, puis
   sélectionner plusieurs communes sur la carte et sur petit écran.
2. Vérifier l'affichage de l'attribution ODbL sur le fond de carte, ainsi
   que les mentions du site ; ne pas déduire une échelle de généralisation
   du nom du fichier GeoJSON.
3. Maintenir l'exclusion des correspondances encore non validées.
4. Fusionner la PR seulement après succès de la CI et recette visuelle.
5. Reporter à un lot ultérieur les autorités sans géométrie, les relations
   historiques et les correspondances non bijectives.

## Préparation des variantes lexicales (lot suivant)

La recherche peut désormais interpréter un champ facultatif `variantes_pactols[]`
dans une autorité, sans modifier les 103 fiches présentes. Chaque variante
attendue est de la forme :

```json
{
  "libelle": "Exemple fictif non publié",
  "langue": "fr",
  "type": "skos:altLabel",
  "uri_source": "https://ark.frantiq.fr/ark:/26678/IDENTIFIANT_CONCEPT"
}
```

Le `uri_source` doit désigner **le même ARK que la fiche**. Le navigateur
rejette une variante incomplète ou mal qualifiée. Cette vérification
structurelle **ne prouve pas** la présence de l'alias dans Pactols :
seul un export officiel SKOS horodaté, vérifié et tracé par l'exporteur
pourra alimenter le champ des données publiées.

Dans cette version, **aucune variante n'a encore été importée**. Les tests
emploient exclusivement des exemples synthétiques non publiés. Les
`skos:prefLabel` restent distincts des `skos:altLabel` ;
les noms COG sont conservés dans `correspondances[]`, non dans
`variantes_pactols[]`. Aucune équivalence SKOS avec le COG n'est inférée.
