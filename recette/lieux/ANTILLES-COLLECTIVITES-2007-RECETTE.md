# Saint-Barthélemy et Saint-Martin — transitions de 2007

**17 novembre 2026 · Audit de deux anciennes communes, deux collectivités, deux codes d'application à cinq positions.**

## Deux types de preuve distincts

Le **COG 2026 de l'Insee** documente deux anciennes communes du département de la Guadeloupe, leurs périodes terminées au **23 février 2007**, et des mouvements `MOD 30` à cette date dont le champ `COM_AP` reste **vide** :

| Avant le 23 février 2007 | Après la réforme de 2007 |
| --- | --- |
| `97123` — commune de Saint-Barthélemy, département `971` | `977` — collectivité de Saint-Barthélemy ; `97701` code à 5 positions |
| `97127` — commune de Saint-Martin, département `971` | `978` — collectivité de Saint-Martin ; `97801` code à 5 positions |

Les nouveaux codes ne sont **pas des codes communaux** au sens où une nouvelle commune aurait été créée. L'[Insee, *Codification des collectivités et territoires français d'outre-mer*](https://www.insee.fr/fr/information/7929495) précise que **`97701` et `97801` sont des formats à cinq chiffres réservés aux applications qui en ont besoin**, et que les collectivités portent les codes `977` et `978` à compter du **23 février 2007**.

La **loi organique n° 2007-223 du 21 février 2007**, [article 18, X et XI](https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000006399955), déclare explicitement que les nouvelles collectivités succèdent à leurs anciennes communes respectives **dans leurs droits et obligations**. L'article [LO6211-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006393813) et l'article [LO6311-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006394046) décrivent leur substitution à la commune et aux deux niveaux départemental et régional de Guadeloupe. La loi est entrée en vigueur le **22 février 2007** ; cette date **juridique** et la date de **codification Insee au 23 février** sont distinctes.

Le COG ne prouve donc pas à lui seul la relation de succession, mais **le texte normatif la prouve**. Il faut exposer clairement les deux provenances.

## Modélisation proposée

Pour chaque territoire, trois types de références :

1. Une **ancienne commune** `97123` ou `97127`, avec son épisode COG `1946-03-21` (inclus) à `2007-02-23` (exclu).
2. Une **collectivité d'outre-mer**, code COG `977` ou `978`, et sa période documentaire historique propre (`v_tom_depuis_1943.csv`).
3. Une **variante de codification à cinq positions**, `97701` ou `97801`, qui **n'est ni une commune nouvelle ni une autre collectivité**.

La relation `succède juridiquement à` est documentée avec son fondement légal ; elle ne signifie **ni `skos:exactMatch` entre concepts Pactols**, ni transfert automatique des métadonnées de la commune ancienne, ni identité géométrique certaine.

### Sources COG contrôlées

Le script `scripts/auditer_transition_saint_barthelemy_saint_martin_2007.py` confronte **sept CSV** de l'[archive officielle du COG 2026](https://www.insee.fr/fr/information/8740222) : séries des communes actuelles et historiques DROM, des mouvements communaux, des collectivités et territoires actuels et historiques, et des zonages ultramarins actuels et historiques.

Les 7 empreintes SHA-256 épinglées, la vérification des dates et codes, les tests synthétiques et la répétition exacte du rapport JSON sont exécutés dans le workflow `lieux-antilles-collectivites-2007.yml`.

### Limites éditoriales

- **Aucun nouveau concept ni alignement Pactols**, même lorsque le nom est identique.
- **Aucune limite géographique historique** issue d'un contour 2026 ou d'une reconstruction non authentifiée.
- **Aucune rétroprojection des codes 977/978 vers les anciennes communes**, ni affectation des nouveaux codes à l'échelon communal dans le filtre `Commune`.
- Les **32 correspondances Pactols–COG 2026 de Guadeloupe** restent inchangées.

## Résultat de la confrontation officielle

L'[audit COG/Loi n°44050874502](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44050874502) est **réussi** et reproductible. Les sept sources COG 2026 épinglées ont confirmé :

| Ancienne commune (fin exclusive) | Collectivité COMER (début inclus) | Code à 5 positions (début inclus) | Nature du zonage |
| --- | --- | --- | --- |
| `97123` · 2007-02-23 | `977` · 2007-02-23 | `97701` · 2007-02-23 | `COM` (code applicatif, pas commune) |
| `97127` · 2007-02-23 | `978` · 2007-02-23 | `97801` · 2007-02-23 | `COM` (code applicatif, pas commune) |

Les deux collectivités disposent chacune d'un seul épisode COG historique depuis le 23 février 2007 sans date de fin. La loi organique contient deux **relations de succession des droits et obligations expressément attestées**. Les deux mouvements communaux n'ont en revanche **aucune destination `COM_AP`**.

Ces états sont désormais intégrés à la frise du référentiel Lieux, avec les trois catégories de codes distinctes, un lien entre ancienne commune et collectivité successeure, et des tests anti-rétroprojection. La [note de provenance publique](../../docs/data/lieux-antilles-collectivites-2007/PROVENANCE.md) détaille la distinction entre la date de codification du 23 février et l'entrée en vigueur de la loi organique le 22 février.

Les correspondances Pactols et les géométries historiques restent inchangées.
