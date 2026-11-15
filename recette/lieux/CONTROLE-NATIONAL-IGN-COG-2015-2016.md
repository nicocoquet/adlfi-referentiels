# Lieux AdlFI — concordance nationale IGN GEOFLA / Insee COG (2015–2016)

**15 novembre 2026 · PR #31 · registre de contrôle non publié.**

## Contrôle effectué

L'audit croise **96 départements métropolitains** (deux shapefiles GEOFLA originaux en Lambert-93) avec les **fichiers départementaux officiels des COG 2015 et 2016**. Les quatre sources sont identifiées par leurs empreintes SHA-256, les correspondances établies sur `CODE_DEPT` et `CODE_REG` côté IGN, `DEP` et `REGION` côté Insee.

| Test | 2015 | 2016 |
|---|---:|---:|
| Départements métropolitains présents dans GEOFLA | 96 | 96 |
| Codes régionaux métropolitains distincts | 22 | 13 |
| Concordances département → région entre IGN et COG | **96 / 96** | **96 / 96** |
| Divergences de rattachement | **0** | **0** |

Les deux archives portent bien les mêmes 96 codes départementaux. **65** d'entre eux changent de code régional entre 2015 et 2016. Ces changements correspondent aux **sept fusions**, reliant **16 régions anciennes** à sept successeurs ; les autres régions restent sous leur code.

### Sources officielles

- IGN GEOFLA 2.0, 2015-03-04 : [paquet DÉPARTEMENT](https://data.geopf.fr/telechargement/resource/GEOFLA/GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04) ; archive téléchargée SHA-256 `7831ad942f3c0646d7b9ebf9ba480dcf746d6f69d46834b38e36fa6681c1060e` ; shapefile SHA-256 `5fa73a71b6775792652549f90d5fc3909fe396bed4692089e08b4fceed28b3b2`.
- IGN GEOFLA 2.2, 2016-06-28 : [paquet DÉPARTEMENT](https://data.geopf.fr/telechargement/resource/GEOFLA/GEOFLA_2-2_DEPARTEMENT_SHP_LAMB93_FXX_2016-06-28) ; archive téléchargée SHA-256 `8e1538791c12b7679ef0ffb638a0fc53f8e9dede359c170af6e15576826ea91a` ; shapefile SHA-256 `3c2f5b03ffbce381e2ddb1f2b1658ca705ccb6c82816d676f384e71b0cc91d6f`.
- COG Insee 2015 : `depts2015-txt.zip`, SHA-256 `67ad93d56606e2b48e3560ca35de70abaea1ed267feb5519204daa0a2cdbc1f6`.
- COG Insee 2016 : `depts2016-txt.zip`, SHA-256 `d8426f9d13e11638a04eb67d27d9b23396a92e510dbd42fabe68974e177c8ac8`.

Les empreintes sont des **calculs vérifiés sur les fichiers téléchargés**, non des signatures de l'IGN. Les archives SIG ont une date d'édition différente de la situation administrative du COG **au 1er janvier**.

## Livrables versionnés

- `scripts/controle_national_geofla_cog_2015_2016.py` : jointure des 96 codes par année, vérification de l'identité des codes entre éditions, contrôle des sept successions régionales et des 65 changements de rattachement.
- `tests/test_controle_national_geofla_cog_2015_2016.py` : tests des sept fusions et veto de publication des sorties de recette.
- `.github/workflows/audit-lieux-geofla-departements-2016.yml` : vérifie les sources par leur SHA-256, exécute l'analyse nationale deux fois et compare les exports **octet par octet**.
- `rattachements-IGN-COG-2015-2016.csv` : **96 lignes départementales**, comprenant code parent avant/après, type de succession et dates distinctes du COG et des archives SIG ; produit dans l'artefact de CI, **pas dans `docs/`**.
- `rapport-national-geofla-cog-2015-2016.json` : cardinalités, correspondances et provenance.

[Exécution CI de qualification n° 43759627331](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43759627331) : **succès** ; la recette nationale et le pilote BFC sont reproductibles à l'octet. Les contrôles généraux du dépôt sont également verts sur le même commit ; une exécution plus ancienne du workflow IGN 2015 a rencontré une erreur DNS transitoire sur le catalogue, indépendante de la qualité des données, et a été relancée.

## Limites et prochaine production

Le résultat national est pour le moment un **audit des rattachements**, et non encore la génération des **35 contours régionaux** (22 en 2015, 13 en 2016). La comparaison de géométries pour le pilote Bourgogne–Franche-Comté est déjà qualifiée et documentée séparément.

Prochaine étape proposée : reconstituer les **35 géométries régionales** par union des départements de leurs éditions respectives, puis tester les sept fusions à partir de deux représentations IGN homogènes. Prévoir la gestion séparée des territoires ultramarins, pour lesquels GEOFLA FXX/Lambert-93 ne couvre pas les géométries.

**Zéro alignement Pactols nouveau ; zéro géométrie 2026 rétroprojetée ; aucune modification de GitHub Pages.**
