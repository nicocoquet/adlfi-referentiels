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

## Résultats contrôlés de la comparaison exhaustive

Exécution GitHub Actions [n°44081927304](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44081927304) : 119/119 codes de la feuille `Ile` présents dans `Geo`, zéro code absent ; 179 observations `Geo`, 14 îles décrites dans plusieurs unités fines, trois dans plusieurs communes, aucune dans plusieurs subdivisions. Les deux exceptions de préfixe Maria sont conservées. **Ces dénombrements portent sur les codes et relations de la source, pas sur des géométries homologuées.**

Le journal de l'exécution [n°44082070138](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44082070138) identifie les **trois îles multicommunales** :

| Code ISPF de l'île | Île | Communes COG concernées |
| --- | --- | --- |
| `45` | Maria (Australes) | `98743` Rimatara ; `98744` Rurutu |
| `74` | Raiatea | `98750` Taputapuatea ; `98754` Tumaraa ; `98758` Uturoa |
| `90` | Tahiti | `98712`, `98715`, `98722`, `98725`, `98733`, `98734`, `98735`, `98736`, `98738`, `98747`, `98748`, `98752` |

Les **14 îles à plusieurs unités fines** sont consignées individuellement dans l'artefact JSON. La présence de plusieurs communes sur Raiatea et Tahiti est compatible avec leur organisation administrative, mais ne permet pas de dessiner ni fusionner leurs contours. Pour Maria, la relation entre les deux communes et les exceptions `CODGEO` demande une instruction spécifique.

La divergence documentaire **119 codes / 121 îles** reste non résolue : l'exhaustivité du classeur vérifiée ici ne prouve pas l'équivalence entre les deux méthodes de dénombrement.


## Qualification institutionnelle des îles Maria — sources retrouvées

**Décision documentaire : rattachement multicommunal légitime, sans correction arithmétique de CODGEO.**

La [documentation officielle ISPF](https://www.ispf.pf/ispf/referentiels), rubrique « Remarques », confirme explicitement le partage : partie **est** des îles Maria rattachée à **Avera**, commune de **Rurutu** (`IDComas 441`, `98744`) ; partie **ouest** à **Amaru**, commune de **Rimatara** (`IDComas 431`, `98743`).

Le [rapport d'observations définitives de la Chambre territoriale des comptes de Polynésie française sur Rimatara (2024), p. 11](https://www.ccomptes.fr/sites/default/files/2024-07/PFR2024006_0.pdf), documente :

- rattachement initial de Maria à Rimatara lors de la création des communes en 1972 ;
- délibération de Rimatara du **13 août 1974**, après une demande de Rurutu du **12 août 1974** ;
- **arrêté n°3659 BAC du 18 septembre 1974** fixant les limites entre Rimatara et Rurutu (acte cité dans le rapport, original non encore contrôlé) ;
- **Haerai** et **Tanimanu** à Rimatara ; **Tapuata** et **Tinimanu** à Rurutu.

La carte reproduite dans le rapport (documentation communale) fournit une illustration, mais **ne constitue pas un polygone géoréférencé homologué**. La date du 18 septembre 1974 est celle de l'acte cité ; son entrée en vigueur et la géométrie légale précise restent à documenter par consultation de l'original.

**Statut éditorial proposé :** `RATTACHEMENT_MULTICOMMUNAL_CONFIRME_ISPF` pour Maria ; `CODGEO_PREFIXE_DEROGATOIRE_DOCUMENTE_SANS_REGLE_FORMELLE` pour les deux lignes `43001` et `44001`. Ces statuts ne sont pas des types officiels ISPF mais des qualifications internes de la recette AdlFI.

**Attention à l'homonymie :** le rapport de la Chambre mentionne aussi « Maria Est » sous administration de Gambier dans un contexte cartographique. Ce référent doit rester distinct de **Maria (Australes), `IDIle=45`** tant que l'identification nominative des îles n'est pas instruite. Le présent audit n'établit aucun alignement entre ces entités.


## Inventaire exhaustif des 14 îles à plusieurs unités fines

Source : [workflow réussi n°44082557647](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44082557647), rapport ISPF recomposé depuis le fichier officiel à empreinte contrôlée.

| IDIle | Île | Unités fines ISPF | Communes COG distinctes |
|---|---|---:|---:|
| `14` | Bora Bora | 3 | 1 |
| `30` | Hiva Oa | 2 | 1 |
| `31` | Huahine | 8 | 1 |
| `45` | Maria (Australes) | 2 | 2 |
| `57` | Moorea | 5 | 1 |
| `67` | Nuku Hiva | 3 | 1 |
| `74` | Raiatea | 8 | 3 |
| `75` | Raivavae | 3 | 1 |
| `84` | Rimatara | 3 | 1 |
| `86` | Rurutu | 3 | 1 |
| `88` | Tahaa | 8 | 1 |
| `90` | Tahiti | 21 | 12 |
| `111` | Tubuai | 3 | 1 |
| `115` | Ua Pou | 2 | 1 |

**Qualification :** onze îles concernent plusieurs unités fines d'une même commune et trois îles concernent plusieurs communes. Ce sont des **relations multiples attendues ou sourcées**, pas automatiquement des erreurs. Les codes `IDIle` désignent des unités de nomenclature et ne sont ni des identifiants INSEE ni des géométries.

Les détails des `IDComas` et des communes concernées sont présents dans le rapport JSON de CI. Maria bénéficie désormais d'une qualification institutionnelle explicite (voir section précédente). Pour Raiatea et Tahiti, la multiplicité des communes doit rester décrite comme un rattachement géographique issu de la nomenclature, sans assimilation à une hiérarchie unique « île → commune ».
