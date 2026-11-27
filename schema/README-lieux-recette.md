# Lieux AdlFI — contrat relationnel de recette

**Statut : outillage technique, sans données publiées.** Ce dossier décrit le schéma, le générateur et les tests d'un instantané de travail dérivé du registre éditorial du 15 novembre 2026.

## Organisation

- schema/lieux-recette.sql : 13 tables, identifiants, clés étrangères et distinction entre événements attestés et groupes techniques des Pays de la Loire.
- scripts/exporter_recette_lieux_relationnelle.py : lecture de 13 CSV ; génération locale JSON + SQLite, toujours marqués non publiables.
- tests/test_exporter_recette_lieux_relationnelle.py : fixtures synthétiques (aucune donnée réelle du registre) et tests de sécurité.

Le registre des **61 dossiers**, les CSV d'instruction, les réponses brutes de Frantiq, les XLSX et la base d'archives **ne sont pas inclus dans cette PR**. Ils doivent rester dans des artefacts de recette et non dans docs/.

## Utilisation locale

Préparer le dossier de travail tables_csv/ contenant les 13 CSV du paquet de recette AdlFI. Puis, depuis la racine du dépôt :

~~~sh
python3 scripts/exporter_recette_lieux_relationnelle.py \
  --tables-csv "$HOME/Desktop/AdlFI-Lieux/recette/tables_csv" \
  --sortie "$HOME/Desktop/AdlFI-Lieux/sortie-relationnelle"
~~~

Deux fichiers sont créés : lieux-recette.json et lieux-recette.sqlite. Ils contiennent toutes les candidatures, non uniquement les décisions approuvées : **ils ne sont pas publiables**.

Chaque CSV doit correspondre exactement aux colonnes de sa table SQL. Les empreintes SHA-256 des fichiers sont conservées dans les métadonnées JSON. Les clés et références des objets sont contrôlées, notamment les références polymorphes liens_dossiers.

## Garanties scientifiques

1. L'ARK Pactols identifie un concept documentaire ; il n'est pas déduit d'un code INSEE.
2. Une période code–libellé ne prouve aucune géométrie historique.
3. MOD=10/31/32/33/34/35/41 représente des conventions de modélisation, non des validations d'alignements individuels.
4. Les événements COG et les regroupements techniques PDL restent deux catégories différentes.
5. Les décisions collectives (ex. recodifications corses de 1976) **ne valent jamais autorisation d'exporter des relations Pactols**.
6. Le générateur produit toujours publication_gate.publication_autorisee = false et des listes vides de nouvelles relations et géométries validées.
7. Il refuse toute sortie sous un répertoire nommé docs/, toute écriture au sein de ses sources et tout écrasement implicite.

Ce mécanisme protège la recette contre une publication accidentelle par cet outil ; il ne remplace pas l'examen éditorial, la revue de code ni le contrôle des accès au registre d'origine.

## Vérifications

~~~sh
python3 -m unittest discover -s tests -p 'test_exporter_recette_lieux_relationnelle.py' -v
python3 -m unittest discover -s tests -v
~~~

Avant toute future publication, prévoir **un autre générateur**, sur des données approuvées individuellement et sourcées, une PR dédiée, et une politique explicite de géométries historiques.

Voir PR 24 — recette nationale Pactols–COG : https://github.com/nicocoquet/adlfi-referentiels/pull/24 (conservée en brouillon).
