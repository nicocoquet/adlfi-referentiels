# Index public de recherche COG ultramarin — 2026

**Recherche documentaire uniquement, sans géométrie publiée.**

## Source et reproduction

Le fichier recherche-2026.json est dérivé de l'artefact [GitHub Actions n°43909408130](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43909408130), produit sur la PR 30 à partir du COG INSEE 2026 et du diagnostic cartographique national (édition du 4 mai 2026). L'artefact contient **212 communes, 21 autres entités typées et un manifeste de provenance**.

Le script scripts/extraire_index_public_outremer_2026.py reproduit cette projection à partir du ZIP et la compare **octet pour octet** au fichier public. Commande : python3 scripts/extraire_index_public_outremer_2026.py --artefact CHEMIN/artefact.zip --validations recette/lieux/GUYANE-VALIDATIONS-PACTOLS-COG-2026.csv --validations recette/lieux/MARTINIQUE-VALIDATIONS-PACTOLS-COG-2026.csv --validations recette/lieux/GUADELOUPE-VALIDATIONS-PACTOLS-COG-2026.csv --validations recette/lieux/REUNION-VALIDATIONS-PACTOLS-COG-2026.csv --verifier docs/data/lieux-outremer/recherche-2026.json. Le registre de validations reste versionné séparément du socle initial : son ajout n'altère pas l'artefact de recette initial.

L'index public conserve : les libellés et codes communaux, les **128 ARK Pactols–COG approuvés pour 2026** (16 Mayotte, 22 Guyane, 34 Martinique, 32 Guadeloupe et 24 La Réunion), un ARK confirmé dont le lien reste à valider, le signalement topologique de Tahaa et Dumbéa, les 21 identités COMER distinctes. Il **ne contient aucune géométrie**.

## Précautions de modélisation

- La situation COG au 1er janvier 2026 est distincte de la date de livraison des contours (4 mai 2026).
- **128 correspondances Pactols–COG sont validées au millésime 2026** : les 16 décisions déjà approuvées à Mayotte, les 22 décisions documentées à Guyane, les 34 décisions documentées à Martinique, les 32 décisions documentées à Guadeloupe et les 24 décisions documentées à La Réunion (voir la politique de validation sous `recette/lieux/POLITIQUE-ALIGNEMENT-PACTOLS-COG.md` et la table `recette/lieux/GUYANE-VALIDATIONS-PACTOLS-COG-2026.csv` et `recette/lieux/MARTINIQUE-VALIDATIONS-PACTOLS-COG-2026.csv` et `recette/lieux/GUADELOUPE-VALIDATIONS-PACTOLS-COG-2026.csv` et `recette/lieux/REUNION-VALIDATIONS-PACTOLS-COG-2026.csv`). **Le Port (97407)** est désormais validé pour le COG 2026 après contrôle de son `skos:exactMatch` univoque ; **Dembeni (97607)** conserve son ARK littéral confirmé, mais la correspondance COG demeure non validée et son ARK n'est pas indexé en tant que lien approuvé.
- Une géométrie topologiquement valide n'est pas un contour adopté : aucun polygone n'est diffusé par cet index, y compris pour les 210 communes possédant une géométrie nationalement disponible.
- Les 21 entités non communales sont accessibles par la recherche globale mais **pas** par un quatrième niveau territorial.
- Les **242 observations historiques** du dossier d'audit ne sont pas assimilées à des fiches intemporelles : cette projection couvre uniquement **2026**, sans rétroprojection.
- Le pilote **PACA de 103 autorités Pactols** n'est pas modifié.

## Conséquences pour l'interface

La sélection d'une fiche COG 2026 affiche ses informations et, si approprié, le lien Pactols approuvé. Elle ne dessine pas automatiquement de limite communale. Lorsque le curseur est placé sur une année différente de 2026, la fiche **reste explicitement datée de 2026** et signale l'absence de qualification historique. La carte conserve les contours déjà qualifiés, limités à quatre régions pilotes pour les communes.

Le sélecteur visible conserve **Région / Département / Commune**.


## Couche géométrique DROM distincte (2026)

L'index `recherche-2026.json` reste **sans polygones** ; une nouvelle couche `contours-communes-drom-2026.geojson` contient uniquement les **129 communes des cinq DROM** au COG 2026, à la généralisation 100 m de l'édition du 4 mai 2026.

