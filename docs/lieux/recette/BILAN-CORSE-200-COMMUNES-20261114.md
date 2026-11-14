# Référentiel Lieux — Corse : 200 autorités, contrôle complet Pactols–COG 2026

**14 novembre 2026 — PR n°24 — recette non validante ; aucun changement sur GitHub Pages.**

## 1. Données exploitées

L'inventaire géographique dérive de l'extraction XML AdlFI nationale v2 (sélection par hiérarchie Pactols). Les codes sont ceux **déjà déclarés en `skos:exactMatch`** dans l'export Frantiq Pactols Lieux du 22 juillet 2026. Trois CSV Insee datés du **COG au 1er janvier 2026** ont été téléchargés et contrôlés lors de l'exécution GitHub Actions :

- `v_commune_2026.csv`, SHA-256 `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3` ;
- `v_commune_depuis_1943.csv`, SHA-256 `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee` ;
- `v_mvt_commune_2026.csv`, SHA-256 `8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`.

Les versions des fichiers d'inventaire corse et du lot 25, identifiées dans `rapport-corse-cog-2026.json`, sont également figées par leur SHA-256. Source officielle : https://www.insee.fr/fr/information/8740222

Contrôle CI **réussi** : https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43600124864

## 2. Résultats attestés par les vrais CSV Insee

| Indicateur | Résultat |
| --- | ---: |
| ARK terminaux de la zone géographique Corse | **200** |
| Codes de commune Insee déjà déclarés par Pactols (`skos:exactMatch`) | **194** |
| Codes trouvés comme **communes `COM` actives au COG 2026** | **194 / 194** |
| Concordances région/département (`94`, `2A` ou `2B`) | **194 / 194** |
| Liens vers des communes dont le code a changé le **01/01/1976**, `MOD=41` | **194 / 194** |
| Autres lieux, hors COG communal | **6** |
| Couples historiques code–libellé documentés pour ces 194 ARK | **393** |
| Lignes de mouvement liées aux codes de ces 194 ARK | **205** |
| Autres mouvements que `MOD=41` | **11** |
| Nouveaux alignements validés éditorialement | **0** |

Les **194 communes** se répartissent en **79** dans le département `2A` et **115** dans `2B`. Les six autres autorités sont : la **Corse** (région), les deux **départements**, **Cap Corse**, **Balagne** et **Filitosa**. Aucun identifiant communal ni contour communal ne doit être attribué aux trois derniers objets.

### 1976 : une recodification systématique, pas 194 énigmes distinctes

Le contrôle du fichier des mouvements montre pour **chacun des 194 ARK communaux** une transition `MOD=41` au **1er janvier 1976**, du code `20...` au code `2A...` ou `2B...`, liée à la création des départements Corse-du-Sud et Haute-Corse. Les deux états successifs restent documentés avec leur date d'effet.

**Méthode proposée :** représenter dans le graphe des événements une famille de transitions datées, tout en conservant la preuve nominative par ARK. Le code `20...` ancien et le code départemental `2A...` / `2B...` moderne ne forment pas deux communes homonymes. La transition administrative ne démontre cependant **aucune permanence cadastrale du contour**.

Parmi les 194 autorités, **190** possèdent exactement **deux** couples code–libellé historiques, **trois** possèdent **trois** couples et **une** possède **quatre** couples. Les **393** lignes sont transcrites en recette dans `corse-200-periodes-cog-1943-2026.csv`, avec un intervalle `[DATE_DEBUT, DATE_FIN[` et une fin ouverte au COG 2026.

### Les véritables changements administratifs singuliers

Le contrôle retrouve **onze autres lignes de mouvement**, concernant **cinq communes**, à soumettre en priorité à l'instruction historique :

