# Référentiels AdlFI

Prototype autonome du site **Référentiels AdlFI**, destiné à la publication de référentiels utilisés pour l'édition d'AdlFI et réutilisables dans l'Atlas documentaire.

## Rubriques

- **Lieux** — autorités Pactols et correspondances historiques COG (en préparation).
- **Autorités (personnes)** — noms, variantes et identifiants (en préparation).
- **Organismes** — premier explorateur fonctionnel des ORG et SER (données réelles du maître 1.10).
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
    organismes/               # images principales ORG-XXXX.jpg, SER-XXXX.jpg...
    logos/                    # identités visuelles de rattachement
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
- Les images doivent être ajoutées après vérification des droits et des crédits. Aucune image commerciale ou institutionnelle n'est récupérée automatiquement.
- La licence des données et les mentions légales du site restent à déterminer avant une publication de production.

## Développement futur

- Identifier les lieux avec le COG millésimé et GeoNames selon la provenance.
- Distinguer facette « type institutionnel » et facette « collectivités et intercommunalités » ; les anciens `echelon_territorial` non applicables seront ignorés dans cette dernière.
- Stabiliser le contrat JSON des autres rubriques et leurs propres cycles de publication.
- Produire un export spécifique à l'Atlas, documenté et versionné, plutôt que faire dépendre sa carte du DOM de ce site.
