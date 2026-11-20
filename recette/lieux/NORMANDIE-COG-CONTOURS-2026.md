# Lieux — Normandie, préparation des états COG et contours communaux 2026

**20 novembre 2026 — prépublication, aucun contour affiché dans l'interface au stade de la recette.**

Suivi : [#152](https://github.com/nicocoquet/adlfi-referentiels/issues/152). Le chargeur régional à la demande est déjà déployé par [#157](https://github.com/nicocoquet/adlfi-referentiels/pull/157). Correspondances Pactols–COG 2026 : **16** validées dans les deux registres indépendants [#156](https://github.com/nicocoquet/adlfi-referentiels/pull/156) et [#160](https://github.com/nicocoquet/adlfi-referentiels/pull/160) ; aucune n'est créée ou rétroprojetée ici.

## Sources officielles contrôlées

- **COG Insee 2026**, `v_commune_2026.csv`, `v_commune_depuis_1943.csv`, `v_mvt_commune_2026.csv`, contrôlés par les empreintes SHA-256 déjà figées dans `scripts/preparer_lieux_chronologie_4regions.py`.
- **Contours administratifs Etalab/IGN, millésime 2026**, `communes-100m.geojson.gz`, édition **4 mai 2026**, <https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/communes-100m.geojson.gz>. Empreinte publiée et déjà vérifiée par le pilote quatre régions : `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778`.
- Les **2 644 communes** sont sélectionnées avec `REG=28` **et** `TYPECOM=COM`, et leurs départements `14`, `27`, `50`, `61`, `76` sont contrôlés. Les communes déléguées et associées ne deviennent pas des communes autonomes.
- Le générateur réutilise le modèle temporel déjà utilisé par PACA, Corse, PDL et BFC : les codes historiques sont inclus à titre **documentaire**, selon les préfixes des cinq départements. Cela ne constitue **pas** une restitution des frontières normandes historiques.

## Génération

`scripts/preparer_lieux_normandie_2026.py` exécute le constructeur commun existant, limité à la région Normandie. Le code partagé n'est pas modifié. Les trois sorties reproductibles prévues sont :

- `cog-normandie.json` : périodes et mouvements COG attestés depuis 1943, observations des communes déléguées/associées au **seul millésime 2026**, **aucun alignement Pactols inclus**, aucune géométrie historique ;
- `contours-2026-normandie.geojson` : géométries issues du fichier Etalab 2026/100 m, libellés repris du COG officiel, statut géométrique **sans ARK inféré**, géométries exclusivement contemporaines ;
- `rapport-normandie-recette.json` : cardinalités, empreintes sources et sorties, nombres de sommets et typologie des polygones, avertissements d'usage et statut non activé.

Le générateur refuse toute source dont le SHA diffère, un doublon de code, un rattachement COG 2026 incompatible, une géométrie vide ou non polygonale, un anneau ouvert, une coordonnée non finie ou incohérente avec l'emprise normande, et toute différence entre les 2 644 codes du COG courant et les 2 644 contours. **Une géométrie manquante bloque la publication plutôt que d'être fabriquée à partir d'une autre année.**

La CI produit deux jeux indépendants et les compare octet à octet, puis archive les résultats pour examen. Les scripts peuvent ensuite être utilisés pour versionner les deux données dans `docs/data/lieux-chronologie/` avec leurs empreintes, une fois le contrôle terminé.

## Règles à préserver lors de l'intégration au site

1. **Aucune activation immédiate** : `docs/assets/lieux-multiechelon.js` ne doit consommer les nouveaux fichiers qu'après validation cartographique, cohérence du modèle COG et recette Chromium.
2. La sélection « Commune » avec `année=2026` affichera alors des contours Etalab/IGN contemporains. Avec `année<2026`, ils ne pourront apparaître qu'en **repère 2026 explicitement distingué**, jamais comme frontière historique.
3. Les 16 correspondances Pactols déjà validées doivent être raccordées par un registre **séparé** des couches géométriques. Le nombre total de communes 2026 et la proportion d'ARK homologués sont deux indicateurs indépendants.
4. Le chargement progressif par vue de [#157](https://github.com/nicocoquet/adlfi-referentiels/pull/157) doit être conservé : au zoom national, il sera nécessaire d'évaluer la surcharge avant d'étendre de quatre à cinq grandes couches métropolitaines.
5. Les limites Etalab sont des **références cartographiques généralisées**, non des plans juridiquement homologués ni des restitutions topographiques historiques.

## Points de vigilance

- **Bourgvallées (50546)** possède au moins deux créations COG, en 2016 puis en 2019 ; l'identité du concept Pactols de 2016 n'est pas reportée sur la géométrie 2026.
- **Breteuil (27112)** et **Isigny-sur-Mer (14342)** restent sans alignement 2026 validé, en raison des collisions de concepts et références externes décrites dans le lot 02.
- **Port-Bail-sur-Mer (50412)** reste aussi à instruire et ne doit pas hériter de l'ARK de Portbail.
- Les géométries officielles simplifiées nécessiteront un contrôle de validité topologique et une recette navigateur avant exposition au public.

**Statut de cette tranche : recette de données.** Aucune augmentation de couverture cartographique publique ne doit être annoncée avant une PR d'activation distincte et la vérification de GitHub Pages.
