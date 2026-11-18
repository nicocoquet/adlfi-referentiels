# Interface Lieux — phase 1, carte prioritaire et menus condensés

**Recette ergonomique, à valider avant publication.** La source documentaire et les données géographiques restent identiques à celles du site principal ; aucune nouvelle autorité, relation ou géométrie n'est introduite.

## Besoin éditorial

Faire de la **carte l'espace central**, en s'inspirant de l'approche du visualiseur cartes.gouv.fr sans en copier l'interface : la navigation « Zoom sur », « Échelon territorial » et « Recherche » doit être **repliée au chargement** puis accessible par clic, clavier et commandes explicites.

## Choix de cette première tranche

- Carte **pleine largeur du module** et hauteur adaptée à la fenêtre (avec minimum lisible).
- Trois contrôles HTML natifs `<details><summary>` regroupés sur la carte, sans `open` initial. Un seul menu à la fois (attribut `name` commun) ; les valeurs de zoom et d'échelon retenues apparaissent dans les boutons.
- Les identifiants existants `zoom`, `level`, `search`, `results`, `year`, `reference`, `reset` et `map` sont conservés.
- La recherche reste un combobox avec suggestions ; son résultat conserve la navigation vers une fiche documentaire. Après sélection, son menu se referme.
- La fiche territoriale n'occupe plus une colonne permanente : elle s'ouvre par-dessus la carte **uniquement lors d'une sélection**, avec bouton de fermeture. Elle est initialement masquée.
- La frise des années, les informations de provenance et l'option d'affichage des limites de référence **ne sont pas déplacées** dans cette tranche.
- Sur écrans étroits, les menus restent condensés en bandeau compact et la fiche devient un panneau bas superposé à la carte. L'ensemble demeure navigable au clavier.
- Révision CSS/HTML/JS de présentation **sans changement d'une seule donnée ni des fonctions de correspondance Pactols–COG**.

## Contrôles de recette

1. Vérifier en Chromium desktop et mobile les trois menus **initialement fermés**, leur ouverture/clôture au clic, et leur accessibilité clavier.
2. Vérifier que la largeur de carte occupe au moins 90 % de la fenêtre sur une largeur de 1 400 px.
3. Vérifier la recherche (nom, code INSEE, ARK), les sélecteurs et la frise **sans régression géographique ni historique**, notamment l'ouverture/fermeture de la fiche.
4. Tester les couches 2026 et les contours de référence datés, outre-mer inclus, puis les cas de tuiles OSM indisponibles.
5. Consulter les captures du workflow avant décision d'intégration sur `main`.

Cette PR ne prétend pas finaliser l'ergonomie du module. Les propositions concernant la frise, la présentation documentaire et les couches feront l'objet de discussions et de tranches ultérieures.
