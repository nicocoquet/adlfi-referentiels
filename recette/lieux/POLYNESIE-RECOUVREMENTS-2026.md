# Polynésie française — recouvrements intra-couche ISPF

**17 novembre 2026 — recette distincte des validations d'identifiants (PR 80).**

## Sources et méthode

L'archive GeoJSON officielle de l'ISPF, [limites géographiques administratives](https://www.data.gouv.fr/datasets/limites-geographiques-administratives), SHA-256 `6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62`, contient trois couches : 48 communes, 116 unités fines et 119 îles. La PR 80 a établi une correspondance sans perte des identifiants et la validité topologique OGC individuelle de ces 283 géométries.

Le script `scripts/auditer_recouvrements_ispf_polynesie.py` confronte **chaque paire pertinente à l'intérieur d'une même couche**, via un index spatial STRtree (Shapely 2.1.2). Trois situations sont différenciées :

- **Contacts de frontière** (`touches`) : deux polygones peuvent avoir une limite commune sans recouvrement intérieur ;
- **Recouvrements surfaciques** (`intersection.area > 0`) : consignés individuellement par leur code ISPF et la relation géométrique (égalité, inclusion ou recouvrement partiel), **à instruire** ;
- **Autres intersections sans aire plane** : signalées séparément, sans les qualifier d'erreurs.

Les coordonnées proviennent de la source en **EPSG:4687** ; les nombres en degrés ne sont jamais convertis en surfaces métriques ou distances. Aucun seuil d'aire n'est introduit : même de très petits recouvrements font l'objet d'une alerte, pas d'une correction.

## Restrictions de preuve

Le travail n'effectue **pas** de recouvrement « îles vs communes » ou « communes associées vs communes » : ces superpositions sont attendues puisqu'elles correspondent à des découpages différents. Il n'utilise pas `make_valid`, ne transforme pas les coordonnées, ne simplifie pas les polygones et ne produit aucun contour public.

Des tests complémentaires seront nécessaires pour :

1. comparer explicitement chaque commune associée au contour de son parent ;
2. caractériser les écarts entre limites communes (slivers), en définissant une précision géodésique institutionnelle ;
3. distinguer les géométries des îlots Maria et du cas Tahaa, puis contrôler la date de validité de chaque source ;
4. qualifier d'éventuels recouvrements à l'aide d'un fond de référence indépendant (GEO PF/DAF) et de la documentation du producteur.

**Statut :** `RECETTE_NON_VALIDANTE`. Rapports et paires recensées dans un artefact CI hors `docs/`, aucun nouvel ARK, aucune autorité nouvelle, aucune modification de la carte publiée. Fusion uniquement après consultation des résultats effectifs de CI.
