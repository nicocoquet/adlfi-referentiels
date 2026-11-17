# Polynésie française — Hao : acquisition locale contrôlée Sentinel-2 (PR 90)

**17 novembre 2026.** Suite à la PR 89. Cette tranche fournit une procédure d'acquisition locale des bandes, **pas** une analyse réelle des pixels.

## Source et justification du mode d'accès

La PR 89 a confirmé **47 assets** du produit Sentinel-2A L2A exact
`S2A_MSIL2A_20221226T193851_N0510_R056_T07KEV_20240715T211924`,
acquis le **26 décembre 2022 à 19:38:51 UTC**. Les bandes nécessaires à un
diagnostic de cinq points sont `B02_10m`, `B03_10m`, `B04_10m`,
`B08_10m` et `SCL_20m`.

Les liens STAC des rasters pointent vers `s3://eodata/…`. Selon la
[documentation officielle Copernicus Data Space sur S3](https://documentation.dataspace.copernicus.eu/APIs/S3.html),
l'accès extérieur au stockage exige des **clés d'accès S3 CDSE**, créées dans
l'espace utilisateur Copernicus, et l'endpoint
`https://eodata.dataspace.copernicus.eu`. L'API OData propose une autre
voie de téléchargement, mais elle exige également un token d'accès :
[documentation OData](https://documentation.dataspace.copernicus.eu/APIs/OData.html).

Le compte Copernicus et les secrets restent dans l'environnement **local** de
l'opérateur ; **aucune clé, secret, URL signée ou jeton n'est transmis dans
GitHub, ChatGPT, les journaux CI ou les documents de recette**.

## Utilisation en local (macOS, terminal VS Code)

Installer `boto3` dans l'environnement Python local, et facultativement
`rasterio` pour l'étape suivante :

```bash
python3 -m pip install boto3 rasterio
```

Commencer par vérifier **sans clé et sans téléchargement** que le produit STAC
et ses cinq chemins S3 correspondent au produit attendu :

```bash
python3 scripts/recuperer_hao_cdse_s3.py \
  --destination "$HOME/Downloads/AdlFI-Hao-Sentinel2-20221226"
```

Si l'utilisateur possède un compte Copernicus Data Space, créer ses **clés S3
dans l'interface CDSE** ; les définir uniquement dans la session terminal
locale, en utilisant une invite silencieuse (aucune valeur littérale dans
l'historique de commandes) :

```bash
read -r -s 'CDSE_S3_ACCESS_KEY?Clé S3 CDSE : '
echo
export CDSE_S3_ACCESS_KEY
read -r -s 'CDSE_S3_SECRET_KEY?Secret S3 CDSE : '
echo
export CDSE_S3_SECRET_KEY
```

Sur certains shells Bash la syntaxe d'invite est différente ; les commandes
ci-dessus sont destinées à **zsh**, le shell observé sur le Mac. La commande
ne nécessite aucune communication des valeurs à un assistant.

Après vérification du préflight et des quotas du compte, télécharger dans un
dossier **hors du dépôt** et **vide** :

```bash
python3 scripts/recuperer_hao_cdse_s3.py \
  --destination "$HOME/Downloads/AdlFI-Hao-Sentinel2-20221226" \
  --download \
  --max-bytes-par-fichier 1000000000
```

Le téléchargement est volontairement limité à **1 Go par fichier** par
défaut. Chaque fichier est d'abord téléchargé avec une extension `.part`,
son nombre d'octets est vérifié contre la réponse S3, puis il est renommé et
haché en SHA-256. Aucun fichier existant n'est remplacé. Le manifeste local
`manifest-local.json` contient les tailles et empreintes, sans secret ;
il ne doit pas être commité avec les images.

Après récupération des cinq JP2, utiliser le lecteur préparé par la PR 89 :

```bash
D="$HOME/Downloads/AdlFI-Hao-Sentinel2-20221226"
python3 scripts/diagnostiquer_pixels_hao_l2a.py \
  --b02-10m "$D/B02_10m.jp2" \
  --b03-10m "$D/B03_10m.jp2" \
  --b04-10m "$D/B04_10m.jp2" \
  --b08-10m "$D/B08_10m.jp2" \
  --scl-20m "$D/SCL_20m.jp2" \
  --sortie "$D/hao-pixels-rapport.json"
```

Enfin, désactiver les identifiants de la session :

```bash
unset CDSE_S3_ACCESS_KEY CDSE_S3_SECRET_KEY
```

## Garanties et limites

Le script `scripts/recuperer_hao_cdse_s3.py` refuse une autre collection,
un autre identifiant STAC, une URI hors `s3://eodata/Sentinel-2/`,
un lien S3 qui n'appartient pas au produit exact, un chemin dangereux et
une tentative d'écrasement. Il interdit aussi les téléchargements dans un
sous-dossier de dépôt Git. Les tests CI simulent un client S3 : **aucun
identifiant n'est requis dans GitHub Actions**.

L'existence des métadonnées et le succès des tests synthétiques ne garantissent
pas l'accès S3 d'un compte utilisateur donné. Le diagnostic des pixels est
limité à cinq cellules échantillonnées et ne permet pas, isolément, de
qualifier les **polygones entiers** comme motu, récifs ou lagons. L'analyse
future de surfaces complètes devra utiliser les masques et les bandes dans
leur grille et millésime géographique attestés.

**Statut : RECETTE_NON_VALIDANTE ; aucun nouveau contour, toponyme, ARK
ou raster publié.**
