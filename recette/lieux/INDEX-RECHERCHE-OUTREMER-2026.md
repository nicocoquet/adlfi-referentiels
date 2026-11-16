# Index de recherche Lieux — extension ultramarine (COG 2026)

**16 novembre 2026 · PR 30 · recette non publiée.**

## Position dans l'architecture

La nouvelle chaîne **scripts/preparer_index_recherche_outremer_2026.py** est un complément à l'index national historique de recherche COG (**scripts/preparer_index_cog_national_temporel.py**) et aux **103 autorités Pactols PACA** déjà publiées. Elle ne les remplace pas.

Elle prépare deux fichiers d'entités **administratives**, et non de nouvelles autorités Pactols :

1. **index-communes-outremer-2026.json** : 212 communes COG 2026, éligibles au niveau de navigation Commune.
2. **index-autres-entites-ultramarines-2026.json** : 21 entités administratives typées, consultables ultérieurement par la recherche globale, mais hors du sélecteur territorial.

Le fichier **manifest-index-outremer-2026.json** consigne les empreintes SHA-256 des entrées et sorties, les comptes et les garanties.

## Périmètre effectivement vérifié

| Source territoriale COG 2026 | Nombre | Niveau proposé |
|---|---:|---|
| Guadeloupe | 32 | Commune |
| Martinique | 34 | Commune |
| Guyane | 22 | Commune |
| La Réunion | 24 | Commune |
| Mayotte | 17 | Commune |
| Polynésie française | 48 | Commune |
| Nouvelle-Calédonie | 33 | Commune |
| Saint-Pierre-et-Miquelon | 2 | Commune |
| **Total** | **212** | **Commune** |
| Saint-Martin et Saint-Barthélemy, zonages particuliers COMER de type COM | 2 | Recherche globale, hors Commune |
| Districts TAAF (DIS 5), circonscriptions Wallis-et-Futuna (CIR 3), Clipperton (CPT 1), île des Faisans (CDM 1) | 10 | Recherche globale, hors Commune |
| Collectivités COMER elles-mêmes | 9 | Recherche globale, hors Commune |
| **Total complémentaire** | **21** | **Hors sélecteur** |

Les **233** identités possèdent toutes une **clé COG typée** de la forme DROM:COM:CODE, COMER:COM:CODE, COMER:DIS:CODE, etc. Un libellé ou un code seul ne détermine pas l'identité juridique.

**Le sélecteur public demeure exclusivement Région / Département / Commune.**

## Pactols : validation éditoriale distincte de la candidature

Les décisions éditoriales préexistantes sont lues dans les deux CSV versionnés :

- Mayotte : **16 correspondances validées uniquement pour COG 2026**. Dembeni (97607) : ARK confirmé, mais **lien communal à valider**.
- La Réunion : **23 correspondances à instruire**. Le Port (97407) : ARK confirmé, mais **lien communal à valider**.

Deux champs distincts empêchent toute confusion :

- **pactols.ark_valide** : renseigné seulement si la décision éditoriale est VALIDE_2026 ; ce terme peut être recherché.
- **pactols.ark_identifiant_confirme** : renseigné pour **Dembeni (26678/crtZcuFSJVYZU)** et **Le Port (26678/pcrtIKvRT9vwUl)** ; ne constitue pas une relation validée et ne doit pas être indexé comme telle.

Le fait qu'un concept Pactols contienne déjà une URI INSEE concordante ne crée pas automatiquement une correspondance approuvée par AdlFI. Les autres candidats non validés restent dans les fichiers de préinstruction, hors index.

## Historique COG : 242 observations, sans équivalence rétroactive

La jointure par code, **uniquement documentaire**, rassemble **242 observations historiques** dans deux familles de sources :

- **COG_DROM** : v_commune_depuis_1943.csv ;
- **COG_COMER** : v_commune_outremer_depuis_1943.csv.

La préinstruction précédente recensait **225 épisodes**. La différence de **17** provient de la prise en compte de la série COMER antérieure au **31 mars 2011** pour les 17 communes de Mayotte. Le changement de famille COG à cette date ne constitue pas une création juridique des communes.

