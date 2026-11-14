# PACA — reprise de l'audit historique au protocole commun

**14 novembre 2026 — recette non validante.**

## Pourquoi reprendre PACA

Le pilote régional a permis de publier **103 relations Pactols–COG validées pour le millésime 2026**. Il n'a pas encore suivi le protocole d'audit historique des opérations COG appliqué à la Bourgogne-Franche-Comté, aux Pays de la Loire et à la Corse. Notre objectif est une **structure de preuve identique** dans les quatre régions, sans effacer les décisions acquises.

**Précision sur le périmètre :** la table éditoriale originale contient **218 lignes de portée nationale**, non 218 lieux de PACA :

| État d'origine | Nombre |
| --- | ---: |
| PACA validées et publiées, COG 2026 | **103** |
| PACA encore candidates | **7** |
| Autres territoires ou lieux sans code communal proposé | **108** |
| **Total de la table d'origine** | **218** |

La sous-sélection des sept candidats provient du fichier éditorial du dépôt privé `nicocoquet/atlas-documentaire`, commit `bc0455c7d1dbf65f579e9b25a01eb7928a8054d5`, chemin `experimentation/donnees/autorite_pactols_insee.csv`, empreinte Git blob `8d039fe574413df89524b39540ba962ce89ca0a0`.

La table privée complète n'est pas copiée ici. Le CSV `paca-sept-candidatures-20261114.csv` n'est **pas une validation**. Les sept objets concernés sont : **La Ciotat, Hyères, Villefranche-sur-Mer, Martigues, Cannes, Nice et Marseille**.

## Vérification historique

La commande `scripts/auditer_lieux_paca_historique.py` rapproche ces **110 objets documentaires** avec les sources officielles COG 2026, sans aucun géocodage implicite :

- identité et statut éditorial d'origine (103 liens existants conservés ; 7 propositions laissées ouvertes) ;
- code, nom et département au **COG 2026**, avec appartenance à la région 93 attestée ;
- périodes historiques de noms de communes `COM` ;
- lignes de mouvements officiels `MOD`, datées, y compris changements de statut et de périmètre ;
- cas ayant plusieurs formes ou événements, à **soumettre à l'instruction**, sans attribuer de succession ni d'équivalence SKOS automatique.

La sortie `PACA-110-REVUE-HISTORIQUE.csv` distingue explicitement :

1. `validation_millesime_2026` : **décision antérieure existante** ;
2. `etat_audit_historique` : données administratives réunies, mais **relation historique non revalidée** ;
3. `decision_historique`, `justification_decision`, `verificateur`, `date_validation` : **tous vides**.

Les événements produisent leurs propres preuves dans `PACA-MOUVEMENTS-COG.csv` et `PACA-RAPPORT-AUDIT.json`.

Les deux géométries historiques et les nouvelles validations sont systématiquement à zéro dans le rapport. Le fond cartographique 2026 déjà publié n'est pas une géométrie de 1943.

## Conditions d'un véritable corpus PACA exhaustif

**Les 110 lignes de cette revue sont le périmètre du pilote plus sept candidatures, pas l'inventaire exhaustif de PACA.** Une seconde passe devra comparer :

- l'ensemble des ARK du corpus XML AdlFI dont la localisation régionale est attestée (sans déduire la région des seules années d'opération) ;
- la branche du thésaurus Pactols correspondant aux six départements PACA, avec vérification des identifiants hiérarchiques et des toponymes homonymes ;
- les changements historiques de commune, la réutilisation des codes, les communes associées/déléguées, et les cas DPM/Drassm qui ne sont pas réductibles à une commune ;
- les **31 formes SKOS** du pilote déjà documentées, à qualifier à part des relations administratives ;
- les sept dossiers encore sans validation et les trois grandes villes (Nice, Marseille, Hyères) précédemment écartées des géométries du pilote.

Les agrégats de la table initiale ne permettent **pas de conclure** que tous les concepts PACA ont été recensés ; le contrôle d'exhaustivité demandera la confrontation des XML, de Pactols et des couches administratives.

## Traçabilité et non-publication

Les trois sources COG sont vérifiées par SHA-256, les 110 codes doivent être des communes du millésime 2026 appartenant aux six départements attendus, et les sorties sont produites deux fois avec comparaison octet par octet. Les scripts échouent si une validation a été renseignée parmi les sept dossiers.

La CI `Lieux — parité PACA historique (recette)` archivera un CSV par autorité, le registre des mouvements et le rapport JSON, **en artefact uniquement**. Aucune entrée de `docs/data` ni de la page `docs/lieux/index.html` n'est modifiée par cette branche.

Un garde-fou `tests/test_isolement_recette_lieux.py` interdit désormais d'inclure sous `docs/lieux/recette` ou `docs/lieux/rapports` des rapports qui deviendraient accessibles sur GitHub Pages : **la PR #24 restera bloquée tant que ces fichiers n'auront pas été sortis de `docs/`**.
