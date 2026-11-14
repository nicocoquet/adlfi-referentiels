# Lieux AdlFI — Recette corse, deuxième phase Pactols ↔ COG historique

**État : contrôle de preuve, non validant et non publié.**

## Provenance et périmètre

Source documentaire : extraction AdlFI v2 (13 novembre 2026). La sélection géographique suit la **hiérarchie des ARK Pactols**, non le nom du dossier XML. Source des liens : `skos:exactMatch` de Pactols Lieux, export Frantiq du 22 juillet 2026, SHA-256 RDF `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.

- Corse : **200** ARK terminaux ; **1 006** occurrences ; **757** notices distinctes.
- **194** assertions Pactols vers des URI de **commune** Insee avec un code à cinq caractères `2A...` ou `2B...`.
- **6** autorités hors rapprochement communal : région Corse, départements Corse-du-Sud et Haute-Corse, Cap Corse, Balagne et Filitosa.
- Premier lot : **25 ARK**, dont **22 communes candidates** et **3** autres lieux (Cap Corse, Balagne, Filitosa).

## Nouvel auditeur régional

`python3 scripts/auditer_lieux_corse_cog.py` joint les 200 autorités avec trois jeux officiels du COG 2026 :

- `v_commune_2026.csv` : type (`TYPECOM`), code, région `94`, département `2A` / `2B`, libellé actuel ;
- `v_commune_depuis_1943.csv` : périodes **des couples code–libellé** et formes antérieures ;
- `v_mvt_commune_2026.csv` : événements administratifs datés depuis 1943.

Sources et définitions : https://www.insee.fr/fr/information/8740222

Le croisement par **identifiant Insee déjà déclaré dans Pactols** est prioritaire. L'auditeur refuse les codes mal formés et les changements non documentés ; il conserve les divergences sans les corriger. La différence de libellé accompagnée d'une parenthèse de département, comme « Saint-Florent (Haute-Corse) », est distincte d'une divergence toponymique réelle.

Le parcours des codes antérieurs **ne traverse que les changements de code `MOD=41`** : les fusions, créations de communes nouvelles et autres événements ne peuvent jamais produire une « continuité » automatique d'identité ou de contour. Toutes les autres lignes de mouvement liées aux codes sont recensées **pour expertise**.

Les périodes `DATE_DEBUT` / `DATE_FIN` ne sont **pas** des périodes certifiées de stabilité territoriale. De même, une année d'opération archéologique ne date pas la création d'une commune. Les concepts de région, département, région naturelle et site archéologique restent hors alignement au COG communal ; leurs géométries devront provenir de référentiels appropriés.

## Cas déjà établis par les preuves COG du lot national 001

- **Afa** : `COM 20001 → COM 2A001`, effet **1976-01-01**, `MOD=41` ; ARK `26678/pcrtgs2LLPYow2`.
- **Aghione** : `COM 20002 → COM 2B002`, effet **1976-01-01**, `MOD=41` ; ARK `26678/pcrtGx0ke7aJM6`.

La présence de ces deux mouvements est un **test bloquant** du workflow régional, mais ne confère pas un statut `validé` aux liens Pactols–COG.

## Sorties attendues

- `corse-200-candidatures-cog.csv` : une ligne par ARK, code Pactols, code COG 2026, forme officielle, catégorie d'audit, mouvement(s) et statut éditorial ;
- `corse-25-prioritaires-cog.csv` : reprise du premier lot sélectionné ;
- `corse-200-evenements-cog.csv` : **indices de mouvement**, éventuellement répétés entre autorités concernées (ne pas confondre avec un décompte d'opérations uniques) ;
- `corse-200-historique-detail.json` : couples code–libellé et événements par ARK ;
- `rapport-corse-cog-2026.json` : effectifs et SHA-256 des cinq sources.

Le workflow `.github/workflows/audit-lieux-corse-cog2026.yml` télécharge les CSV Insee, exécute les tests puis archive les résultats en **artefact GitHub Actions**, distinct des fichiers publiés par Pages.

### Règles de validation

Aucun `skos:exactMatch` de Frantiq n'est créé ni modifié. **Un lien Insee existant dans Pactols reste une assertion de Frantiq**, pas une validation éditoriale AdlFI. Il faut conserver séparément les identités historiques, événements COG, attestations TEI et provenance de la géométrie. **Aucun fichier `docs/data/lieux*` n'est modifié par cette étape.**
