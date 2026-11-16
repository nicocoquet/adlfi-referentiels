# Logos des autorités AdlFI — règle unique

## Un seul format et un seul nommage

La bibliothèque est `docs/assets/organismes/`. Chaque logo porte **l’identifiant stable de son autorité**, jamais le nom littéral de la structure (qui peut changer ou être homonyme) :

```text
docs/assets/organismes/
  ORG-0001.jpg
  ORG-0023.jpg
  SER-0155.jpg
```

- **Seul le format JPEG `.jpg`** est accepté. Pas de fichiers `-logo.webp`, `-logo.svg`, `-illustration.*`, `.jpeg` ou `.png` dans ce dossier.
- Format graphique de référence : **320 × 320 pixels, RVB/sRGB**, fond blanc opaque, sans déformer le dessin ni rogner le logo.
- Un fichier par autorité `ORG-XXXX` ou `SER-XXXX` ; le même JPEG sert dans sa fiche, les miniatures de succession et les logos de tutelle.
- Toute image doit correspondre à une autorité connue. Pour une autorité sans JPEG, l'interface affiche un pictogramme de remplacement.
- Les droits de reproduction, la provenance et la fidélité aux identités visuelles officielles restent à contrôler.

**Le nom canonique est l’identifiant**, par exemple `ORG-0023.jpg` pour le ministère de la Culture. Il ne faut pas créer de fichiers à partir des dénominations institutionnelles (`Ministere-de-la-Culture.jpg`).

## Ajouter un logo depuis VS Code

Copier le JPEG dans `docs/assets/organismes/`, puis, à la racine du dépôt :

```bash
git status --short --branch
git add docs/assets/organismes/
git diff --cached --stat
git commit -m "Mettre à jour les logos des organismes"
git push origin main
```

Le navigateur déduit directement le chemin `ID.jpg` : **aucune modification du JSON n’est nécessaire pour afficher un JPEG ajouté**. GitHub Pages publie le fichier au prochain déploiement. Si un logo remplacé paraît inchangé, recharger la page sans cache.

Pour **actualiser également les références facultatives** dans le JSON documentaire, utiliser `python3 scripts/synchroniser_logos_publies.py --write` et versionner le JSON obtenu. Cela n’est pas nécessaire pour la simple consultation en ligne.

## Tests

```bash
python3 -m unittest discover -s tests -p 'test_export.py' -v
python3 scripts/synchroniser_logos_publies.py --check
node --check docs/assets/organismes.js
node tests/test_tutelles_order.js
```

`--check` vérifie que les références de médias du JSON sont **synchronisées** avec les JPEG présents ; cette commande est un audit éditorial optionnel lors des ajouts directs de logos. Les tests généraux interdisent les références cassées et les anciens formats.

Les anciens logos non JPEG ont été retirés de la bibliothèque publiée : aucun mécanisme de repli sur ces anciens fichiers n’est conservé.