Chaque observation conserve sa date de début incluse, sa date de fin exclue lorsqu'elle existe, sa famille de source, et le statut **relation_identite_avec_2026 = NON_ETABLIE**. La géométrie historique demeure **nulle**.

**Important :** la correspondance par code ne démontre pas qu'un état ancien possède le même nom, périmètre ou régime juridique qu'en 2026. Les successions et transformations doivent être instruites séparément à partir des événements administratifs et des sources territoriales.

## Géométrie : statut technique, jamais adoption automatique

Le fichier national du 4 mai 2026 contient **210 géométries topologiquement valides** pour les 212 communes et deux géométries invalides : **Tahaa (98745)** et **Dumbéa (98805)**.

Chaque fiche stocke le millésime du COG (1er janvier 2026), la date d'édition des contours (4 mai 2026), le statut topologique, la provenance et deux garanties :

- **contour_adopte_pour_publication = false**
- **geometrie = null**

Une validité topologique n'est ni une attestation des limites juridiques, ni une homologation d'un millésime historique. Les deux alternatives documentées pour Tahaa et Dumbéa ne sont pas automatiquement substituées aux contours nationaux.

## Recherche préparée, mais non branchée au site public

Les 212 communes sont cherchables par **libellé COG, code INSEE, nom/code du territoire parent**, et, le cas échéant, ARK **validé**. Les homonymes restent distingués par le code et le contexte territorial.

Les 21 entités hors échelon possèdent elles aussi des champs de **recherche globale**, mais leur **niveau_recherche** est nul et leur **interdiction_assimilation_commune** est vraie. Les *Kerguelen* et l'*île des Faisans* demeurent donc trouvables sans devenir des communes.

**Ce n'est pas encore une nouvelle interface publique.** Le moteur actuel **docs/assets/lieux-search.js** exige des autorités Pactols dotées d'un ARK et d'une correspondance ; la carte **docs/assets/lieux-multiechelon.js** n'expose les communes 2026 que pour quatre régions pilotes. Brancher directement les 212 fiches dans cette interface, sans adapter les types de résultats et les états de disponibilité cartographique, serait trompeur.

L'intégration ultérieure devra distinguer une fiche COG autonome d'une autorité Pactols, puis gérer explicitement les résultats sans contour adopté ou sans contour du millésime demandé.

## Reproduction CI

Workflow **.github/workflows/lieux-index-recherche-outremer-2026.yml**.

1. Télécharger les six CSV officiels COG 2026 et la couche nationale des communes à 100 m, contrôler les SHA-256.
2. Recalculer le diagnostic des 233 entités sans modifier les géométries.
3. Relire les CSV de décisions Mayotte et La Réunion sans déduire de nouvelles validations.
4. Générer **deux fois exactement les mêmes trois fichiers** et comparer leur contenu byte à byte.
5. Contrôler les volumes **212 / 21**, les **210 / 2** statuts géométriques, les **16** correspondances approuvées, les **2** ARK confirmés sans lien et la non-publication des géométries.
6. Conserver les trois fichiers dans un **artefact GitHub Actions de recette**, hors répertoire docs/.

Les CSV éditoriaux existants emploient parfois un point-virgule comme ponctuation dans le dernier champ « justification » sans guillemets. La lecture spécifique de ce champ préserve les justifications sans modifier les données de décision.

**Exécution initiale réussie :** [CI n°43908315923](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43908315923). Les modifications suivantes doivent être vérifiées dans leurs CI propres.

## Étape suivante

1. Adapter le modèle de résultats du moteur de recherche pour qu'il accepte les identités COG **sans ARK Pactols**, sans altérer les 103 autorités validées du pilote PACA.
2. Proposer les 212 communes dans l'autocomplétion nationale avec leurs contextes d'homonymie et états de disponibilité cartographique.
3. Autoriser la recherche globale des 21 autres entités sans quatrième échelon cartographique.
4. N'afficher des contours qu'après qualification explicite de la source et du millésime ; ne jamais appliquer silencieusement les contours 2026 aux années antérieures.

**Zéro nouvelle relation Pactols inférée, zéro géométrie publiée, aucune modification de docs/.**
