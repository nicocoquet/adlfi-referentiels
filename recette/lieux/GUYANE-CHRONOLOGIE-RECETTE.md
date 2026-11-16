# Guyane — chronologie administrative et couverture cartographique

**16 novembre 2026 · Lot 02 · recette non publiée.**

## Objet

Consolider les **22 communes COG 2026**, les **26 codes communaux distincts**, les **41 périodes** et les **52 lignes de mouvements** de la série 973 déjà audités. Les **22 ARK Pactols des communes actuelles** sont validés éditorialement pour l'état COG 2026 ; les quatre ARK des codes anciens **97351, 97354, 97355, 97359** sont conservés séparément.

Le script scripts/construire_chronologie_guyane.py génère la situation administrative au **1er janvier de chaque année entre 1943 et 2026** : codes, libellés, épisodes de validité et événements COG. **Aucune géométrie historique n'est inférée.** Les 22 alignements de 2026 ne sont pas rétroprojetés.

## Conventions chronologiques

- [Insee, fichiers COG et leur historique depuis 1943](https://www.insee.fr/fr/information/2560452) : la validité d'un couple code–libellé est un intervalle de dates.
- [Insee, portail historique des communes de Guyane](https://www.insee.fr/fr/metadonnees/historique-commune?debut=0&departement=973&taille=100) : changements de noms, créations, fusions et démembrements.
- [Insee, modalités des événements communaux](https://www.insee.fr/fr/information/8377252) : MOD 10 = changement de nom ; MOD 20 = création ; MOD 31 = fusion simple.

Le fichier des mouvements COG mentionne la réorganisation **du 27 mars 1969**, tandis que le portail Insee la présente **au 26 mars 1969**. Ces dates ne doivent pas être uniformisées sans qualification. Une vue **au 1er janvier 1969** représente l'état avant les changements de mars ; la vue **au 1er janvier 1970** leur état postérieur.

Les premières périodes COG observées commencent en 1946. L'absence d'observations actives en 1943 est une **absence de couverture par cette source**, pas la preuve de l'absence d'institutions communales.

## Événements à instruire

| Groupe | Mouvement documenté | Précaution |
| --- | --- | --- |
| 1949–1953 | Ouanary / Oyapoc ; créations et changements de dénomination concernant Approuague, Samson, Moyenne-Mana, La Comté, Grand-Santi, Maripasoula et Saint-Élie | Création, changement de nom et déplacement de frontière sont des opérations distinctes |
| 1969 | Fusions impliquant 97351 → 97301, 97354 → 97352, 97355 → 97306 et 97359 → 97310 ; réorganisations et changements de noms | Date des mouvements COG : 27 mars ; ne pas traiter une fusion comme un renommage |
| 1976 | Création d'Apatou à partir de Grand-Santi-Papaichton | MOD et dates d'effet à conserver par ligne |
| 1989 | Détachement d'Awala-Yalimapo de Mana | Date d'effet 1er janvier 1989 dans le COG |
| 1993 | Division de Grand-Santi-Papaichton et création de Papaichton | Date d'effet 1er janvier 1993 dans le COG |

Le rapport de recette conserve **les lignes avant/après du COG**, leur MOD et leur date. Ces relations sources ne sont pas une approbation d'une succession juridique permanente ni d'un polygone cartographique.

## Résultats contrôlés du lot 02 — chronologie effective

[CI de recette n°43931916896](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43931916896) : génération de **84 vues au 1er janvier**, **41 périodes COG**, **52 lignes de mouvements sur 8 dates distinctes** et **4 autorités disparues**. Le comptage s'établit comme suit :

| Date d'effet COG | Lignes de mouvements | Modalités | Avant → Après (nombre de communes) |
| --- | ---: | --- | ---: |
| 21 mars 1946 | 18 | 18 créations (20) | 0 → 18 dans le fichier COG (le 0 ne désigne pas un vide historique réel) |
| 12 novembre 1949 | 1 | 1 création (20) | 18 → 19 |
| 7 avril 1950 | 2 | 2 lignes création (20) | 19 → 20 |
| 1er janvier 1953 | 11 | 5 changements de nom (10), 6 lignes création (20) | 20 → 23 |
| 27 mars 1969 | 14 | 6 changements de nom (10), 8 lignes fusion (31) | **23 → 19** |
| 12 novembre 1976 | 2 | 2 lignes création (20) | 19 → 20 |
| 1er janvier 1989 | 2 | 2 lignes création (20) | 20 → 21 |
| 1er janvier 1993 | 2 | 2 lignes création (20) | 21 → 22 |

Le **nombre de lignes** d'un événement de création ou de fusion n'est pas nécessairement égal au **nombre de communes créées ou supprimées** : une seule transformation peut comporter une ligne pour la commune conservée et une autre pour le territoire détaché.

### Photographies administratives au premier janvier

| Année | Communes attestées |
| --- | ---: |
| 1943 et 1946 | 0 actif dans le fichier au premier janvier, faute d'observations antérieures au 21 mars 1946 |
| 1947 | 18 |
| 1953 | 23 |
| 1969 | 23 (avant la réforme de mars) |
| 1970 | 19 |
| 1976 | 19 (avant la création d'Apatou) |
| 1977 | 20 |
| 1989 | 21 |
| 1993 et 2026 | 22 |

### Liens issus des mouvements de fusion simple du 27 mars 1969

Ces quatre transitions sont **explicitement représentées par des lignes MOD 31** du fichier COG. Elles fournissent le *sens de l'événement administratif*, mais **pas** une équivalence entre les concepts Pactols ni une géométrie de l'ancienne commune.

| Ancien code et libellé final | Code destinataire | Date COG | Nature |
| --- | --- | --- | --- |
| 97351 — Approuague (chef-lieu Régina) | 97301 — Régina | 1969-03-27 | Fusion simple COG |
| 97354 — Samson (chef-lieu Dégrad-Samson) | 97352 — Saül | 1969-03-27 | Fusion simple COG |
| 97355 — Moyenne-Mana (chef-lieu Mana) | 97306 — Mana | 1969-03-27 | Fusion simple COG |
| 97359 — La Comté (chef-lieu Dégrad-Edmond) | 97310 — Roura | 1969-03-27 | Fusion simple COG |

**Périodes de libellé final** : les quatre noms précédents sont attestés entre **le 1er janvier 1953 et le 27 mars 1969** (fin exclue). Les codes 97351, 97354 et 97355 existaient avant le 1er janvier 1953 avec d'autres noms COG : Centre-Approuague, Haute-Mana et Mana respectivement. **La Comté (97359)** n'a qu'un épisode répertorié à compter du 1er janvier 1953.

## Quatre autorités historiques distinctes

| Code ancien | ARK Pactols | Statut |
| --- | --- | --- |
| 97351 | 26678/pcrtIPUh7AuXTg | Concept historique à instruire |
| 97354 | 26678/pcrtRJeVr9K5TB | Concept historique à instruire |
| 97355 | 26678/pcrtbvSjznYKWV | Concept historique à instruire |
| 97359 | 26678/pcrtCD30P0XhAE | Concept historique à instruire |

Le registre recette/lieux/GUYANE-CANDIDATS-HISTORIQUES-PACTOLS-2026.csv contient ces quatre identifiants. Ils sont confrontés aux preuves exactMatch de l'export RDF Pactols daté de juillet 2026, mais **aucun n'est fusionné avec une commune actuelle**.

## Inventaire cartographique — sources candidates

| Source | Périodes indiquées | Statut pour la Guyane |
| --- | --- | --- |
| [IGN BD TOPO Historique](https://www.data.gouv.fr/datasets/bd-topo-r-historique) | Saisons 1993–1996 et 1994–2002 ; BD TOPO Pays 2002–2009, dont DOM pour la saison 3 | **À inspecter** : présence effective des limites communales de Guyane non vérifiée. Les saisons 1–2 ne doivent pas être présumées couvrir la Guyane |
| [Archives GEOFLA et ADMIN EXPRESS](https://www.data.gouv.fr/pages/donnees-geographiques) | GEOFLA : éditions annoncées en 1997, 2002 et 2010–2016 ; ADMIN EXPRESS depuis 2017 | **À inspecter** : packages de Guyane, couches, date du levé ou de l'édition et précision géométrique |
| [Contours administratifs Etalab](https://www.data.gouv.fr/datasets/contours-administratifs) | Référence du 4 mai 2026 déjà contrôlée | **22/22 polygones valides topologiquement**, mais non représentatifs automatiquement de 1953, 1969, 1976, 1989 ou 1993 |
| Actes et plans d'archives, cartes IGN datées | Variable | **À rechercher** en priorité pour les divisions antérieures aux années 1990 |

Une union des polygones 2026 (par exemple Mana + Awala-Yalimapo, ou Grand-Santi + Papaichton + Apatou) reste **une hypothèse de reconstruction**, jamais une limite historique officielle par défaut. Elle ne pourra être retenue que si les changements complémentaires et la provenance cartographique sont vérifiés.

## Livraison reproductible

Le script scripts/construire_chronologie_guyane.py et le test tests/test_construire_chronologie_guyane.py sont exécutés dans la CI du lot Guyane. Le rapport d'audit original et les deux registres de validations sont les entrées. Deux générations successives doivent donner des sorties **octet pour octet identiques**.

L'artefact contient :
- guyane-etats-1943-2026.json (84 états au 1er janvier, sans polygones) ;
- guyane-evenements-1943-2026.json (MOD, date, codes et libellés avant/après) ;
- guyane-autorites-historiques.json (quatre fiches anciennes, relations successeurs non approuvées) ;
- manifest-guyane-chronologie.json (empreintes SHA-256 et garanties).

Aucune donnée publique n'est ajoutée au répertoire docs/, aucun contour historique n'est publié et aucune nouvelle autorité ou relation Pactols n'est validée. Le sélecteur public reste **Région / Département / Commune**.
