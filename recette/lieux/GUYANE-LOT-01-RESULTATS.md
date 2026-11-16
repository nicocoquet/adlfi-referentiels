# Guyane — résultats de la recette COG / Pactols, lot 01

**Analyse du 16 novembre 2026 · PR 44 · Source : COG 2026 et export Pactols Lieux du 22 juillet 2026 · Statut non validé éditorialement.**

La [CI spécialisée (exécution n°43923775488)](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43923775488) a exécuté le traitement deux fois, sur les sources SHA-256 épinglées, avec résultats octet à octet identiques. [Artefact de recette : cinq fichiers, dont la table de prévalidation des 26 concepts](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43923775488/artifacts/14255162269).

## Bilan effectivement constaté

| Contrôle | Constat |
| --- | ---: |
| Communes COG actives au 1er janvier 2026 | **22** |
| Codes de commune historiques distincts dans la série 973 | **26** |
| Périodes code–libellé documentées depuis 1943 | **41** |
| Lignes du fichier officiel des mouvements impliquant un code 973 | **52** |
| Géométries communales 2026 présentes et topologiquement valides | **22/22** |
| Communes actuelles avec au moins une URI INSEE citée explicitement dans Pactols | **22/22** |
| Concepts Pactols supplémentaires renvoyant à des codes guyanais non actuels | **4** |
| Concepts portant un prédicat exactMatch vers un code COG de Guyane | **26** |
| Concept marqué déprécié parmi ces 26 | **0** |
| Correspondances Pactols nouvellement approuvées par le traitement | **0** |
| Contours publiés ou réparés | **0** |

Les 52 lignes de mouvements COG ne doivent pas être confondues avec les **56 résultats** de l'interface historique de l'Insee : les périmètres documentaires et les règles de comptage diffèrent.

## Candidats Pactols des 22 communes actuelles

Chaque lien ci-dessous est une assertion **skos:exactMatch** vers l'URI Insee correspondante, dans la version RDF Lieux du 22 juillet 2026. Aucun n'a encore le statut AdlFI de relation éditorialement validée.

| INSEE | Commune COG 2026 | ARK Pactols relevé dans le RDF |
| --- | --- | --- |
| 97301 | Régina | 26678/pcrttIps5Ffwr4 |
| 97302 | Cayenne | 26678/pcrtEim2rVrqfb |
| 97303 | Iracoubo | 26678/pcrt7FR0qV0Is6 |
| 97304 | Kourou | 26678/pcrtWpKDHtMSkB |
| 97305 | Macouria | 26678/pcrt9aK5fmOuXJ |
| 97306 | Mana | 26678/pcrtTfEYcHIXJW |
| 97307 | Matoury | 26678/pcrt2Gm9yHAfxn |
| 97308 | Saint-Georges | 26678/pcrtFDuzqh49Ol |
| 97309 | Remire-Montjoly | 26678/pcrtrRfBpKfIhe |
| 97310 | Roura | 26678/crtIVELOBKloW |
| 97311 | Saint-Laurent-du-Maroni | 26678/pcrtlWNYtaYba9 |
| 97312 | Sinnamary | 26678/pcrtYLrXNz151S |
| 97313 | Montsinéry-Tonnegrande | 26678/pcrtvi4CkgpqF9 |
| 97314 | Ouanary | 26678/pcrt1XynuLu667 |
| 97352 | Saül | 26678/pcrt4qijlxa29n |
| 97353 | Maripasoula | 26678/pcrtT6No9jDPfh |
| 97356 | Camopi | 26678/pcrtzVD7muUZjn |
| 97357 | Grand-Santi | 26678/pcrtTl4tAI3YCA |
| 97358 | Saint-Élie | 26678/pcrtQLBrvr2ygL |
| 97360 | Apatou | 26678/pcrtlaYvADNGdY |
| 97361 | Awala-Yalimapo | 26678/pcrt74xZfQYJNg |
| 97362 | Papaichton | 26678/pcrtJ8esax997c |

