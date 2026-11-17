# Bourgogne-Franche-Comté — registre de 3 614 décisions Pactols–COG 2026 (recette)

**17 novembre 2026. PR de recette sans publication sur GitHub Pages.**

## Périmètre

Sur les 3 685 communes BFC (TYPECOM=COM, REG=27) du COG au 1er janvier 2026, l'audit régional PR 97 établit :

| État | Communes | Décision |
| --- | ---: | --- |
| exactMatch univoque et libellé compatible | 3 614 | Validation par règle, registre de recette |
| plusieurs concepts ARK | 44 | Instruction |
| divergence de libellé, statut ou URI | 26 | Instruction |
| aucun exactMatch à URI de code reconnue | 1 | Instruction : Val-d'Usiers 25060 |

**71 communes sont exclues du registre des 3 614 décisions.** Les identités anciennes ne sont pas automatiquement rattachées aux communes nouvelles.

## Préflight renforcé

Le script scripts/preparer_validations_pactols_bfc_2026.py utilise les mêmes sources RDF Pactols et COG 2026 épinglées que la publication corse. Pour chacun des 3 614 concepts sélectionnés, il vérifie *à nouveau dans le RDF brut* que la totalité des exactMatch INSEE (y compris URI UUID et types administratifs non reconnus par le parseur de la PR 97) se réduit bien à la seule URI de commune attendue. Une contradiction bloque la recette.

Les identifiants ARK et COG sont uniques. Le CSV reprend les colonnes du registre corse : code, libellé, région, département, ARK, URI exacte, prédicat RDF, libellé Pactols, empreinte de source, portée et statut éditorial. Le JSON d'exceptions liste les 71 communes restant à instruire.

Le statut des 3 614 correspondances est VALIDE_ADLFI_2026 par application de la politique déjà approuvée d'alignement explicite et univoque ; le champ publication_site reste EN_ATTENTE_RECETTE_PUBLICATION. Les 71 exceptions restent NON_PRISE. Il n'existe ici **aucune publication sur le site**.

## Reproductibilité

Le workflow réalise deux exportations CSV et JSON identiques octet à octet, contrôle le SHA des sources, les 3 614 décisions et les 71 exceptions, ainsi que le maintien des géométries, chronologies et index publics. Les sorties sont téléchargées en tant qu'artefact de recette et non commitées dans docs.

Suite proposée : contrôler les cardinalités réelles, puis créer une PR **distincte** de publication d'un index Pactols BFC 2026, analogue à la PR 100 pour la Corse. Les dossiers ambigus seront instruits séparément, notamment les URI UUID de Val-d'Usiers détectées dans la PR 101.

## Exécution de recette sur sources officielles — 17 novembre 2026

- [GitHub Actions, exécution 44173036696](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44173036696) : réussite des **12 tests Python** (5 nouveaux, 7 tests régionaux), contrôle SHA-256 des deux sources, double exécution réelle, comparaison octet à octet et archive de recette.
- **3 614** couples Pactols–COG 2026 sélectionnés, **3 614** ARK et codes uniques ; **71** exceptions réparties en 44 plusieurs ARK, 26 divergences et 1 absence d'URI de code.
- Le second passage sur les exactMatch du RDF brut n'a révélé **aucune URI INSEE supplémentaire contradictoire parmi ces 3 614 concepts**.
- Empreinte SHA-256 des deux CSV identiques : **494dad4ddbf562b96a0b37a5e10ea56ba2deff1289255bb7e35bcdecefa5d0c5**.
- Artefact GitHub Actions : **recette-bfc-3614-pactols-cog-2026** (CSV des décisions et JSON des 71 exceptions).
- La CI générale du référentiel a également réussi ([44173036511](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44173036511)).

Aucune écriture dans docs/data ni modification de l'index public ; la publication reste une étape distincte.
