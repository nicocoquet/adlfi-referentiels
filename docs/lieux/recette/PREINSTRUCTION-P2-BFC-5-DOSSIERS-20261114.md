# Lieux — Bourgogne-Franche-Comté : préinstruction des cinq dossiers P2

**14 novembre 2026 — PR n°24 — recette non validante.**

## Périmètre et méthode

Les cinq dossiers P2 issus du lot éditorial de 29 relations sont examinés à partir :
- des assertions Pactols documentées dans `LOT-P2-BFC-5-CANDIDATURES.csv` ;
- des trois concepts pertinents à la désambiguïsation de Hauteroche, restitués depuis le RDF Pactols-Lieux th17 du **22 juillet 2026**, dans `LOT-P2-BFC-CONTEXTE-ARK-39177.csv` ;
- de `v_commune_2026.csv` et `v_mvt_commune_2026.csv` de l'Insee, dont les SHA-256 sont **exigés dans l'auditeur**.

Script : `scripts/instruire_p2_bfc_cog.py`. Contrôles : `tests/test_instruire_p2_bfc_cog.py`, workflow `audit-lieux-bfc-cog2026.yml`.

**Unités de comptage distinctes : 5 candidatures de relation documentaire, 6 événements administratifs datés et 19 lignes COG avant/après.** Parmi ces 19 lignes, **16** correspondent aux cinq événements initiaux (2 + 2 + 6 + 3 + 3), et **3** à la suppression ultérieure des communes déléguées de Hauteroche, en 2020.

Les tableaux fournis sont des **preuves et propositions de nature de relation**, pas des validations de successions entre ARK, ni des équivalences `skos:exactMatch`.

## Dossiers et orientations éditoriales proposées

| Ancien concept Pactols | Commune réceptrice ou parente | Épisode Insee | Nature de relation à instruire |
| --- | --- | --- | --- |
| **Marchaux**, `26678/pcrtHVMF65Ey3z`, code `25368` | **Marchaux-Chaudefontaine**, `26678/pcrtPEJhK71UsV`, code `25368` | `MOD=32`, **2018-01-01** | **Participation à la création d'une commune nouvelle**, pas équivalence conceptuelle |
| **Sancey-le-Grand**, `26678/pcrtSYhbegbvSU`, code `25529` | **Sancey**, `26678/pcrtqvgozFu6dO`, code `25529` | `MOD=32`, **2016-01-01** | **Participation à la création d'une commune nouvelle**, code conservé mais entité nouvelle |
| **Mirebel**, `26678/pcrtSkDaYjLST1`, code `39332` | **Hauteroche (Jura)**, `26678/pcrtdDWDTOLZXu`, code `39177` | `MOD=32`, **2016-01-01** ; `MOD=35`, **2020-03-15** | Participation à une création, **puis suppression du statut COMD** de Mirebel |
| **Antorpe**, `26678/pcrtdIcMrh2mh8`, code `39012` | **Saint-Vit**, `26678/pcrtw7D5DZnli2`, code `25527` | `MOD=33`, **1974-06-01** | **Rattachement administratif par fusion-association**, pas succession/équivalence |
| **Frettes**, `26678/pcrtANt29rHaDo`, code `52210` | **Champlitte**, `26678/pcrtNslpgoFloZ`, code `70122` | `MOD=33`, **1974-07-01** | **Rattachement administratif par fusion-association**, pas succession/équivalence |

### 1. Marchaux et Sancey : codes conservés, nouvelles communes distinctes

Les deux lignes COG de Marchaux-Chaudefontaine (`25368`) décrivent les participations de **Marchaux (`25368`)** et **Chaudefontaine (`25137`)** au **1er janvier 2018**. Celles de Sancey (`25529`) concernent **Sancey-le-Grand (`25529`)** et **Sancey-le-Long (`25530`)** au **1er janvier 2016**.

Le code `25368`, comme `25529`, demeure identique au précédent code d'une commune fondatrice. Ce constat **n'autorise pas à fusionner les deux ARK** ni à attribuer rétrospectivement la géométrie 2026 à la commune ancienne. Une relation `a_participé_à` portant sur un événement daté est plus fidèle à l'évolution administrative qu'un `sameAs` ou un `skos:exactMatch` entre les concepts.

Références Insee :
- https://www.insee.fr/fr/statistiques/2011101?geo=COM-25368
- https://www.insee.fr/fr/statistiques/8643952?geo=COM-25529

### 2. Mirebel : deux événements distincts et une homonymie

**2016-01-01, `MOD=32` :** six lignes documentent l'opération Hauteroche. Les anciennes communes **Crançot (`39177`)**, **Granges-sur-Baume (`39260`)** et **Mirebel (`39332`)** rejoignent **Hauteroche (`39177`)**, tout en devenant communes déléguées.

**2020-03-15, `MOD=35` :** trois lignes enregistrent la suppression du **statut COMD** pour ces trois anciennes communes. Elles ne décrivent ni une disparition des lieux ni une nouvelle fusion.