**Contrôle lexical :** 21 noms de communes actuelles concordent littéralement après normalisation avec un libellé français de leur concept. **Saint-Georges (97308)** apparaît sous le préfLabel Pactols **« Saint-Georges (Guyane) »** : le suffixe territorial explique l'absence de concordance littérale, alors que l'URI INSEE citée correspond exactement au code attendu. Cela doit être conservé comme désambiguïsation, pas comme une anomalie de concept.

## Quatre autorités Pactols de codes communaux historiques disparus

| Ancien code COG | Libellé historique COG | ARK Pactols du concept correspondant |
| --- | --- | --- |
| 97351 | Approuague (chef-lieu Régina) | 26678/pcrtIPUh7AuXTg |
| 97354 | Samson (chef-lieu Dégrad-Samson) | 26678/pcrtRJeVr9K5TB |
| 97355 | Moyenne-Mana (chef-lieu Mana) | 26678/pcrtbvSjznYKWV |
| 97359 | La Comté (chef-lieu Dégrad-Edmond) | 26678/pcrtCD30P0XhAE |

Les quatre concepts ne sont pas dépréciés dans l'export RDF analysé. Cela ne signifie pas qu'ils constituent des communes actuelles. **Ne pas rediriger automatiquement leurs ARK vers les communes successeurs**, même si le COG enregistre un rattachement en 1969.

Exemple à documenter : **Mana** a porté son nom actuel sous le code 97306 alors que le code historique 97355 avait pour libellé « Mana » puis « Moyenne-Mana (chef-lieu Mana) ». Un rapprochement fondé exclusivement sur le libellé « Mana » pourrait donc confondre des autorités distinctes.

## Jalons temporels effectivement présents dans le fichier des mouvements COG

La recette recense notamment **18 mouvements datés du 21 mars 1946**, **11 du 1er janvier 1953**, **14 du 27 mars 1969**, **2 du 12 novembre 1976**, **2 du 1er janvier 1989** et **2 du 1er janvier 1993**. Les événements sont enregistrés avec leur code avant et après, et le MOD officiel (10, 20, 31). Les 52 lignes ne sont pas toutes des créations ou disparitions.

Une **différence de convention temporelle** doit rester visible : le portail de l'Insee affiche pour certaines transformations le **26 mars 1969**, tandis que le fichier des mouvements COG enregistre **27 mars 1969** comme date d'effet. De même, le portail présente les événements d'Awala-Yalimapo au 31 décembre 1988 et de Papaichton au 31 décembre 1992, alors que le COG des mouvements donne respectivement les 1er janvier 1989 et 1993. Ne pas corriger silencieusement une source à partir de l'autre.

La première période de commune répertoriée dans la série 973 commence en **1946** : l'absence d'une période active au 1er janvier 1943 dans ces fichiers ne démontre pas l'absence d'organisation administrative antérieure.

## Décision proposée pour la suite

1. **Lot Pactols actuel** : examiner les 22 correspondances à preuve forte, en vérifiant l'identité du concept, son préfLabel et les usages historiques. Les proposer à une validation éditoriale collective **uniquement sur l'état COG 2026**.
2. **Lot historique distinct** : conserver les quatre codes anciens et leurs quatre ARK comme autorités documentaires candidates ; qualifier séparément les événements de 1953 et 1969 qui ont transformé ou supprimé ces unités.
3. **Géométries** : les 22 polygones 2026 sont techniquement valides, mais non publiés par cet audit. La couverture historique exige un millésime représentatif ou une reconstruction explicite ; les contours 2026 ne peuvent être simplement reculés au-delà des démembrements.
4. **Recherche publique** : les 22 communes sont déjà retrouvables par nom et code INSEE sur GitHub Pages. Aucune nouvelle relation Pactols ou frontière ne sera affichée avant les validations.

La table éditoriale **guyane-pactols-candidats-26.csv** est générée directement à partir des sources épinglées et doit rester avec son manifeste de provenance. Les résultats complets (dont les surfaces diagnostiques et toutes les dates) sont disponibles dans l'artefact de recette de la CI.
