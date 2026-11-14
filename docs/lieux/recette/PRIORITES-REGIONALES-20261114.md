# Lieux AdlFI — Préparation des trois régions prioritaires (14 novembre 2026)

**État : recette non validante.** Aucun nouveau lien Pactols–COG, ni aucune géométrie, n'est publié.

## 1. Périmètre et méthode

Le corpus national analysé est l'extraction XML AdlFI v2 du 13 novembre 2026 :
`autorites_lieux.csv` (9 928 ARK) et `occurrences_lieux.csv` (30 772 occurrences).
Les zones sont sélectionnées par la **chaîne hiérarchique Pactols attestée**,
non par le répertoire régional du XML, qui peut contenir des synthèses
interdépartementales, des index hydrographiques ou des mentions d'autres régions.

Les trois régions sont classées en géographie administrative **COG 2026**, tout
en conservant les dénominations antérieures comme *Bourgogne* et *Franche-Comté* :

| Région ciblée | Code région 2026 | Départements | ARK terminaux | Occurrences | Notices distinctes |
| --- | --- | --- | ---: | ---: | ---: |
| Corse | `94` | `2A`, `2B` | **200** | **1 006** | **757** |
| Pays de la Loire | `52` | `44`, `49`, `53`, `72`, `85` | **806** | **3 007** | **2 108** |
| Bourgogne-Franche-Comté | `27` | `21`, `25`, `39`, `58`, `70`, `71`, `89`, `90` | **736** | **1 885** | **1 034** |
| **Total** | | | **1 742** | **5 898** | **Non sommables sans dédoublonnage** |

Les compteurs de notices comprennent les index terminaux de niveau **région** et
**département** (et non les seules communes). La note narrative initiale de
reprise avait omis ces quelques index de niveau supérieur en comptant les notices ;
les valeurs du présent rapport sont les chiffres exacts du périmètre complet.

Sources officielles :
- https://www.insee.fr/fr/metadonnees/geographie/region/94-corse
- https://www.insee.fr/fr/metadonnees/geographie/region/52-pays-de-la-loire
- https://www.insee.fr/fr/metadonnees/geographie/region/27-bourgogne-franche-comte
- https://www.insee.fr/fr/information/8740222

## 2. Exploitation de Pactols SKOS avant tout rapprochement lexical

