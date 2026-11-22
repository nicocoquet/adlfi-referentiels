# Référentiels AdlFI

Prototype autonome du site **Référentiels AdlFI**, destiné à la publication de référentiels utilisés pour l'édition d'AdlFI et réutilisables dans l'Atlas documentaire.

## Rubriques

- **Lieux** — autorités Pactols et correspondances historiques COG (en préparation).
- **Personnes** — noms, variantes et identifiants (en préparation).
- **Organismes** — premier explorateur fonctionnel des ORG et SER (données du maître qualifié 1.61, 22 novembre 2026).
- **Natures d’opération** — codes historiques, libellés et référentiels (en préparation).

Le dépôt `atlas-documentaire` reste **indépendant** : il pourra importer des exports JSON versionnés du présent dépôt.

## Arborescence

```text
docs/                        # fichiers publiés par GitHub Pages
  index.html
  lieux/index.html
  personnes/index.html
  autorites/index.html       # ancienne URL redirigée vers /personnes/
  organismes/index.html
  natures-operations/index.html
  assets/
    site.css
    organismes.js
    organismes/               # médias uniques des autorités : ORG-XXXX.jpg,
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
- Les logos d'autorités sont déposés **une seule fois** dans `docs/assets/organismes/`, sous le nom canonique `ORG-XXXX.jpg` ou `SER-XXXX.jpg`. Les tutelles et rattachements sont représentés par des liens de fiches, non par un bandeau de logos. Voir `docs/assets/GUIDE-IMAGES.md`.
- Les images doivent être ajoutées après vérification des droits et des crédits. Aucune image commerciale ou institutionnelle n'est récupérée automatiquement.
- La licence des données et les mentions légales du site restent à déterminer avant une publication de production.

## Évolution institutionnelle des autorités

L'explorateur présente les liens de succession entre autorités **distinctes**, sans réattribuer ni fusionner leurs affiliations historiques.

- Types représentés : `succession_institutionnelle`, `succession_service`, `succession`, `fusion_constitutive`, `scission_constitutive`, `succession_partielle` et `filiation_partielle`. Les fusions et filiations partielles ne valent pas succession juridique totale.
- Les relations doivent être au statut `valide` ; celles à vérifier demeurent dans le JSON mais ne sont pas présentées comme établies.
- Les relations sont lisibles dans les deux sens : « Structure ayant succédé » et « Structure antérieure ».
- Les deux premiers liens éventuels figurent dans les cartouches ; la fiche détaillée présente toutes les relations éligibles avec leur date et la navigation vers les autorités du catalogue.
- Le cartouche reste dans la grille à deux colonnes, même après un filtrage.
- Une autorité exclue du catalogue reste identifiable par son nom mais ne déclenche pas une navigation vers une fiche publique.
- Les fusions et filiations sont restituées dans les deux sens, y compris de SER vers ORG, en conservant le type exact de relation.

Le maître éditorial reste hors du dépôt. Le JSON de publication est daté et porte le SHA-256 du classeur source.

## Secteur institutionnel des services

Le secteur `public`/`prive` des SER est calculé dans le JSON par héritage des relations validées de type `rattachement_service`, y compris le long de chaînes SER → SER → ORG, **sauf lorsqu'une valeur explicite est documentée dans la feuille `Services`**. Les relations non validées ne sont pas prises en compte ; le champ `classification.sector_origin` conserve la provenance des rattachements retenus. Ce classement ne prétend pas attribuer un secteur à une date donnée.

La version **1.61 (22 novembre 2026)** qualifie sept activités auparavant indéterminées (six actives, une inactive : Atelier Bell) et établit à **2011** la date de début de la Cellule alpine de recherches archéologiques (SER-0193), sans préjuger de son activité actuelle. La répartition passe à **719 actives, 142 inactives et 74 indéterminées**. Le JSON compte toujours **935 autorités, 683 fiches visibles et 600 relations** ; aucune identité institutionnelle ou filiation n'est ajoutée. La date de fin d'Atelier Bell demeure à instruire ; l'indicateur documentaire « fin manquante » devient donc vrai. La recette du lot est conservée dans `recette/organismes/`.

La version **1.60 (22 novembre 2026)** qualifie quatre activités supplémentaires (AVVAS, ARSSAT, Archeoverde et Escles-Archéologie), sans nouvelle autorité ni relation institutionnelle. Les activités passent à **713 actives, 141 inactives et 81 non renseignées**. Le service SER-0195 reste à instruire. Les preuves et réserves sont consignées dans le registre de recette du lot 1.60.

La version **1.59 (22 novembre 2026)** qualifie 34 activités auparavant non renseignées (33 actives et une inactive) et corrige la date de fin d’`ORG-0503` en `2008`. L’état publié comporte **709 autorités actives, 141 inactives et 85 sans activité renseignée** ; les 935 autorités, 683 fiches visibles et 600 relations sont conservées. Cette consolidation n’ajoute ni autorité ni relation institutionnelle.

Dans le JSON du maître **1.58 (22 novembre 2026)** : **935 autorités** (735 ORG et 200 SER), **683 fiches visibles**, 252 autorités conservées hors catalogue et **600 relations** (342 REL et 258 RSE). Les **200 SER** possèdent un secteur résolu (**197 publics**, **3 privés**). La résolution des échelons institutionnels donne **190 échelons classés**, **8 explicitement non applicables** et **2 à instruire** (SER-0178 et SER-0202), dont **33 héritages historiques** documentés. Deux secteurs sont hérités de rattachements validés et 198 explicitement documentés dans le maître. Le lot A05 a validé les identités de l'AFAN (ORG-0068), du CNRS (ORG-0004) et de l'Inrap (ORG-0008), sans transférer les occurrences AFAN à l'Inrap. Neuf formes d'affiliation ont été qualifiées, portant sur dix-huit correspondances et 2 332 occurrences **de formes sources** (non de notices distinctes) ; les autres correspondances encore à vérifier restent provisoires. Le lot A05b a qualifié quinze autres formes composites (32 COR) associant le CNRS et l’Inrap à des laboratoires, représentant 59 occurrences de formes sources ; les compteurs passent à **18/173 CNRS** et **14/46 Inrap**. Aucun lien de tutelle ou de succession supplémentaire n’a été créé lors de ce lot. Le lot A05c (maître 1.55) a validé cinq formes AFF et dix COR (dont deux nouvellement créées) associant GAVS, Inrap, CRAHAM, CNRS et Préhistoire et Technologie (UMR 7055). La forme XML « nrap » est reliée à l’Inrap après vérification éditoriale. GAVS est une autorité validée et documentée depuis 1976, sans nouvelle relation institutionnelle ; les autres formes encore non qualifiées restent provisoires. Le lot A05d (maître 1.56) qualifie dix formes AFF supplémentaires et vingt COR existantes sans créer d'autorité ni de relation. Archéo Atlantica (AFF-0690) et Université de Nantes/GAVS (AFF-1485) restent partielles : chacune possède une composante COR validée mais son AFF conserve le statut provisoire. Le lot A05e (maître candidat 1.57) qualifie la composante Université de Nantes historique de la forme `AFF-1485` (« Université de Nantes/GAVS »), à partir de la signature publiée dans le *BSR Normandie 2016* ; il porte le compteur `ORG-0156.usage.affiliations_validated` de 1 à 2, sans modifier les 934 autorités, les 600 relations ni les autres compteurs. La composante Archéo Atlantica de `AFF-0690` demeure à instruire ; aucun SIREN ni nouvel ORG n'est validé. L'identification de la notice XML source exacte demeure une réserve documentaire, distincte du rapprochement nominal publié. Le lot A05f (maître 1.58) crée `ORG-0756` **Archéo Atlantica** comme entreprise privée, sur décision éditoriale et attestations professionnelles, sans l'assimiler à l'UMR 7055 ; la nouvelle `COR-2144` complète `AFF-0690`, désormais validée pour ses deux composantes. L'activité est située à Batz-sur-Mer ; la date de création « vers 2002 » est une estimation uniquement consignée dans le maître, sans `date_debut` certain ni SIREN officiellement validé. Cette publication ajoute **une autorité**, **une validation institutionnelle** et **une fiche visible**, sans nouvelle relation institutionnelle ; la partie PréTech `COR-0864` reste inchangée. Les compteurs `usage.affiliations_validated` portent sur les liens AFF–autorité ayant au moins une COR validée, et **non** sur les seules AFF entièrement qualifiées. La SCP `ORG-0292` conserve une catégorie BSR `PRIV` et un secteur institutionnel `public`. Les secteurs de `SER-0151` (DRASM) et `SER-0152` (CNRAS) sont **renseignés directement** dans la feuille `Services`, sur pièces institutionnelles historiques, sans les déduire de la fusion constitutive du Drassm. Le secteur institutionnel est distinct de la catégorie BSR et de la forme juridique.


## Héritage de l'échelon institutionnel des services

L'exporteur résout `classification.level` pour les SER à partir d'un champ explicite
facultatif `Services.echelon_institutionnel` (si présent) ou de relations validées
`rattachement_service`, directes et chaînées, applicables au jour de l'export.
Les relations terminées, futures, non validées et de succession sont exclues.
En cas de parents contradictoires ou sans échelon renseigné, la valeur reste
indéterminée : aucune inférence à partir du nom de la direction ou de sa ville.

`classification.level_origin` garde `method`, les ORG sources et les relations
utilisées ; `quality.level_unresolved` signale les SER non résolus.
Le champ décrit un **échelon institutionnel**, jamais le territoire de compétence.
La facette, la fiche et le CSV utilisent la même valeur calculée.


**Contrat de champs (compatible avec le maître actuel) :** pour une ORG,
`echelon_institutionnel` explicite prime sur l'ancien
`echelon_territorial` ; pour un SER, l'échelon explicite se trouve
uniquement dans `Services.echelon_institutionnel`. Le champ facultatif
`perimetre_competence` est exporté séparément sous
`classification.territorial_competence` et **n'est jamais hérité** de l'ORG.
Le maître 1.50 et le JSON de publication contiennent désormais des valeurs explicites pour ces champs. Elles restent facultatives : l'absence de renseignement n'autorise aucune inférence sur l'étendue de compétence.

Le vocabulaire de `perimetre_competence` est contrôlé : `national`,
`interregional`, `regional`, `departemental`, `intercommunal`, `communal`,
`local` (ou vide si indéterminé). Ce champ décrit l'étendue de la compétence,
**pas la liste des territoires couverts** : les ressorts géographiques et leurs
versions historiques doivent être modélisés séparément. L'exporteur rejette
une valeur hors vocabulaire.

Une ORG possédant un échelon explicite conserve désormais une trace
`classification.level_origin`, comme les SER héritant de leur rattachement.
La facette affiche un échelon dès lors qu'il est documenté ; elle ne masque
plus les catégories d'ORG initialement exclues par type.

**Décision appliquée au maître 1.49 :** l'ORG nationale Inrap (`ORG-0008`) possède l'échelon institutionnel `national` et le périmètre de compétence `national`. Ses huit directions interrégionales (`SER-0168` à `SER-0175`) héritent de l'échelon institutionnel **national**, mais leurs périmètres de compétence explicitement documentés sont **régionaux ou interrégionaux**. Le JSON publié comporte treize périmètres renseignés (Inrap, ses huit directions et quatre SER complémentaires) ; 907 autorités n'ont pas encore ce champ renseigné. L'explorateur affiche la compétence lorsqu'elle existe, **sans l'assimiler à la facette Échelon institutionnel**. Aucun maître XLSX n'est modifié par l'exporteur et aucun rattachement d'affiliation XML n'est créé.

## Développement futur

- Identifier les lieux avec le COG millésimé et GeoNames selon la provenance.
- Distinguer facette « type institutionnel » et facette « collectivités et intercommunalités » ; les anciens `echelon_territorial` non applicables seront ignorés dans cette dernière.
- Stabiliser le contrat JSON des autres rubriques et leurs propres cycles de publication.
- Produire un export spécifique à l'Atlas, documenté et versionné, plutôt que faire dépendre sa carte du DOM de ce site.
