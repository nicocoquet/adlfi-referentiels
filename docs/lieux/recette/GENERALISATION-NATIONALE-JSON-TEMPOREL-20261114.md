# Lieux — généralisation nationale du JSON temporel, curseur annuel unique

**14 novembre 2026 — PR n°24, recette non publiée.**

## Choix d'architecture confirmé

La recherche documentaire par ARK Pactols et la consultation historique du Code officiel géographique (COG) sont **deux index distincts** :

1. **Index XML AdlFI–Pactols :** les **9 928 ARK terminaux** attestés dans les XML actuellement disponibles, leurs libellés et variantes, les années d'opération uniquement à titre documentaire. **103 correspondances Pactols–COG du pilote PACA sont déjà validées**. Les **9 825 autres** n'obtiennent aucun code Insee par inférence lexicale ou hiérarchique.
2. **Index COG temporel national :** les codes, libellés et événements administratifs attestés par l'Insee depuis 1943, utilisables avec un curseur **à une seule année**, correspondant précisément au **1er janvier** de l'année sélectionnée. Cet index n'attribue aucun ARK.

Le moteur de recherche des ARK doit rester **indépendant de la date sélectionnée** : un ancien nom de lieu demeure recherchable en 2026, même si son statut de commune a disparu.

Le module public **`docs/lieux/index.html`** et les données publiques **`docs/data/lieux.json`** demeurent inchangés à cette étape.

## Génération nationale du COG

Source : [COG au 1er janvier 2026, Insee](https://www.insee.fr/fr/information/8740222), fichiers CSV `v_commune_2026`, `v_commune_depuis_1943` et `v_mvt_commune_2026`. Les SHA-256 des trois fichiers sont exigés.

Générateur : `scripts/preparer_index_cog_national_temporel.py`.

| Objet | Volume contrôlé |
| --- | ---: |
| Codes ayant connu un état `COM` depuis 1943 | **39 117** |
| Périodes historiques de communes `COM` | **42 288** |
| Périodes d'arrondissements municipaux `ARM` | **45** |
| Communes `COM` observées en 2026 | **34 875** |
| Communes déléguées `COMD` observées en 2026 | **2 105** |
| Communes associées `COMA` observées en 2026 | **471** |
| Arrondissements municipaux `ARM` en 2026 | **45** |
| Mouvements officiels distincts, tous types MOD | **13 734** |
| **Segments JSON** | **98** |

Le générateur produit :

- `manifest-cog-national.json` : volumes, provenance, SHA des segments et années autorisées ;
- `index-toponymes-cog.json` : recherche lexicale des noms administratifs historiques, **sans liens Pactols présumés** ;
- `segments/cog-XX.json` : états `COM` et `ARM`, observations `COMA`/`COMD` limitées à 2026, et mouvements avant/après pertinents.

**XX est un préfixe de code Insee, et non une preuve de localisation géographique à toutes les dates.** Les changements interdépartementaux apparaissent dans les segments des deux codes concernés, avec un identifiant commun de mouvement pour permettre leur dédoublonnage.

L'index lexical COG comporte **39 162 entrées de code** (39 117 codes `COM` et 45 codes `ARM` distincts ; les communes associées et déléguées réutilisent des codes historiques). Les périodes de validité sont traitées comme des intervalles **[DATE_DEBUT, DATE_FIN[**.

### Deux cas spécifiques révélés par le contrôle national

Les deux lignes de source Insee **Freigné (`44225`) et Pont-Farcy (`50649`)** ont `DATE_DEBUT=DATE_FIN=2018-01-01` : elles sont conservées comme **périodes de durée nulle** dans les segments, mais ne sont jamais actives à une date de consultation.

Les mouvements `MOD=20` peuvent n'avoir **aucune commune avant** (127 lignes), tandis que deux mouvements `MOD=30`, concernant Saint-Barthélemy et Saint-Martin en 2007, n'ont **aucune commune après**. Ces absences officielles sont conservées : aucun code fictif n'est ajouté.

## Index national des autorités XML AdlFI–Pactols

Script versionné : `scripts/preparer_index_pactols_xml_national.py`. Exécution sur l'extraction XML du 13 novembre 2026, dont les CSV `autorites_lieux.csv` et `occurrences_lieux.csv` sont vérifiés par empreintes SHA-256.

| Objet | Résultat |
| --- | ---: |
| ARK terminaux indexés | **9 928** |
| Occurrences XML témoins | **30 772** |
| Formes documentaires distinctes, cumulées par ARK | **12 326** |
| Correspondances PACA conservées comme validées | **103** |
| ARK sans correspondance COG validée | **9 825** |
| Nouveaux alignements ou contours historiques | **0** |

Le résultat `index-autorites-pactols-xml.json` contient le libellé et les variantes XML, les nombres de notices et d'occurrences et, exclusivement pour les 103 autorités validées, le code et le nom COG 2026. Les années d'opérations sont maintenues **sans les présenter comme dates d'identité administrative**.

L'extraction XML représente **le corpus converti disponible au 13 novembre 2026**, non l'intégralité de Pactols ni la totalité des notices archéologiques régionales. Les retards de conversion de certains XML bourguignons ne doivent donc pas être interprétés comme une absence de sites ou d'autorités.

## CI, reproductibilité et intégration future

Les sources COG sont désormais acquises par `scripts/recuperer_cog_2026.py` depuis l'[archive officielle Insee](https://www.insee.fr/fr/statistiques/fichier/8740222/cog_ensemble_2026_csv.zip), ses CSV individuels ou les ressources du même jeu de données diffusées sur data.gouv.fr. **La reprise automatique depuis un artefact GitHub expirant a été supprimée** ; la validation des trois SHA-256 reste obligatoire.

La [CI nationale](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43645817832) a réussi : les **98 segments** et le manifeste sont générés deux fois, comparés octet par octet et contrôlés individuellement. Les transitions Marchaux, Saint-Hymetière-sur-Valouse, Verdun-Ciel et Vaire ont été vérifiées, ainsi que les liens interdépartementaux d'Antorpe.

La CI comporte également des tests synthétiques de l'index XML, notamment l'interdiction d'attribuer un code Insee à une autorité sans validation éditoriale. L'index XML complet a été produit sur les deux CSV locaux vérifiés, et conservé dans le dossier de recette livré au titre de ce chantier.

### Prochaines étapes

1. Définir le **contrat de données commun** entre l'index ARK, l'index COG et la fiche affichée, avec statuts de preuve explicites.
2. Construire l'autocomplétion sur **les noms des ARK et les noms administratifs historiques**, en distinguant clairement concepts Pactols et entités COG sans lien validé.
3. Brancher le **curseur unique 1943–2026** sur les états `COM` datés et les événements COG, sans interpréter l'absence d'une `COM` comme la disparition d'un lieu.
4. Reprendre les **contours 2026**, en les affichant exclusivement comme géométries du millésime 2026. Ne pas dessiner de contours anciens faute de source.
5. Recette éditoriale et technique, puis seulement décision de publication sur GitHub Pages.

**Aucune relation P1/P2/P3 encore candidate n'a été validée ; aucun fichier de production n'a été changé ; la PR n°24 reste en brouillon.**
