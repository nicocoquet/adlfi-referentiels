# Lieux AdlFI — criblage Pactols intégral et COG ultramarin, 233 entités

**15 novembre 2026 · PR #30 · lot de recette, non validant.**

## 1. Sources réellement exploitées

L'exécution réussie [GitHub Actions 43734275167](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43734275167) a obtenu par Git LFS et contrôlé **octet par octet** le snapshot RDF/XML de Frantiq `Pactols_Lieux_th17_20260722.rdf`, 93 418 191 octets, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.

La recherche a traité **50 560 concepts RDF porteurs d'un ARK `26678/`** ; ce décompte ne doit pas être confondu avec le nombre de toutes les ressources RDF présentes dans le fichier. Le statut `deprecated`, les `skos:prefLabel`, `skos:altLabel`, `skos:hiddenLabel` français et les `skos:exactMatch` vers les identifiants Insee ont été lus comme **indices documentaires**.

Les cibles sont établies indépendamment dans le COG Insee **2026** :
- `v_commune_2026.csv` : **129 communes COM** des cinq DROM ;
- `v_comer_2026.csv` : **9 collectivités et territoires** ;
- `v_commune_comer_2026.csv` : **95 subdivisions typées** (COM, DIS, CIR, CPT, CDM).

Soit **233 entités administratives distinctes**. Les entités sont identifiées par `DROM:COM:CODE`, `COMER:TERRITOIRE:CODE` ou `COMER:NATURE_ZONAGE:CODE`. Ainsi, le code et le niveau d'identification sont conservés séparément.

L'index des **9 928 autorités terminales attestées dans les XML AdlFI au 13 novembre 2026** a servi uniquement à signaler si une autorité candidate figure déjà dans ce corpus. Son absence n'est pas interprétée comme une absence dans Pactols.

## 2. Résultats du criblage intégral

| Contrôle | Résultat |
|---|---:|
| Cibles COG | **233** |
| Concepts Pactols avec ARK exploitable | **50 560** |
| Associations brutes nom / code | **371** |
| Cibles présentant un indice | **224** |
| Cibles sans indice strict | **9** |
| Cibles avec plusieurs indices bruts | **35** |
| Lignes brutes dont le qualificatif territorial ne correspond pas à la cible | **142** |
| Associations retenues pour instruction (non validées) | **229** |
| Cibles conservant plusieurs pistes pertinentes | **5** |

Les 229 lignes à instruire se répartissent en **221** associations qui combinent un libellé concordant (parfois qualifié territorialement) et une URI Insee de même code déjà déclarée dans Pactols, **2** pistes par code seul et **6** par libellé seul. Ces nombres ne sont **ni** des validations `skos:exactMatch` supplémentaires **ni** des preuves de continuité historique.

Pour les cinq DROM, les **129 communes** ont au moins une URI Insee de même valeur numérique portée par un concept Pactols. Pour les **104 entités COMER**, **94** ont cet indice, et **95** présentent au moins une piste de qualification. Les neuf autres ne possèdent aucun signal selon les critères du criblage.

## 3. Neuf cibles sans signal direct

Les critères stricts (code Insee déclaré et formes exactes ou qualifiées) n'ont pas retrouvé :
- les cinq districts des TAAF : `98411`, `98412`, `98413`, `98414`, `98415` ;
- les circonscriptions de **Alo (`98611`)** et **Sigave (`98612`)** à Wallis-et-Futuna ;
- l'**île des Faisans** au niveau territorial `981` et au niveau de zonage `98101`.

Cette liste ne démontre pas l'absence de ces lieux du thésaurus : un district administratif peut couvrir plusieurs îles ayant chacune leur propre concept documentaire. Une recherche complémentaire par variantes, groupes d'îles, hiérarchie SKOS et dénominations historiques est nécessaire.

## 4. Désambiguïsations prioritaires

Cinq cibles possèdent deux candidats après écart des homonymies contextuellement étrangères au territoire ciblé :

| Code COG | Cible | Contrôle |
|---|---|---|
| `98817` | Le Mont-Dore (Nouvelle-Calédonie) | Distinction du nom « Mont-Dore » métropolitain |
| `97132` | Trois-Rivières (Guadeloupe) | Forme qualifiée / forme non qualifiée |
| `97213` | Le Lamentin (Martinique) | Formes avec et sans article |
| `97217` | Le Marin (Martinique) | Homographe « Marín » sans identité prouvée |
| `97407` | Le Port (La Réunion) | Commune réunionnaise / toponyme générique « Port » |

Les cas **Saint-Martin** et **Saint-Barthélemy** illustrent le filtrage contextuel : les concepts explicitement qualifiés `(Gers)`, `(Landes)`, etc., restent conservés dans les lignes d'audit mais **ne sont pas des candidats prioritaires** pour les collectivités antillaises. Les concepts `(Antilles Françaises)` possèdent au contraire des signaux territoriaux et des URI Insee documentaires à contrôler.

## 5. Fichiers, méthode et limites

`scripts/auditer_pactols_outremer_integral.py` parcourt le RDF en flux, contrôle les empreintes de ses sources et exporte trois tableaux de recette et un rapport. `scripts/qualifier_candidats_pactols_outremer.py` classe sans supprimer les candidats bruts. Les deux générateurs disposent de tests Python et sont exécutés deux fois dans le workflow `.github/workflows/audit-lieux-pactols-outremer-integral.yml` ; les résultats doivent être reproductibles à l'octet.

**Aucun ARK n'est attribué à une entité COG par automatisme.** Une URI numérique de même code ou un libellé concordant demeure une **assertion à examiner** : la portée géographique, le statut COM / DIS / CIR / CPT / CDM, les homonymies, la temporalité du code et l'éventuelle réutilisation historique restent distincts.

Il n'existe dans ce lot **aucune nouvelle correspondance Pactols–COG validée, aucune géométrie historique attribuée et aucun changement du module publié dans `docs/`**. La PR #30 reste en brouillon pour la campagne de validation éditoriale.

### Prochaine instruction

Chercher les éventuels concepts de groupe et les variantes des **neuf cibles sans signal**, à commencer par les cinq districts TAAF, puis contrôler individuellement les cinq cas à plusieurs candidats. Les relations approuvées seulement pourront entrer ultérieurement dans un JSON de production mondial.
