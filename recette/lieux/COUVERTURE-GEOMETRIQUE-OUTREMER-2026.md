# Lieux — contrôle de couverture des géométries ultramarines 2026

**16 novembre 2026 · PR #30 · recette seule, aucune publication.**

## Décision d'interface

Le sélecteur public « Échelon territorial » est limité à **Région / Département / Commune** (PR #41, fusionnée le 16 novembre 2026). Cette simplification ne supprime aucune entité administrative des données.

Les collectivités et subdivisions ultramarines restent indexées sous leurs types d'origine ; la présence d'un objet COG dans le fichier géographique « communes » ne permet pas à elle seule de lui attribuer le statut de commune de droit commun.

## Données et provenance

- **États administratifs au 1er janvier 2026 :** [Insee, COG 2026](https://www.insee.fr/fr/information/8740222), fichiers v_commune_2026.csv, v_commune_comer_2026.csv, v_comer_2026.csv.
- **Contours datés du 4 mai 2026 :** [data.gouv.fr, Contours administratifs](https://www.data.gouv.fr/datasets/contours-administratifs), fichier communes-100m.geojson.gz (GeoJSON WGS84, généralisation 100 m, licence ODbL).
- La provenance des contours est **mixte** : produits IGN, OSM pour des COM, données géographiques spécifiques à la Polynésie française et à la Nouvelle-Calédonie. Il est inexact d'étiqueter tous les contours comme « IGN ».

L'audit compare **233 identités typées** : 129 DROM:COM, 85 COMER:COM, 5 COMER:DIS, 3 COMER:CIR, 1 COMER:CPT, 1 COMER:CDM et 9 COMER:TERRITOIRE.

Les **212 communes** constituant le lot éditorial prioritaire sont un sous-ensemble : 129 DROM, 48 Polynésie française, 33 Nouvelle-Calédonie et 2 Saint-Pierre-et-Miquelon. Les zonages COM de Saint-Martin et Saint-Barthélemy sont volontairement instruits à part ; ils ne sont pas ajoutés artificiellement aux 212.

## Contrôle mis en place

Le script scripts/auditer_contours_outremer_2026.py croise les identifiants exacts des tables 2026 avec la couche « communes » ; il ne rapproche aucun ARK Pactols. Pour chaque entité :

1. présence ou absence du code dans la source cartographique ;
2. doublons de codes éventuels ;
3. type géométrique Polygon / MultiPolygon et validité topologique Shapely, **sans réparation automatique** ;
4. emprise longitudinale supérieure à 180° comme **alerte de contrôle**, non comme erreur certaine, pour l'antiméridien ;
5. nature de zonage COG et territoire de rattachement, sans attribuer un statut de commune à DIS, CIR, CPT ou CDM.

Les 9 collectivités COMER:TERRITOIRE sont **non évaluées** dans cette couche de communes : même si toutes leurs subdivisions avaient une géométrie, leur union ne serait pas une frontière institutionnelle officiellement attestée.

La comparaison aboutit aux statuts descriptifs PRESENTE_VALIDE_A_QUALIFIER, PRESENTE_INVALIDE, ABSENTE_DU_FICHIER_COMMUNES, DOUBLON_CODE_DANS_SOURCE ou NON_EVALUE_TERRITOIRE_SANS_COUCHE_DEDIEE. Le premier signifie seulement que le polygone lu est structurellement et topologiquement utilisable ; **il ne valide ni son identité juridique, ni sa source locale, ni ses limites historiques**.

## Reproduction

CI : .github/workflows/audit-lieux-contours-outremer-2026.yml.

1. Télécharger les deux sources officielles ; contrôler SHA-256, dont les empreintes COG déjà établies en PR #30.
2. Exécuter les tests synthétiques, avec Shapely.
3. Générer deux fois, de manière strictement identique, controle_233_cibles.csv et rapport_couverture_2026.json dans un dossier temporaire.
4. Conserver un artefact **de recette** dans GitHub Actions pendant 30 jours ; aucune image vectorielle source et aucun CSV candidat ne sont ajoutés sous docs/.

## Résultats constatés — CI réussie du 16 novembre 2026

[Audit spécialisé n°43894284872](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43894284872) : tests synthétiques, acquisition des sources, contrôle des 233 cibles, double génération identique et artefact de recette réussis.

| Nature COG | Entités | Présentes et topologiquement valides | Invalides | Absentes | Non évaluées comme territoire |
|---|---:|---:|---:|---:|---:|
| DROM:COM | 129 | 129 | 0 | 0 | 0 |
| COMER:COM | 85 | 83 | **2** | 0 | 0 |
| COMER:DIS (TAAF) | 5 | 5 | 0 | 0 | 0 |
| COMER:CIR (Wallis-et-Futuna) | 3 | 3 | 0 | 0 | 0 |
| COMER:CPT (Clipperton) | 1 | 1 | 0 | 0 | 0 |
| COMER:CDM (Île des Faisans) | 1 | 0 | 0 | **1** | 0 |
| COMER:TERRITOIRE | 9 | 0 | 0 | 0 | **9** |
| **Total** | **233** | **221** | **2** | **1** | **9** |

**Cas à instruire individuellement :**

- **Tahaa**, code COMER:COM:98745 (Polynésie française) : MultiPolygon présent, mais topologiquement invalide dans la source 2026.
- **Dumbéa**, code COMER:COM:98805 (Nouvelle-Calédonie) : MultiPolygon présent, mais topologiquement invalide dans la source 2026.
- **Île des Faisans**, code COMER:CDM:98101 : pas de Feature correspondante dans le GeoJSON de communes. L'absence n'est pas une preuve d'inexistence de géométrie dans une autre source.

**Empreintes SHA-256 contrôlées :**

- communes-100m.geojson.gz : 4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778
- v_commune_2026.csv : 7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3
- v_commune_comer_2026.csv : 9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8
- v_comer_2026.csv : d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed

## Diagnostic ciblé des deux multipolygones invalides

[Exécution spécialisée n°43895384451](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43895384451), réussie sur l'extension du diagnostic.

| Code | Motif Shapely dans la source | Type après make_valid sur copie | Écart de surface planaire |
|---|---|---|---:|
| 98745 — Tahaa | Self-intersection[-151.447423287671 -16.5649232876712] | MultiPolygon | 0,001741883 % |
| 98805 — Dumbéa | Self-intersection[166.4384 -22.1726] | MultiPolygon | 0,0 % à la précision affichée |

L'écart est un **ratio de surfaces planaires en coordonnées géographiques**, non une mesure géodésique. Un écart faible ne suffit pas à approuver un contour ou son appartenance territoriale. Aucune sortie réparée n'a été introduite dans les fichiers géographiques publiés.

Une vérification explicite de la validité des multipolygones issus de make_valid est désormais testée ; cette opération reste **strictement diagnostique et non publiable**.

## Comparaison avec les producteurs géographiques territoriaux

**Tahaa (98745) — Polynésie française.** Un FeatureServer public Te Fenua est identifiable :

- Service : https://services.arcgis.com/L4H4rU26VyhEF588/ArcGIS/rest/services/Communes_de_la_Polyn%C3%A9sie_fran%C3%A7aise_%28Tefenua%29/FeatureServer/0
- Champs d'identité de la couche : com_nom, com_id, date_maj_donnee, source. Attention : com_id est un **identifiant de source**, à ne pas assimiler au COG 98745 sans table de correspondance.
- La couche est en EPSG:3857 et permet un retour GeoJSON en EPSG:4326, mais la date de mise à jour du service n'est pas la date d'effet de chaque limite.
- Source complémentaire : jeu « Géographie administrative de la Polynésie-française » (Section Cadastre-Topographie, data.gouv.fr, 28 février 2022).

**Dumbéa (98805) — Nouvelle-Calédonie.** Couche publique du Gouvernement de Nouvelle-Calédonie / DITTT :

- Service : https://services1.arcgis.com/TZcrgU6CIbqWt9Qv/arcgis/rest/services/limites_terrestres/FeatureServer/0
- Champs : nom, code_com ; projection source RGNC91-93 (EPSG:3163). Le code du service doit être vérifié comme identifiant COG actuel avant d'utiliser une correspondance.
- Généalogie annoncée : limites Dumbéa et Grand Nouméa révisées le 2 mars 2022, jeu mis à jour le 28 octobre 2024 ; date de livraison et validité historique non confondues.
- Source complémentaire : BDADMIN-NC « Limites administratives » du Gouvernement de Nouvelle-Calédonie.

**Île des Faisans (98101).** La BD TOPO IGN (descriptif de contenu v3.4, octobre 2024, section 6.7 p. 47) définit une classe administrative distincte **condominium** de géométrie MultiPolygone, qui correspond explicitement à l'île sur la Bidassoa. Ce référentiel est à privilégier pour la récupération d'un contour identifié, plutôt que de produire un polygone à partir des communes voisines ; le rattachement au code de zonage COG CDM 98101 doit être contrôlé **explicitement**.

Référence IGN : https://geoservices.ign.fr/sites/default/files/2025-01/DC_BDTOPO_3-4.pdf

**Recette comparative ajoutée :** scripts/comparer_sources_geometrie_outremer.py, tests/test_comparer_sources_geometrie_outremer.py et .github/workflows/lieux-comparer-sources-outremer.yml. L'outil capture les deux sources ArcGIS **une fois**, fige leurs réponses et compare chacune au contour national du 4 mai 2026, puis répète la comparaison de manière reproductible. Les mesures de surface, intersection et différence symétrique sont calculées dans EPSG:6933 (projection équivalente). Les réparations Shapely, lorsqu'elles sont nécessaires, restent des **copies de diagnostic**. Aucun alignement Pactols ou contour approuvé n'est généré.

### Première comparaison effective — CI n°43898929958

[Exécution GitHub Actions](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43898929958) **réussie** : source nationale vérifiée par SHA-256, données territoriales acquises, tests, double comparaison identique et artefact temporaire.

| Code COG | Géométrie territoriale | Géométrie nationale | Surface territoriale EPSG:6933 | Surface nationale EPSG:6933 | Différence symétrique | Recouvrement du polygone territorial |
|---|---|---|---:|---:|---:|---:|
| 98745 — Tahaa | **Invalide** | **Invalide** | 90,207751 km² | 89,980115 km² | 3,132074 km² | 98,137793 % |
| 98805 — Dumbéa | **Valide** | **Invalide** | 251,408562 km² | 251,219692 km² | 3,097760 km² | 99,346357 % |

Pour permettre la différence symétrique sur des géométries initialement invalides, les deux comparaisons utilisent **make_valid seulement en mémoire, sur des copies de diagnostic**. Les résultats n'attestent pas la continuité légale des limites ; les écarts reflètent aussi des différences de généralisation et des dates de production.

**Identifiants et provenance fournis par les services :**
- Te Fenua, Tahaa : com_nom=TAHAA, com_id=45, ObjectId=35 ; date_maj_donnee=« Date non connue », source=« Source inconnue ». Le code interne 45 n'est **pas** un code INSEE complet et la confirmation du référent reste ouverte. SHA-256 du retour GeoJSON : 3f13ad59acbffaee4e87f1ca57ec5eec0f96604b2dc0032704363fc70884b4e4.
- DITTT, Dumbéa : nom=DUMBEA, code_com=98805, objectid=10 ; code COG concordant dans la couche territoriale. SHA-256 du retour GeoJSON : b3b5d264d97aa71647182ea0d199e6c010bd62b9444bf96c09a9ee4559e12cb6.

**Arbitrage technique provisoire :** Dumbéa dispose d'une géométrie externe valide à évaluer pour une éventuelle adoption ; Tahaa reste non résolue puisqu'une seconde source est elle-même invalide. Aucune substitution automatique. Contrôler impérativement les deux écarts spatiaux et les emprises avant une décision de publication.

**Attention aux millésimes :** la comparaison croise plusieurs éditions ; elle ne démontre pas que les sources territoriales décrivent précisément le 1er janvier 2026. Les résultats métriques doivent être interprétés à cette lumière, et la présence d'un contour n'implique pas une modification autorisée de la carte publique.

## Archive administrative polynésienne de 2022 — second contrôle indépendant à instruire

Une archive publiée par la Section Cadastre-Topographie de Polynésie française a été retrouvée via le jeu « Géographie administrative de la Polynésie-française » (data.gouv.fr). Ressource principale : fichier ZIP de 14,6 Mo intitulé « Limite administrative des communes et communes associées » (28 février 2022), URL fournie par le portail de téléchargement :

https://static.data.gouv.fr/resources/geographie-administrative-de-la-polynesie-francaise/20220228-205331/loc-commune-associee.zip

Outils ajoutés : scripts/inventorier_source_polynesie_2022.py, tests/test_inventorier_source_polynesie_2022.py et workflow lieux-inventaire-polynesie-2022.yml. La CI doit extraire **en mémoire** les attributs, l'emprise documentaire, le système de coordonnées inscrit dans les fichiers .prj et rechercher les mentions exactes de Tahaa. Les identifiants locaux (IDCom, etc.) ne sont pas transformés automatiquement en codes COG. Un inventaire n'est **pas** encore une validation de la géométrie de Tahaa ni une preuve d'indépendance par rapport à Te Fenua.

**En attente de confirmation de la CI d'inventaire et, le cas échéant, d'un audit topologique de la géométrie alternative.** L'archive complète ne sera pas intégrée au dépôt ni au site.

## Étapes avant publication cartographique

- Examiner les géométries absentes, invalides ou traversant potentiellement l'antiméridien ; identifier des sources alternatives, notamment pour TAAF, Wallis-et-Futuna, Clipperton et Île des Faisans.
- Vérifier les contours des 212 communes prioritaires au millésime précis, puis les 2 zonages COMER particuliers de Saint-Martin/Saint-Barthélemy.
- Définir la sélection dans la recherche textuelle pour les territoires COMER:TERRITOIRE et les zonages non communaux **sans ajout de quatrième échelon au sélecteur**.
- Introduire les seuls alignements Pactols–COG décidés éditorialement, sans extrapolation temporelle.
- Ne jamais afficher une géométrie 2026 comme celle d'une situation antérieure.

Aucune correction des sources, aucune géométrie publiée, aucun alignement créé par cette tranche.
