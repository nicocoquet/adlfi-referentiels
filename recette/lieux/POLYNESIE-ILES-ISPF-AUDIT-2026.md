# Polynésie française — audit descriptif des îles ISPF

**17 novembre 2026 — PR de recette, sans publication de nouvelles autorités.**

## Périmètre

Suite aux PR [74](https://github.com/nicocoquet/adlfi-referentiels/pull/74) et [75](https://github.com/nicocoquet/adlfi-referentiels/pull/75), cette tranche exploite la nomenclature [ISPF officielle](https://www.ispf.pf/ispf/referentiels), XLSX [Codes géographiques](https://www.ispf.pf/content/uploads/Codes_geographiques_ce46ed21ee.xlsx), SHA-256 :

`d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6`.

La feuille administrative `Commune associée` contient 98 communes associées et 18 unités conventionnelles non subdivisées. La feuille `Ile` contient 119 codes et la feuille `Geo` 179 enregistrements. **Un code d'île, une commune et une commune associée ne sont pas interchangeables.**

## Audit ajouté

Le script `scripts/auditer_iles_ispf_polynesie.py` consomme uniquement le rapport de qualification source `adlfi.lieux.polynesie.ispf.associees.audit.v1` validé par la procédure de PR75. Il groupe les observations `Geo` par `IDIle` et conserve :

- libellé et code d'île explicitement attestés ;
- `IDComas`, communes COG parentes, subdivisions et `CODGEO` déjà présents dans le classeur ;
- indicateurs `isCom`, `isComas`, `isIleRattachee` ;
- îles présentes dans plusieurs unités fines, communes ou subdivisions, à **qualifier** sans les fusionner ni en inférer une géométrie.

Chaque rapport comporte le même SHA source ; double génération JSON et comparaison octet par octet dans GitHub Actions. Le rapport reste un artefact CI, **hors `docs/`**.

## Anomalies déjà constatées, non résolues artificiellement

1. **Maria :** `CODGEO 43001` → `IDComas 431` (Amaru/Rimatara), `CODGEO 44001` → `IDComas 441` (Avera/Rurutu). La différence de préfixe est documentée ; elle ne peut être « corrigée » par concaténation.
2. **Gambier :** unité administrative `190` attestée ; aucune ligne géographique `19000`, mais seize observations `19001` à `19016` classées comme îles rattachées.
3. **119/121 :** 119 codes dans la feuille `Ile` ; la page explicative ISPF mentionne 121 îles. Les périmètres de comptage ne sont pas considérés identiques sans preuve.
4. **179/116 :** les 179 codes `Geo` ne sont pas 179 communes ou communes associées.

### Limite à lever dans une tranche ultérieure

Le script recoupe maintenant **directement les 119 lignes de la feuille `Ile`** et les observations `Geo` du même classeur contrôlé par SHA-256. Les codes de la nomenclature sans observation `Geo` sont listés avec leur libellé et leur subdivision, sans création de rattachement ou géométrie. Les accords de libellé et subdivision sont contrôlés pour chaque observation. Ce contrôle ne résout pas, à lui seul, l'écart entre les 119 codes et les 121 îles évoquées par la documentation explicative.

## Contrat éditorial

Zéro nouvelle autorité publiée, zéro ARK Pactols déduit, zéro code INSEE construit, zéro contour spatial validé, aucune date historique rétroprojetée. Les **176 liens Pactols–COG communaux**, **4 liens de collectivités** et **98 communes associées ISPF** déjà publiés demeurent inchangés.

**Recette conditionnelle :** examiner l'artefact JSON réel et les alertes de relations multiples après passage de la CI avant d'autoriser une intégration cartographique.
