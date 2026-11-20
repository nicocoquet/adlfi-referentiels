# Lieux — chargement progressif des communes selon la vue

**20 novembre 2026 — première tranche de montée en charge, sans nouvelle géométrie ni correspondance.**
Suivi : [#152](https://github.com/nicocoquet/adlfi-referentiels/issues/152).
Mesures de référence : [AUDIT-CHARGE-COMMUNES-2026.md](AUDIT-CHARGE-COMMUNES-2026.md) (6 410 contours, 336 846 sommets, 7,26 Mo bruts).

## Constat et choix de rétrocompatibilité

Auparavant, l'entrée dans l'échelon **Commune 2026** téléchargeait simultanément les quatre grandes couches métropolitaines (PACA, Corse, Pays de la Loire, Bourgogne-Franche-Comté), quelle que soit la zone visible, plus quatre couches ultramarines. Cela pénalisait particulièrement les liens profonds vers une région.

Cette première modification **ne masque pas les contours au zoom national** : pour une vue Leaflet au zoom inférieur à 7, les quatre régions métropolitaines sont toujours chargées et visibles comme auparavant. Au zoom **7 et plus**, seules les couches intersectant la fenêtre cartographique sont demandées et dessinées, en conservant les régions voisines lorsque la fenêtre coupe leurs emprises.

Cette règle s'appuie sur les quatre cadrages déjà validés dans l'interface : l'intersection utilise leurs **rectangles de chargement**, et **ne constitue ni une validation de limites administratives ni un rattachement historique COG**. Les contours eux-mêmes conservent leur provenance Etalab/IGN 2026.

## Mesures de comportement prévues

| Scénario | Données métropolitaines attendues | Outre-mer |
|---|---|---|
| France métropolitaine, zoom 6 | Les quatre couches publiées (6 219 contours) | 191 contours publiés, sans modification |
| Zoom local en Pays de la Loire | Couche PDL (1 228), régions limitrophes seulement si intersection | inchangé dans cette tranche |
| Zoom local en Corse | Couche corse (360) | inchangé |
| Zone sans couverture communale publiée (par exemple Île-de-France) | **Aucune commune métropolitaine inventée** ; message de couverture explicite | inchangé |
| Recherche d'une commune hors de la zone courante | Cadrage automatique sur sa région, chargement de sa couche, puis centrage sur le contour | inchangé |
| Retour sur une région déjà consultée | Réutilisation des promesses et couches mises en cache | inchangé |
| Année antérieure avec repère contemporain activé | Couches 2026 sélectionnées selon la vue, **qualifiées explicitement de repères non historiques** | inchangé |

Le premier bénéfice mesurable est la réduction des **requêtes réseau initiales** pour les entrées régionales. Les données déjà téléchargées restent en mémoire pour permettre le retour rapide : cette tranche ne promet donc pas une libération de mémoire JavaScript en cours de navigation.

## Architecture et non-régressions

- `docs/assets/lieux-communes-vue.js` : moteur indépendant et testé de l'intersection entre la vue Leaflet et les cadres des régions publiées ; seuil 7, choix conservateur au zoom national, clé d'identité de sélection.
- `docs/assets/lieux-multiechelon.js` : promesses mémorisées séparément par région, chargement outre-mer inchangé, invalidation de rendu au changement d'emprise ; `activeRequest` protège toujours contre une réponse tardive lors des changements de zone/année.
- `docs/lieux/index.html` : chargement du petit module avant la carte, version de ressource actualisée pour éviter le cache du navigateur.
- Tests Node : emprises, voisinage, zoom national, région absente et paramètres incorrects.
- Tests Chromium : départ sur PDL sans télécharger BFC/PACA/Corse, déplacement Corse et retour cache PDL, recherche d'Afa depuis PDL, retour au national 6 410, curseur 1975 et absence de rétroprojection.
- Non-régressions navigateur en Corse, PDL, BFC, PACA.

## Limites et tranches suivantes

1. Les **quatre** couches ultramarines restent groupées et chargées ensemble ; leur séparation par zone géographique et les filtres de visibilité seront une deuxième tranche, sous réserve de recette DROM/SPM/NC/Polynésie.
2. À l'échelle nationale, le chargement complet des **quatre** couches métropolitaines demeure volontairement inchangé : avant de passer à treize régions, il faudra décider d'une représentation de synthèse (par exemple limites régionales ou départementales **explicitement qualifiées**) sans prétendre afficher des communes absentes.
3. Les données administratives COG et les index de recherche restent chargés intégralement : **seul le rendu géométrique** est progressif dans cette première tranche.
4. La Normandie compte désormais neuf correspondances Pactols–COG 2026 versionnées au [lot #156](https://github.com/nicocoquet/adlfi-referentiels/pull/156), mais **aucun contour communal normand n'est ajouté ni affiché dans cette PR**.
5. Les mesures détaillées de performance navigateur et de mémoire sont encore à établir. Ne pas extrapoler le gain de temps depuis la seule réduction du nombre de téléchargements.
