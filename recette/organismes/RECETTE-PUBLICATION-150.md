# Recette de publication du référentiel Organismes — maître 1.50

**État : préparation de publication.** Le JSON public actuel reste le 1.49 tant qu'une PR dédiée n'a pas été validée.

## Maître de recette retenu (privé)

- Fichier : `AdlFI_referentiel_1-50_lot_institutionnel_20261120_QUALIFIE_RECETTE.xlsx`.
- SHA-256 : `6b6bf9a0ea0da8c54a56fc4b33224ac1161b5f885b599a0a4c6ca2d71cfe0668`.
- Produit par modification ciblée du maître 1.50 conservateur, SHA `d05b716428eaa05b3f5a70111e0666e9f863825e05cf8b0f1f04b9a9f0b4f95f`.
- Contrôle de fidélité OOXML : **17 feuilles**, **34 hyperliens natifs**, **8 tableaux structurés**, **0 erreur, 0 avertissement**.
- Contrôle différentiel cellule à cellule : **17 cellules de contenu modifiées ou créées**, toutes attendues ; **0 autre modification de valeur** ; **803 cellules de formule identiques**.

## Arbitrages scientifiques appliqués

1. **SFECAG** `ORG-0751` : qualification documentaire `valide`. Début 1962 et forme historique **Groupe d’étude de la céramique antique en Gaule (GECAG)**, `HIS-0143`, 1962–1973 ; actuel nom SFECAG après changement en 1973. Ville de référence actuelle : Marseille.
   Sources : https://sfecag.org/index.php/histoire/ ; https://cths.fr/an/societe.php?id=1707 ; https://catalogue.bnf.fr/ark:/12148/cb120430151 ; https://sfecag.org/index.php/adhesion-2022/
2. **Musée archéologique de Riez** `SER-0202` : fondé en 1929, collections attestées et conservées en réserves. `actif` laissé **indéterminé**, `statut_validation=a_verifier`. Ne pas inférer une ouverture actuelle.
   Sources : https://pop.culture.gouv.fr/notice/museo/M0862 ; https://www.ville-riez.fr/histoire-patrimoine/histoire-village
3. **Rattachement Riez → commune** `RSE-0258` : reste `a_verifier`. Ne pas transformer une hypothèse de gestion en rattachement validé.

## Contrat de publication

Le maître contient un nombre substantiel d'autorités `a_verifier` déjà visibles au catalogue (258 ORG + 6 SER **avant** validation de SFECAG). **La présence au catalogue et la qualification documentaire sont deux dimensions indépendantes.** Le modèle JSON exporte désormais `validation.status` et `validation.established` ; le site doit présenter la réserve et ne pas dissimuler ces fiches.

Après export du maître 1.50 qualifié :

```bash
python3 scripts/export_organismes.py '/chemin/AdlFI_referentiel_1-50_lot_institutionnel_20261120_QUALIFIE_RECETTE.xlsx'
python3 scripts/recette_publication_organismes_150.py docs/data/organismes.json
python3 -m unittest discover -s tests -v
node tests/test_aliases_organismes.js
node tests/test_affiliations_federales.js
node tests/test_validation_documentaire_organismes.js
```

Le contrôle exige **934 autorités (734 ORG, 200 SER)**, **594 relations**, **3 alias** dont `SER-0063 → ORG-0747`, les trois liens éditoriaux du GRASM, la relation FFESSM `REL-0338`, le nouvel historique SFECAG et la prudence documentaire sur Riez.

**Attention :** les tests de publication historiquement figés sur les comptes 1.49 doivent être adaptés dans la PR de publication, avec vérification des nouveaux effectifs et des prérequis des 193 anciens rattachements. Aucun changement de ces tests ne doit être fusionné avant la PR de données.

La recette visuelle Chromium doit compléter ces contrôles (fiches GRASM, IRAMAT/CEB/LMC, CEA, SFECAG, Riez, liens historiques et logos). Le XLSX source privé ne doit pas être ajouté au dépôt public.

Suivi : [issue #174](https://github.com/nicocoquet/adlfi-referentiels/issues/174).