Le référentiel Frantiq **Pactols Lieux**, export RDF/XML du 22 juillet 2026
(th17, empreinte SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`)
contient des assertions `skos:exactMatch` pointant vers des URI Insee.

| Région | ARK avec URI Insee `/geo/commune/` suivie d'un code à cinq caractères | Sans ce type d'URI |
| --- | ---: | ---: |
| Corse | 194 | 6 |
| Pays de la Loire | 797 | 9 |
| Bourgogne-Franche-Comté | 727 | 9 |
| **Total** | **1 718** | **24** |

La seconde colonne **ne signifie pas 24 identités non connues** :
plusieurs ARK sont des régions ou départements, des pays naturels,
des sites archéologiques, ou possèdent une URI Insee non numérique.
Un lien `skos:exactMatch` est ici **une assertion du producteur Pactols** :
il ne remplace pas le contrôle des mouvements COG, de l'identité de l'entité
administrative, de la temporalité, ni la validation éditoriale d'AdlFI.

Trois URI de commune possèdent un préfixe départemental différent de
l'actuel département de la hiérarchie Pactols, **sans que cela constitue
à ce stade une erreur** :

- **Antorpe** : `39012` (ancien code Jura), aujourd'hui intégré à
  Saint-Vit, Doubs ; source : https://adresse.data.gouv.fr/commune/25527
- **Frettes** : `52210` (ancien code Haute-Marne), aujourd'hui intégré à
  Champlitte, Haute-Saône ; source : https://adresse.data.gouv.fr/commune/70122
- **Le Puy-Saint-Bonnet** : `79224` (commune associée de Cholet), code
  conservé malgré le rattachement au Maine-et-Loire ; source Insee :
  https://www.insee.fr/fr/metadonnees/geographie/commune-associee/79224-le-puy-saint-bonnet

**Règle impérative :** ne jamais « corriger » un code historique en
remplaçant son préfixe départemental par celui de la commune de rattachement.
Conserver `TYPECOM`, le code historique, les événements de succession et
la date de validité documentée.

## 3. Priorisation opérationnelle

- **Corse (lot pilote de 25 ARK)** : commencer par Afa et Aghione
  (`MOD=41`, 1976), puis distinguer les communes des pays naturels
  **Cap Corse**, **Balagne**, et du site archéologique **Filitosa**.
- **Pays de la Loire (lot pilote de 25)** : commencer par la
  commune associée **Le Puy-Saint-Bonnet**, les URI Insee non numériques de
  **Thouarsais-Bouildroux** et **Grandchamp-des-Fontaines**, et
  **Cherré-Au**. La commune **Béthon** (Sarthe) possède un ARK Pactols
  propre (`26678/pcrtGHlbdiOta1`, code `72036`), à confronter à la
  **mauvaise indexation probable** de la notice « Autoroute A28 ».
- **Bourgogne-Franche-Comté (lot pilote de 25)** : examiner d'abord
  **Antorpe** et **Frettes**, et conserver séparément l'alerte
  **Brain/Brains** dans la notice *Pays de Retz*. Le dossier
  **Bethon/Béthon** concerne, lui, la notice *Autoroute A28* ; ces deux
  confusions documentaires ne doivent pas être amalgamées.
  Le lot doit être **stratifié par département** pour ne pas reproduire
  la forte surreprésentation des départements de l'ancienne Franche-Comté.

Les lots sont volontairement limités à **25 ARK par région**, avec une
présélection explicite de cas historiques et documentaires, puis
un échantillonnage équilibré entre les départements (par ordre de nombre
de notices). Les fichiers de recette sont :

- `lot-01-corse.csv`
- `lot-01-pays-de-la-loire.csv`
- `lot-01-bourgogne-franche-comte.csv`

Le **total de 75 lignes est un programme de vérification, pas 75 alignements validés**.

## 4. Couverture XML : état d'avancement Bourgogne

Dans le répertoire BFC du corpus v2, seuls **deux fichiers Bourgogne 2009**
sont retenus (9 et 4 notices), tandis qu'une série importante de BSR
Franche-Comté couvre les années 1992–2011. Les 736 ARK de BFC ne
constituent donc **pas** un échantillon équilibré de toute la région.
Le faible effectif de Côte-d'Or, Nièvre, Saône-et-Loire et Yonne
s'explique, selon le responsable éditorial, par le **nombre encore limité de notices d'opérations de l'ancienne Bourgogne déjà mises au format XML**. Ce constat n'établit pas une défaillance de l'extraction et n'appelle pas, à lui seul, un audit de fichiers prétendument manquants. Toute conclusion sur
la couverture géographique du référentiel. Les notices de synthèse,
les XML du Drassm et les lieux attestés dans d'autres régions ne doivent
pas être artificiellement déplacés pour corriger cette disproportion.

## 5. Régions des index et régions éditoriales

Un deuxième fichier `contextes-editoriaux-hors-region.csv` conserve,
sans les réaffecter, les ARK dont l'occurrence se trouve dans un XML
éditorial de l'une des trois régions mais est **indexée sous une autre
hiérarchie Pactols** :

| Dossier éditorial | ARK hors région hiérarchique | Occurrences correspondantes |
| --- | ---: | ---: |
| Corse | 4 | 71 |
| Pays de la Loire | 31 | 40 |
| Bourgogne-Franche-Comté | 23 | 28 |

Dans les fichiers de Corse, par exemple, plusieurs occurrences sont
indexées sous **Mer Méditerranée** et ne doivent pas être décrétées
« communes corses ». Les index documentaires d'autres départements
peuvent être justifiés par le caractère transversal des notices.

## 6. Sources, versionnement et reproductibilité

Génération avec `scripts/preparer_lots_lieux_regions.py` et ses tests.
L'export SKOS utilisé provient de l'audit national réalisé sur le fichier
Frantiq officiel, avec vérification préalable de l'empreinte RDF.

```bash
python3 scripts/preparer_lots_lieux_regions.py \
  --autorites "$HOME/Desktop/AdlFI-audit-lieux-v2/autorites_lieux.csv" \
  --occurrences "$HOME/Desktop/AdlFI-audit-lieux-v2/occurrences_lieux.csv" \
  --skos-csv "/chemin/vers/controle_concepts_pactols.csv" \
  --sortie "$HOME/Desktop/AdlFI-lieux-regions-prioritaires" \
  --taille-lot 25
```

Le fichier `rapport-priorites-regionales.json` conserve les **empreintes
SHA-256 des trois CSV d'entrée** ; les cartes et JSON publics de Lieux
ne sont pas affectés. Ne pas confondre les URI SKOS avec des codes COG
contemporains : un lien Insee vers un ancien code, une commune associée
ou un identifiant UUID ne fournit **pas** en soi la géométrie 2026.
