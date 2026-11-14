# Pays de la Loire — contrôle structurel exhaustif des 806 ARK (14 novembre 2026)

**Statut : recette non validante ; aucun changement sur GitHub Pages.**

## Sources

Reconstruction de l'inventaire régional à partir des trois sources nationales de l'extraction XML v2 et du contrôle SKOS Pactols du 22 juillet 2026. Les SHA-256 des sources ont été confrontés au rapport `rapport-priorites-regionales.json`.

- `autorites_lieux.csv` : `878aa70f32d43313ea5bd36bbb30bbd6b57b4872ba2f68a5117ac6c35b6380b6`
- `occurrences_lieux.csv` : `b2e7332515c051e0c63e1fb29c840fa338aa85040fb2358a7df64d735b2942cd`
- `controle_concepts_pactols.csv` : `502db0f84188beca666d521417ad6775fb5f670c5b9a295250a9024fd4ede407`, récupéré dans l'artefact du [workflow de contrôle Pactols](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43587570258).

## Résultats établis sur l'ensemble des 806 autorités

| Indicateur | Résultat |
| --- | ---: |
| ARK terminaux | **806** |
| ARK avec code de commune dans l'assertion SKOS Pactols | **797** |
| ARK sans code communal numérique SKOS | **9** |
| Codes Insee distincts présents dans les assertions | **775** |
| Codes déclarés sur deux ARK distincts | **22** |
| ARK impliqués dans ces partages de code | **44** |
| Concepts classés comme « lieu imbriqué sous département » par la hiérarchie Pactols | **120** |
| Parmi ceux-ci, signalés `T2` dans la première catégorisation | **119** |

Le 120e lieu imbriqué est **Le Puy-Saint-Bonnet**, classé prioritairement `H1_episode_historique_interdepartemental`, car son code historique `79224` appartient à un autre département que le rattachement hiérarchique actuel.

### Répartition des 22 codes partagés

- Loire-Atlantique : **4**.
- Maine-et-Loire : **14**.
- Mayenne : **1**.
- Sarthe : **1**.
- Vendée : **2**.

### Liste des 22 couples de concepts partageant un code

| Code | Concept 1 | Concept 2 |
| --- | --- | --- |
| `44005` | Arthon-en-Retz | Chaumes-en-Retz |
| `44021` | Bourgneuf-en-Retz | Villeneuve-en-Retz |
| `44087` | Machecoul | Machecoul-Saint-Même |
| `44163` | Saint-Herblon | Vair-sur-Loire |
| `49018` | Baugé | Baugé-en-Anjou |
| `49021` | Beaufort-en-Vallée | Beaufort-en-Anjou |
| `49023` | Beaupréau | Beaupréau-en-Mauges |
| `49050` | Brissac-Quincé | Brissac Loire Aubance |
| `49069` | Champtoceaux | Orée d'Anjou |
| `49092` | Chemillé | Chemillé-en-Anjou |
| `49125` | Doué-la-Fontaine | Doué-en-Anjou |
| `49167` | Juigné-sur-Loire | Les Garennes sur Loire |
| `49244` | La Pommeraye (Mauges-sur-Loire) | Mauges-sur-Loire |
| `49248` | Pouancé | Ombrée d'Anjou |
| `49301` | Saint-Macaire-en-Mauges | Sèvremoine |
| `49323` | Saint-Sylvain-d'Anjou | Verrières-en-Anjou |
| `49331` | Segré | Segré-en-Anjou Bleu |
| `49367` | Vern-d'Anjou | Erdre-en-Anjou |
| `53255` | Sainte-Suzanne (Sainte-Suzanne-et-Chammes) | Sainte-Suzanne-et-Chammes |
| `72071` | Château-du-Loir | Montval-sur-Loir |
| `85009` | Auzay | Auchay-sur-Vendée |
| `85084` | Les Essarts (Essarts en Bocage) | Essarts en Bocage |

**Attention :** cette liste décrit uniquement la situation de l'export Pactols : un code partagé entre deux ARK. Elle ne prouve pas, sans les mouvements et périodes COG, la nature administrative des liens entre les deux autorités, ni la période de validité de leur emprise territoriale. Il est interdit de fusionner automatiquement ces 44 ARK.

## Suites techniques

Les fichiers de travail complets ont été générés localement et ne sont pas injectés dans le référentiel public : `inventaire-pays-de-la-loire.csv`, `collisions-codes-insee-22.csv`, `lieux-imbriques-120.csv`, `sans-code-communal-9.csv`, `rapport-structure-806.json`. Une archive de recette est fournie dans la conversation.

La prochaine analyse, qui **n'est pas encore exécutée sur les 806**, doit croiser les trois fichiers Insee COG 2026 (`v_commune_2026.csv`, `v_commune_depuis_1943.csv`, `v_mvt_commune_2026.csv`) pour qualifier `TYPECOM`, les dates des événements, les statuts de communes déléguées/associées, et les prédécesseurs/successeurs. Les fichiers officiels n'étaient pas accessibles dans l'environnement de calcul de cette session ; éviter d'interpréter les seules collisions comme des événements officiels vérifiés.

**Aucune nouvelle validation Pactols–COG ni géométrie historique attribuée.**
