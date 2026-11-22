# Recette Organismes 1.60 — lot 01 (activités)

Date de préparation : 22 novembre 2026.

## Périmètre documentaire

Maître de départ : `AdlFI_referentiel_1-59_activites_CANDIDAT.xlsx` (SHA-256 `3926b703b9e0fb20d3ed09068282ca97ea718eff14659ba8e3692b2cae0fe53e`).

Candidat : `AdlFI_referentiel_1-60_lot01_quatre_activites_CANDIDAT.xlsx` (SHA-256 `70aeff4fedc66a54d1a45240af0d22cee1130565e2b29cefb1495e83aa434098`).

Un audit OOXML indépendant a constaté **quatre cellules modifiées exclusivement** sur la feuille `Organismes` : `L171` (`ORG-0179`), `L320` (`ORG-0328`), `L338` (`ORG-0347`), `L432` (`ORG-0446`). Les quatre valeurs passent de vide à `oui`. Tous les autres membres de l'archive XLSX sont inchangés ; seule `xl/worksheets/sheet2.xml` diffère.

## Justificatifs et réserves

| Autorité | Modification | Référence documentaire | Réserve |
|---|---|---|---|
| ORG-0179 — AVVAS | `actif = oui` | [TV Vendée : exposition anniversaire en 2026](https://tvvendee.fr/actu/les-sables-dolonne-une-exposition-pour-plonger-dans-les-fonds-marins-vendeens/) | Ne pas inférer une date de création précise |
| ORG-0328 — ARSSAT | `actif = oui` | [Forum des associations 2026](https://sites-et-patrimoine-tregastel.info/WordPress3/2026/08/forum-des-associations-2026/) | Ne pas inférer de nouvelle relation |
| ORG-0347 — Archeoverde | `actif = oui` | [Avis BOAMP de juin 2025](https://www.boamp.fr/telechargements/FILES/PDF/2025/06/25-70484.pdf) ; [ARTEHIS — Cécile Travers](https://artehis.ube.fr/membres/travers-cecile/) | Distinguer l'enseigne et l'identité juridique, ne pas inventer de SIREN |
| ORG-0446 — Escles-Archéologie | `actif = oui` | [Commune d'Escles](https://sites.google.com/site/mairiedescles/la-mairie-descles/actualit%C3%A9s) | Aucune date de création supplémentaire |

**SER-0195** (Laboratoire de Préhistoire Nice-Côte d'Azur) reste à instruire : l'attestation d'activité d'une structure à dénomination voisine ne suffit pas à qualifier l'identité de ce service.

## Contrôles de publication

La publication du JSON 1.60 doit impérativement vérifier :

- provenance exacte (nom du maître et SHA-256), horodatage reproductible du 22 novembre 2026 ;
- **935 autorités**, **735 ORG**, **200 SER**, **683 incluses**, **252 exclues**, **600 relations** ;
- **713 actives**, **141 inactives**, **81 indéterminées** ;
- comparaison *exhaustive* au JSON du commit 1.59 `3b34b353f11cc702531de0e83237bcb4c81fac90` : quatre `activity.active`, quatre `quality.activity_unknown`, deux champs de provenance et rien d'autre ;
- suites Python, Node, Chromium et GitHub Actions réussies avant fusion.

**État** : candidature préparée ; aucune publication validée tant que l'export officiel et la CI ne sont pas terminés.