La source géométrique et les codes sont contrôlés avant publication par `scripts/publier_contours_drom_2026.py`. Les contours ne valident pas les ARK Pactols, et inversement. Pour les années anciennes, cette couche ne peut être affichée que comme **repère 2026 optionnel**.

La Polynésie, la Nouvelle-Calédonie et Saint-Pierre-et-Miquelon restent hors de ce lot ; Tahaa (98745) et Dumbéa (98805) conservent leurs réserves topologiques.


## Saint-Pierre-et-Miquelon : contours de référence 2026

La couche cartographique autonome `contours-communes-spm-2026.geojson` fournit **Miquelon-Langlade (97501)** et **Saint-Pierre (97502)**, datés du COG au 1er janvier 2026, géométries Etalab du 4 mai 2026, généralisation 100 m. Ces tracés ont subi un contrôle de validité topologique sans réparation et sont indépendants des deux correspondances Pactols déjà approuvées.

Il ne s'agit pas de limites juridiquement homologuées ni de restitutions historiques ; hors de 2026, elles ne peuvent apparaître que comme repères contemporains facultatifs. Les géométries de Polynésie et de Nouvelle-Calédonie restent à instruire.


## Nouvelle-Calédonie : 32 contours communaux de référence 2026

La couche autonome `contours-communes-nc-2026.geojson` rassemble **32 des 33 communes COG 2026** de Nouvelle-Calédonie. Elle provient de l'édition Etalab du **4 mai 2026**, généralisation **100 m** (SHA-256 de l'archive : `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778`). Codes et libellés sont confrontés à `recherche-2026.json`.

**Dumbéa (98805)** est explicitement exclue : son multipolygone national est auto-intersectant dans cette édition. Aucune réparation géométrique ni limite de remplacement n'est inférée. **Poya (98827)** reste une commune unique, dont le contour ne présume aucun rattachement provincial exclusif.

Les 32 géométries sont des **repères cartographiques contemporains** : validité topologique vérifiée, mais aucune homologation juridique des limites ni restitution historique. Les alignements Pactols–COG demeurent indépendants de cette couche. Pour les millésimes antérieurs, l'affichage facultatif du repère 2026 est distinct des limites historiques non qualifiées.

Recette : `scripts/preparer_contours_nouvelle_caledonie_2026.py` ; vérification de la reproductibilité, contrôles Node.js, Chromium et non-régressions en CI. Suivi : issue #105 et PR #113.


## Polynésie française — lot de 28 contours cartographiques de référence 2026

Le fichier autonome `contours-communes-pf-28-2026.geojson` contient **28 des 48 communes COG au 1er janvier 2026**, sélectionnées dans la couche Etalab du 4 mai 2026, généralisation 100 m. Les sources Etalab et les rapports d'audit sont contrôlés par empreinte SHA-256, sans correction ni géométrie déduite. Les codes et noms sont confrontés à l'index COG publié. Les géométries retenues sont topologiquement valides selon GEOS.

**Critères de sélection éditoriaux et reproductibles :** IoU (intersection/union) ≥ 0,95 entre les références territoriales ISPF et GEO PF diffusées en 2022, ≥ 0,90 entre Etalab et ISPF, et ≥ 0,90 entre Etalab et GEO PF, sans anomalie topologique dans Etalab. La liste des 28 codes est figée dans le générateur ; toute variation des sources, du résultat de comparaison ou de la liste bloque la génération.

Cette convergence **ne certifie pas juridiquement** les limites en 2026 : le producteur Etalab déclare réutiliser les sources GEO PF pour les îles polynésiennes, et les jeux territoriaux diffusés en 2022 ne documentent pas une date de validité juridique exhaustive des contours. Ces surfaces restent donc des **repères cartographiques contemporains d'édition 2026**, pas des restitutions historiques ni des périmètres homologués. Aucun nouvel ARK Pactols n'en découle.

**20 contours restent exclus et à instruire**, dont Tahaa (`98745`), auto-intersectant dans la source Etalab, et les atolls présentant des divergences importantes entre fonds. La recherche COG et les alignements Pactols déjà validés demeurent disponibles pour ces communes sans limite géographique affichée.

Rapports sources : `recette/lieux/PF-COMPARAISON-GEOMETRIQUE-2022-2026.json` et `recette/lieux/PF-DIAGNOSTIC-ANNEAUX-2022.json`. Dossiers de suivi : #114 et #105. Les années antérieures à 2026 n'utilisent le tracé que comme repère de 2026 facultatif et explicitement daté.
