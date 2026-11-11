# Lot 01 — arbitrages validés et modalités d'application

**Date :** 10 novembre 2026  
**État :** arbitrages éditoriaux acceptés ; modifications du maître encore à appliquer, sous contrôle.

Les identifiants et les données ci-dessous ont été vérifiés sur `AdlFI_referentiel_1-40_20261110_secteur_historique_DRASM_CNRAS.xlsx`. **Ne jamais déposer ce maître dans le dépôt public.**

## Corrections déterministes de la feuille `Organismes`

| ORG | Cellule cible (maître 1.40) | Ancienne valeur | Nouvelle valeur | Preuve |
| --- | --- | --- | --- | --- |
| ORG-0249 Valenciennes Métropole | `G241` / `type_organisme` | `collectivite_territoriale` | `epci` | BANATIC SIREN 245901160 |
| ORG-0249 | `M241` / `echelon_territorial` | `metropole` | `intercommunal` | BANATIC : communauté d'agglomération |
| ORG-0429 Commune de Port-Vendres | `M417` / `echelon_territorial` | `intercommunal` | `communal` | Insee COG 66148 |

Les coordonnées sont **propres au maître 1.40** ; ne pas les appliquer à un autre millésime sans rechercher la ligne par identifiant. Préserver `statut_validation=a_verifier` pour ces deux autorités, puisque toutes les autres caractéristiques ne sont pas validées.

**Forme actuelle d'ORG-0249 :** `communaute_agglomeration`. Date d'effet **31 décembre 2000**, selon BANATIC. Cette information peut entrer dans `Statuts_historiques.forme_juridique` (période depuis 2000-12-31) en attendant un vocabulaire de formes contrôlées stabilisé.

Sources :
- https://www.banatic.interieur.gouv.fr/intercommunalite/245901160-ca-valenciennes-metropole
- https://www.insee.fr/fr/metadonnees/geographie/commune/66148-port-vendres

## Maintien documenté — ORG-0650 (Métropole de Lyon)

- Garder `type_organisme=collectivite_territoriale` ; collectivité à statut particulier créée le 1er janvier 2015.
- La valeur `metropolitain` de l'échelon est conservée **provisoirement**, sans la convertir en `intercommunal` et sans la traiter comme une métropole-EPCI.
- Sa **forme juridique** peut être portée dans `Statuts_historiques.forme_juridique=collectivite_statut_particulier` avec `date_debut=2015-01-01`.
- La refonte de la facette devra gérer cette exception explicitement, en distinguant statut juridique et compétence territoriale.

Sources :
- https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000028528966/2026-04-29
- https://www.insee.fr/fr/information/7929497

## Dossier suspendu — ORG-0093 (Archéologie Alsace)

Le nom « Archéologie Alsace » recouvre **deux personnes morales** :
- SIREN **200006336** : établissement public interdépartemental, 2006–2020.
- SIREN **200094746** : syndicat mixte ouvert créé le **11 décembre 2020**, par substitution de personne morale.

Le maître 1.40 concentre les deux périodes dans `ORG-0093` (activité indiquée depuis 2006) et 181 occurrences d'affiliations. **Ne pas effacer ou renommer `ORG-0093` sans arbitrage d'identifiant**, ni lui attribuer définitivement `syndicat_mixte` tout en conservant les affiliations anciennes, ce qui produirait une fausse identité intemporelle.

Il faudra :
1. Choisir laquelle des deux personnes morales conserve `ORG-0093` ; créer une seconde autorité stable.
2. Créer la relation datée `succession_institutionnelle`, sans transformer un rattachement historique en succession.
3. Répartir les affiliations existantes sur une base **chronologique documentée**, en vérifiant leurs notices sources.
4. Corriger les dates `date_debut` / `date_fin` et les formes des deux autorités ; veiller à ne pas rétroprojeter un rattachement à la CeA.
5. Compléter idéalement les ORG françaises avec un `identifiant_siren` facultatif pour fiabiliser les limites de personne morale, sans l'étendre aux personnes étrangères ou non immatriculées.

Sources :
- https://www.banatic.interieur.gouv.fr/intercommunalite/200094746-smo-archeologie-alsace-aa
- https://www.archeologie.alsace/fr/actualites/actualite?cHash=9e5ed42a8371c6403457d8a378449e67&tx_news_pi1%5Baction%5D=detail&tx_news_pi1%5Bcontroller%5D=News&tx_news_pi1%5Bnews%5D=137

## Publication

Aucune modification de `docs/data/organismes.json` ou de la facette n'est à publier tant que le **XLSX maître** n'a pas été consolidé et le nouveau JSON vérifié par les tests. Les données du site restent celles du maître 1.40.
