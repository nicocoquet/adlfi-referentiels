# Lot 03 — continuités institutionnelles des EPCI (maître privé 1.43)

**Date :** 11 novembre 2026  
**Statut :** contrôles éditoriaux terminés ; **PR n° 14 toujours en brouillon**, aucune donnée 1.43 publiée sur GitHub Pages.

## Maître privé

- Fichier : `AdlFI_referentiel_1-43_20261111_historique_EPCI_lot03.xlsx`
- SHA-256 : `4062516f4f5bf66b4c160d980c7199cbca8edb91dd10d50ab2ffb1dc06d10108`
- Source : `AdlFI_referentiel_1-42_20261111_EPCI_syndicats_lot02.xlsx` (SHA-256 `4003217420d73ae03ec05f96385f9e7efa0f52b99191cdbd7402f9500169869c`).
- **17 feuilles et 8 tables Excel**, dont `TabStatutsHistoriques` étendue de `A1:L31` à `A1:L43`; même inventaire de 40 parties OOXML. Contrôles ZIP CRC, parsabilité XML, formules et comparaison cellule à cellule réussis.
- Source privée : **ne pas publier le XLSX sur GitHub**.

## Six dossiers consolidés : douze séquences supplémentaires

| ORG | Naissance de la personne morale | Statuts juridiques ajoutés | Forme existante conservée |
|---|---|---|---|
| `ORG-0219` Roissy Porte de France | 1994 inchangé | `STH-0031` CC, `0032` CA (2013–2015) | Fusion en 2016 documentée par `REL-0299` |
| `ORG-0415` Riom Communauté | 1999 (année) | `STH-0033` CC, 1999–2016 | `actif=non` ; `date_fin=2016-12-31` |
| `ORG-0658` Clos du Cotentin SIVU | 1998-12-28 inchangé | `STH-0034` SIVU, jusqu'au 2015-12-31 | Succession `REL-0292` vers une autre personne morale (`ORG-0659`) |
| `ORG-0190` Toulouse Métropole | **1992**, et non 2015 | `STH-0035` district (1992), `0036` CA (2001), `0037` CU (2009) | Métropole `STH-0013` (2015) |
| `ORG-0242` Nantes Métropole | **1991**, et non 2015 | `STH-0038` district, `0039` CU (2001) | Métropole `STH-0016` (2015) |
| `ORG-0516` Orléans Métropole | **1999**, et non 2017 | `STH-0040` CC, `0041` CA (2002), `0042` CU (janv.–avril 2017) | Métropole `STH-0024` (mai 2017) |

**Règle :** une transformation juridique sans changement de personne morale ne déclenche pas la création d'une nouvelle ORG. L’année d'opération et la date d'un arrêté ne valent pas nécessairement date d'effet. Les périodes anciennes de précision annuelle conservent une borne à l'année (`precision_dates=annee` ou `mixte`).

### Cinq dossiers restant ouverts

1. `ORG-0162` SAN Ouest Provence : continuité éventuelle SCA (1972) → SAN (1984) non démontrée.
2. `ORG-0659` syndicat mixte du Clos du Cotentin : arrêté constitutif et convention d’échelon intercommunal à instruire, sans le transformer en EPCI.
3. `ORG-0213` CC Nord du Bassin de Thau : prise d'effet de l'arrêté de décembre 2000 à vérifier.
4. `ORG-0403` Cap Calaisis : ancien arrêté et SIREN à confirmer.
5. `ORG-0214` Sète agglopôle : second EPCI prédécesseur à documenter avant création éventuelle d'une autorité.

**Clos sans changement :** `ORG-0633` Seine et Yvelines Archéologie, dont `STH-0026` suffit déjà (syndicat mixte ouvert ; acte constitutif du 17 août 2022).

## Reproductibilité et publication

- Dans le XLSX, les 12 dossiers historiques disposent désormais d’un état explicite `TRAITÉ`, `OUVERT` ou `CLOS`. Le journal éditorial contient **34 entrées supplémentaires** et le vocabulaire inclut `district`.
- Seules quatre ORG ont des champs directement changés ; le reste correspond à des statuts historiques supplémentaires et à la documentation.
- **Données inchangées :** 654 ORG, 166 SER, 1 580 affiliations sources, 2 140 correspondances, 303 relations ORG, 219 relations SER ; 820 autorités au total, 615 visibles.
- Activité : 111 autorités inactives, 154 indéterminées.
- JSON de prépublication : `AdlFI_organismes_1-43_JSON_prepublication_20261111.json`, SHA-256 `028f03bff74a2b1a55a8a894ac33595e4ff8a831b5e4211487bc9839dbb1e5b4`, blob Git `ffbfa83c3c5b3e40ae52150865ece22d11bbd139`.
- **Méthode JSON :** transformation contrôlée du JSON officiel 1.42 et confrontation de toutes les ORG et des 42 STH avec le maître 1.43, en tenant compte des dates sérielles d’Excel. Ce n’est **pas encore un export intégral réexécuté à partir de l’outil natif**.
- La PR n° 14 contient déjà l'adaptation de la facette vers « Échelon institutionnel » ; elle n'est pas fusionnée dans l'attente d'une recette visuelle.

## Sources principales

- Toulouse : https://metropole.toulouse.fr/institutions-et-territoires/toulouse-metropole/decouvrir-la-metropole
- Nantes / BANATIC : https://www.banatic.interieur.gouv.fr/intercommunalite/244400404
- Orléans : https://www.orleans-metropole.fr/fileadmin/orleans-metropole/MEDIA/kiosque/divers/RA_2017_Metropole_WEB.pdf
- Riom / CRC : https://www.ccomptes.fr/fr/publications/communaute-de-communes-riom-communaute-puy-de-dome-0
- Roissy : https://politique.pappers.fr/commune/document/160074f44e4460f8af523ea0f0b3e20a
- Clos du Cotentin : https://politique.pappers.fr/commune/document/103dc57174feb7e5e9f681d33c935dd2
