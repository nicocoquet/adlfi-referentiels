# Politique d'alignement Pactols ↔ COG (communes)

**Décision éditoriale du 16 novembre 2026**, prise après l'audit du premier lot de Guyane et applicable aux lots territoriaux suivants. Cette politique règle la validation des **correspondances entre identifiants**, non la validité de l'ensemble des données d'une commune.

## Principe d'acceptation

Une correspondance **commune COG au millésime étudié ↔ concept Pactols** est **validable sans confirmation manuelle supplémentaire** lorsque **toutes** les conditions suivantes sont réunies :

1. Le concept est retrouvé dans un **export Pactols Lieux RDF identifié par commit, date et SHA-256** ; son identifiant ARK est complet et unique.
2. Le concept porte une **assertion explicite `skos:exactMatch`** vers l'URI géographique INSEE de forme `http://id.insee.fr/geo/commune/XXXXX` (ou la variante HTTPS équivalente), dont le code figure comme **commune de type COM** dans le COG de référence.
3. La relation est **non ambiguë** dans le lot : un seul ARK admissible par code COG, un seul code COG par concept pour cette assertion, absence d'autre correspondance contradictoire, d'identifiant recyclé comme autre nature administrative ou de rattachement temporel incompatible.
4. Le concept n'est **ni déprécié ni remplacé** dans la source examinée. Le libellé est cohérent ; une précision géographique entre parenthèses est admissible (ex. « Saint-Georges (Guyane) »). Les divergences substantielles de dénomination restent à instruire.
5. La décision est **traçable** : code et libellé COG, ARK, URI exacte citée, prédicat RDF, état de dépréciation, millésime, source épinglée, date et statut de validation conservés dans un registre de décisions versionné.

**Si ces conditions sont réunies**, le lien peut recevoir le statut **`VALIDE_ADLFI_2026`** pour l'état COG du **1er janvier 2026** (ou l'état daté explicitement étudié dans les lots suivants). La validation éditoriale est appliquée par règle et documentée ; elle n'est pas une inférence à partir d'une homonymie.

## Cas exclus de la validation automatique

- L'URI n'apparaît que comme texte, note ou source vague, sans relation `skos:exactMatch`.
- Relation `skos:closeMatch`, `skos:relatedMatch`, `owl:sameAs` ou tout prédicat autre que l'assertion exacte retenue : **examen spécifique**.
- Code INSEE désignant une commune **historique absente du millésime courant**, un arrondissement, une circonscription ou un autre zonage. Conserver le concept avec son propre ARK sans le raccorder automatiquement à un successeur.
- Concept déprécié, remplacé, doublon ARK, plusieurs ARK pour le même code ou plusieurs codes contradictoires pour un concept.
- Libellé manifestement incompatible ou date de référence indéterminée.

Une assertion `skos:exactMatch` est une **preuve forte de correspondance sémantique entre autorités**, pas un certificat de permanence de l'identité juridique du territoire à travers les siècles. Voir [W3C, SKOS Simple Knowledge Organization System Primer](https://www.w3.org/TR/skos-primer/).

## Portée limitée de la décision

**La validation porte exclusivement sur le couple Pactols–COG pour le millésime retenu.**

Elle ne valide **pas** :

- les **contours IGN/data.gouv** et leur adéquation géographique à l'état de la commune ;
- les **frontières historiques** ou le report de la géométrie 2026 vers 1943–2025 ;
- les **successions, fusions et démembrements** ou la continuité historique d'un identifiant ;
- les autres champs descriptifs, relations administratives ou données documentaires d'une fiche.

Le COG tient les **couples code–libellé et leurs périodes** séparément des géométries (Insee : https://www.insee.fr/fr/information/2560452).

## Première application : Guyane, 22 communes actuelles

Le lot 01 a établi **22 relations `skos:exactMatch` univoques vers les 22 codes COG 2026**. Les 22 ARK sont distincts ; les concepts ne sont pas déclarés dépréciés dans l'export Pactols du **22 juillet 2026**. La précision « Saint-Georges (Guyane) » est conservée comme désambiguïsation.

**Validation éditoriale confirmée le 16 novembre 2026 pour les 22 relations**, dans `recette/lieux/GUYANE-VALIDATIONS-PACTOLS-COG-2026.csv`, issue du rapport de source `guyane-pactols-candidats-26.csv` (SHA-256 **b9d7d7c84f1b5d5f39dee30a16cb2cbc18d10c1b13bd07964eea5fb5ba7f98dc**), qui provient du RDF épinglé (SHA-256 **3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7**).

Les **4 autres concepts** vers 97351, 97354, 97355, 97359 restent **historique à instruire** ; ils ne sont pas concernés par cette validation.

La recette conserve la distinction entre un **rapport brut antérieur à la décision** (tous candidats `A_INSTRUIRE`) et le **registre éditorial post-validation**. Le code de publication superpose les deux et contrôle les preuves : `scripts/extraire_index_public_outremer_2026.py`, CI Guyane et tests. Les **16 relations Mayotte déjà approuvées** restent identiques : le total publié après la Guyane était de **38** (22 Guyane et 16 Mayotte). **Le lot Martinique du 16 novembre 2026 ajoute ensuite 34 exactMatch univoques**, inscrits dans `recette/lieux/MARTINIQUE-VALIDATIONS-PACTOLS-COG-2026.csv`, portant le total actuel à **72 correspondances validées**. Les 7 préfLabels Pactols précisés par « (Martinique) » sont conservés comme désambiguïsations.

**Le lot Guadeloupe du 17 novembre 2026** ajoute **32 correspondances `skos:exactMatch` univoques** pour le COG 2026, conservées dans `recette/lieux/GUADELOUPE-VALIDATIONS-PACTOLS-COG-2026.csv`, portant le total ultramarin à **104 relations validées**. Sept libellés Pactols présentent une désambiguïsation explicite « (Guadeloupe) ». Les codes historiques `97123` et `97127` sont exclus des 32 décisions 2026 ; leur ancienne présence dans le COG ne constitue pas un alignement Pactols. Pour les prochains lots, conserver la même structure de preuves et de décision, sans promouvoir les simples concordances nominales.
