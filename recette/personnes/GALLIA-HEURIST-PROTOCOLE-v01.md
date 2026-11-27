# Personnes — protocole d'intégration Gallia / Gallia Préhistoire (v0.1)

**Statut : architecture technique en cours de recette ; aucune contribution Heurist ajoutée au site.**

## Sources et périmètre du pilote

- Extrait Heurist original : `Export_Revue_Gallia_20261127115832.json`, SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`. **Source privée : ne jamais committer le JSON brut.**
- Projection de travail filtrée : `Heurist_Gallia_pilote_roles_securise_20261127.zip`, conservée hors du site.
- Rapprochements exacts par IdRef avec les **202** autorités `PER` publiées. Pour le sous-ensemble qui possède des contributions : **193** autorités, **338** articles de `gallia` et `gallia_prehistoire`, **474** relations (425 `auteur` ; 49 `collaborateur`). **Toutes ces relations sont candidates, sans visa de publication.**
- `gallia_informations` n'est pas assimilée à l'une de ces deux revues.
- Un article du pilote n'a pas d'URL ; un lien absent ne doit pas être inventé. Certains DOI ont des préfixes répétitifs : conserver une version canonique et le JSON source hors publication.

## Politique de confidentialité et de rôles

- **Liste blanche positive et exclusive** : champ article Heurist `15` → `auteur` ; champ article Heurist `1057` → `collaborateur`.
- Les autres relations personne–article, en particulier les interventions relevant des processus éditoriaux internes, **ne sont ni extraites, ni représentées, ni exposées**. Leur absence publique n'indique rien sur l'organisation interne de la revue.
- Ne pas utiliser les rôles généraux des fiches de personnes pour attribuer un rôle à un article.
- Exclure les données personnelles non nécessaires (coordonnées, dates de naissance, champs internes et relations éditoriales non publiables).
- Écarter les valeurs d'identifiant provisoires (p. ex. `####`) et ne pas inférer d'identité à partir d'une simple graphie.
- La position `position_in_role` est locale à chaque champ répétable : ne jamais en déduire un rang combiné auteur/collaborateur.

## Architecture technique

- Catalogue AdlFI existant : `docs/data/personnes.json` (schéma 0.4.0), **inchangé**.
- Futur catalogue bibliographique **distinct**, une fois visé : `docs/data/personnes-articles.json` (schéma `docs/schemas/personnes-articles.schema.json`, v0.1.0).
- Dans ce complément : liste normalisée des **articles uniques** et liste des relations `article_id`–`person_id`–`role`, chacune avec sa position locale au rôle.
- Les liens de lecture doivent accepter exclusivement HTTPS sur `journals.openedition.org` et `www.persee.fr` ; en cas d'absence, afficher le titre sans lien.
- L'interface charge le complément **facultativement**, uniquement s'il porte le statut `PUBLIC_PILOT` et passe les vérifications. En son absence, l'affichage AdlFI et les mentions « À venir » des autres revues sont conservés.
- Les filtres de rôle permettent de sélectionner séparément auteur et collaborateur ; les métadonnées bibliographiques (volume, année, pages) sont affichables sans duplication des articles.
- Le script `scripts/preparer_personnes_articles_gallia.py` produit uniquement une projection `CANDIDAT_NON_VALIDE` dans un emplacement **hors `docs/`**. La validation éditoriale et le dépôt du JSON public seront une opération explicite et séparée.

## Séquence prévue

1. Vérifier la CI, les schémas, le script de projection et les tests de confidentialité sur cette PR **technique**, dépourvue de données candidates.
2. Contrôler et faire viser le corpus de 338 articles et 474 contributions, notamment les URL absentes et les cas d'identité incertains.
3. Seulement après visa, créer une PR **de données** portant le fichier `docs/data/personnes-articles.json`, avec compteurs et contrôles stricts.
4. Effectuer une recette visuelle de l'affichage et des filtres, puis fusionner la PR de données.
5. Les nouvelles autorités Heurist hors des 202 `PER` existants feront l'objet d'un chantier d'autorités distinct, non d'un lot 09 AdlFI.

**Interdit :** copier le JSON source Heurist, les liens d'évaluation éditoriale ou un candidat non validé dans `docs/`.
