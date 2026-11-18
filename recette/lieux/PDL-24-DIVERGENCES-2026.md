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
