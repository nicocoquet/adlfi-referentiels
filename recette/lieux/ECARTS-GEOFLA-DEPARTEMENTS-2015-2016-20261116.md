# Lieux AdlFI — écarts géométriques départementaux IGN GEOFLA 2015–2016

**16 novembre 2026 · PR #31 · qualification de recette, sans publication.**

## Méthode

Calculs en **Lambert-93 (EPSG:2154)** sur les **96 départements** des deux archives originales IGN GEOFLA (2015-03-04 et 2016-06-28) déjà vérifiées par SHA-256. Pour chaque code départemental stable : aire de 2015 et de 2016, intersection/union, différence symétrique, aires perdues et gagnées, distance de Hausdorff.

Cette mesure **ne permet pas**, seule, de qualifier une différence comme véritable mutation administrative : il faut une source juridique et un rattachement territorial documenté. Le scénario des 35 régions n'impliquait jusque-là que la stabilité de leur **composition en codes départementaux**, non la stabilité des limites des départements.

## Écarts majeurs localisés

| Département | Différence symétrique entre éditions | Décomposition observée |
|---|---:|---|
| **33 Gironde** | **225,188 km²** | Gain 2016 : 224,970 km² ; perte : 0,218 km² ; principal ensemble dans le secteur de l'estuaire de la Gironde |
| **17 Charente-Maritime** | **153,762 km²** | Gain 2016 : 149,302 km² ; perte : 4,459 km² ; principal ensemble dans le secteur de l'estuaire de la Gironde |
| **56 Morbihan** | **25,669 km²** | Gain 2016 : 0,980 km² ; perte : 24,689 km² ; deux principales composantes perdues, de 14,26 et 9,35 km², dans le secteur du golfe du Morbihan |
| **44 Loire-Atlantique** | **6,251 km²** | Perte 2016 : 6,190 km² ; gain : 0,061 km² |
| **49 Maine-et-Loire** | **6,237 km²** | Gain 2016 : 6,180 km² ; perte : 0,057 km² |

Les localisations proviennent d'une analyse des composantes de la différence géométrique entre shapefiles, et ne sont **pas** une explication par l'IGN de la modification. Il serait inexact d'interpréter les fortes variations estuariennes ou littorales comme plusieurs centaines de kilomètres carrés de nouveaux territoires terrestres. Une instruction du traitement des surfaces maritimes et de l'évolution de représentation cartographique entre éditions reste nécessaire.

Sources produit : [IGN GEOFLA 2015](https://data.geopf.fr/telechargement/resource/GEOFLA/GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04) et [IGN GEOFLA 2016](https://data.geopf.fr/telechargement/resource/GEOFLA/GEOFLA_2-2_DEPARTEMENT_SHP_LAMB93_FXX_2016-06-28). Le descriptif IGN rappelle que GEOFLA dérive d'une géométrie BD CARTO généralisée : [présentation du jeu GEOFLA](https://www.data.gouv.fr/fr/datasets/geofla-r/).

## Mutation administrative avérée : Le Fresne-sur-Loire, 44 → 49

La superposition des seules surfaces **perdues par le 44** et **gagnées par le 49** représente **6,1424 km²** dans les éditions IGN. La surface se situe à proximité de **47,4037° N, 0,9388° O**.

Cette différence est corroborée par un texte légal primaire : le **décret n° 2015-1751 du 23 décembre 2015**, articles 1, 2 et 4, rattache **Le Fresne-sur-Loire** (ancien département de Loire-Atlantique) au **Maine-et-Loire** et modifie les limites départementales en conséquence, avec **entrée en vigueur le 31 décembre 2015**.

- [Texte complet du décret sur Légifrance](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000031690124/).
- [Arrêté de création d'Ingrandes-Le Fresne sur Loire](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000032097633), commune nouvelle au **1er janvier 2016**.

**Ne pas confondre les deux événements :** le transfert départemental prend effet le **31 décembre 2015**, tandis que la création de la commune nouvelle prend effet le **1er janvier 2016**. Les deux départements restent dans les **Pays de la Loire (code régional 52)** : l'événement est donc **invisible dans le seul audit des 13 contours régionaux**, alors qu'il est réel à l'échelon départemental.

La surface de 6,1424 km² est **une mesure calculée à partir des géométries IGN**, et non une superficie certifiée par le décret.

## Reproductibilité et suite

Ajout au workflow de GEOFLA 2016 de :

- `scripts/auditer_ecarts_departementaux_geofla_2015_2016.py` et ses tests ;
- `comparaison-96-departements-GEOFLA-2015-2016.csv` (96 départements, métriques complètes) ;
- `rapport-ecarts-departements-GEOFLA-2015-2016.json` (principaux écarts, acte juridique, sources, réserves).

**Contrôle à confirmer sur la CI du nouveau commit**. Les sorties sont fabriquées deux fois et comparées à l'octet, uniquement sous `$RUNNER_TEMP`, jamais dans `docs/`.

### Conséquence pour le modèle territorial

Le niveau **Département** du futur sélecteur doit enregistrer **les états géométriques millésimés et les modifications légales de périmètre**, même quand le code du département et son appartenance régionale ne changent pas. Cela concerne par exemple le transfert 44→49. Les écarts purement cartographiques non qualifiés juridiquement ne doivent pas générer de successions administratives fictives. Les régions AdlFI historiques restent un référentiel éditorial distinct.
