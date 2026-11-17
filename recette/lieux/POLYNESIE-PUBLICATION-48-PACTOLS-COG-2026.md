# Polynésie française — décisions de validation Pactols–COG 2026 (48 communes)

**17 novembre 2026 — validation éditoriale des identifiants, pas des géométries.**

## Décision et preuves documentaires

La politique éditoriale [Pactols–COG du 16 novembre 2026](POLITIQUE-ALIGNEMENT-PACTOLS-COG.md) prévoit la validation d'une correspondance communale dès lors qu'un concept actif et non remplacé porte un **`skos:exactMatch` explicite vers l'URI INSEE communale exacte du millésime**, avec unicité ARK/code et libellé cohérent.

L'[audit indépendant PR n°71](https://github.com/nicocoquet/adlfi-referentiels/pull/71), [GitHub Actions n°44061695614](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44061695614), a démontré ces critères pour **l'intégralité des 48 communes COG polynésiennes `98711` à `98758`** :

| Contrôle | Résultat |
| --- | --- |
| Communes COG 2026 | 48 |
| Concepts Pactols possédant un `skos:exactMatch` communal | 48 |
| Concepts distincts, non dépréciés et non remplacés | 48 |
| Libellés communaux compatibles | 48 |
| URI INSEE concurrente, homonymie seule, concept multiple | 0 |
| Alertes lexicales « île / atoll » dans les libellés préférés | 0 |
| Validations enregistrées | **48 — `VALIDE_ADLFI_2026`** |

Sources épinglées :
- [Frantiq/PACTOLS](https://github.com/frantiq/PACTOLS), `Pactols_Lieux_th17_20260722.rdf`, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 **`3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`** ;
- [INSEE COG 2026](https://www.insee.fr/fr/information/8740222) : six CSV originaux, chacun vérifié par SHA-256, dont `v_commune_comer_2026.csv`.

Le registre [`POLYNESIE-VALIDATIONS-PACTOLS-COG-2026.csv`](POLYNESIE-VALIDATIONS-PACTOLS-COG-2026.csv) contient les **48 preuves individuelles vérifiées**. La publication a été régénérée **depuis l'index antérieur 128 validés** de la fusion [PR n°71](https://github.com/nicocoquet/adlfi-referentiels/pull/71) par `appliquer_validations` dans `scripts/extraire_index_public_outremer_2026.py`, et son empreinte est contrôlée contre le fichier public sous `docs/data/lieux-outremer/recherche-2026.json`.

## Portée : correspondances 2026 uniquement

- **128 → 176** correspondances communales ultramarines publiées, dont **48 en Polynésie**.
- L'unité de territoire `987` possède un concept Pactols distinct `26678/pcrt4K8nLVxWOP` ; cette **collectivité** n'est pas ajoutée aux 176 correspondances de **communes** et sa proposition sera examinée séparément.
- Les **98 communes associées ISPF** et les cinq subdivisions administratives n'acquièrent pas d'identifiants COG communaux nouveaux.
- **Clipperton `98799`**, code historique du COG jusqu'en 2007, demeure exclu.
- **Tahaa `98745`** : ARK validé `26678/pcrteZcqWgVUaT`, **mais contour 2026 toujours invalide topologiquement**. Aucun nouveau contour n'est publié.
- Les dates COG documentées depuis le 21 mai 1972 ne sont pas des dates de création de toutes les communes ; la correspondance validée **n'est pas rétroactive**.

## Recette de publication

Le workflow `lieux-polynesie-pactols-publication-2026.yml` reconfronte les **48 lignes du registre** au RDF Frantiq et aux CSV INSEE officiels épinglés, exige l'unicité des ARK, puis **reconstruit octet par octet** l'index publié depuis le précédent état à 128 validés. Il vérifie également le manifeste, la chronologie, les 48 entités et les invariants spatiaux. La recette Chromium vérifie Anaa, Papeete, Tahaa et le territoire `987`.

**Aucune géométrie ni autorité historique inventée.** Les correspondances avec les communes associées et la validation des contours nécessiteront des instructions indépendantes.
