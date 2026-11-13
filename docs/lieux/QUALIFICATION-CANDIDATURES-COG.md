# Référentiel Lieux — qualification géographique des candidats COG (recette)

## Pourquoi ce second passage ?

Le premier rapprochement du corpus AdlFI avec `v_commune_depuis_1943.csv` (COG Insee 2026) compare des **libellés**. Il ne peut pas, à lui seul, établir l'identité d'une autorité Pactols : 7 998 ARK ont un seul code candidat, 532 plusieurs codes et 1 256 aucun dans le premier bilan. Une correction du statut « hors champ communal » ramène ce dernier effectif à **1 226**, et porte les hors champ à **69** ; il s'agit d'une correction de catégorisation, sans modification des candidatures.

Ce second script exploite les **départements explicitement présents dans les hiérarchies Pactols** et le fichier des départements 2026 de l'Insee. Il n'effectue **aucune validation automatique** et n'écrit rien dans `docs/data`.

## Sources nécessaires

- `autorites_nationales.json`, produit par `construire_referentiel_lieux_national.py` avec le COG historique ;
- `candidatures_cog_historiques.csv`, même exécution ;
- `v_departement_2026.csv`, Insee, COG au 1er janvier 2026 :
  https://www.insee.fr/fr/statistiques/fichier/8740222/v_departement_2026.csv

Source documentaire : https://www.insee.fr/fr/information/8740222

Le fichier COG départemental 2026 **ne permet pas de résoudre directement les changements de limites ou de départements anciens** (ex. anciennes entités, changements de dénomination, anciennes subdivisions corses). Un rattachement non concordant ou introuvable reste à instruire. L'identité administrative doit finalement être reconstruite avec les mouvements de communes depuis 1943 (`v_mvt_commune_2026.csv`) et, si nécessaire, les états COG par millésime.

## Exécution

Depuis la racine locale du dépôt `adlfi-referentiels`, branche `feat/lieux-national-historique-cog-20261113` :

```bash
curl -fL --retry 3 \
  'https://www.insee.fr/fr/statistiques/fichier/8740222/v_departement_2026.csv' \
  -o "$HOME/Desktop/AdlFI-sources-COG-2026/v_departement_2026.csv"

python3 scripts/qualifier_candidatures_cog.py \
  --autorites "$HOME/Desktop/AdlFI-lieux-national-recette/autorites_nationales.json" \
  --candidatures "$HOME/Desktop/AdlFI-lieux-national-recette/candidatures_cog_historiques.csv" \
  --departements "$HOME/Desktop/AdlFI-sources-COG-2026/v_departement_2026.csv" \
  --sortie "$HOME/Desktop/AdlFI-lieux-qualification-recette" \
  --taille-lot 100
```

## Résultats

- `audit_candidatures_par_ark.csv` : **une ligne par ARK**, codes candidats, code(s) de département issu(s) de Pactols, concordance, alerte temporelle et statut d'instruction ;
- `lot_editorial_prioritaire_001.csv` : **jusqu'à 100 ARK** pour la première validation manuelle, répartis par département, en privilégiant les homonymies nationales résolubles par la hiérarchie départementale ;
- `rapport_qualification_cog.json` : répartition des classes et empreintes SHA-256 des trois entrées.

## Points de méthode

- Les correspondances PACA déjà validées sont **préservées et exclues du nouveau lot**.
- Les lieux sous une commune (anciennes communes, communes déléguées ou associées, sites) sont exclus de l'auto-priorisation et demeurent à qualifier individuellement. Le COG historique lu par le premier outil ne contient **dans son index de travail** que `TYPECOM = COM`. Les `COMD`, `COMA` et les événements sont à traiter par une couche spécifique tenant compte des identités `(TYPECOM, COM)` : **un code INSEE seul peut désigner des entités de type différent**.
- La concordance départementale est une **corroboration** fondée sur une hiérarchie documentaire Pactols et le COG 2026, non une certification historique de l'identité géographique.
- Une date d'opération AdlFI n'est **jamais** la date de validité d'un nom administratif, ni celle d'une géométrie.
- Après validation éditoriale, associer au **type de relation** (`identite`, `succession`, `partie de`, etc.) et à la période de validité la source précise et son empreinte ; ne pas affirmer qu'un contour 2026 représente une limite ancienne.
- Les 100 lignes constituent une **file d'instruction**, sans `skos:exactMatch` généré et sans changement des jeux publics.

## Tests

```bash
python3 -m unittest discover -s tests -p 'test_referentiel_lieux_national.py' -v
python3 -m unittest discover -s tests -p 'test_qualification_cog.py' -v
```