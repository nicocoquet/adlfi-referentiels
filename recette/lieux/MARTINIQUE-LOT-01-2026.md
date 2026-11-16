# Martinique — lot 01 : audit COG / Pactols / contours

**16 novembre 2026. Recette non publiée, préparée après le lot Guyane.**

## Méthode

Le référentiel public contient actuellement **34 communes COG 2026 de Martinique** (codes 97201 à 97234) et **aucun lien Pactols–COG déjà approuvé** pour ces codes. Les données de la page Lieux restent inchangées pendant l'audit.

Le script scripts/auditer_martinique_2026.py reprend les contrôles de la Guyane et réexamine exclusivement :

- [Insee COG 2026](https://www.insee.fr/fr/information/2560452) : v_commune_2026.csv, v_commune_depuis_1943.csv et v_mvt_commune_2026.csv, téléchargés et vérifiés par SHA-256 ;
- [Frantiq / Pactols Lieux](https://github.com/frantiq/PACTOLS), export RDF daté du **22 juillet 2026**, commit 69bf9697e24cefd645a69465bbd271702786285a, SHA-256 3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7 ;
- [Contours administratifs nationaux 2026](https://www.data.gouv.fr/datasets/contours-administratifs), GeoJSON 100 m, SHA-256 4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778.

Le rapport distingue **34 communes actuelles**, **toutes les périodes et mouvements communaux impliquant le département 972**, les concepts Pactols dont l'URI INSEE est explicitement citée et les simples homonymies lexicales. Les géométries 2026 sont contrôlées sans être publiées.

## Alignements : application prudente de la décision éditoriale

La [politique Pactols–COG du référentiel](POLITIQUE-ALIGNEMENT-PACTOLS-COG.md) autorise la validation automatique contrôlée lorsque l'on observe un **skos:exactMatch explicite** d'un concept actif vers un **unique code de commune INSEE 2026**, sans autre code contradictoire, sans dépréciation ou remplacement et avec libellé français compatible.

Le rapport classe chaque commune :

- **ELIGIBLE_SELON_REGLE** : toutes les preuves vérifiées ; la fiche peut être qualifiée en appliquant la politique, après validation de la recette ;
- **A_INSTRUIRE** : absence d'URI, prédicat non exact, libellé incompatible, concept déprécié ou autres ambiguïtés, avec motif explicite.

Les autorités associées à **d'anciens codes communaux** sont consignées séparément, **sans les fusionner automatiquement** avec les communes actuelles. Le nombre d'anciennes autorités, de périodes, de mouvements et de concepts Pactols sera constaté par l'exécution, sans cardinalités postulées à l'avance.

**Aucune correspondance nouvelle n'est injectée sous docs/ pendant cette première recette**, aucune géométrie 2026 n'est attribuée à un état historique et aucune succession administrative n'est inférée d'une homonymie.

## Contrôles

La CI spécialisée lieux-martinique-audit-2026.yml effectue deux exécutions du lot avec les mêmes sources et contrôle leur identité octet à octet. Elle archive une table de revue complète, une table de qualification des 34 liens, les états et mouvements COG, un bilan des 34 géométries et les empreintes des sources/sorties.

Les résultats factuels et les éventuels cas à arbitrer seront reportés ici après l'exécution de la CI.
