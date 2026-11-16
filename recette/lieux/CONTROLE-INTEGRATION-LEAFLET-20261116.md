# Recette de raccordement Leaflet / OpenStreetMap — navigation multi-échelon

**16 novembre 2026. PR n°31, non publiée.**

## Objet

La première recette cartographique SVG vérifiait les archives GEOFLA et les correspondances COG des régions et départements pour **2015 et 2016**. Ce second modèle remplace le moteur de rendu de recette par **Leaflet + fond OpenStreetMap** et y raccorde les **données réellement publiées** du référentiel communal AdlFI.

Il ne remplace ni les fiches Pactols, ni les états communaux historiques existants. Il ne modifie aucun document public sous `docs/`.

## Contrat du parcours

| Commande | Effet attendu | Effet interdit |
|---|---|---|
| **Zoom sur** | Cadrer la carte OSM sur Métropole, BFC, Pays de la Loire, Corse, PACA, Antilles–Guyane, océan Indien, Pacifique, Atlantique Nord ou TAAF | Ne modifie ni la date ni l'échelon ; ne fabrique pas de polygones ultramarins |
| **Échelon territorial** | Choisir la couche interactive Région, Département, Commune, Arrondissement municipal ou Collectivité/territoire | Ne crée ni codes COG, ni autorités Pactols |
| **Situation au 1er janvier** | Choisir 1943–2026 ; affichage des états communaux selon les données existantes ; géométries région/département uniquement pour 2015–2016 ; contours communaux 2026 uniquement au présent | Ne remplace pas une géométrie historique absente par celle de 2026 |
| **Recherche** | Noms/identifiants des quatre corpus communaux et des régions/départements 2015–2016, ARK validés | Ne transfère pas une correspondance Pactols validée en 2026 vers une date antérieure |
| **Repère actuel** | Affichage volontaire de contours communaux **2026** de quatre régions, comme surcouche contemporaine distincte | Ne présente pas cette couche comme limite historique |

**Les tuiles OSM sont toujours contemporaines**, même lorsque le menu affiche un état administratif passé. Toute géométrie éditorialement représentée comme historique vient exclusivement d'un jeu SIG millésimé qualifié.

## Sources effectivement branchées

- `docs/data/lieux-chronologie/cog-{paca,corse,pdl,bfc}.json` (quatre corpus communaux 1943–2026, **sans géométrie historique**) ;
- `docs/data/lieux-chronologie/contours-2026-{paca,corse,pdl,bfc}.geojson` (quatre couches communales contemporaines) ;
- `docs/data/lieux.json` (103 autorités Pactols PACA validées au **18/10/2026**) ;
- `docs/assets/lieux-chronologie-core.js` (**code original** des fonctions de recherche et de consultation COG, incorporé tel quel) ;
- `recette/AdlFI_Lieux_Multiechelon_2015_2016.html` produit et contrôlé par le générateur précédent : **22 régions + 96 départements 2015** et **13 régions + 96 départements 2016**.

Les neuf documents communaux sont copiés **sans réécriture de leur contenu interprété** dans un document de recette autonome (à l'exception de leur encapsulation JSON), avec conservation de leurs empreintes SHA-256 source dans le rapport. Les géométries originelles IGN, leur archive et les rapports d'audit restent disponibles séparément en artefact GitHub Actions ; la version simplifiée à 100 m reste une couche d'affichage.

## Fichiers

- `scripts/construire_vue_lieux_leaflet_integree.py` : postprocesseur contrôlé et lecteur des sources publiées ;
- `recette/lieux/vue-lieux-leaflet-integree-modele.html` : modèle Leaflet, contrôles indépendants, recherche et fiches ;
- `tests/test_construire_vue_lieux_leaflet_integree.py` : tests de non-régression du référentiel et des garde-fous ;
- Dans l'artefact de recette CI, `recette/AdlFI_Lieux_Leaflet_Integration_2015_2016.html` et `recette/rapport-integration-leaflet.json`.

## Vérifications en CI

- Réemploi **sans altération** des quatre corpus communaux existants, de leurs géométries 2026 et des **103 ARK PACA**.
- Contrôle des éditions 2015/2016 et des **227 états régionaux/départementaux** ; aucune rétroprojection depuis 2026.
- Refus des correspondances Pactols sans validation 2026 ou introduites hors du pilote PACA.
- Refus d'une sortie sous `docs/` ; aucune mutation des données sources et aucun alignement supplémentaire.
- Production deux fois, comparaison HTML et rapport **octet par octet**.

## Limites explicites

- La preuve du raccordement des données est **technique et non une validation éditoriale** des nouvelles appartenances.
- Les régions/départements hors 2015 et 2016 sont en attente de géométries historiquement qualifiées.
- Les communes 1943–2025 ont une **fiche d'état administratif mais pas de contour historique** dans le corpus publié. Les quatre couches 2026 peuvent servir de repère clairement signalé et opt-in.
- Les arrondissements municipaux et les collectivités/territoires ultramarins restent à intégrer selon le travail de validation des PR voisines. En revanche, **leur cadrage OSM fonctionne** dès cette recette.
- Il s'agit d'une **recette d'intégration** : ne pas remplacer la page publique `/lieux/` tant que les fiches, les performances au niveau communal et la navigation n'ont pas été validées avec les utilisateurs.
