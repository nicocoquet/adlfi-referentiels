# Extraction nationale des lieux indexés dans les XML AdlFI — pilote technique

## Objet et périmètre

Ce script produit une **table d'observations documentaires** à partir des fichiers TEI/Métopes du corpus éditorial. Il ne génère **aucune correspondance COG nouvelle** et ne modifie ni les sources XML, ni les données publiées dans `docs/data`.

Répertoire communiqué par l'éditeur (Mac, via `sDrive`) :

```text
~/sDrive/DR05_USR3225_ADLFI/AdlFI_NOTICES-FAITES
```

La recherche est **récursive** et porte sur les fichiers XML dont le **nom** :

- possède l'extension `.xml` (casse indifférente) ;
- contient `AdlFI` (casse indifférente) ;
- **ne** contient **pas** `Edito` ou `Édito` (casse et accents indifférents).

Le filtre s'applique au **nom de base du fichier**, pas aux noms de sous-dossiers. Les fichiers exclus sont explicitement décrits dans `inventaire_xml.csv`. Les autres formats (PDF, ZIP, etc.) ne sont pas étudiés dans l'inventaire XML.

## Préflight : contrôler les fichiers avant de parser

Depuis la racine locale de `adlfi-referentiels`, sur la branche de recette contenant le script :

```bash
python3 scripts/extraire_lieux_xml_adlfi.py \
  "$HOME/sDrive/DR05_USR3225_ADLFI/AdlFI_NOTICES-FAITES" \
  --output-dir "$HOME/Desktop/AdlFI-audit-lieux" \
  --inventaire-seul
```

Consulter `~/Desktop/AdlFI-audit-lieux/inventaire_xml.csv` pour vérifier les fichiers inclus/exclus. Le script affiche leur nombre. **À ce stade, aucun XML n'est ouvert pour extraction.**

## Extraction complète

Lorsque l'inventaire est satisfaisant, relancer sans `--inventaire-seul` :

```bash
python3 scripts/extraire_lieux_xml_adlfi.py \
  "$HOME/sDrive/DR05_USR3225_ADLFI/AdlFI_NOTICES-FAITES" \
  --output-dir "$HOME/Desktop/AdlFI-audit-lieux"
```

Prévoir un temps d'exécution proportionnel au volume des XML. Le script affiche la progression fichier par fichier. Python standard uniquement ; aucune installation de paquets n'est nécessaire. Les fichiers de sortie sont réécrits lors d'une nouvelle exécution.

L'exécution est en **lecture seule** sur les XML, et refuse de placer les sorties dans le répertoire du corpus ou sous `docs/` (publication GitHub Pages).

## Contrat d'extraction

- Une **notice** = un `div` avec `@subtype="notice"` ou `@type="notice"`. L'identifiant local est le chemin relatif du fichier suivi de l'ordinal (`fichier.xml::notice-000001`). Un `xml:id` déjà présent est également conservé : l'ordinal n'est pas un identifiant public permanent.
- Une **occurrence géographique** = **feuille terminale** d'une chaîne `index[@indexName="pactols:Lieux"]`. On conserve tous les niveaux ancêtres dans `chaine_ark` et `chaine_libelles_fr` ; on ne multiplie pas artificiellement les lieux par Europe, France, région et département.
- Les index sont recherchés **dans toute la notice**, et non uniquement dans son titre : les métadonnées contenues dans le titre et celles présentes dans le corps sont prises en compte.
- L'**année d'opération** vient des blocs `<ab type="meta-archeo">` et de leurs éléments `<date>` (texte et attributs `when`, `from`, `to`, etc.). On conserve les années attestées, le texte original et un indicateur des intervalles. **On ne développe pas automatiquement les années intermédiaires** : `2018–2020` n'atteste pas à lui seul une opération en 2019.
- L'année de publication et l'année qui figure seulement dans un sous-titre ne sont **pas** substituées automatiquement à une année d'opération manquante.
- Les index Pactols mal formés, les notices sans index et les années absentes sont inscrits au rapport ; ils ne déclenchent pas d'invention d'ARK ou de date.
- Deux **fichiers strictement identiques** (même SHA-256) sont identifiés comme doublons ; seul le premier chemin relatif dans l'ordre de parcours entre dans les statistiques. Cela ne détecte pas les **doublons de notices** entre deux XML distincts : cet audit reste à prévoir.
- Le pilote public PACA apporte **seulement** les 103 correspondances Pactols–COG validées, comme table de contrôle. Tous les autres ARK sont notés `hors_pilote_non_instruit` et **ne sont pas considérés comme mal alignés**.

## Livrables locaux

| Fichier | Contenu |
|---|---|
| `inventaire_xml.csv` | Fichiers XML retenus, exclus, erreurs et doublons SHA-256 |
| `notices.csv` | Notice, titre, sous-titre, années d'opération, état de contrôle |
| `occurrences_lieux.csv` | Une ligne par occurrence terminale, avec chaîne d'ARK et contexte TEI |
| `autorites_lieux.csv` | Agrégation par ARK : notices distinctes, années et état du pilote |
| `alignements_lieux.csv` | Alignements **déjà validés**, à distinguer des ARK restant à instruire |
| `rapport_audit.json` | Statistiques et anomalies par type, sans correction automatique |

