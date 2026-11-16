# ADR — Intégration de la navigation multi-échelon dans le référentiel Lieux AdlFI

**16 novembre 2026 · PR #31 · décision de méthode, recette hors `docs/`.**

## Décision centrale

Le prototype autonome SVG (`AdlFI_Lieux_Multiechelon_2015_2016.html`) est un **banc d'essai pour l'audit spatial et le parcours des 227 états 2015–2016** ; ce **n'est pas** une seconde application publique, ni un référentiel alternatif.

**L'interface cible est une seule carte Leaflet avec fond OpenStreetMap et couches administratives datées**, intégrée au **module Lieux existant** et connectée à ses données communales, au COG historique et aux alignements Pactols validés. Les contrôles `Zoom sur`, `Échelon territorial`, `Situation au` sont des dimensions orthogonales de la même carte et de la même recherche.

Ne pas remplacer le travail communal par le prototype régional, ni dupliquer les autorités éditoriales.

## État vérifié du site au 16 novembre 2026

- `docs/lieux/index.html`, `docs/assets/lieux.js` et `docs/assets/lieux-search.js` : premier explorateur PACA, **Leaflet**, tuiles `https://tile.openstreetmap.org/{z}/{x}/{y}.png`, recherche Pactols / code INSEE, fiches des **103 correspondances éditoriales validées** et polygones communaux **COG 2026** ; données `docs/data/lieux.json` et `docs/data/lieux-communes.geojson`.
- `docs/lieux/chronologie/index.html`, `docs/assets/lieux-chronologie.js` et `docs/assets/lieux-chronologie-core.js` : seconde interface *déjà publique* sur la chronologie des communes de PACA, Corse, Pays de la Loire et Bourgogne-Franche-Comté de **1943 à 2026**, utilisant **elle aussi Leaflet + fond OSM**. Les données COG communales comportent états, mouvements, noms anciens et alignements Pactols explicitement validés, mais **aucun contour historique de commune** ; les contours éventuellement visibles restent au **millésime 2026**, indiqués comme repères actuels.
- PR #31 : deux sources IGN GEOFLA originales (03/2015, 06/2016) → **35 polygones régionaux dérivés** et **192 états départementaux** (96 par millésime) ; leurs codes et noms proviennent des deux COG respectifs. Ce sont des *états administratifs* et non de nouveaux concepts Pactols.
- PR #30 : audit territorial ultramarin, séparé et non encore publié.

**Limite actuelle à lever :** la chronologie publique regroupe des codes communaux par préfixe départemental et par région **2026** ; ce regroupement n'est pas une preuve de rattachement à une région historique. Ajouter les liens de hiérarchie régionale datés, là où ils sont qualifiés, sans rétroprojection.

## Architecture cible (une seule interface, plusieurs sources)

| Couche logique | Source de vérité | Fonction de l'interface | Précaution |
|---|---|---|---|
| Identités documentaires | Référentiel Pactols et correspondances éditoriales AdlFI déjà validées | ARK, libellés, variantes et fiches | Ne jamais inférer de correspondance ARK ↔ COG par simple homonymie, code ou intersection spatiale |
| Identités et états administratifs | COG Insee, millésimes, événements sourcés | Codes, noms et statuts datés ; successions et rattachements | Le code seul ne définit pas une entité à travers le temps ; utiliser type et date |
| Géométries actuelles | Contours administratifs 2026 déjà publiés pour les zones concernées | Couche communale actuelle, repère optionnel | Ne pas présenter 2026 comme contour de 1943/2015/2016 |
| Géométries régionales historiques | Unions de départements GEOFLA 2015 et 2016 qualifiées dans la PR #31 | Polygones des 22 régions 2015 et 13 régions 2016 | Géométrie d'une **édition SIG**, distincte de l'état administratif au 1er janvier |
| Géométries départementales historiques | GEOFLA DÉPARTEMENT 2015 et 2016 | 96 départements par édition, y compris l'effet du transfert 44→49 | Conserver les événements de limites sans supposer la continuité des périmètres |
| Fonds de carte | OpenStreetMap, via Leaflet | Contexte toponymique et géographique | **OSM est contemporain** : ses noms et ses limites d'arrière-plan ne constituent pas une source de géographie historique |

