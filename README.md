# Référentiels AdlFI

Prototype autonome du site **Référentiels AdlFI**, destiné à la publication de référentiels utilisés pour l'édition d'AdlFI et réutilisables dans l'Atlas documentaire.

## Rubriques

- **Lieux** — autorités Pactols et correspondances historiques COG (en préparation).
- **Autorités (personnes)** — noms, variantes et identifiants (en préparation).
- **Organismes** — premier explorateur fonctionnel des ORG et SER (données réelles du maître 1.15).
- **Natures d'opérations** — codes historiques, libellés et référentiels (en préparation).

Le dépôt `atlas-documentaire` reste **indépendant** : il pourra importer des exports JSON versionnés du présent dépôt.

## Arborescence

```text
docs/                        # fichiers publiés par GitHub Pages
  index.html
  lieux/index.html
  autorites/index.html
  organismes/index.html
  natures-operations/index.html
  assets/
    site.css
    organismes.js
    organismes/               # médias uniques des autorités : ORG-XXXX-logo.svg,
                               # ORG-XXXX-illustration.webp, SER-XXXX-logo.svg...
  data/organismes.json        # JSON généré pour l'interface
  data/manifest.json          # état des modules et format des exports
  schemas/organismes.schema.json
scripts/export_organismes.py   # export lecture seule depuis XLSX
tests/test_export.py           # tests sans dépendances
```

## Regénérer le JSON (sans modifier le XLSX)

Depuis la racine du dépôt :

```bash
python3 scripts/export_organismes.py /chemin/vers/AdlFI_maitre.xlsx
python3 -m unittest discover -s tests -v
```

L'exporteur ne dépend que de la bibliothèque standard Python ; il lit l'OOXML du XLSX en lecture seule. Il reconnaît les valeurs `oui/non` dans `affichage_catalogue`, le champ `numero_lab` et la feuille `Statuts_historiques`.

La feuille `Statuts_historiques` est exportée avec son **statut de validation** : les données à vérifier sont signalées comme telles dans les fiches et ne doivent pas être considérées comme définitivement établies.

**Ne pas verser le maître XLSX dans ce dépôt public** : il contient des commentaires, des journaux de relecture et des dossiers éditoriaux. Les exports JSON ne reprennent pas ces notes de travail.

## Tester localement

```bash
cd docs
python3 -m http.server 8000
```

Ouvrir : http://localhost:8000/ puis http://localhost:8000/organismes/

## Initialiser le dépôt GitHub

1. Créer sur GitHub un dépôt nommé `adlfi-referentiels` sous le compte ou l'organisation choisi, **sans README initial ni licence par défaut**.
2. Depuis le dossier de ce prototype :

```bash
git init -b main
git add .
git commit -m "Initialiser le site Référentiels AdlFI"
git remote add origin git@github.com:nicocoquet/adlfi-referentiels.git
git push -u origin main
```

Adapter `nicocoquet` si le dépôt est créé dans une organisation.

3. Pour publier via GitHub Pages : **Settings → Pages → Build and deployment → Deploy from a branch → main → /docs → Save**.

Ce prototype ne nécessite ni MkDocs, ni construction JavaScript : le serveur publie directement le contenu statique du dossier `docs`. Une intégration MkDocs/Material, à l'image de Mosar, pourra être décidée lorsque les rubriques documentaires seront étoffées.

## Contrat de données et précautions

- Les identifiants ORG/SER sont stables et réutilisables.
- Les ORG/SER exclus du catalogue restent **présents dans le JSON** afin de documenter leurs relations et logos, mais ne disposent pas de cartouche dans la page publique.
- Les relations non validées ne sont jamais affichées comme des rattachements certains.
- `pays_iso2` désigne le **pays de rattachement institutionnel**, `ville_reference` les villes déclarées ; **ne pas géocoder** un nom de ville libre sans identifiant vérifié.
- Les libellés institutionnels suivent les conventions éditoriales AdlFI, distinctes des formes juridiques littérales.
- Tous les médias des autorités (y compris les logos utilisés dans les bandeaux de tutelles) sont déposés **une seule fois** dans `docs/assets/organismes/`, avec les suffixes `-logo` et `-illustration`. Voir `docs/assets/GUIDE-IMAGES.md`.
- Les images doivent être ajoutées après vérification des droits et des crédits. Aucune image commerciale ou institutionnelle n'est récupérée automatiquement.
- La licence des données et les mentions légales du site restent à déterminer avant une publication de production.

## Évolution institutionnelle des autorités

L'explorateur présente les liens de succession entre autorités **distinctes**, sans réattribuer ni fusionner leurs affiliations historiques.

- Types affichés dans la première version : `succession_institutionnelle` (ORG) et `succession_service` (SER).
- Les relations doivent être au statut `valide` ; celles à vérifier demeurent dans le JSON mais ne sont pas présentées comme établies.
- Les relations sont lisibles dans les deux sens : « Structure ayant succédé » et « Structure antérieure ».
- Les deux premiers liens éventuels figurent dans les cartouches ; la fiche détaillée présente toutes les relations éligibles avec leur date et la navigation vers les autorités du catalogue.
- Le cartouche reste dans la grille à deux colonnes, même après un filtrage.
- Une autorité exclue du catalogue reste identifiable par son nom mais ne déclenche pas une navigation vers une fiche publique.
- Les autres types historiques (`fusion_constitutive`, `scission_constitutive`, `succession_partielle`, `filiation_partielle`) sont conservés dans les données mais nécessitent une rédaction et une visualisation propres ; ils ne sont pas assimilés à une succession simple.

Le maître éditorial reste hors du dépôt. Le JSON de publication est daté et porte le SHA-256 du classeur source.

## Développement futur

- Identifier les lieux avec le COG millésimé et GeoNames selon la provenance.
- Distinguer facette « type institutionnel » et facette « collectivités et intercommunalités » ; les anciens `echelon_territorial` non applicables seront ignorés dans cette dernière.
- Stabiliser le contrat JSON des autres rubriques et leurs propres cycles de publication.
- Produire un export spécifique à l'Atlas, documenté et versionné, plutôt que faire dépendre sa carte du DOM de ce site.
