# Recherche Lieux — classer les homonymes au millésime COG sélectionné

**20 novembre 2026.** Traçabilité : [issue #159](https://github.com/nicocoquet/adlfi-referentiels/issues/159), classement chronologique et non-assimilation des identités communales.

## Cas documenté : Afa (Corse)

La recodification corse de 1976 conserve des **épisodes COG distincts**. Le corpus des périodes communales permet de demander explicitement une date et de vérifier si le code était en vigueur à son premier janvier.

| Recherche | Millésime affiché | Résultat privilégié | Autres résultats |
|---|---:|---|---|
| `Afa` | 2026 | Commune `2A001`, COG actif | Ancien code `20001`, étiqueté comme non actif en 2026 |
| `Afa` | 1975 | Commune `20001`, COG actif | `2A001`, non actif en 1975 |
| `20001` | 2026 | Code `20001` demandé explicitement | La recherche explicite par identifiant prévaut sur la préférence chronologique |
| `2A001` | 1975 | Code `2A001` demandé explicitement | Identifiant futur signalé non actif au millésime sélectionné |
| `26678/pcrtgs2LLPYow2` | 1975 | ARK demandé explicitement | Le libellé `Pactols validé pour 2026` conserve la date de sa validation |

**L'index historique n'est pas modifié :** ni les codes, ni les concepts Pactols, ni les relations administratives ne sont fusionnés. Les deux résultats continuent d'être proposés. La préférence tient uniquement à la validité de l'état COG pour la date demandée.

## Méthode

- `docs/assets/lieux-recherche-millesime.js` rassemble les intervalles `periodes_com` existants, indexés par `zone:code`. Il évalue `debut_inclus <= YYYY-01-01 < fin_exclue` pour les communes `typecom=COM`.
- La recherche privilégie, à libellé équivalent, les **codes COG actifs** de l'année sélectionnée ; l'ARK Pactols reste une validation **2026**, sans rétroprojection. Un code ou un ARK **explicitement saisi** reste prioritaire indépendamment du millésime.
- Les résultats actifs et anciens portent une indication de situation administrative. Une entrée ancienne reste accessible, même si elle ne dispose d'aucune géométrie historique.
- Le même mécanisme sert pour Normandie et ses autres régions : il ne suppose pas la continuité d'une commune nouvelle sous le code de sa commune historique.
- Ce classement ne remplace pas une vérification d'identité en cas de code INSEE conservé après fusion : deux concepts Pactols peuvent conserver le même code tout en restant historiquement distincts.

## Recette

- Node : simulation Afa 20001 → 2A001 autour de 1976, priorité de l'ancienne commune en 1975 et de la commune actuelle en 2026, surclassement des identifiants saisis explicitement, cas Normandie 50129 depuis 2016.
- Chromium : recherche réelle « Afa » en 2026 puis 1975, inspection du premier résultat et de ses qualificatifs ; recherche par `20001`, `2A001` et ARK direct.
- Non-régression des cinq régions et de la sélection des géométries communales.
- Aucun nouveau contour, aucun alignement Pactols, aucun changement de schéma de publication ; le COG déjà chargé fait foi.

## Suite

Réexaminer les quatre exceptions normandes encore ouvertes : Port-Bail-sur-Mer, Breteuil, Isigny-sur-Mer et Bourgvallées. Puis reprendre le chantier Organismes/Services avec le maître XLSX **1.49**, la génération JSON et les facettes de secteur/périmètre, **avant** de publier une sixième région.