Le moteur cartographique **unique** doit gérer des `L.geoJSON` superposés aux tuiles OSM, et non remplacer la carte Leaflet par le moteur SVG autonome du pilote. La sélection de la couche dépend du couple **(échelon, date)** ; le zoom se contente de modifier l'emprise de la carte et ne change ni le niveau choisi ni le millésime.

Les surcouches régionales et départementales doivent être filtrées par date, et affichées avec une **légende et une notice de provenance propres à la couche**. Les communes historiques doivent continuer d'afficher leurs états COG et mouvements même en absence de polygone correspondant. Lorsqu'on choisit 2015 ou 2016, une couche régionale/départementale sourcée peut être affichée ; lorsqu'on choisit 1943, elle doit rester indisponible tant qu'un contour daté fiable n'a pas été établi.

Les liens parent/enfant sont **datés et typés** : Région → Département → Commune → Arrondissement municipal uniquement lorsque les sources concernées les documentent. Les territoires non comparables (COMER, TAAF, etc.) suivent leurs propres types, sans être forcés dans cette arborescence.

## Commandes et comportement attendu

1. **Zoom sur** : déplacer/recadrer la carte Leaflet (Métropole, Corse, Pays de la Loire, BFC, Caraïbes, océan Indien, Pacifique, etc.) ; ne pas filtrer ou modifier les données par simple choix de cadrage. L'indisponibilité de fonds vectoriels régionaux n'empêche pas d'afficher le fond OSM sur le territoire choisi.
2. **Échelon territorial** : région, département, commune, arrondissement municipal et collectivité/territoire selon disponibilité. Le choix détermine la **couche interactive principale**, non la validité d'une recherche documentaire.
3. **Situation au** : calendrier administratif au 1er janvier (dans le domaine temporel démontré du niveau actif) et événements datés en cours d'année lorsque documentés. Afficher à part la **date d'édition** du contour vectoriel.
4. **Recherche transversale** : requêtes Pactols, libellés historiques COG et identifiants, avec résultats portant explicitement **niveau**, **date**, **état de validation**, provenance et lien de sélection dans la carte. Aucune attribution automatique d'ARK à une ancienne région ou à un département.
5. **Fiche latérale unique** : identité documentaire éventuelle, état administratif à la date, rattachements connus, mouvements, provenance du contour affiché, limites de la représentation. Ne pas supprimer les informations déjà présentes dans la fiche Pactols PACA.
6. **Repère contemporain** : possibilité explicite d'afficher les limites 2026 en surimpression lorsque les limites historiques sont absentes, avec style distinct et message « repère actuel, non historique ». Aucune sélection historique ne doit être inférée du repère.
7. **Accessibilité et performance** : chargement à la demande par niveau/année/emprise ou zone ; gestion de l'annulation des requêtes concurrentes ; rendu adapté aux mobiles et navigation clavier ; attribution OSM conservée et attribution des sources des surcouches visible.

## Ordre de réalisation proposé

**A. Recette d'intégration hors publication**, dans la PR #31 : réutiliser les composants Leaflet, les styles et la logique de recherche de la page communale **chronologique** ; y ajouter les 35 contours régionaux et les 192 états départementaux **sans toucher aux états ni aux identifiants des communes existantes**. Choisir explicitement un affichage dans un modèle HTML de recette qui charge les JSON de données existantes, puis ajouter les sélecteurs orthogonaux.

**B. Tests d'intégrité** : nombre de communes, états et mouvements inchangés à entrée égale ; 103 correspondances PACA intactes ; aucune association Pactols supplémentaire ; région 26/43 en 2015 → région 27 en 2016 ; département 44/49 ; avertissements sur le millésime OSM et les limites d'édition IGN ; aucune dépendance aux GeoJSON simplifiés du pilote SVG pour les mesures SIG.

**C. Après recette visuelle et éditoriale** : migrer les contrôles dans le module Lieux public en évitant deux applications concurrentes, avec liens profonds stables. Le choix exact du chemin public (`/lieux/` et/ou `/lieux/chronologie/`) sera fait à partir du parcours existant, sans casser les URLs actuelles.

**D. Extension progressive** : 2026 et anciens millésimes régionaux qualifiés, arrondissements municipaux PLM, autres régions, DROM puis COMER/TAAF ; à chaque étape, rattachement aux données existantes et validation indépendante.

**Statut :** contrat d'intégration proposé en recette ; aucun changement de `docs/` et aucune modification des alignements ou des états communaux par cet ADR.
