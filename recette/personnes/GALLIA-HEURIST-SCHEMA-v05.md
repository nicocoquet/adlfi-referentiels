# Personnes — schéma 0.5.0 : autorités Heurist sans contribution AdlFI

**Objet :** préparer les ajouts d'autorités identifiées dans la base Heurist pour *Gallia* et *Gallia Préhistoire*, sans les assimiler à des auteurs de notices AdlFI. **Aucune nouvelle autorité n'est publiée dans cette étape.**

## Situation vérifiée au départ

- `docs/data/personnes.json` : 202 autorités, 1 980 relations **AdlFI**, 1 779 notices AdlFI distinctes (lots antérieurs préservés).
- `docs/data/personnes-articles.json` : 337 articles et 473 contributions bibliographiques (424 auteur et 49 collaborateur), pour 193 `PER`.
- Au moment de la migration, les 202 fiches présentent toutes une valeur `contributions_count > 0` exactement égale au nombre de leurs contributions AdlFI.

## Règles du schéma 0.5.0

1. **`contributions_count` : nombre de relations AdlFI**, et uniquement AdlFI, associées au `PER`. Il peut désormais valoir `0` pour une nouvelle autorité connue exclusivement par *Gallia* / *Gallia Préhistoire*.
2. **Aucune contribution AdlFI fictive** n'est créée pour rendre une autorité éligible. Si `contributions_count = 0`, une contribution bibliographique publique de cette personne doit exister dans `docs/data/personnes-articles.json`. Cette contrainte inter-fichiers est testée en Python.
3. Les nombres `totals.contributions` et `totals.notices` du catalogue principal restent les compteurs d'AdlFI ; les effectifs *Gallia* figurent exclusivement dans `articles_lies` du manifeste et le catalogue complémentaire.
4. Le champ `identifiers.idref` demeure **obligatoire et unique** pour ce jalon : les 200 fiches Heurist sans PPN exploitable et les quatre valeurs de PPN partagées entre deux fiches nécessitent un arbitrage séparé ; aucune valeur artificielle ne peut être attribuée.
5. Les relations bibliographiques conservent uniquement `auteur` et `collaborateur`. Les autres rôles de la base Heurist sont hors projection publique et ne peuvent pas être inférés par l'interface.
6. L'identifiant `PER` est indépendant de l'identifiant Heurist et du PPN IdRef ; la provenance interne reste dans les dossiers de recette non publiables.

## Impact de la migration technique

- Mise à jour du schéma `personnes.schema.json` de 0.4.0 à 0.5.0 : seul le minimum de `contributions_count` passe de 1 à 0 et la sémantique du champ est précisée.
- Mise à jour **uniquement du numéro `schema_version`** dans `docs/data/personnes.json` ; listes, noms, identifiants, notes et contributions inchangés.
- Alignement `data_schema` du module Personnes dans `docs/data/manifest.json`.
- Interface : si une autorité possède des articles mais aucune notice AdlFI, ne pas afficher de section « Notices AdlFI (0) » ; ses articles et ses facettes restent disponibles.
- Test Node synthétique : `PER-000203` fictif, zéro contribution AdlFI, une relation bibliographique `collaborateur`, visible dans l'interface. **Aucune autorité `PER-000203` n'est créée dans les données réelles.**
- Tests Python : correspondance stricte des compteurs AdlFI individuels, obligation d'une relation Gallia pour chaque `PER` à zéro contribution AdlFI, et conservation par SHA-256 des **202 autorités** et **1 980 contributions** antérieures.
- Tests historiques Gallia : préservation des premiers 337 objets articles et 473 objets contributions par SHA-256, sans bloquer leur extension future.

## Hors périmètre et décisions à prendre plus tard

- La qualification des **2 019 fiches avec PPN non partagé** recensées dans le diagnostic ne vaut pas un visa de création en bloc. L'absence de PPN partagé est nécessaire mais ne suffit pas à démontrer l'identité et la cohérence de tous les attributs.
- Les **200 fiches sans PPN**, les **quatre PPN partagés** (huit fiches) et l'**auteur institutionnel** ne sont pas inclus ; leur traitement relève du dossier GitHub [#217](https://github.com/nicocoquet/adlfi-referentiels/issues/217).
- Aucun nouveau `PER` ni aucune nouvelle relation Gallia n'est ajouté dans cette PR.
- Lors d'un import ultérieur provenant d'un nouvel export Heurist, la provenance du catalogue bibliographique (`source_sha256` actuellement unique) devra être adaptée à une provenance multi-lots ou vérifier que toutes les nouvelles relations proviennent du même export.

**Statut :** migration structurelle sans ajout de données nominatives.
