# Index public de recherche COG ultramarin — 2026

**Recherche documentaire uniquement, sans géométrie publiée.**

## Source et reproduction

Le fichier recherche-2026.json est dérivé de l'artefact [GitHub Actions n°43909408130](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43909408130), produit sur la PR 30 à partir du COG INSEE 2026 et du diagnostic cartographique national (édition du 4 mai 2026). L'artefact contient **212 communes, 21 autres entités typées et un manifeste de provenance**.

Le script scripts/extraire_index_public_outremer_2026.py reproduit cette projection à partir du ZIP et la compare **octet pour octet** au fichier public. Commande : python3 scripts/extraire_index_public_outremer_2026.py --artefact CHEMIN/artefact.zip --verifier docs/data/lieux-outremer/recherche-2026.json.

L'index public conserve : les libellés et codes communaux, les 16 ARK Pactols–COG éditorialement approuvés pour 2026, deux ARK confirmés dont le lien reste à valider, le signalement topologique de Tahaa et Dumbéa, les 21 identités COMER distinctes. Il **ne contient aucune géométrie**.

## Précautions de modélisation

- La situation COG au 1er janvier 2026 est distincte de la date de livraison des contours (4 mai 2026).
- Les **16 ARK validés** concernent Mayotte, pour **2026 uniquement**. Dembeni (97607) et Le Port (97407) ont un identifiant Pactols confirmé, **sans correspondance COG éditorialement validée** ; leur ARK n'est pas ajouté aux mots-clés de recherche.
- Une géométrie topologiquement valide n'est pas un contour adopté : aucun polygone n'est diffusé par cet index, y compris pour les 210 communes possédant une géométrie nationalement disponible.
- Les 21 entités non communales sont accessibles par la recherche globale mais **pas** par un quatrième niveau territorial.
- Les **242 observations historiques** du dossier d'audit ne sont pas assimilées à des fiches intemporelles : cette projection couvre uniquement **2026**, sans rétroprojection.
- Le pilote **PACA de 103 autorités Pactols** n'est pas modifié.

## Conséquences pour l'interface

La sélection d'une fiche COG 2026 affiche ses informations et, si approprié, le lien Pactols approuvé. Elle ne dessine pas automatiquement de limite communale. Lorsque le curseur est placé sur une année différente de 2026, la fiche **reste explicitement datée de 2026** et signale l'absence de qualification historique. La carte conserve les contours déjà qualifiés, limités à quatre régions pilotes pour les communes.

Le sélecteur visible conserve **Région / Département / Commune**.
