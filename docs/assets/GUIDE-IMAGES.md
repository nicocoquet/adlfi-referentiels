# Préparer les images de l’explorateur des organismes AdlFI

Les visuels sont ajoutés **manuellement** au dépôt, après contrôle des droits, des sources et de l’identité de chaque autorité. Aucun logo n’est téléchargé, inventé ou inféré par le pipeline.

## Deux rôles distincts

| Usage | Emplacement dans le dépôt | Format conseillé | Dimensions sources | Présentation |
| --- | --- | --- | --- | --- |
| Illustration d’un laboratoire (photographie, façade, représentation documentaire) | `docs/assets/organismes/ORG-XXXX.webp` | WebP, ou JPEG pour une photo | **800 × 800 px** (carré 1:1) | Bloc carré d’environ 144 CSS px, `object-fit: cover` |
| Logo propre du laboratoire | `docs/assets/logos/ORG-XXXX.svg` | SVG vectoriel sûr, sinon PNG transparent | SVG avec `viewBox`, sinon **640 × 240 px** au maximum naturel, proportions conservées | Dans le bloc principal **uniquement si aucune illustration** n’est fournie ; `object-fit: contain` |
| Logo d’une tutelle | `docs/assets/logos/ORG-XXXX.svg` | SVG vectoriel sûr, sinon PNG transparent | SVG avec `viewBox`, sinon **640 × 240 px** environ pour un logo horizontal | Bandeau inférieur ; jusqu’à 160 × 58 CSS px, sans recadrage |

Les dimensions raster sont des **recommandations de préparation**, pas des formats imposés. Pour un écran à forte densité, la source devrait être au moins deux fois plus grande que son affichage CSS : une image de 320 × 320 px suffit techniquement au cartouche carré actuel, mais 800 × 800 px laisse davantage de marge. Pour un logo, préserver les proportions d’origine plutôt que d’étirer artificiellement le graphisme pour atteindre 640 × 240 px.

**Poids indicatifs** : image WebP de laboratoire idéalement inférieure à 200 Ko ; logo SVG optimisé de quelques dizaines de Ko ; PNG transparent de préférence inférieur à 200 Ko. Ces seuils ne justifient pas de rendre une identité institutionnelle illisible.

## Convention de nommage

Le nom est toujours **l’identifiant stable de l’autorité**, jamais son sigle, son nom courant ou le code du laboratoire auquel une tutelle est associée :

- `docs/assets/organismes/ORG-0001.webp` : illustration du Centre Camille-Jullian.
- `docs/assets/logos/ORG-0001.svg` : logo propre du Centre Camille-Jullian (facultatif).
- `docs/assets/logos/ORG-0004.svg` : logo du CNRS, utilisable comme tutelle de plusieurs laboratoires.
- `docs/assets/logos/ORG-0022.svg` : logo d’Aix Marseille Université, utilisable comme tutelle de plusieurs laboratoires.

Ces noms sont des **exemples d’emplacements**, pas des fichiers d’identité graphique déjà fournis ou validés.

Une seule image et un seul logo par autorité sont reconnus, chacun dans son dossier. Éviter les suffixes `-final`, `-v2` et `_copie`. Plusieurs extensions pour un même identifiant dans un même dossier provoquent volontairement une erreur à l’export.

## Règles éditoriales et graphiques

1. **Illustration principale** : privilégier une photographie ou un visuel représentatif dont l’usage est autorisé. Conserver une zone importante au centre de l’image (le carré peut être recadré). Éviter les textes intégrés.
2. **Logo institutionnel** : partir du fichier fourni par l’institution, idéalement vectoriel. Ne pas recoloriser, déformer ou fabriquer un faux logo ; préserver les marges de protection indiquées dans la charte graphique.
3. **SVG** : retirer tout script, lien externe, police embarquée ou référence réseau ; conserver un `viewBox` et des tracés autonomes. Les SVG doivent être vérifiés avant d’être publiés.
4. **PNG** : fond transparent si le logo l’exige, conversion en sRGB et suppression des métadonnées privées superflues. Tester la lisibilité sur fond blanc.
5. **Absence de logo** : le nom de la tutelle demeure affiché ; aucun pictogramme générique ne prend la place d’une identité institutionnelle officielle dans le bandeau.
6. **Droits et crédits** : conserver pour chaque média la source, l’auteur ou l’organisme dépositaire, la date de consultation, les conditions de reproduction et les crédits requis. L’existence d’un logo sur un site officiel n’autorise pas automatiquement sa réutilisation. Les mentions publiques nécessaires devront être intégrées au site avant diffusion de médias imposant une attribution.

## Actualisation après ajout d’une image

Depuis la racine du dépôt, après avoir placé les fichiers sous `docs/assets/` :

```bash
python3 scripts/export_organismes.py /chemin/vers/AdlFI_referentiel_1-10_20261106.xlsx
python3 -m unittest discover -s tests -v
node --check docs/assets/organismes.js
python3 -m http.server 8000 --directory docs
```

Consulter ensuite `http://localhost:8000/organismes/`, rechercher « Centre Camille-Jullian » et vérifier le résultat dans les vues « Cartouches » et « Liste », y compris sur petit écran.

L’exporteur détecte les fichiers dans `docs/assets/organismes/` et `docs/assets/logos/`, puis renseigne leurs chemins dans `docs/data/organismes.json`. **Ajouter seulement les fichiers images sans régénérer le JSON ne suffit pas à les afficher.**

## Cas de recette conseillés

- Un laboratoire avec illustration, deux tutelles dotées de logos (Centre Camille-Jullian).
- Un laboratoire sans illustration et sans logo propre : affichage du visuel neutre.
- Un laboratoire dont une tutelle n’a pas de logo : le nom reste visible sans faux logo.
- Un laboratoire à trois ou quatre tutelles : gestion de la largeur du bandeau.
- Un laboratoire inactif ou historique : respect de l’état et des relations datées.
- Un laboratoire dont les tutelles sont proposées mais **non validées** : aucune tutelle ne doit être présentée comme établie.

Le cartouche détaillé est réservé pour l’instant aux autorités `ORG` dont `type_organisme = laboratoire`. Les autres cartes gardent leur présentation actuelle.
