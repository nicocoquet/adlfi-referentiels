# Saint-Pierre-et-Miquelon — provenance de l'index historique public

**17 novembre 2026 — Référentiel Lieux AdlFI.** Trois **épisodes code–libellé** (deux communaux et un territorial), aucune géométrie historique.

## Source officielle et résultat contrôlé

Le [COG 2026 de l'Insee](https://www.insee.fr/fr/information/8740222), dans ses séries historiques :

| Fichier COG | Code | Libellé | Début inclus | Fin exclusive |
| --- | --- | --- | --- | --- |
| `v_commune_outremer_depuis_1943.csv` | `97501` | Miquelon-Langlade | **1976-07-21** | En cours |
| `v_commune_outremer_depuis_1943.csv` | `97502` | Saint-Pierre | **1976-07-21** | En cours |
| `v_tom_depuis_1943.csv` | `975` | Saint-Pierre-et-Miquelon | **1985-06-15** | En cours |

La série `v_commune_depuis_1943.csv` ne renvoie **aucune ligne pour ces deux codes**, y compris pour la période de statut DOM de l'archipel. La classification **COMER est celle du fichier historique**, et **ne signifie pas que l'archipel n'était pas un DOM entre 1976 et 1985**.

Le [rapport de préinstruction GitHub Actions](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44047579281) a acquis six fichiers officiels, vérifié leurs empreintes SHA-256, puis extrait ces trois lignes. Le script `scripts/verifier_index_public_saint_pierre_miquelon_2026.py` confronte l'index public aux mêmes sources, octet par octet pour les empreintes et champ par champ pour les épisodes.

## Date documentaire ≠ date de création

**Le 21 juillet 1976** marque la première observation de ces couples code–libellé dans la série COG historique consultée, **pas une date de création attestée des communes**. Les années antérieures à cette borne ne sont pas représentées par ces épisodes, sans conclusion sur l'existence des communes.

**Le 15 juin 1985** marque le début du couple code–libellé `975` dans le fichier historique des collectivités et territoires d'outre-mer ; ce n'est pas la date d'apparition géographique de l'archipel.

La [notice officielle de l'Insee sur Saint-Pierre-et-Miquelon](https://www.insee.fr/fr/information/7929495) indique quatre textes concernant son statut : loi du **19 juillet 1976** (DOM), loi du **11 juin 1985** (collectivité territoriale), loi constitutionnelle du **28 mars 2003** (COM relevant de l'article 74), loi organique du **21 février 2007** (actualisation). Les dates citées sont **celles des textes**, pas nécessairement des dates d'effet quotidiennes. Le module n'affiche pour ces statuts que des repères annuels sûrs **au 1er janvier**.

## Effet sur le référentiel Lieux

- Les communes `97501` et `97502` et la collectivité `975` sont **trois entrées COG distinctes**, déjà indexées en recherche 2026.
- La chronologie publique est **documentaire**. Elle ne crée aucune fiche nouvelle d'autorité Pactols.
- **0 correspondance Pactols 2026 approuvée** pour ces deux communes dans l'index public ; cela ne préjuge pas du contenu du thésaurus ni des candidats qu'un audit RDF pourrait révéler.
- **0 contour historique**, **0 équivalence rétrospective**, **0 relation de succession inférée**.
- Le filtre temporel de la page est un filtre d'**observation au 1er janvier**, non une interface de reconstitution cartographique au jour exact des lois.

**Aucun contour actuel n'est présenté comme historique, et aucun code de collectivité n'est utilisé comme code de commune.**