Trois concepts sont à distinguer pour le nom Hauteroche et le code historique `39177` ; **seuls deux portent effectivement ce code** :
- **Hauteroche (Jura)**, ARK `26678/pcrtdDWDTOLZXu` : `skos:exactMatch` `39177`, `skos:broader` `26678/pcrtX910KjTURm` (Jura) ;
- **Crançot**, ARK `26678/pcrtycqXknDXqF` : ancien nom/ancienne commune, `skos:exactMatch` `39177`, `skos:broader` vers le concept Hauteroche (Jura) ;
- **Hauteroche (Côte-d'Or)**, ARK `26678/pcrtayvw3natsF` : **autre commune**, `skos:exactMatch` **`21314`**, `skos:broader` `26678/pcrtGQwa5EVqVh` (Côte-d'Or).

Plus précisément, les deux premiers partagent `39177` ; **le concept Hauteroche de Côte-d'Or possède le code distinct `21314`**. Il serait incorrect de mettre les trois sur le même code. L'accord du **nom qualifié**, du **code Insee** et du **parent Pactols Jura** permet de désambiguïser la cible Mirebel → Hauteroche.

Sources :
- https://www.insee.fr/fr/statistiques/2011101?geo=COM-39177
- https://www.insee.fr/fr/metadonnees/geographie/commune/21314-hauteroche
- RDF Frantiq, `Pactols_Lieux_th17_20260722.rdf`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.

### 3. Antorpe et Frettes : fusions-associations interdépartementales

L'Insee observe simultanément, pour chacune, deux transitions `MOD=33` de la commune initiale : l'une vers la commune parente de type `COM`, l'autre vers le statut **`COMA` portant le code historique**. Une troisième ligne décrit la continuité du code du récepteur.

Au COG du **1er janvier 2026** :
- **Antorpe**, `TYPECOM=COMA`, `COM=39012`, `COMPARENT=25527` (**Saint-Vit**, département **25**) ;
- **Frettes**, `TYPECOM=COMA`, `COM=52210`, `COMPARENT=70122` (**Champlitte**, département **70**).

**Les préfixes `39` et `52` sont des codes historiques légitimes**, malgré le rattachement à une commune parente située dans un autre département. L'Insee confirme ces deux passages interdépartementaux dans les séries historiques harmonisées. Il faut conserver simultanément le code propre à la commune associée, le parent administratif observé en 2026 et l'événement initial de 1974.

Références :
- https://www.insee.fr/fr/statistiques/8643952?geo=COM-25527
- https://www.insee.fr/fr/statistiques/8643952?geo=COM-70122
- https://www.insee.fr/fr/statistiques/8292790?sommaire=2414232

Un `COMPARENT` 2026 n'est pas à lui seul une preuve de continuité du rattachement à toutes les dates intermédiaires. Le COG de mouvements permet néanmoins de documenter le début de la fusion-association en 1974, et le COG courant son état administratif au millésime 2026.

## Modèle éditorial recommandé

Pour ce lot, ne pas créer une relation indifférenciée « successeur de » entre deux ARK. Modéliser séparément :

1. **Concept Pactols** : ARK propre au lieu, même si son code Insee est réutilisé ;
2. **Événement administratif** : identifiant interne de recette, date d'effet, modalité `MOD`, toutes les lignes avant/après, preuve Insee ;
3. **Participation à l'événement** : concept ancien et commune nouvelle réceptrice, avec rôle explicite ;
4. **Rattachement de commune associée** : identité COMA et `COMPARENT` millésimé, avec provenance ;
5. **Évolution du statut administratif** : notamment `COMD → COM` lors des suppressions de 2020.

Les termes de relation proposés sont des **catégories internes de modélisation**, pas des propriétés SKOS standard. Un `skos:exactMatch` ne doit pas être employé pour une succession de communes.

## Sorties et statut

La CI de la branche produit le dossier `preinstruction-p2/` :
- `preinstruction-p2-bfc-5.csv` : cinq relations candidates, décision/justification/vérificateur/date **vides** ;
- `evenements-p2-bfc-6.csv` : six épisodes, dont une suppression de statut ;
- `preuves-mouvements-p2-bfc-19.csv` : dix-neuf lignes d'origine COG avant/après ;
- `contexte-hauteroche-p2-bfc-3.csv` : distinctions entre Hauteroche (Jura), Crançot et Hauteroche (Côte-d'Or) ;
- `rapport-p2-bfc.json` : cardinalités, SHA-256 des sources et limites.

Le script contrôle les quatre empreintes des sources, les dates et les modalités des mouvements, les états `COM`/`COMA` au millésime 2026, le statut `COMD` puis sa suppression pour Mirebel, et les trois concepts nécessaires à la désambiguïsation. La CI exécute deux générations successives et exige des sorties identiques.

**Résultat : cinq dossiers P2 préinstruits techniquement ; zéro nouvelle relation validée, zéro `skos:exactMatch` ajouté, zéro géométrie historique attribuée. PR n°24 en brouillon.**
