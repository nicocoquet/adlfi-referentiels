# Module Lieux — architecture temporelle V1, curseur annuel unique

**14 novembre 2026 — version de recette non publiée, PR n°24.**

## Arbitrage d'architecture

Le module Lieux utilisera **un seul curseur d'année**, initialisé à **2026**. L'année sélectionnée désigne précisément **le 1er janvier**, et non une plage de 365 jours.

La recherche des toponymes et des ARK restera indépendante de cette année : un ancien nom doit rester retrouvable lorsque le curseur indique l'année actuelle.

La priorité de réalisation est **JSON temporel → recherche et états historiques → géométries documentées → interface avec curseur → recette → publication**. Le curseur ne doit pas reconstituer des histoires administratives à partir de la similarité des noms.

## Jeu témoin réalisé en Bourgogne-Franche-Comté

Le prototype utilise **uniquement les 53 codes Insee** associés aux 29 candidatures et aux 86 lignes de mouvements du graphe historique BFC P1/P2/P3.

| Donnée | Contenu |
| --- | ---: |
| Codes Insee suivis | **53** |
| Périodes de noms de communes COM depuis 1943 | **69** |
| Entités COMA/COMD observées *au COG 2026 seulement* | **3** |
| Groupes d'événements administratifs datés | **28** |
| Années du curseur disponibles | **1943–2026** |
| Année affichée par défaut | **2026** |
| Nouveaux alignements Pactols–COG validés | **0** |
| Géométries historiques attribuées | **0** |

Le modèle est produit avec **scripts/preparer_lieux_temporel_bfc.py** à partir du graphe transversal validé et des fichiers officiels **v_commune_depuis_1943.csv** et **v_commune_2026.csv**. Les sources administratives sont contrôlées par SHA-256.

Le générateur écrit les trois fichiers suivants dans un **répertoire de recette**, jamais dans les données publiques :

- **lieux-temporel-bfc-recette.json** : 53 codes, 69 périodes de nom COM, 3 états complémentaires observés en 2026, 28 événements datés et provenance des sources ;
- **exemples-curseur-bfc.json** : témoins calculés à certaines années entre 1943 et 2026 ;
- **rapport-temporel-bfc.json** : cardinalités, empreintes et limites.

Le code JavaScript pur **docs/assets/lieux-temps.js** propose la consultation des états au 1er janvier et la recherche de tous les noms historiques d'un code, indépendamment de l'année sélectionnée. Il n'est pas encore chargé dans l'interface publique **docs/lieux/index.html**.

## Règle de temps

Pour une période administrative décrite par le COG :

**DATE_DEBUT est inclus, DATE_FIN est exclu**.

La commune est affichée comme commune COM attestée à l'année Y si et seulement si :

**DATE_DEBUT ≤ Y-01-01 et (DATE_FIN est vide ou Y-01-01 < DATE_FIN)**.

Cette convention évite d'afficher simultanément deux états de nom lorsqu'une nouvelle commune prend effet le 1er janvier.

| Code | Curseur avant | Curseur après | Changement |
| --- | --- | --- | --- |
| **25368** | 2017 : Marchaux | 2018 : Marchaux-Chaudefontaine | Commune nouvelle au 1er janvier 2018 |
| **25137** | 2017 : Chaudefontaine | 2018 : aucune entrée COM autonome | Rattachement à Marchaux-Chaudefontaine, sans disparition du lieu |
| **39137** | 2018 : Chemilla | 2019 : Saint-Hymetière-sur-Valouse | Commune nouvelle au 1er janvier 2019, même code |
| **71566** | 2024 : Verdun-sur-le-Doubs | 2025 : Verdun-Ciel | Commune nouvelle au 1er janvier 2025, même code |
| **25575** | 2016 : Vaire-Arcier | 2017 : Vaire | Création de Vaire au 1er juin 2016 : non encore effective au 1er janvier 2016 |

Ces exemples sont vérifiés en CI sur les données officielles, et non simulés.

## Distinction indispensable entre statut administratif et disparition d'un lieu

La table Insee **v_commune_depuis_1943.csv** ne contient que des périodes de communes **COM** et d'arrondissements municipaux **ARM** ; elle ne fournit **pas de série continue de statuts COMA/COMD**.

Ainsi, **Antorpe (39012)** dispose d'une entrée COM au 1er janvier 1974, mais pas après son rattachement. Cela **ne signifie pas que le lieu n'existe plus** : l'Insee l'atteste comme **COMA en 2026**. Nous pouvons montrer le rattachement de 1974 comme événement daté, sans inventer une chronologie continue de son statut depuis lors.

Les trois statuts complémentaires de notre jeu de test sont **des observations au millésime 2026 uniquement**, jamais rétroprojetées sur les années précédentes.

### Cartographie : une borne scientifique ferme

Les **géométries de 2026 sont des contours contemporains**, non des géométries historiques. L'export temporel ne contient actuellement **aucun polygone**. Un ancien nom ou une ancienne commune peut être recherché et décrit historiquement sans que son contour soit affiché à tort.

Dans l'interface future, les contours actuels pourront être proposés dans un **fond cartographique explicitement millésimé 2026** ; lorsqu'un état antérieur est sélectionné, aucun contour 2026 ne devra être présenté comme celui de l'époque.

## Tests et conditions de généralisation

La [CI de recette BFC](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43644323742) vérifie :

1. Deux générations du JSON **octet par octet** ;
2. La transition exacte Marchaux 2017/2018 et la suppression de l'entrée COM de Chaudefontaine ;
3. Chemilla 2018 / Saint-Hymetière-sur-Valouse 2019 ;
4. Verdun-sur-le-Doubs 2024 / Verdun-Ciel 2025 ;
5. Vaire-Arcier en janvier 2016 / Vaire en janvier 2017 ;
6. La non-rétroprojection des statuts COMA et des mouvements intervenant après le 1er janvier ;
7. La recherche des anciens noms indépendante de l'année ;
8. L'absence de géométries historiques et d'alignements Pactols non validés dans le JSON destiné au moteur d'affichage.

**Étape suivante :** appliquer le même contrat aux données nationales et construire l'index de recherche géographique, en conservant séparément les **103 alignements PACA déjà validés**, les candidatures encore ouvertes et les lieux hors COG communal. Puis seulement brancher le curseur sur la page cartographique.

**Aucune donnée publiée dans docs/data, aucune validation historique, aucune fusion de la PR n°24.**
