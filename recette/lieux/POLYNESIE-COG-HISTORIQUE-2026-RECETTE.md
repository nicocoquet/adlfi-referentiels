# Polynésie française — audit COG 2026 et programme d'autorités

**17 novembre 2026 — phase de contrôle des sources, sans alignement Pactols ni publication de nouvelles fiches.**

## Périmètre et précautions sémantiques

Le [COG Insee 2026](https://www.insee.fr/fr/information/8740222) contient **48 communes de Polynésie française** sous les codes `98711` à `98758`. Ces 48 codes sont déjà présents dans `docs/data/lieux-outremer/recherche-2026.json`, **sans correspondance Pactols validée à ce stade**.

La [source ISPF](https://www.ispf.pf/ispf/referentiels) et le [Haut-commissariat](https://www.polynesie-francaise.gouv.fr/Actions-de-l-Etat/Accompagnement-des-communes/Presentation) permettent de distinguer :

| Entité | Nombre | Relation à établir |
| --- | ---: | --- |
| Commune principale | **48** | Autorité COG en 2026 |
| Commune associée | **98** | Réparties dans **30** communes principales ; nomenclature ISPF distincte |
| Commune sans commune associée | **18** | ISPF : code conventionnel à trois positions se terminant par 0 dans sa nomenclature fine |
| Subdivision administrative | **5** | Échelon d'administration de l'État, ne se substitue pas au découpage communal |

L'ISPF décrit ainsi une partition en **116 unités fines** (98 communes associées et 18 communes sans associées), et précise que les découpages administratifs `subdivision > commune > commune associée` et géographiques `subdivision > île` ne correspondent **pas directement**. Une commune peut couvrir plusieurs îles, et une île regrouper plusieurs communes. Les codes ISPF à trois positions **ne doivent pas être mécaniquement transformés** en identifiants COG à cinq positions.

Le [Sénat](https://www.senat.fr/rap/r24-017/r24-0178.html) souligne que les communes associées polynésiennes **ne résultent pas d'une fusion de communes indépendantes** au sens métropolitain. Aucune relation d'anciennes communes ne sera créée sur cette seule dénomination.

## Fondement juridique et profondeur temporelle

La [loi n° 71-1028 du 24 décembre 1971](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000693681/) et le [décret du 17 mai 1972](https://www.insee.fr/fr/information/7929495) documentent une réforme communale. Toutefois, le [rapport officiel publié au JO le 4 juin 2026](https://www.legifrance.gouv.fr/jorf/id/JORFARTI000054191111) précise qu'elle a **ajouté 44 communes à quatre communes préexistantes**, sans autoriser à dater de 1972 la création de l'ensemble des communes.

Il faut distinguer **création juridique de l'autorité**, **première attestation du couple code–libellé dans le COG** et **validité d'une éventuelle géométrie cartographique**.

La [notice historique de codification de l'Insee](https://www.insee.fr/fr/information/7929495) signale aussi l'ancien code **`98799` de Clipperton**, supprimé à la suite du changement de rattachement en 2007. Celui-ci n'est **ni l'une des 48 communes de 2026 ni une autorité à réintroduire automatiquement dans la hiérarchie polynésienne contemporaine**.

## Protocole d'audit reproductible

Le script `scripts/auditer_cog_polynesie_2026.py` confronte les 48 codes publiés aux six tables originales du COG 2026, épinglées par SHA-256 :

- `v_comer_2026.csv` et `v_commune_comer_2026.csv` : territoire et communes courants ;
- `v_tom_depuis_1943.csv` et `v_commune_outremer_depuis_1943.csv` : historiques code–libellé des unités COMER ;
- `v_commune_2026.csv` et `v_commune_depuis_1943.csv` : contrôle négatif de toute confusion avec les communes DROM.

Le workflow reproduit deux fois exactement les sorties, extrait les **épisodes COG de chaque code**, les anciens codes non courants, les changements de libellé éventuels, et vérifie que les codes de communes associées ISPF ne sont **pas inventés** à partir du COG.

Les dates et les nombres d'épisodes **seront inscrits dans une restitution publique seulement après examen du rapport officiel produit par la CI**.

## Interdictions éditoriales

**Zéro alignement Pactols nouveau, zéro géométrie historique, zéro commune associée générée, zéro identité juridique rétroprojetée.** La recette est distincte de toute PR ultérieure de publication des périodes ou d'alignements.
