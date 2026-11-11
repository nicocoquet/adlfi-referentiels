# Logos des autorités AdlFI — convention 320 × 320

## Principe

**Tous les visuels des autorités sont des logos, jamais des photographies.**

Une autorité possède un fichier JPEG carré, identifié par son ID stable :

```text
docs/assets/organismes/
  ORG-0004.jpg
  ORG-0023.jpg
  SER-0001.jpg
```

- Format **JPEG .jpg**, image de **320 × 320 pixels**, espace colorimétrique **sRGB**, fond blanc opaque.
- Qualité d'export conseillée : **85–90** ; pas de rééchantillonnage automatique par le site.
- **Conserver les proportions du logo d'origine** : placer le dessin dans une toile blanche carrée, avec des marges internes adaptées. Ne pas étirer, recadrer ou modifier le dessin officiel.
- Les logos allongés, les inscriptions très petites et les marques comportant des traits fins peuvent souffrir de la conversion JPEG. Conserver le fichier source (SVG ou PNG) en local et contrôler le JPEG produit. Si la lisibilité est insuffisante, conserver l'ancien logo SVG/PNG en attendant une solution de présentation.
- L'autorisation de reproduction et les éventuels crédits demeurent à vérifier.
- Un identifiant désigne **un seul fichier principal** ; pas de copie dans les dossiers des laboratoires ou des tutelles.

## Mise à jour directe avec VS Code

Depuis la racine du dépôt, placer le logo déjà préparé dans `docs/assets/organismes/ORG-XXXX.jpg`
(ou `SER-XXXX.jpg`). Puis :

```bash
git add docs/assets/organismes/ORG-XXXX.jpg
git commit -m "Ajouter le logo ORG-XXXX"
git push origin main
```

**Il n'est plus nécessaire de régénérer `docs/data/organismes.json`** pour ajouter
ou remplacer un JPEG : la page recherche directement un fichier `ID.jpg`.
Si une image n'existe pas, la page essaie l'ancien chemin enregistré dans le JSON.
Si aucun fichier n'existe, elle affiche un pictogramme de substitution.
Les relations de tutelle, titres et métadonnées continuent de provenir du JSON.

Les logos apparaissent comme visuel principal, comme identité de rattachement
et dans le bandeau des tutelles. Le CSS utilise `object-fit: contain` :
les marges internes prévues dans le JPEG évitent le rognage.

Lors de la modification d'un logo existant, un rechargement complet du navigateur
peut être nécessaire pour contourner son cache.

## Transition depuis la bibliothèque existante

La bibliothèque contient des fichiers historiques
`ORG-XXXX-logo.svg`, `ORG-XXXX-logo.webp`, `ORG-XXXX-illustration.webp`, etc.

- **Ne pas les supprimer lors de ce changement.** Ils servent de repli tant que
  le nouveau JPEG correspondant n'a pas été déposé.
- Un logo `ORG-XXXX.jpg` devient prioritaire dès son arrivée sur GitHub Pages.
- Après validation de la migration de tous les logos, les anciens fichiers devenus
  inutiles pourront être inventoriés et supprimés dans une PR distincte.
- Lors des prochains exports XLSX→JSON, l'exporteur identifie également le
  `ID.jpg` présent ; les anciens champs `presentation.media.logo/image`
  restent lisibles pour les jeux de données plus anciens.

Les images ne sont **jamais incorporées** au classeur XLSX.
Les coordonnées historiques des autorités, leurs noms et leurs relations ne sont
pas déduits des fichiers JPEG.

## Contrôles

```bash
python3 -m unittest discover -s tests -v
node --check docs/assets/organismes.js
python3 -m http.server 8000 --directory docs
```

Visiter `http://localhost:8000/organismes/` et vérifier au minimum :
1. Une autorité avec uniquement un nouveau JPEG carré.
2. Une autorité encore dotée seulement d'un ancien `-logo.svg` ou `-logo.webp`.
3. Une autorité sans aucun visuel (pictogramme de remplacement).
4. Un laboratoire disposant de plusieurs tutelles, certaines avec et d'autres sans logos.
5. Une fiche présentant une succession d'autorités (miniatures des deux entités).

Les tests de publication des données institutionnelles sont indépendants des médias.
