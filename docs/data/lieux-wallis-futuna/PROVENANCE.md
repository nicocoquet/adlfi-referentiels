# Wallis-et-Futuna — chronologie COG 2026 et fondement légal des circonscriptions

**17 novembre 2026 — publication documentaire sans limites géographiques historiques.**

## Identités et typologie du territoire

| Code COG | Libellé | Type d'entité | Première date dans la série COG consultée |
| --- | --- | --- | --- |
| `98609` | Wallis-et-Futuna | Ancien code de territoire | 31 juillet 1961 — terminé le 1er janvier 1985 |
| `986` | Wallis-et-Futuna | Territoire actuel | 1er janvier 1985 |
| `98611` | Alo | **Circonscription territoriale (CIR)** | 1er janvier 1985 |
| `98612` | Sigave | **Circonscription territoriale (CIR)** | 1er janvier 1985 |
| `98613` | Uvea | **Circonscription territoriale (CIR)** | 1er janvier 1985 |

Ces **cinq épisodes code–libellé** proviennent des fichiers officiels du [COG 2026 Insee](https://www.insee.fr/fr/information/8740222). Le script de recette vérifie six fichiers originaux avec SHA-256 et compare les épisodes publics directement à leurs enregistrements.

Un contrôle complémentaire du fichier `v_tom_depuis_1943.csv` établit que `98607` est **libellé « Nouvelle-Calédonie »** du 1er janvier 1943 au 30 mars 1969. Même si la [notice de codification Insee](https://www.insee.fr/fr/information/7929495) évoque les îles Wallis-et-Futuna antérieurement rattachées à cet ensemble, **nous ne transformons pas `98607` en ancienne autorité Wallis-et-Futuna**, ni en code directement successeur ou équivalent de `98609` ou `986`. Le fichier COG n'atteste pas ici de succession explicite.

## Fondation juridique : 1961 n'est pas 1985

L'[article 17 de la loi n° 61-814 du 29 juillet 1961](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000684031) divise le territoire des îles Wallis-et-Futuna en **trois circonscriptions territoriales Uvea, Alo et Sigave**. L'article 18 leur confère la **personnalité morale**. La loi est en vigueur depuis le **30 juillet 1961**.

La **première date du code COG propre à chacune** est le **1er janvier 1985**, ce qui ne signifie nullement que ces circonscriptions ont été créées cette année-là. La coexistence de structures administratives et de royaumes coutumiers ne permet pas non plus de confondre leurs natures d'autorités.

Wallis-et-Futuna ne possède **aucune commune**, comme le rappelle le [site officiel du territoire](https://www.wallis-et-futuna.gouv.fr/Actualites/Presentation-de-Wallis-et-Futuna/Organisation-institutionnelle). Dans le COG 2026, les trois unités sont de type `CIR`, distinct du type `COM` des communes.

## États annuels affichés

Le curseur de notre module restitue l'**état au 1er janvier** :

| Année | Code territorial documenté | Codes CIR documentés dans la série COG |
| --- | --- | --- |
| 1943 | Aucun code 986/98609 attribué au territoire | Aucun |
| 1961 | Aucun à la date du 1er janvier | Aucun — la loi est postérieure au 1er janvier |
| 1962 à 1984 | `98609` (code historique) | Aucun code CIR propre, mais existence juridique attestée depuis 1961 |
| 1985 à 2026 | `986` | `98611`, `98612`, `98613` |

Les épisodes `98611`–`98613` ne sont **pas** rétroprojetés sur 1961–1984. La mention juridique ne remplace pas un enregistrement du COG.

## Contraintes d'intégration

Les quatre entités COG 2026 étaient déjà dans le moteur de recherche `lieux-outremer/recherche-2026.json` : la collectivité `COMER:TERRITOIRE:986` et les trois `COMER:CIR:98611/12/13`. Le module historique **les enrichit sans les dupliquer**. Le terme `98609` renvoie au dossier territorial, avec la chronologie datée, et non à une commune ou à un nouvel ARK.

Aucun contour ancien ou contemporain des trois circonscriptions n'est publié ; la carte peut seulement **recentrer** sur l'archipel. La rubrique `Commune` n'est pas étendue aux circonscriptions. **Aucun ARK Pactols** n'est validé pour les quatre autorités par cette étape.

### Sources et recette

- [INSEE, COG 2026](https://www.insee.fr/fr/information/8740222) : six fichiers originaux épinglés.
- [INSEE, histoire de codification Wallis-et-Futuna](https://www.insee.fr/fr/information/7929495).
- [Légifrance, loi n° 61-814, articles 17 et 18](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000684031).
- [Recette d'extraction COG, Actions n°44055036186](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44055036186).

Les scripts `auditer_cog_wallis_futuna_2026.py` et `verifier_index_public_wallis_futuna_2026.py` empêchent de confondre le code historique `98607` (Nouvelle-Calédonie) avec Wallis-et-Futuna et certifient **0 commune, 0 géométrie historique, 0 nouvel alignement Pactols**.
