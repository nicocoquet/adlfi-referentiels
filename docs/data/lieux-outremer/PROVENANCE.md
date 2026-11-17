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
