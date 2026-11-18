# Pays de la Loire — deux alignements 2026 fondés sur les mouvements administratifs de 2024

**Décision éditoriale proposée le 18 novembre 2026.** Publication indépendante de la [PR de recette 147](https://github.com/nicocoquet/adlfi-referentiels/pull/147) et des [neuf collisions, PR 145](https://github.com/nicocoquet/adlfi-referentiels/pull/145).

## Ingrandes-le-Fresne-sur-Loire (49160) : création MOD32 du 1er janvier 2024

L’[Insee (COG 2026)](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49160) et l’[arrêté de création du 16 novembre 2023](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000048728239) attestent la nouvelle entité formée le 1er janvier 2024 par réunion d’Ingrandes-Le Fresne sur Loire (commune nouvelle de 2016) et de Saint-Sigismond. Le code `49160` est conservé, **mais il s’agit d’une autre création administrative**.

L’ARK contemporain Pactols est **`26678/pcrtj64zr6gnns4mnfd2828b`** (créé par Inist le 31 mai 2024). Son `prefLabel` correspond exactement au libellé 2026 ; la définition mentionne la fusion 2024. Il porte deux assertions `skos:exactMatch` : (i) une URI INSEE de forme UUID `http://id.insee.fr/geo/commune/2cdbc96f-9287-4279-80c9-b3c169bb1fed` ; (ii) `https://www.wikidata.org/wiki/Q123475717`. **La résolution directe de l’UUID n’est pas démontrée ici.** Elle reste explicitement qualifiée de non résolue dans l’index.

La [révision figée de Wikidata `Q123475717`](https://www.wikidata.org/w/index.php?title=Q123475717&oldid=2309862185), conservée dans [le registre](PDL-INGRANDES-WIKIDATA-2024.json), indique `P31=Q484170` (commune française), `P374=49160` (code INSEE) et `P571=2024-01-01` (création). La correspondance repose donc sur la **chaîne éditorialement vérifiée Pactols → Wikidata (P374/P571) → COG 2026**, et non sur une prétendue équivalence directe entre UUID non résolu et code numérique.

L’ARK `26678/pcrtQBSwT6fBDW` décrit la commune nouvelle **créée en 2016**, sa définition mentionnant explicitement sa fusion en 2024. Il reste distinct, non promu et sans `owl:sameAs` automatiquement inféré.

## Essarts-en-Bocage (85084) : rétablissement de deux communes MOD21

La création de 2016 concerne Boulogne, Les Essarts, L’Oie et Sainte-Florence. Le **1er janvier 2024**, le mouvement administratif `MOD21` rétablit L’Oie (`85165`) et Sainte-Florence (`85212`) comme communes. Essarts-en-Bocage conserve `85084`, mais avec un périmètre réduit : ce n’est pas un simple changement typographique.

Le concept Pactols **`26678/pcrt0PrU3oVWxo`** est explicitement aligné par `skos:exactMatch` sur `http://id.insee.fr/geo/commune/85084`, porte le `prefLabel` de 2026 et sa définition décrit **les arrêtés du 19 octobre 2023 et les rétablissements de 2024**. La note Inist du 3 juin 2024 documente une actualisation des libellés, de la définition et de l’alignement INSEE. La combinaison de ce contenu actualisé et des mouvements officiels donne une preuve suffisamment circonstanciée pour attribuer ce concept au **périmètre de 2026**. [Insee, dossier communal](https://www.insee.fr/fr/statistiques/2011101?geo=COM-85084).

L’ancien concept de la commune des Essarts (`26678/pcrtFmygG5m3QZ`) reste séparé. Aucun lien historique entre les deux ARK n’est inféré.

## Contrôles et portée

Le générateur `scripts/publier_pdl_deux_mouvements_2024_2026.py` vérifie le SHA-256 du RDF Pactols th17, la séparation des ARK, les URI INSEE/Wikidata complètes, les définitions et notes datées, le registre Wikidata figé, les épisodes COG et **la différence entre `MOD32` et `MOD21`**. Les 1 215 publications antérieures demeurent uniques. La recette doit être exécutée deux fois avec un JSON identique au fichier versionné, puis testée en Node et Chromium.

**Après réussite et fusion uniquement : 1 217 / 1 228, 11 exceptions.** Aucune géométrie ni équivalence temporelle ou ontologique produite. La preuve ne s’étend pas automatiquement à d’autres millésimes COG ou périmètres historiques.

Les autres dossiers restent à instruire sans les forcer : Baugé-en-Anjou, Le Lion-d’Angers, Montsûrs, Le Lude, Les Hauts-d’Anjou, Rives-du-Fougerais et cinq communes dépourvues de candidat Pactols contemporain. La refonte graphique du module Lieux suivra la consolidation PDL selon les idées de l’éditeur.
