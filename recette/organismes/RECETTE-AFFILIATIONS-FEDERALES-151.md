# Lot 1.51 — affiliations fédérales FFESSM et FFS

**Date d'instruction :** 20 novembre 2026. **Statut :** maître privé de recette, export JSON en PR. La publication ne confond pas affiliation fédérale et rattachement administratif, tutelle ou succession institutionnelle.

## Provenance et intégrité

- Source : `AdlFI_referentiel_1-50_lot_institutionnel_20261120_QUALIFIE_RECETTE.xlsx`, SHA-256 `6b6bf9a0ea0da8c54a56fc4b33224ac1161b5f885b599a0a4c6ca2d71cfe0668`.
- Maître de recette : `AdlFI_referentiel_1-51_affiliations_federales_20261120_RECETTE.xlsx`, SHA-256 `af3ee809099a28373a5b183afe70af27066aeb3d23e1776fd501a192be91e1d4`.
- Reconstruction conservatrice : **17 feuilles, 8 tableaux structurés, 34 hyperliens et 803 formules préservés**, 0 anomalie de fidélité OOXML, 0 modification de formule.
- Audit des cellules : **32 cellules modifiées ou ajoutées**, dont 28 dans les quatre nouvelles relations et 4 dans la ville, l'URL et la feuille de suivi.
- Exporteur officiel réexécuté : **934 autorités (734 ORG, 200 SER), 598 relations (342 REL et 256 RSE), 682 cartes visibles**, trois alias d'identifiants inchangés, 1 580 AFF et 2 140 COR inchangées.

## Relations validées dans le maître

| Relation | De | Vers | Répertoire et sources | Décision |
| --- | --- | --- | --- | --- |
| REL-0341 | ORG-0069 — CASAVO | ORG-0120 — FFESSM | Liste FFESSM, CASAVO à Taverny, code **07950920** ; site officiel `https://casavo.fr/` | `affiliation_federale`, `valide` |
| REL-0342 | ORG-0419 — IERO | ORG-0120 — FFESSM | Liste FFESSM, club IERO à Hyères, code **33830118** ; guide des sports 2022–2023 de la Ville de Hyères | `affiliation_federale`, `valide` |
| REL-0343 | ORG-0521 — Royan Océan Club Plongée | ORG-0120 — FFESSM | FFESSM, licences saison **2023–2024** et club **02170078** ; répertoire du comité départemental FFESSM 17 | `affiliation_federale`, `valide` |
| REL-0344 | ORG-0355 — Équipe d'explorations spéléologiques de Villefranche (EESV) | ORG-0701 — FFS | Annuaire **Trouver un club** du site FFS, EESV à Chessy-les-Mines | `affiliation_federale`, `valide` |

### Sources primaires

- FFESSM, liste des clubs et identifiants : https://ffessm.fr/uploads/media/docs/0001/12/d9bf52a41c5041bbe443e29f605cad6fac6cb80d.pdf
- FFESSM, saison 2023–2024 : https://ffessm.fr/uploads/media/docs/0001/12/a2710587114d4af065dc4aaa36750f7b8385447e.pdf
- Ville de Hyères, guide sports 2022–2023 : https://www.hyeres.fr/sites/default/files/atoms/files/guide_sports_2022-2023.pdf
- FFESSM Charente-Maritime, annuaire : https://www.codepessm17.org/fr/component/contact/category/22-clubs?Itemid=101
- FFS, annuaire des clubs : https://ffspeleo.fr/index.php?alias=trouver-un-club&sectionopts%5Ba0484cfe4329480dd1bcf8ac056c128b%5D%5Bfirst%5D=280
- EESV au catalogue documentaire fédéral : https://catalogue.cnds.ffspeleo.fr/index.php?id=206&lvl=publisher_see

**Dates :** les quatre lignes ont volontairement `date_debut` et `date_fin` vides. Une saison sportive ou une apparition dans un annuaire atteste une appartenance **à un moment donné**, mais ne prouve ni sa date de première adhésion ni une continuité ininterrompue jusqu'à aujourd'hui. L'interface affiche « Dates non documentées ».

**Validations des autorités :** les entrées `ORG-0355` (EESV), `ORG-0419` (IERO) et `ORG-0521` (Royan) restent au statut global `a_verifier` ; la validation de leur lien fédéral n'implique pas la validation de tous les champs institutionnels.

## Cas non intégrés

- `ORG-0418` — Clan spéléo pontoisien : une notice du CNDS FFS documente des travaux/éditions, pas une preuve suffisante de son affiliation fédérale actuelle ou historique.
- `ORG-0531` — Société spéléo-archéologique de Caussade : présence dans la documentation FFS et prix fédéral en 2011, sans détermination sûre de l'intervalle d'affiliation ; organisme inactif depuis 2021 selon le maître. **Ne pas créer de lien automatiquement**.
- Aucun doublon des deux affiliations `REL-0338` (GRASM) et `REL-0339` (CDS 06) existantes.

## Recette et publication

- `scripts/recette_publication_organismes_151.py` contrôle 934 autorités, 598 relations, six affiliations documentées, alias, provenance SHA-256, maintien des autorités provisoires et conservation intégrale des invariants du 1.50.
- Contrôles Node et Chromium : navigation réciproque membre ↔ fédération, absence de confusion avec les tutelles, dates non documentées.
- Publication du JSON seule, sans divulgation des commentaires ni des feuilles du maître XLSX privé. Le XLSX de recette doit être adopté explicitement comme source canonique de la prochaine version de travail avant ouverture d'autres lots.

Suivi : [issue 174](https://github.com/nicocoquet/adlfi-referentiels/issues/174).
