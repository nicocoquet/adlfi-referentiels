# Aperçu national Lieux : recherche Pactols–COG et curseur unique

**14 novembre 2026 — recette fonctionnelle de la PR n°24, non publiée.**

## Ce qui fonctionne

Un premier aperçu autonome est disponible sous `recette/lieux/apercu-national.html`, avec les deux jeux de données exportés dans un paquet ZIP séparé :

- **9 928 autorités Pactols attestées dans les XML AdlFI** : recherche par ARK, libellé et formes XML, nombre de mentions et de notices ;
- **39 162 identifiants administratifs Insee** : recherche par code et anciens noms depuis 1943 ;
- **Curseur unique 1943–2026**, initialement positionné sur **2026**, interprété comme le **1er janvier** de l'année choisie ;
- **Fiche d'un code Insee** : forme administrative applicable au 1er janvier et événements COG déjà survenus, avec prudence sur les anciens statuts de commune associée/déléguée ;
- **Fiche d'un ARK Pactols** : identifiant et métadonnées XML ; code Insee uniquement pour les **103 correspondances PACA éditorialement validées** au millésime 2026 ;
- **Carte Leaflet à fond actuel**, superposant **uniquement en 2026** les 103 contours PACA du pilote validé. Les contours sont masqués quand l'année sélectionnée est antérieure à 2026.

Les résultats sont explicitement séparés en **« Pactols » et « Insee »** même pour des noms identiques : rechercher « Marchaux » fait apparaître distinctement un ARK documentaire et un code communal. Une autorité Pactols sans correspondance validée ne reçoit **ni code Insee ni géométrie** par rapprochement lexical.

## Portée temporelle de la validation PACA

Une correspondance Pactols–COG du pilote PACA a été validée pour le **millésime 2026**. Lorsque l'utilisateur choisit une année antérieure, le moteur peut afficher **l'état historique du même code Insee**, mais dans un champ **« consultation documentaire du même code »**. Il ne présente pas cet état comme une identité Pactols–COG historiquement validée.

Les années d'opération archéologique figurant dans les notices XML ne datent ni les noms administratifs ni les contours communaux.

## Tests effectués

La CI `audit-lieux-cog-national-temporel.yml` vérifie :

1. Les 98 segments COG, 42 288 périodes de communes et 13 734 mouvements distincts ;
2. Les tests Node du **moteur de recherche commun** et la syntaxe JavaScript de l'aperçu ;
3. Les homonymies Hauteroche, les noms anciens Marchaux et Verdun-Ciel, et la distinction des résultats d'autorité et de code ;
4. La recherche historique indépendante de l'année, et les transitions au 1er janvier ;
5. L'interdiction de rétroprojeter en 2017 une correspondance Pactols–COG qui n'a été validée qu'en 2026 ;
6. Les performances de classement par **top-K** des résultats lorsque des milliers de formes concurrentes existent.

Une recette locale sur **l'intégralité des 49 090 entrées** a également contrôlé les quatre transitions Marchaux (2018), Chemilla (2019), Verdun-Ciel (2025) et Vaire (2016–2017), ainsi que le statut d'Antorpe (commune associée en 2026, non rétroprojetée en 1975).

**Limite actuelle :** un contrôle automatisé du moteur et de ses données ne remplace pas une recette visuelle et d'interaction dans plusieurs navigateurs. Le navigateur de l'environnement d'exécution a bloqué l'accès aux URL locales ; ce test graphique reste donc à conduire depuis un navigateur normal. Le fond cartographique et les tuiles nécessitent une connexion externe.

## Lancer l'aperçu autonome sur macOS

Décompresser `AdlFI_Lieux_apercu_national_fonctionnel_20261114.zip`, ouvrir un terminal dans le répertoire extrait, puis :

```bash
python3 -m http.server 8000
```

Ouvrir : **http://localhost:8000/recette/lieux/apercu-national.html**.

Des exemples utiles : rechercher **Marchaux**, puis passer de **2017 à 2018** ; rechercher **Hauteroche** et examiner les deux résultats Insee ; rechercher **Verdun-Ciel** (2024 puis 2025) ; rechercher **Antorpe** (1974, 1975, 2026) ; rechercher **Draix**, sélectionner l'autorité Pactols et déplacer le curseur avant 2026.

## Limites avant publication

- L'aperçu utilise un **paquet JSON de recette autonome**, non des fichiers publiés sous `docs/data` ;
- La carte ne représente actuellement que les 103 contours PACA validés au millésime 2026 ; **aucune géométrie historique** n'est disponible ou inventée ;
- Les **29 candidatures historiques de Bourgogne-Franche-Comté** restent non validées, même lorsque leurs événements Insee sont établis ;
- Les communes et statuts COG antérieurs à 1943, les périodes COMA/COMD continues et les lieux Pactols jamais présents dans les XML AdlFI ne sont pas traités par cet export ;
- La publication du module national nécessitera un paquet JSON de production, une recette d'interface et des arbitrages éditoriaux explicites.

Le code de l'aperçu et ses tests sont versionnés dans la branche de recette. **`docs/lieux/index.html`**, **`docs/data/lieux.json`** et la publication GitHub Pages ne sont pas modifiés. **La PR n°24 reste en brouillon.**