Les CSV sont en UTF-8 avec BOM et séparateur `;` pour faciliter l'ouverture avec Excel français. Les chaînes structurées d'ARK et les listes d'années sont des tableaux JSON encodés dans les cellules CSV.

## Recette et critères de passage à l'enrichissement

1. **Inventaire** : examiner la cohérence des fichiers retenus et exclus, la présence d'éventuelles copies et l'exhaustivité des millésimes.
2. **Structure XML** : contrôler les fichiers déclarés `aucune_div_notice`, `erreur_lecture_xml`, `aucun_index_pactols_lieux` ; ne pas supposer que les XML de toutes les périodes Métopes ont le même balisage.
3. **Chronologie** : vérifier les absences, intervalles et années multiples avant agrégation chronologique.
4. **Géographie** : comparer les ARK uniques à la table Pactols–COG historique du dépôt `atlas-documentaire` et au millésime du COG retenu, en respectant les relations non bijectives et les cas hors COG (îles, archipels, sites, espaces maritimes, etc.).
5. **Géométries** : rattacher uniquement les codes officiellement contrôlés aux contours de leur millésime ; aucune géométrie actuelle ne constitue une limite historique.
6. **Publication** : produire un export séparé et validé avant de toucher aux JSON du site.

Le premier corpus national réel n'a **pas encore été exécuté** : sa localisation se trouve sur l'ordinateur de l'éditeur, inaccessible depuis cette exécution distante. Les tests du script utilisent un corpus TEI synthétique inspiré des structures réellement examinées dans les fichiers Grand Est et Alsace.

## Tests

```bash
python3 -m unittest discover -s tests -p 'test_extraire_lieux_xml_adlfi.py' -v
```

## Résultats du premier audit national — 13 novembre 2026

Première extraction du dossier local, **non publiée** (copie du ZIP conservée hors dépôt public) :

| Mesure | Résultat |
| --- | ---: |
| XML recensés | 1 511 |
| XML répondant aux filtres de nom AdlFI / hors Edito | 701 |
| Fichiers auxiliaires `*_indexList.xml` | **19** |
| Fichiers à parser comme notices | **682** |
| Éléments `div[notice]` comptés par le premier extracteur | 23 242 |
| Éléments artificiels attribuables aux indexList | **688** |
| Notices hors indexList (avant dédoublonnage) | **22 554** |
| Occurrences terminales Pactols | **30 772** |
| Autorités ARK distinctes | **9 928** |
| ARK du pilote PACA présents | **103 / 103** |
| Notices sans index géographique hors indexList | **285** |
| Notices sans année d'opération hors indexList | **102** |

**Correctifs de l'extracteur :**

- Les 19 `*_indexList.xml` conservent leur statut de fichiers répondant au **filtre de nom** demandé, mais sont marqués `decision=auxiliaire` et ne sont plus parsés comme notices. L'inventaire ne les confond pas avec les 810 exclusions du filtre de nom.
- Si un niveau de la chaîne hiérarchique Pactols possède un `source` vide/invalide, `chaine_ark` conserve sa position sous la forme `null`. Les ARK ne sont plus artificiellement décalés par rapport aux libellés français. Le diagnostic `ark_ancetre_invalide` reste signalé.

**Anomalies éditoriales non résolues :**

- **152 groupes candidats** de notices en doublon entre des fichiers différents, sur titre, sous-titre, année et ensemble d'ARK identiques : 130 Reims (original/`enriched`), 14 ARA 2016, 3 ARA 2025, 2 ARA 2024 et 3 autres. Ce n'est **pas** une décision de fusion ou de suppression.
- Les **285** notices sans index géographique comprennent 196 notices du sous-corpus Reims et 29 notices dans `AdlFI_PACA_2021_83.xml` : le balisage source nécessite une instruction spécifique.
- Parmi les **102** notices sans année extraite, 79 relèvent des fichiers ARA 2025. Exemple à contrôler dans le XML source : `Mozac – Ancien Carmel de Mozac`, année brute `20232` (2023 ne doit pas être corrigé implicitement).
- **9** libellés français normalisés pointent vers deux ARK distincts ; **14** autorités ont plusieurs libellés français attestés dans les XML. Aucune variante d'identité n'est validée automatiquement.
- **40** occurrences présentent une source ARK ancêtre manquante ou invalide ; l'extraction corrigée conserve ces lacunes explicitement.

**Portée :** les valeurs hors pilote signifient « non instruit », et non « sans correspondance COG ». L'inventaire d'un répertoire sDrive n'établit pas à lui seul l'exhaustivité de toutes les notices AdlFI publiées. Le total de 22 554 notices n'est ni dédoublonné ni comparable directement à un décompte OAI-PMH sans audit des identifiants éditoriaux.
