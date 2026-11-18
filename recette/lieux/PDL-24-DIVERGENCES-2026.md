# Pays de la Loire — instruction des 24 divergences Pactols–COG 2026

**Recette documentaire non validante (18 novembre 2026).** Le point de départ publié est de **1 194 / 1 228 communes** (34 exceptions) après la PR 140. Cette passe concerne exclusivement les **24 codes** du rapport régional `A_INSTRUIRE_LIBELLE_STATUT_OU_URI`, et non les neuf collisions d'ARK historiques ni Rives-du-Fougerais.

L'audit `scripts/qualifier_pdl_24_divergences_2026.py` reconstitue les preuves à partir du RDF Pactols-Lieux th17 du 22 juillet 2026 et du COG INSEE 2026 épinglés. Il récupère pour **chacun des 24 concepts uniques** :

- ses `skos:prefLabel` et `skos:altLabel` français, les définitions et notes ;
- les URI `skos:exactMatch` **complètes**, y compris les UUID INSEE, et les éventuels autres codes géographiques ;
- les propriétés de dépréciation et de remplacement ;
- les périodes de libellé COM du même code dans la chronologie historique COG.

Le rapport distingue **statut ou remplacement RDF**, **URI ou codes concurrents**, **catégorie géographique à vérifier**, **libellé non concordant**, et **structure RDF atypique**. Les causes ne sont pas mutuellement exclusives ; chaque dossier conserve ses motifs.

**Règles éditoriales :** un `altLabel` compatible n'est pas une validation ; une URI INSEE secondaire n'est pas arbitrairement ignorée ; un libellé d'ancienne commune ne suffit pas à qualifier un concept contemporain. Les codes COG sont contrôlés par comparaison aux publications existantes, sans réutilisation d'un ARK déjà validé.

La CI exécute deux recettes identiques octet à octet et dépose un rapport JSON contenant les 24 dossiers et leurs preuves RDF/COG. Elle vérifie **0 publication, 0 géométrie et 0 succession historique inférée**. Les cas éventuellement simples seront publiés dans une PR séparée seulement après instruction des résultats réels.

Les neuf collisions à examiner ensuite sont Baugé-en-Anjou, Ingrandes-le-Fresne-sur-Loire, Le Lion-d'Angers, Mauges-sur-Loire, Montsûrs, Sainte-Suzanne-et-Chammes, Villeneuve-en-Perseigne, Le Lude, Essarts-en-Bocage. Rives-du-Fougerais constitue un dossier supplémentaire distinct.

La refonte de l'interface graphique du module Lieux est réservée à l'étape suivant la consolidation des Pays de la Loire, à partir du cahier des idées éditoriales à recueillir.

## Résultats des recettes réelles — 18 novembre 2026

La [recette 44346325259](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44346325259) a confirmé que **les 24 divergences relèvent toutes du libellé principal d'une ancienne commune** : leur `prefLabel` Pactols concorde avec un épisode COM COG terminé avant 2026, mais non avec la commune actuelle du même code. Aucun des 24 concepts historiques n'est déprécié ni doté d'une autre URI INSEE contradictoire dans le snapshot RDF ; **aucune de ces 24 anciennes autorités ne peut être promue automatiquement**.

L'examen des candidats contemporains révèle :
- **17** concepts Pactols portant le libellé actuel, mais **sans aucun `exactMatch` INSEE**, y compris de type UUID, dans le RDF inspecté ;
- **2** concepts Pactols au libellé contemporain, mais dont l'`exactMatch` renvoie à **un autre code** : Les Hauts-d'Anjou (candidat `26678/pcrtJmNskrfHiK`, code `49065` au lieu de `49080`) et Orée d'Anjou (candidat `26678/pcrtS50omR9Tb5`, code `49069` au lieu de `49126`) ;
- **5** communes sans concept de libellé contemporain identifié par le parseur : Laigné-Saint-Gervais `72155`, Val-de-la-Hune `72382`, Cugand-la-Bernardière `85076`, Saint-Jean-d'Hermine `85223`, Terval `85289`.

Un [registre nominatif stable](PDL-24-DIVERGENCES-NOMINATIF-2026.json) conserve les 24 codes, les deux séries d'ARK lorsqu'elles existent, la fin des épisodes COM historiques, ainsi que les URI RDF explicitement présentes et le statut `NON_PUBLIE`.

### Incident de disponibilité des sources officielles

Une exécution complémentaire (workflow `44347500532`) a échoué **à l'acquisition réseau** de l'archive COG de l'Insee et du miroir data.gouv.fr (timeouts TLS et connexions réinitialisées), non aux tests du référentiel. Pour rendre la qualification reproductible sans dépendance aux serveurs externes, le workflow utilise **les trois dérivés COG 2026 déjà versionnés** (`cog-pdl.json`, `cog-corse.json`, `cog-bfc.json`) : il vérifie leurs régions, millésimes, effectifs courants (1 228 + 360 + 3 685) et reconstitue l'audit des **1 140 éligibles, 60 collisions, 24 divergences et 4 absences** par analyse du RDF épinglé.

Il s'agit **d'une recette du COG dérivé déjà validé**, et non d'un nouveau téléchargement ni d'une nouvelle vérification SHA-256 des fichiers CSV officiels. Cette distinction est explicitement conservée dans les métadonnées de provenance du rapport. Le RDF Pactols est toujours contrôlé par sa véritable empreinte SHA-256.

### Arbitrage pour les travaux suivants

Les 17 concepts courants sans `exactMatch` demandent un **alignement éditorial documenté** ou un enrichissement de Pactols : une coïncidence lexicale ne suffit pas à affirmer une identité. Les deux concepts porteurs d'un autre code doivent faire l'objet d'une instruction de la relation administrative et, éventuellement, d'une demande de correction à Frantiq. Les cinq autorités contemporaines non trouvées appellent une recherche complémentaire.

**Pas d'accroissement mécanique de couverture** pour cette catégorie. La couverture reste **1 194 / 1 228** (34 exceptions) jusqu'à de nouvelles décisions fondées.
