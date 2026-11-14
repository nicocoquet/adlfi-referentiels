# Référentiel Lieux — sous-lots 02 et 03 / étape de vérification SKOS

**État : recette. Vingt candidatures COG contrôlées administrativement. Zéro nouvel alignement Pactols–COG validé.**

## Sources utilisées

- `docs/lieux/recette/REVUE-CONTEXTES-LOT-001.md` (lot national 001, 83 dossiers ordinaires).
- `docs/lieux/recette/lot-001-prearbitrages.csv` : source des ARK, codes candidats, intervalles et attestations.
- Fiches communales **Insee / Code officiel géographique au 1er janvier 2026**, vérifiées individuellement par code et libellé.
- Extraction nationale AdlFI v2 (`notices.csv` et `occurrences_lieux.csv`) : titres, index géographiques, contexte des notices.

## Sous-lot 02 — dix communes administrativement corroborées

| Libellé Pactols | Département | COG 2026 | Particularité |
| --- | ---: | --- | --- |
| Ajac | 11 | `11003` | Lieu nommé dans le titre d'opération |
| Baraqueville | 12 | `12056` | Commune créée en 1973 : conserver la date historique |
| Tarascon | 13 | `13108` | Distinct du candidat lexical du département 09 ; plusieurs titres AdlFI corroborent les Bouches-du-Rhône |
| Avenay | 14 | `14034` | Autre code historique `51028` en Marne ; notice de synthèse normande |
| Dienne | 15 | `15061` | Autre code lexical `86094` (Vienne), département Pactols concordant avec le Cantal |
| Fontenille | 16 | `16141` | Autre code lexical `79122` ; étude interrégionale Loire–Charente |
| Arces | 17 | `17015` | L'Insee retient **Arces**, alors que la notice porte « Arces-sur-Gironde » : conserver la forme documentaire, vérifier son statut dans Pactols |
| Vinon | 18 | `18287` | Distinct de la candidature du Var ; mentionné dans une étude des carrières de sarcophages |
| Forgès | 19 | `19084` | Plusieurs homonymies anciennes ; notice corrézienne « Canton d'Argentat » |
| Belle-Isle-en-Terre | 22 | `22005` | Notice de synthèse du Trégor |

Les index non présents dans le titre (Avenay, Fontenille, Vinon, Forgès et Belle-Isle-en-Terre) n'ont pas été pénalisés : ils sont bien attestés parmi les **index TEI du corps**. Leur contexte n'est pas en contradiction directe avec le département Pactols.

## Sous-lot 03 — dix communes administrativement corroborées

| Libellé Pactols | Département | COG 2026 | Particularité |
| --- | ---: | --- | --- |
| Chéniers | 23 | `23062` | Autre code historique `51146` ; synthèse géoarchéologique du Limousin |
| Bussac | 24 | `24069` | Ancien candidat `17073` dans un autre département ; contexte de la vallée de la Dronne |
| Blamont | 25 | `25063` | **Blamont** (Doubs), distinct de **Blâmont** (Meurthe-et-Moselle) ; contexte de châteaux comtois |
| Aleyrac | 26 | `26003` | Prieuré d'Aleyrac dans un titre AdlFI |
| Bernay | 27 | `27056` | Plusieurs autres codes historiques ; synthèse de Haute-Normandie |
| Pont-l'Abbé | 29 | `29220` | Distinct de la candidature historique `17284` ; lien Insee avec slug `pont-labbe` |
| Belvézet | 30 | `30035` | Autre code historique `48023` ; ancienne église Saint-André |
| Baziège | 31 | `31048` | Site Pigné-Lupis dans un titre |
| Aignan | 32 | `32001` | Chantier de gazoduc dans le Gers |
| Ambarès-et-Lagrave | 33 | `33003` | Plusieurs attestations localisées dans les titres |

Les index non présents dans le titre (Bussac et Blamont) restent valides comme **attestations documentaires** dans le corps de leurs notices. Aucune concordance de titre n'est exigée pour valider une autorité.

## État des contrôles

- **20/20** couples code–nom–département concordent avec les fiches Insee 2026.
- **20 ARK distincts**, tous attestés dans les XML et cohérents avec la hiérarchie départementale du corpus.
- Les anciens codes secondaires demeurent documentés ; ils ne sont ni fusionnés ni attribués automatiquement aux ARK.
- **0** nouvelle équivalence SKOS, **0** nouvelle géométrie, **0** modification du pilote validé PACA.
- Les fichiers `sous-lot-02-cog2026-controle.csv` et `sous-lot-03-cog2026-controle.csv` préservent les preuves et le statut `non_valide`.

## Passage à l'examen des concepts Pactols vivants

Le dépôt officiel [frantiq/PACTOLS](https://github.com/frantiq/PACTOLS) fournit un
export **Lieux th17 du 22 juillet 2026**. Deux fichiers sont gérés par Git LFS ;
le pointeur Git ne contient **pas** le RDF. L'export RDF/XML complet fait
**93 418 191 octets** et porte le SHA-256 :

`3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`

Cette source a déjà servi à l'audit du pilote PACA (103/103 concepts trouvés,
103 libellés préférentiels concordants) : consulter le lot de revue
`AdlFI_Lieux_audit_Pactols_20260722.zip` du 12 novembre.

### Auditeur national ajouté

`scripts/auditer_export_pactols_lieux.py` compare les **9 928 ARK** du maître
national à cet export SKOS : existence à la date d'export, `skos:prefLabel`
français, `skos:altLabel`, `skos:hiddenLabel`, `skos:exactMatch`
documentaires et `owl:deprecated` s'il est déclaré.

Le programme lit le XML en flux (pas de chargement intégral en mémoire),
vérifie le **SHA-256** de l'export (et refuse les pointeurs Git LFS),
et n'infère **aucune** nouvelle correspondance COG ou géométrie.
L'absence d'un ARK dans un export daté ne constitue pas à elle seule
une absence dans le Pactols vivant.

Quatre tests sur des données synthétiques réussissent :

```bash
python3 -m unittest discover -s tests -p 'test_auditer_export_pactols_lieux.py' -v
```

### Exécution sur un export complet déjà téléchargé

```bash
python3 scripts/auditer_export_pactols_lieux.py \
  --autorites "$HOME/Desktop/AdlFI-lieux-national-recette/autorites_nationales.json" \
  --pactols-rdf "/chemin/reel/vers/Pactols_Lieux_th17_20260722.rdf" \
  --sortie "$HOME/Desktop/AdlFI-lieux-qualif-Pactols"
```

Un export non disponible sur le Mac peut être récupéré avec Git LFS
en ne téléchargeant que le fichier RDF concerné :

```bash
git lfs version
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/frantiq/PACTOLS.git \
  "$HOME/Desktop/AdlFI-sources-Pactols-20260722/PACTOLS"
cd "$HOME/Desktop/AdlFI-sources-Pactols-20260722/PACTOLS"
git sparse-checkout set pactols-latest-version/pactols_lieux_all
git lfs pull --include="pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf" --exclude=""
```

L'exécution sur le vrai RDF **reste à effectuer** ; aucun effectif national
d'ARK présents ou absents n'est annoncé avant cette lecture.

**Étape suivante :** exploiter le rapport SKOS pour distinguer les concepts
confirmés, les changements de libellés et les ARK à réexaminer,
puis soumettre les alignements Pactols–COG vérifiés à validation
éditoriale avant tout changement de `docs/data/lieux.json`.
