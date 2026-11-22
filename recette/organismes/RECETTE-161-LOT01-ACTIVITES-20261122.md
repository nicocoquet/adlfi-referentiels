# Organismes 1.61 — recette du premier lot

Date de préparation : 22 novembre 2026. **État : candidat non fusionné.**

## Provenance et périmètre

- Maître source 1.60 : `AdlFI_referentiel_1-60_lot01_quatre_activites_CANDIDAT.xlsx`; SHA-256 `70aeff4fedc66a54d1a45240af0d22cee1130565e2b29cefb1495e83aa434098`.
- Maître candidat 1.61 : `AdlFI_referentiel_1-61_lot01_activites_et_date_CANDIDAT.xlsx`; SHA-256 `fb475d0270ca74757c7d34dc97978897dccdf5b12cc10c2ec8aa3f35a65e8b98`.
- Contrôle OOXML indépendant : 41 membres d'archive, dont deux modifiés (`xl/worksheets/sheet2.xml`, `xl/worksheets/sheet3.xml`). **Huit cellules changées, aucune autre.**
- Référence publique 1.60 : commit `8dbac1ed2afe0e7a65022da8f332d0338f54bc3b`.

| Identifiant | Cellule | Champ | Avant | Après | Justification / réserve |
|---|---|---|---|---|---|
| ORG-0349 — ArchéoSolution | Organismes!L340 | actif | vide | oui | [La Rochelle Université](https://lienss.univ-larochelle.fr/Bruniaux-Guillaume-2007), [manifestation juin 2026](https://s-pace.fr/a-la-decouverte-des-secrets-de-carnac/) ; ne pas confondre EI et UMR |
| ORG-0375 — Atelier Bell | Organismes!L366 | actif | vide | non | [Dissolution/radiation, SIREN 445029457](https://entreprises.lefigaro.fr/atelier-bell-50/entreprise-445029457) ; date_fin non arbitrée (effet 2019 / radiation 2020) |
| ORG-0438 — IMMADRAS | Organismes!L425 | actif | vide | oui | [Annuaire des entreprises, SIREN 317034916](https://annuaire-entreprises.data.gouv.fr/entreprise/317034916), [DRAC PACA](https://www.culture.gouv.fr/zh/regions/drac-provence-alpes-cote-d-azur/la-direction-regionale-des-affaires-culturelles-drac-provence-alpes-cote-d-azur/service-regional-de-l-archeologie/la-grotte-cosquer-30-annees-de-recherches) ; raison sociale à préciser |
| ORG-0468 — GEOMAR | Organismes!L454 | actif | vide | oui | [Registre et comptes, SIREN 794408542](https://www.pappers.fr/entreprise/geomar-794408542) ; écarter l'homonyme luxembourgeois |
| ORG-0494 — Archéo-Île | Organismes!L479 | actif | vide | oui | [Collectivité de Corse, manifestation octobre 2025](https://www.isula.corsica/culture/agenda/Conference-Les-decouvertes-de-la-vallee-du-Prunelli-2A-par-Nadia-Ameziane-Federzoni-docteure-en-archeologie_ae1954953.html) ; SIREN non identifié |
| ORG-0716 — Urbe pro Orbe | Organismes!L696 | actif | vide | oui | [Suivi du registre mercantile, CIF B86996261](https://apiempresas.es/B86996261-urbe-pro-orbe-patrimonio-cultural-sl), [marché archéologique 2025](https://www.alicitar.es/licitacion/9011138/direccion-tecnica-arqueologica-de-la-obra-de-obras-de-consolidacion-de-la-crujia) ; contrôle direct du registre à envisager |
| SER-0195 — Laboratoire de Préhistoire Nice-Côte d'Azur | Services!J194 | actif | vide | oui | [HNHP](https://hnhp.mnhn.fr/fr/annuaire/dominique-cauche-11256), [publication scientifique déc. 2025](https://www.em-consulte.com/article/1782042/les-lapins-du-pleistocene-moyen-genre-oryctolagus-) ; ne pas confondre avec le Lazaret |
| SER-0193 — Cellule alpine de recherches archéologiques | Services!K192 | date_debut | vide | 2011 | [Annonce départementale, création explicitement datée de 2011](https://www.prehistoire.org/offres/file_inline_src/515/515_pj_260215_162757.pdf) ; ne pas assimiler à l'agrément 2013, actif reste indéterminé |

## État attendu du JSON

- **935 autorités** : 735 ORG, 200 SER ; 683 incluses et 252 exclues du catalogue.
- **600 relations institutionnelles**, sans changement d'identifiant ni de contenu.
- Activité : **719 actives**, **142 inactives**, **74 indéterminées**.
- Comparaison stricte 1.60 → 1.61 : **18 modifications de valeurs exclusivement** :
  - sept `activity.active` ;
  - sept `quality.activity_unknown` ;
  - un `quality.end_missing` (ORG-0375 inactif, fin encore inconnue) ;
  - un `activity.start` (SER-0193, `2011`) ;
  - deux champs `provenance` (`source_filename`, `source_sha256`).
- Horodatage reproductible inchangé : `2026-11-22T00:00:00+00:00`.

## État de la preuve

Le JSON candidat de la branche est **une projection déterministe du JSON 1.60**, effectuée exclusivement sur les champs que l'exporteur officiel `scripts/export_organismes.py` produit à partir des huit cellules modifiées. Cette projection est vérifiée par `tests/test_recette_publication_organismes_161.py`.

**Point bloquant avant fusion : vérifier la parité exacte avec l'exporteur officiel** depuis le maître 1.61, en exécutant :

```bash
SOURCE_DATE_EPOCH=1795305600 python3 scripts/export_organismes.py \
  "$HOME/Downloads/AdlFI_referentiel_1-61_lot01_activites_et_date_CANDIDAT.xlsx"
git diff --exit-code -- docs/data/organismes.json
```

La deuxième commande doit retourner un code 0, sans différence. Si elle révèle un écart, examiner la sortie de l'exporteur et corriger le candidat en priorité ; ne jamais affaiblir les assertions différentielles pour faire passer la recette.

Les tests Python, Node et Chromium de la PR doivent également être verts avant fusion.
