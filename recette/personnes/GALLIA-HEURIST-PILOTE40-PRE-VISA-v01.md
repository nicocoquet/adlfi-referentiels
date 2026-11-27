# Personnes — premier pilote Heurist de 40 autorités (recette technique avant visa)

**État :** `CANDIDAT_NON_VALIDE`. Aucune nouvelle autorité, aucun article et aucune contribution de ce lot ne sont publiés. Aucun identifiant `PER` n'a été proposé ou attribué.

**Source :** export privé Heurist *Revue_Gallia* du 27 novembre 2026, SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`. Archive privée de travail `AdlFI_Heurist_Personnes_pilote40_v01_PRE_VISA.zip` (SHA-256 `4ad67ae408dd54081d2a50e4a2f1094fd80d5c7b7ae4966c58dd93d587b4787c`). Les matrices nominatives restent hors du dépôt.

## Objectif et méthode

Le tirage est **stratifié par cas à éprouver**, et non aléatoire : il vise la validation technique d'un import avant extension, sans prétention de représentativité statistique. Les profils ont été choisis dans les 2 019 fiches ayant un PPN IdRef unique dans l'export, après exclusion des trois cas à identifiant secondaire partagé.

| Cas de recette | Autorités |
|---|---:|
| Deux revues, plusieurs rôles bibliographiques | 3 |
| Deux revues, autres profils | 5 |
| Auteur et collaborateur dans Gallia | 4 |
| Auteur et collaborateur dans Gallia Préhistoire | 4 |
| Auteur dans Gallia seul | 4 |
| Auteur dans Gallia Préhistoire seul | 4 |
| Collaborateur dans Gallia seul | 5 |
| Collaborateur dans Gallia Préhistoire seul | 5 |
| Variantes de noms (plusieurs variantes) | 4 |
| Identifiant externe limité au seul IdRef : Gallia / Gallia Préhistoire | 2 |
| **Total** | **40** |

Une même personne peut présenter plusieurs caractéristiques, mais chaque personne appartient à une seule strate de sélection. Les variantes sont représentées sur cinq fiches au total, dont quatre comportant plusieurs variantes.

## Résultat documentaire vérifié

| Contrôle | Résultat |
|---|---:|
| Nouveaux profils de personne candidats | 40 |
| Relations explicites `auteur` | 69 |
| Relations explicites `collaborateur` | 36 |
| **Relations candidates distinctes** | **105** |
| Articles distincts liés à ces relations | 90 |
| Articles du pilote v0.2 déjà publiés et réutilisés | 26 |
| **Articles nouveaux candidats** | **64** |
| Dont Gallia | 35 |
| Dont Gallia Préhistoire | 29 |
| Articles nouveaux sans URL | 1 |
| Articles nouveaux sans DOI | 4 |
| URL historiques HTTP normalisées en HTTPS (résolution non vérifiée) | 2 |
| Autorités `PER` effectivement créées | **0** |

Le rapprochement de chaque relation avec l'export Heurist original a été vérifié sur l'identifiant de l'article, l'identifiant de la personne, la valeur du rôle `Auteur(s)` / `Collaborateur(s)` et la position **dans le champ répétable propre à ce rôle**. Les métadonnées des **337 articles publiés** ont été reconstituées à l'identique avant la création du nouveau candidat ; aucun DOI ni URL des 64 articles nouveaux ne duplique un article déjà publié ou un autre article candidat.

Les cinq fiches à variantes conservent les formes attestées sous le type général `autre_forme_attestee` ; aucun statut de nom marital ou de graphie canonique IdRef n'est déduit.

## Contrôle de confidentialité

- Les projections de travail sont produites par **liste blanche** à partir de la seule information bibliographique susceptible d'être publiée : noms, variantes attestées, identifiants pérennes, titres, année, volume, pages, DOI, URL, relations auteur/collaborateur.
- Aucune information personnelle de contexte (coordonnées, dates de naissance) et aucune relation relevant d'un processus de validation éditoriale interne ne doivent être extraites ou publiées.
- Les identifiants `rec_ID` Heurist servent uniquement à prouver les rapprochements dans le dossier privé ; ils ne sont pas assimilés aux identifiants publics `PER`.
- `scripts/auditer_pilote_personnes_heurist.py` accepte les projections **préfiltrées uniquement**, rejette les champs inattendus et les relations non publiques, interdit l'attribution d'un `PER` avant le visa et contrôle les collisions de DOI, URL et identifiants pérennes.
- Les tests `tests/test_auditer_pilote_personnes_heurist.py` sont entièrement **synthétiques** et ne nécessitent aucune donnée nominative de la source.

## Décisions avant publication

1. Visa du sous-ensemble des 40 personnes et de leurs 105 relations (matrices privées `matrice_visa_40.csv` et `matrice_relations.csv`).
2. Confirmation des quatre formes de variantes multiples, sans attribution non étayée de type marital.
3. Vérification facultative des deux URL historiques converties en HTTPS, ou maintien de la réserve documentaire si la plateforme interdit le contrôle.
4. Après visa seulement : créer de nouveaux `PER` à la suite des 202 existants, conserver `contributions_count = 0` pour ces fiches, réutiliser 26 articles existants et ajouter 64 nouveaux articles, puis publier les 105 relations via une **PR de données distincte**.
5. Contrôler que les facettes et la fiche des auteurs sans notices AdlFI restent fonctionnelles, puis réaliser une recette visuelle post-déploiement.

**Limite importante :** les 40 candidatures ne constituent ni un échantillon de qualité statistique ni un visa implicite des 1 979 autres fiches du diagnostic. Le dossier [#217](https://github.com/nicocoquet/adlfi-referentiels/issues/217) reste le suivi du chantier Heurist.
