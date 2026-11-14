# Lieux — enrichissement temporel du graphe COG (lot 001)

**Statut : recette non validante.** Aucun ARK nouvellement validé, aucune géométrie historique déduite, aucun fichier publié du site modifié.

## Source et portée

L'Insee diffuse, pour le millésime COG 2026, une table des **couples `TYPECOM`–`COM`–`LIBELLE` depuis 1943** avec `DATE_DEBUT` et `DATE_FIN` (date de fin exclusive). La date de fin vide signifie que le couple est actif au **1er janvier 2026**. La table concerne les communes et arrondissements municipaux ; elle **ne démontre pas à elle seule** les périodes des communes associées (`COMA`) et déléguées (`COMD`).

**Instantané contrôlé :** SHA-256 `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`, obtenu lors de l'exécution GitHub Actions du 14 novembre 2026. La CI refuse une modification silencieuse de ce CSV.

Sources officielles : [COG 2026](https://www.insee.fr/fr/information/8740222), [table historique CSV](https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_depuis_1943.csv).

**Distinction conceptuelle indispensable :** une période `DATE_DEBUT`–`DATE_FIN` est une période officielle de **code et libellé**, pas une preuve de permanence du contour. Un changement de limites sans changement de nom/code est documenté par les événements (`v_mvt_commune_2026.csv`), pas obligatoirement par un nouveau couple code–libellé.

## Entrées

- `docs/lieux/recette/graphe-episodes-cog-lot001.json` : **33 états**, **11 opérations**, **23 arcs** fondés sur les fichiers officiels de mouvements du lot 001, déjà vérifiés.
- `v_commune_depuis_1943.csv` : table historique Insee 2026, téléchargée sans transformation, empreinte SHA-256 inscrite dans le rapport.

Le script `scripts/enrichir_periodes_cog_lot001.py` rattache à chaque état une ligne du couple historique seulement si la clé `TYPECOM`, `COM`, `LIBELLE` et les **dates d'entrée et de sortie connues** la rendent compatible. Les libellés sont normalisés pour la comparaison, mais la forme Insee originale est conservée. Si plusieurs périodes restent compatibles, aucune n'est choisie arbitrairement.

## Sorties de recette

- `graphe-episodes-cog-lot001-dates.json` : états du graphe existant, avec période code–libellé proposée et sa source ; **sans remplacement** des dates d'événements.
- `revue-periodes-cog-lot001.csv` : une ligne par état (33), avec périodes, ambiguïtés et statuts de validation nuls.
- `rapport-periodes-cog-lot001.json` : effectifs, anomalies et empreintes SHA-256 des deux entrées.

Les états portent un `statut_qualification_temporelle` :

- `couple_code_libelle_unique_compatible` : ligne Insee unique et compatible avec les événements observés ; **ne certifie pas le contour** ;
- `aucun_couple_code_libelle_trouve` : aucun couple de cette clé dans la source (notamment statut `COMD` / `COMA`) ;
- `plusieurs_periodes_compatibles_a_instruire` : plusieurs intervalles possibles ;
- `couples_trouves_mais_dates_incompatibles` : conflit entre périodes et mouvement, à instruire avant consolidation.

### Limites explicites

1. Le début `1943-01-01` peut être une **borne documentaire** de l'historique et non une date de création de commune.
2. Une fin vide équivaut à un couple actif au millésime 2026, non à une garantie de validité indéfinie.
3. Le fichier Insee peut contenir des **intervalles de durée nulle** (`DATE_DEBUT = DATE_FIN`) : ils sont conservés et comptés dans l'audit, mais ne justifient aucune période de validité. Les intervalles strictement inversés sont rejetés.
4. Un état `COMD`/`COMA` peut avoir une date d'entrée attestée par l'événement, sans que sa **période complète** figure dans l'export des couples historiques.
5. Deux états partageant un code ne doivent pas être fusionnés : **Mougon, Mougon-Thorigné et Aigondigné (`79185`)** sont distincts.
6. Les épisodes du graphe conservent `periode_validite_officielle_complete = false` : la période code–libellé est un attribut, pas la totalité de l'histoire administrative.
7. **Aucune géométrie de 2026 n'est assimilée à une limite de 1943, 1976, 2017 ou 2019**.

## Vérifications et exécution

Tests synthétiques :

```bash
python3 -m unittest discover -s tests -p 'test_enrichir_periodes_cog_lot001.py' -v
```

Audit sur le fichier Insee réel : workflow `.github/workflows/audit-periodes-cog-lieux-2026.yml`. Les fichiers sont déposés comme **artefact de recette non publié**, sans intervention sur `docs/data/`.

**Après l'exécution réelle**, examiner prioritairement les intervalles incompatibles, puis préparer l'instruction historique complète des `COMD` et `COMA` à partir des événements et millésimes pertinents, sans fabriquer de bornes absentes de la source.