| Commune actuelle | Code 2026 | Événement(s) distinct(s) documenté(s) | Traitement |
| --- | --- | --- | --- |
| **Sainte-Lucie-de-Tallano** | `2A308` | **1965-01-01**, `MOD=31` ; intégration de Poggio-di-Tallano et Sant'Andréa-di-Tallano, ancien nom Santa-Lucia-di-Tallano | Fusion simple, changement de composition et de libellé ; ne pas prolonger l'ancien contour automatiquement |
| **Montegrosso** | `2B167` | **1972-01-01**, puis **1973-01-01**, `MOD=31` ; étapes Montemaggiore → Saint-Rainier-de-Balagne → Montegrosso avec Lunghignano puis Cassano | Plusieurs états successifs et deux événements de fusion simple avant le recodage de 1976 |
| **Propriano** | `2A249` | **1974-04-01**, `MOD=31`, fusion avec Tivolaggio | Conserver l'ancienne commune absorbée et distinguer les contours d'avant/après fusion |
| **Sari-Solenzara** | `2A269` | **1985-01-19**, `MOD=10`, ancien nom Sari-di-Porto-Vecchio | Changement de nom ; pas de changement de contour inféré du seul `MOD=10` |
| **Pianottoli-Caldarello** | `2A215` | **2001-01-01**, `MOD=10`, ancienne graphie Pianotolli-Caldarello | Changement de dénomination / graphie ; date à conserver sans déduire de modification territoriale |

Les `MOD=31` comprennent **neuf lignes** pour **quatre opérations de fusion simple** (Sainte-Lucie 1965, Montegrosso 1972 et 1973, Propriano 1974). Les `MOD=10` représentent deux changements de nom (Sari 1985 et Pianottoli 2001). Source des modalités Insee : https://www.insee.fr/fr/information/5057793

### Trois libellés Pactols explicitement désambiguïsés

- **Asco (France)**, COG `2B023` **Asco** ;
- **Saint-Florent (Haute-Corse)**, COG `2B298` **Saint-Florent** ;
- **Villanova (Corse-du-Sud)**, COG `2A351` **Villanova**.

La parenthèse relève du libellé d'autorité, pas du nom de commune au COG 2026. Après neutralisation **explicite** de ces trois qualificatifs géographiques reconnus, les 194 noms candidats sont concordants avec le nom officiel de leur code. La suppression des parenthèses ne modifie **ni le `prefLabel` Pactols ni le nom officiel** stockés séparément.

## 3. Pièces de preuve conservées dans la branche

- `corse-200-candidatures-cog-2026.csv` — 200 autorités, types, codes, statuts, liens documentaires non validés ;
- `corse-25-prioritaires-cog-2026.csv` — 22 communes + Cap Corse, Balagne, Filitosa ;
- `corse-200-periodes-cog-1943-2026.csv` — les **393** périodes code–libellé documentées ;
- `corse-200-evenements-cog-2026.csv` — les **205** lignes de mouvement, à lire comme indices par ARK, pas comme 205 opérations administratives distinctes ;
- `rapport-corse-cog-2026.json` — compteurs et empreintes de sources.

Le script `scripts/auditer_lieux_corse_cog.py`, ses six tests et le workflow dédié assurent la reproductibilité. **Ne pas publier** `skos:exactMatch` ou une géométrie en sortie de ce contrôle : les 194 liens Frantiq sont des **assertions préexistantes**, non des arbitrages AdlFI. Les géométries 2026 sont contemporaines ; les formes d'anciennes communes absorbées doivent être recherchées indépendamment.

## 4. Prochaine décision éditoriale

**Proposition :** examiner collectivement la règle de gestion des **194 recodifications de 1976**, puis décider individuellement du traitement des cinq communes ayant d'autres événements et des trois autorités naturelles/archéologiques du lot de 25. Ce travail est plus utile qu'une revue aveugle des 194 communes par ordre alphabétique.

**Aucune modification de `docs/data/lieux.json`, `docs/data/lieux-communes.geojson` ni de l'interface publique.**
