# Normandie — neuf validations d'identités Pactols–COG 2026 (lot 01)

**20 novembre 2026 — registre 2026 indépendant de la cartographie et non activé dans l'interface.**

Instruction préalable : [PR #155](https://github.com/nicocoquet/adlfi-referentiels/pull/155), preuves RDF complémentaires et chronologie officielle dans [NORMANDIE-LOT01-IDENTITES-2026.md](NORMANDIE-LOT01-IDENTITES-2026.md). Projet national : [#152](https://github.com/nicocoquet/adlfi-referentiels/issues/152).

## Résultat

**9/10** codes du premier lot disposent d'une correspondance **validée uniquement pour la commune actuelle au COG du 1er janvier 2026**. Le dixième, **Port-Bail-sur-Mer (50412)**, n'a dans le RDF examiné qu'un `exactMatch` porté par l'ancienne commune *Portbail* ; il reste exclu.

Le registre est : `docs/data/lieux-chronologie/pactols-normandie-lot01-2026.json` ; schéma `adlfi.lieux.pactols.normandie.lot01.2026.public.v1`.

| Code actuel | Commune nouvelle | Date de création attestée | ARK retenu exclusivement pour 2026 |
|---|---|---|---|
| `14014` | Colomby-Anguerny | 2016-01-01 | `26678/pcrtAHatdH8M5h` |
| `14098` | Thue et Mue | 2017-01-01 | `26678/pcrt32xA0aWOKZ` |
| `14200` | Creully sur Seulles | 2017-01-01 | `26678/pcrtEU57VjwLxi` |
| `14456` | Moult-Chicheboville | 2017-01-01 | `26678/pcrtNAhK2vpwPa` |
| `14762` | Vire Normandie | 2016-01-01 | `26678/pcrt78ZZg0wMbU` |
| `27022` | Le Val d'Hazey | 2016-01-01 | `26678/pcrt5SNyKsPv04` |
| `27467` | Pont-Audemer | 2018-01-01 | `26678/pcrttaqrTGrSS9` |
| `50129` | Cherbourg-en-Cotentin | 2016-01-01 | `26678/pcrt4Ft3j507NA` |
| `61194` | Monts-sur-Orne | 2018-01-01 | `26678/pcrtZtrHp1bjSL` |

Chaque objet JSON conserve, **sans le promouvoir**, l'ARK de l'ancienne commune porteuse du même code COG, la date de création, la source INSEE, l'URI `exactMatch` du concept contemporain, sa qualification spécifique et la date d'arbitrage.

## Chaîne de preuves et contrôles

1. Le RDF Pactols est versionné par commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`. La sélection reprend le préflight de **2 644** communes normandes `TYPECOM=COM`, `REG=28`.
2. Pour **sept** concepts actuels, `prefLabel` + `skos:exactMatch` INSEE + `skos:historyNote` détaillant explicitement la création à la date COG attestent l'identité contemporaine. Les concepts de l'ancienne commune ont des ARK distincts et ne sont jamais promus.
3. Pour **Le Val d'Hazey**, la définition Pactols décrit la création en 2016 à partir d'Aubevoye, tandis que les métadonnées officielles INSEE documentent la même transition. L'ancienne commune reste une autorité distincte.
4. Pour **Pont-Audemer**, où ancienne commune et commune nouvelle portent le même nom et le code `27467`, la distinction repose sur le libellé « Pont-Audemer (commune déléguée) », les définitions RDF opposant *ancienne commune* et *commune*, et surtout les deux `exactMatch` distincts vers **Wikidata Q367667** (ancienne) et **Q47067820** (actuelle). Cette séparation est corroborée par l'arrêté préfectoral du 6 décembre 2017 et le COG INSEE, effet au 1er janvier 2018.
5. Le script `scripts/valider_normandie_lot01_pactols_2026.py` reconstruit le registre à partir du RDF et de l'audit du lot #155 ; **tout changement d'ARK, de note, de Wikidata, de millésime ou de provenance empêche la validation**. La CI compare la version contrôlée aux deux générations identiques et teste la non-promotion de Portbail ou des anciennes communes.

Sources de contrôle : [COG Insee 2026](https://www.insee.fr/fr/information/8740222), [Pont-Audemer – arrêté du 6 décembre 2017](https://www.legifrance.gouv.fr/eli/arrete/2017/12/6/INTB1735365A/jo/texte), [Wikidata Q47067820](https://www.wikidata.org/wiki/Q47067820), [Wikidata Q367667](https://www.wikidata.org/wiki/Q367667). Les dix dossiers ont également leur lien INSEE individuel dans le registre d'instruction #155.

## Limites et règles d'affichage

- **Ce registre n'affirme pas la couverture de Normandie** : 9 correspondances locales, non les 2 644 communes COG 2026 et encore moins toutes les autorités indexées dans les notices.
- **Non activé dans la carte** (`active_dans_interface=false`) : aucun nouveau contour normand n'est affiché et aucun code de l'interface Lieux n'est modifié dans ce lot.
- **Aucune validation rétrospective** des opérations antérieures à la création des communes nouvelles. L'année d'opération peut précéder la création administrative de la commune qui sert de descripteur géographique actuel.
- Les anciens ARK ne deviennent ni des alias ni des `skos:exactMatch` du nouveau concept ; aucune relation de succession ontologique ne découle automatiquement du COG.
- **Port-Bail-sur-Mer** reste sans ARK contemporain validé dans cette tranche. Ne pas requalifier les 19 occurrences de Portbail en correspondances de Port-Bail-sur-Mer.
- Aucun contour 2026 ne devient limite historique à travers ce registre.

## Suite

La publication cartographique de Normandie doit attendre le chargeur de géométries régional (dossier #152) ; les autres correspondances `exactMatch` normandes admissibles seront intégrées par **lots distincts et contrôlés**, en conservant les 148 exceptions du préflight et l'index séparé des événements historiques COG.
