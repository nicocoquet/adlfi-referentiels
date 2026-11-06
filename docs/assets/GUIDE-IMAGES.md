# Préparation des médias des autorités AdlFI

## Principe : une bibliothèque unique pour les organismes et leurs tutelles

Chaque organisme (ou service) possède une identité stable `ORG-XXXX` (ou `SER-XXXX`). Ses médias sont conservés **une seule fois**, dans :

```text
docs/assets/organismes/
  ORG-0001-logo.svg
  ORG-0001-illustration.webp
  ORG-XXXX-logo.png
  SER-XXXX-logo.svg
```

Ces noms illustrent la convention : seuls les fichiers réellement documentés et autorisés sont déposés. **Il n’existe plus de dossier de médias distinct pour les tutelles.**

La différence entre un **logo** et une **illustration** concerne le type de fichier, non le rôle de l’organisme dans une fiche :

- `ORG-XXXX-logo.svg` est affiché **comme visuel principal** de l’autorité lorsque celle-ci n’a pas d’illustration propre.
- Le **même fichier de logo**, sans copie, peut être affiché dans le bandeau de tutelles de tous les laboratoires ayant une relation de tutelle validée avec cet organisme.
- `ORG-XXXX-illustration.webp` (photo ou illustration) peut être utilisé comme visuel principal de l’autorité. **Il ne remplace pas son logo dans un bandeau institutionnel**.
- Si les deux existent, l’illustration est privilégiée dans la carte de l’organisme, et le logo demeure utilisé dans les bandeaux de tutelles.
- Si seule une illustration existe pour une tutelle, son nom est affiché sans photo dans le bandeau : pas de confusion entre image documentaire et identité officielle.

Le format JSON public conserve deux champs complémentaires (`presentation.media.image` pour l’illustration, `presentation.media.logo` pour le logo), mais **chaque chemin est une référence au fichier unique de l’autorité** : il n’y a aucune copie dans une arborescence propre au laboratoire qui l’utilise.

## Formats et dimensions

| Type | Recommandation | Dimensions source | Rendu dans la carte |
| --- | --- | --- | --- |
| Illustration / photographie | WebP ou JPEG, recadrage carré lorsque pertinent | **800 × 800 px** | Environ 144 × 144 CSS px, `object-fit: cover` |
| Logo officiel vectoriel | **SVG**, tracés autonomes, `viewBox` | Sans dimensions matricielles imposées | `object-fit: contain`, sans rognage |
| Logo officiel matriciel | PNG avec fond transparent (sRGB) | Pour un logo horizontal, viser **640 × 240 px** environ, en conservant son ratio | Jusqu’à **160 × 58 CSS px** dans le bandeau ; `object-fit: contain` |

Les dimensions sont indicatives. Un affichage `retina` requiert idéalement une source d’au moins deux fois la taille CSS. Pour les logos, ne pas imposer un ratio ou un recadrage qui déformerait la charte officielle. Les paramètres ppp/dpi sont sans incidence sur la netteté web à dimensions en pixels égales.

**Poids souhaitables** : photographie WebP d’environ 100–200 Ko ; SVG optimisé aussi léger que possible ; PNG transparent de préférence inférieur à 200 Ko. Privilégier la lisibilité à un plafond arbitraire.

## Contraintes techniques

- Le nom suit exactement le motif `ORG-0001-logo.svg`, `ORG-0001-illustration.webp`, etc. (mêmes règles pour `SER`).
- Extensions reconnues : `.jpg`, `.jpeg`, `.png`, `.webp`, `.svg`.
- Une seule extension est autorisée **par identifiant et par type** : deux `ORG-0001-logo.*` provoquent une erreur à l’export.
- On peut posséder **un logo et une illustration** pour un même identifiant, mais ce sont deux médias différents, pas deux exemplaires du même visuel.
- Le logo d’une tutelle doit être enregistré sous **son propre identifiant**, et non celui de chaque laboratoire où il apparaît.
- Aucun média n’est inféré, téléchargé ou généré automatiquement par l’exporteur.
- Vérifier les conditions de réutilisation et de crédit de chaque visuel, même lorsqu’il est publié sur le site institutionnel.
- Pour les SVG : aucun script, contenu actif, référence réseau externe ou police embarquée ; vérifier le rendu sur fond clair.

## Mise à jour locale

Depuis la racine du dépôt, après avoir ajouté les médias à `docs/assets/organismes/` :

```bash
python3 scripts/export_organismes.py /chemin/vers/AdlFI_referentiel_1-10_20261106.xlsx
python3 -m unittest discover -s tests -v
node --check docs/assets/organismes.js
python3 -m http.server 8000 --directory docs
```

Ouvrir `http://localhost:8000/organismes/`. **La régénération du JSON est nécessaire** pour que de nouveaux fichiers soient reconnus.

## Scénarios de recette

1. Centre Camille-Jullian, illustration propre et deux tutelles dotées de logos officiels.
2. Organisme possédant seulement un logo : le même fichier doit être exploitable comme visuel principal et comme logo de tutelle.
3. Tutelle sans logo officiel : seule la dénomination apparaît, sans photo de remplacement.
4. Laboratoire à quatre tutelles : contrôler la densité et le comportement sur mobile.
5. Relation de tutelle non validée ou terminée : aucun logo présenté comme celui d’une tutelle actuelle.
6. Organisme avec logo **et** illustration : image principale et logo institutionnel doivent rester correctement distingués.

La refonte porte à ce stade sur les cartes des ORG de type `laboratoire`, sans modifier les autres catégories.
