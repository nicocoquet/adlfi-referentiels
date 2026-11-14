# Référentiel Lieux — audit national des hiérarchies Pactols (14 novembre 2026)

**Statut : recette non validante.** Aucun alignement Pactols–COG ni contour géographique n'est modifié.

## Résultats

| Indicateur | Autorités ARK |
|---|---:|
| ARK attestés dans le corpus AdlFI | **9 928** |
| Au moins deux chaînes brutes ARK + libellés | **2 034** |
| Différences uniquement dues à la racine facultative « entités actuelles » | **1 994** |
| Variantes résiduelles à instruire | **40** |
| Avec ancêtre incomplet dans au moins une chaîne XML | 25 |
| Différences de libellés sans changement des ARK ancêtres | 13 |
| Hiérarchies hydrographiques alternatives | 1 |
| Branche de classement historique distincte | 1 |

La racine facultative est reconnue **par son ARK** `26678/pcrtd5d8pstxspv6dbhp7d8g`, et non par un libellé. Selon les XML, elle apparaît sous plusieurs libellés : « entités actuelles », « _entités politiques et administratives actuelles », « entités géopolitiques actuelles ». Elle est ignorée **seulement pour la comparaison**. Les chaînes originales sont toutes conservées.

Le détail exhaustif des 40 exceptions, avec les chemins d'origine et les fichiers témoins, se trouve dans `hierarchies-residuelles-40.csv`.

## Les exceptions de libellés

Les 13 variantes de libellés incluent notamment des couples qui peuvent correspondre à un changement historique de dénomination, comme **Montignac (Dordogne) / Montignac-Lascaux**, **Céreste / Céreste-en-Luberon**, **Exideuil / Exideuil-sur-Vienne**, ainsi que des différences typographiques ou de description (grotte Cosquer, Roëzé-sur-Sarthe). Ces variantes ne doivent pas être fusionnées ou datées automatiquement à partir des années d'opération archéologique. Elles nécessitent un contrôle de l'autorité Pactols et du COG historique.

Les 25 hiérarchies avec ancêtre incomplet contiennent un nœud sans libellé, fréquemment dans des XML du Rhône-Alpes ancien : il faut vérifier la provenance et ne pas déduire un changement administratif à partir d'un vide XML.

Les deux exceptions d'un autre type concernent une hiérarchie hydrographique alternative (`26678/pcrtTJFe71EA69`, lac d'Annecy) et un classement à la fois actuel et dans les entités du passé (`26678/pcrtvyPdfBr78V`, Poitou-Charentes). Ces cas appellent une instruction typologique, pas un raccordement communal forcé.

## Méthode et limites

L'audit conserve une ligne par concept Pactols. Il distingue les variantes de racine, les variantes de libellé, les lacunes d'ancêtres et les changements de branche hiérarchique. **Les 40 exceptions ne représentent pas 40 contradictions géographiques avérées.**

Reproduction depuis le dépôt local :

```bash
python3 scripts/auditer_variantes_hierarchiques.py \
  --occurrences "$HOME/Desktop/AdlFI-audit-lieux-v2/occurrences_lieux.csv" \
  --sortie "$HOME/Desktop/AdlFI-hierarchies-recette"
```

Source : extraction nationale v2 `occurrences_lieux.csv`, SHA-256 `b2e7332515c051e0c63e1fb29c840fa338aa85040fb2358a7df64d735b2942cd`. Le script et ses six tests n'impliquent aucune suppression ou réécriture des XML originaux.
