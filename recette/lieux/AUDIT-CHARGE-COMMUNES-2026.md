# Lieux — audit de charge des contours communaux 2026

**19 novembre 2026 — audit reproductible, non publiant**  
Suivi : [#152](https://github.com/nicocoquet/adlfi-referentiels/issues/152).  
Première exécution réelle réussie : [GitHub Actions #44534194986](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44534194986).

## Méthode

Commande, depuis la racine du dépôt :

```bash
python3 scripts/auditer_charge_carte_lieux.py --sortie /tmp/lieux-charge-2026.json
```

Le script inspecte les **huit fichiers GeoJSON effectivement chargés** par `chargerCommunes2026()` dans `docs/assets/lieux-multiechelon.js` au niveau « Commune », année 2026. Il mesure l'effectif de `Feature`, les positions GeoJSON de toutes les géométries, le poids brut, le poids gzip **simulé** (compression niveau 9, horodatage nul) et l'empreinte SHA-256 de chaque fichier. Il vérifie les codes, la structure Polygon/MultiPolygon, l'emprise WGS84, le millésime lorsqu'il est explicité et la cohérence des effectifs de provenance. Il ne crée aucun alignement et n'altère aucun contour.

**Attention :** ces chiffres n'évaluent ni la latence réseau réelle (compression HTTP dépend du serveur), ni la consommation mémoire JavaScript/Leaflet, ni le temps de premier rendu Chromium.

## Résultats sur le commit de recette du 19 novembre

| Couche | Contours | Sommets (positions GeoJSON) | Octets bruts | Octets gzip simulés |
|---|---:|---:|---:|---:|
| PACA | 946 | 53 746 | 1 114 302 | 273 539 |
| Corse | 360 | 19 925 | 414 226 | 99 708 |
| Pays de la Loire | 1 228 | 71 698 | 1 537 225 | 376 980 |
| Bourgogne-Franche-Comté | 3 685 | 148 296 | 3 309 019 | 785 146 |
| Cinq DROM | 129 | 24 326 | 484 150 | 123 377 |
| Saint-Pierre-et-Miquelon | 2 | 362 | 8 285 | 2 635 |
| Nouvelle-Calédonie | 32 | 14 243 | 295 272 | 74 549 |
| Polynésie française | 28 | 4 250 | 98 790 | 23 503 |
| **Total** | **6 410** | **336 846** | **7 261 269** | **1 759 437** |

Le sous-ensemble métropolitain représente **6 219 communes** ; l'outre-mer publié **191 contours**. Ces comptes concernent des géométries, non le taux d'alignement Pactols–COG. Ils n'incluent pas les 20 communes polynésiennes en attente ni Dumbéa, non publiées pour des motifs documentés.

La Bourgogne-Franche-Comté concentre à elle seule environ **46 % du poids brut** et **44 % des sommets**. Elle constitue donc un candidat adapté aux premiers essais de chargement différé.

## Conséquence architecturale

Le chargement complet des huit sources demeure gérable à la date de cet audit ; l'étendre mécaniquement à toutes les communes françaises serait une mauvaise option. Pour préserver les performances, la prochaine tranche devra :

1. **Mesurer en navigateur**, sur machine comparable et à vues fixes, le délai d'affichage, le nombre de requêtes, les opérations Leaflet et le comportement au changement de zone et de millésime. Ne pas annoncer des gains de mémoire avant ces essais.
2. Introduire un **registre des sources régionales** contrôlant COG, GeoJSON, index Pactols et disponibilité. Cette description ne doit pas créer de code métier spécial pour chaque nouvelle région.
3. Charger les **géométries à la demande**, selon l'emprise visible et la sélection documentaire, avec cache et prévention des réponses obsolètes. Définir explicitement la représentation des communes au zoom national au lieu de masquer silencieusement des limites.
4. Préserver les principes d'identité : codes COG `TYPECOM=COM`, ARK Pactols et géométries indépendants, aucune attribution d'un contour 2026 à une année historique.
5. Intégrer les nouvelles régions selon une priorité fondée sur les **9 928 autorités documentaires AdlFI** et, si disponibles, les occurrences des notices. Ces exports n'étant pas versionnés comme entrée exploitable du dépôt, **aucun classement régional par intérêt AdlFI n'est encore établi**.

L'instruction des arrondissements municipaux de Paris, Lyon et Marseille relève d'une tranche distincte. La Polynésie française demeure ajournée conformément au choix éditorial du 18 novembre.

## Contrôles

- Quatre tests unitaires de mesures, cohérence d'effectifs, codes dupliqués, millésime et coordonnées.
- Workflow dédié `Lieux — audit de charge des contours 2026` ; artefact `lieux-audit-charge-2026`.
- Vérifications générales du référentiel.
- Rapport écrit **hors de `docs/`**, sans changement de la carte et sans publication de nouveaux contours.
