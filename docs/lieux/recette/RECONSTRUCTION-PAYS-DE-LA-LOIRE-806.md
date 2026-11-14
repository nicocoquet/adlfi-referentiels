# Pays de la Loire — reconstruire les 806 autorités (recette non validante)

Le dépôt contient désormais l'orchestrateur `scripts/reconstituer_lieux_pays_loire_806.py`, ses trois tests et le workflow pilote. **Le traitement intégral n'a pas encore été exécuté**, car les trois CSV de l'extraction nationale v2 ne sont pas versionnés dans la branche.

## Préconditions

Depuis la racine du dépôt, vérifier la présence de :

- `$HOME/Desktop/AdlFI-audit-lieux-v2/autorites_lieux.csv`
- `$HOME/Desktop/AdlFI-audit-lieux-v2/occurrences_lieux.csv`
- `controle_concepts_pactols.csv` provenant de l'audit SKOS national 2026-07-22 (chemin à définir)
- les fichiers Insee COG 2026 sous `$HOME/Desktop/AdlFI-sources-COG-2026/` ; s'ils sont absents, les télécharger depuis https://www.insee.fr/fr/information/8740222

Ne pas utiliser un export ultérieur silencieusement : toutes les sources ont une empreinte SHA-256 vérifiée par le programme.

## Commande

```bash
python3 scripts/reconstituer_lieux_pays_loire_806.py \
  --autorites "$HOME/Desktop/AdlFI-audit-lieux-v2/autorites_lieux.csv" \
  --occurrences "$HOME/Desktop/AdlFI-audit-lieux-v2/occurrences_lieux.csv" \
  --skos-csv "/CHEMIN/controle_concepts_pactols.csv" \
  --pilote "docs/lieux/recette/lot-01-pays-de-la-loire.csv" \
  --communes "$HOME/Desktop/AdlFI-sources-COG-2026/v_commune_2026.csv" \
  --historique "$HOME/Desktop/AdlFI-sources-COG-2026/v_commune_depuis_1943.csv" \
  --mouvements "$HOME/Desktop/AdlFI-sources-COG-2026/v_mvt_commune_2026.csv" \
  --sortie "$HOME/Desktop/AdlFI-lieux-PdL-806-recette"
```

Le dossier de sortie doit être neuf : le script refuse de remplacer `inventaire-pays-de-la-loire.csv` déjà existant.

## Garde-fous

1. Identité des empreintes des trois sources XML/SKOS contre `rapport-priorites-regionales.json` ; contrôle des trois fichiers Insee du COG 2026.
2. Nombre exact **806** et unicité des ARK de l'inventaire.
3. Reproduction des **25** ARK du pilote avec identité des libellés, département, catégorie géographique et assertions SKOS numériques ou UUID.
4. Production du contrôle historique sur **806 ARK** après ces vérifications, sans publication d'alignements ou de contours.
5. Écriture d'un `bilan-reconstruction.json` et d'un sous-dossier `audit-cog/` contenant candidats, périodes, événements et rapport.

**Limite actuelle :** l'auditeur rattache des périodes et mouvements aux codes déclarés, mais ne construit pas encore une généalogie transitive des communes fusionnées ou absorbées. Les résultats numériques produits à cette étape doivent être considérés comme des indices d'instruction, non comme des identités historiques validées.

## Contrôles continus

- Workflow pilote du 14 novembre : https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43602852827 — tests et contrôle sur données Insee officiels **réussis**.
- CI générale (même commit) : échec préexistant ou indépendant du présent traitement sur le test des logos Organismes : `assets/organismes/ORG-0023-logo.svg` absent. Ne pas confondre avec un échec de l'auditeur Lieux ; à corriger séparément.
