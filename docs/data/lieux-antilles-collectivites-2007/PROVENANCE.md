# Saint-Barthélemy et Saint-Martin — preuve COG et succession juridique de 2007

**17 novembre 2026.** Dossiers connexes à la [chronologie communale de Guadeloupe](../lieux-guadeloupe/PROVENANCE.md), sans nouveaux contours ni correspondances Pactols.

## Trois identifiants distincts par territoire

| Famille | Saint-Barthélemy | Saint-Martin | Nature |
| --- | --- | --- | --- |
| Ancienne commune guadeloupéenne | `97123` | `97127` | Communes de Guadeloupe jusqu'au 23 février 2007 (COG historique) |
| Collectivité d'outre-mer | `977` | `978` | Collectivités distinctes à partir du 23 février 2007 (COG historique) |
| Code d'application à cinq positions | `97701` | `97801` | Variantes de codification, **non des communes créées en 2007** |

### Dates exactes du COG 2026 vérifiées

Les **six épisodes historiques** (deux par famille) sont contrôlés par les sept fichiers source :

- `97123` et `97127` : du **21 mars 1946** (inclus) au **23 février 2007** (exclu).
- `977` et `978` : du **23 février 2007** (inclus) à la date du COG 2026, sans date de fin.
- `97701` et `97801` : du **23 février 2007** (inclus), catégorie `NATURE_ZONAGE=COM` dans la table COG ultramarine, **mais codification à cinq positions de la collectivité d'après l'Insee**.

À l'**état au 1er janvier 2007**, les anciennes communes sont encore documentées ; les codes `977`/`978` ne le sont pas. À l'**état au 1er janvier 2008**, c'est l'inverse.

Le fichier des mouvements communaux contient **deux MOD 30** au 23 février 2007, avec **`COM_AP` vide**. Ce champ ne constitue donc pas la source de la relation successorale.

### Une succession administrative fondée sur la loi, non sur le mouvement COG

La [loi organique n° 2007-223 du 21 février 2007, article 18, X et XI](https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000006399955), prévoit expressément la succession des deux collectivités aux anciennes communes dans leurs droits et obligations. Les [articles LO6211-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006393813) et [LO6311-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006394046) du CGCT précisent leur substitution aux communes et aux deux niveaux départemental et régional de Guadeloupe.

La loi organique est **entrée en vigueur le 22 février 2007**, et le **changement de codes dans le COG date du 23 février 2007**. Nous enregistrons ces dates dans des champs différents ; nous ne calculons **aucune date d'effet quotidienne de transfert des droits** à partir du seul COG.

La [note de codification de l'Insee](https://www.insee.fr/fr/information/7929495) établit de façon explicite que `97701` et `97801` servent aux applications requérant cinq positions. Même si le fichier de zonages emploie le code `COM`, l'appellation **commune actuelle** serait incorrecte dans le présent contexte.

### Décisions d'indexation

- Les anciennes communes guadeloupéennes et les collectivités sont des **autorités distinctes** liées par une **succession juridique sourcée**.
- **Aucune destination `COM_AP` n'est inventée** dans les données du COG.
- **Aucune équivalence `skos:exactMatch` Pactols** ancienne commune / collectivité n'est créée ou transférée.
- Les **32 alignements Pactols validés de Guadeloupe** restent inchangés ; le total ultramarin publié reste **128**.
- **Aucune géométrie historique** n'est créée ; les liens entre fiches ne sont pas une preuve que leurs géométries seraient identiques.

### Sources et contrôles

- [Insee, Code officiel géographique 2026](https://www.insee.fr/fr/information/8740222).
- [Insee, Codification des collectivités et territoires français d'outre-mer](https://www.insee.fr/fr/information/7929495).
- [Légifrance, loi organique n° 2007-223](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000465963).
- [Recette de l'audit initial](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44050874502).

Le script `scripts/verifier_index_public_antilles_collectivites_2007.py` et les tests Node.js, Python et Chromium vérifient séparément chaque famille de codes et refusent toute interprétation de `97701` ou `97801` comme nouvelle commune.
