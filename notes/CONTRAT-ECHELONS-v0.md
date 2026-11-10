# Échelon institutionnel — contrat de travail v0

> **Statut : proposition à instruire (10 novembre 2026).** Ce texte n'autorise aucune migration automatique du maître ni des données publiées.

## Motivation

Le champ `Organismes.echelon_territorial` est déjà rempli pour 202 des 653 ORG du maître 1.40. Il concerne notamment des musées, des DRAC et des établissements publics : il ne doit pas être réservé aux collectivités territoriales.

En revanche, le champ regroupe aujourd'hui des **échelons** (`communal`, `departemental`, `regional`, `national`) et des **formes institutionnelles** (`metropole`). L'interface en ligne écarte de la facette les ORG dont le type diffère de `collectivite_territoriale`, même lorsque l'échelon est connu.

## Dimensions à dissocier

1. **Nature de la structure** : `type_organisme`, vocabulaire existant, par exemple `collectivite_territoriale`, `epci`, `syndicat_mixte`, `musee`, `service_deconcentre_etat`.
2. **Échelon institutionnel** : `echelon_territorial`, niveau de l'autorité administrative, indépendant du lieu d'implantation et du territoire d'activité.
3. **Forme juridique ou institutionnelle détaillée** : métropole, communauté d'agglomération, communauté urbaine, communauté de communes, syndicat intercommunal, syndicat mixte ouvert/fermé, etc. La table existante `Statuts_historiques.forme_juridique` doit être étudiée comme support temporel avant d'ajouter un champ redondant.
4. **Territoire de compétence / d'activité** : dimension géographique séparée ; elle ne doit pas être inférée à partir de l'échelon.

Un organisme dont l'échelon est **non applicable** ne doit pas être confondu avec un organisme pour lequel il serait **pertinent mais non documenté**.

## Principes techniques non destructifs

- Conserver les identifiants des autorités et les relations historiques ; aucun regroupement par la seule ressemblance des noms.
- Pour les **EPCI métropolitains**, le niveau serait `intercommunal` ; la forme détaillée serait `metropole`.
- **Métropole de Lyon** : collectivité territoriale à statut particulier, pas EPCI ; la modalité exacte d'affichage reste à arbitrer sans l'assimiler à un EPCI.
- **Syndicats mixtes** : type institutionnel à conserver ; leur composition peut impliquer plusieurs échelons et ne justifie pas un niveau automatique.
- **Musées** : échelon pertinent selon l'autorité gestionnaire ; ne pas en déduire leur territoire d'activité ou le rayonnement de leurs collections.
- **SER** : envisager la déduction de l'échelon depuis les rattachements `rattachement_service` **validés et datés**, avec provenance. Une succession, une convention de participation ou une fusion constitutive ne sont pas des rattachements administratifs. En cas de changement historique de gestionnaire, ne pas projeter l'état récent sur toute l'histoire du service.
- Pour les **changements de forme au sein d'une même personne morale**, envisager des séquences dans `Statuts_historiques` ; si la personne morale change, conserver des autorités et des relations distinctes.

## Lot pilote : 46 autorités

Concentrer la vérification sur les ORG présentant `intercommunal`, `metropole` ou `metropolitain`, sur les types `epci` ou `syndicat_mixte`, et sur `ORG-0093` (Archéologie Alsace). Le maître 1.40 comprend 33 lignes `valide` et 13 lignes `a_verifier` dans ce lot : la validation d'une autorité ne vaut pas validation de chacun de ses attributs.

Dossiers sensibles :
- **ORG-0249** : Valenciennes Métropole est juridiquement une communauté d'agglomération, et non une métropole — [BANATIC](https://www.banatic.interieur.gouv.fr/intercommunalite/245901160-ca-valenciennes-metropole).
- **ORG-0429** : commune de Port-Vendres, échelon `intercommunal` incohérent, à rectifier `communal` après validation éditoriale.
- **ORG-0093** : Archéologie Alsace était un établissement public interdépartemental avant de devenir un syndicat mixte ouvert en décembre 2020 — [Archéologie Alsace](https://www.archeologie.alsace/fr/actualites/actualite?tx_news_pi1%5Baction%5D=detail&tx_news_pi1%5Bcontroller%5D=News&tx_news_pi1%5Bnews%5D=137). Le territoire alsacien n'implique pas un statut institutionnel `regional`.
- **ORG-0650** : Métropole de Lyon, statut particulier — [Insee](https://www.insee.fr/fr/information/7929497).
- **ORG-0652** : Grand Besançon Métropole demeure une communauté urbaine ; son libellé commercial ne crée pas le statut juridique de métropole — [Grand Besançon](https://www.grandbesancon.fr/la-communaute-urbaine/linstitution/que-fait-la-cu/).

## Audit reproductible

Depuis la racine du dépôt, avec le maître conservé **hors du GitHub public** :

```bash
python3 -m scripts.audit_echelons /chemin/vers/maitre.xlsx --output-dir /tmp/audit-adlfi-echelons
python3 -m unittest discover -s tests -v
```

Sorties : `rapport-echelon.json` (synthèse, inventaire, contrôles) et `points-a-verifier.csv`. Ce sont des **alertes**, pas des corrections : plusieurs alertes peuvent concerner la même autorité. Aucun XLSX n'est modifié, ni aucun JSON publié. Aucun changement de la facette n'est déployé à ce stade.

## Étapes conditionnées aux arbitrages

1. Valider le vocabulaire et le traitement des exceptions (notamment Lyon et les syndicats mixtes).
2. Corriger de façon documentée les ORG du lot pilote dans le maître suivant ; historiser les transformations datées.
3. Étendre la classification aux musées, puis construire l'héritage temporel des SER avec tests.
4. Modifier ensuite l'export JSON et la facette « Échelon institutionnel » ; contrôler les effectifs et l'absence de régression.
