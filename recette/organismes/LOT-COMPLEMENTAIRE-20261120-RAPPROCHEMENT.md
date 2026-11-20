# Lot complémentaire ORG/SER du 20 novembre 2026 — rapprochement avec le catalogue

**État :** audit éditorial sourcé, en attente de mise à jour du maître XLSX privé ; aucun nouvel ID attribué et aucune donnée publique modifiée.

**Base examinée :** JSON public `docs/data/organismes.json`, export du maître `AdlFI_referentiel_1-49_enrichi_relations_586_20261120.xlsx`, SHA-256 `2fcec08dccecc1532cbd25b590514118156e0161292de4b368d665ca992768f4` (920 autorités, 586 relations).

**Portée de la vérification d'existence :** recherche d'appellations, acronymes et variantes dans le **JSON public**. Une absence signifie « non repéré dans ce JSON », **pas** « preuve d'absence du dernier XLSX privé ». Dédupliquer à nouveau sur ce dernier avant attribution d'identifiants.

## Cas trouvés et arbitrages prioritaires

### IRAMAT — deux ORG existantes et continuité partielle déjà documentée

- **ORG-0393** : IRAMAT **UMR 5060**, 1999-01-01 → 2021-12-31, inactif ; RNSR `199911751G`.
- **ORG-0299** : IRAMAT **UMR 7065**, depuis 2022-01-01, actif ; RNSR `202224174K`, ROR `https://ror.org/01cw28e72`.
- **REL-0127** : ORG-0393 → ORG-0299, `succession_partielle`, validée, début 2022-01-01. **REL-0128** : ORG-0393 → ORG-0537, autre succession partielle. Ne jamais fusionner ORG-0393 et ORG-0299 ni remplacer les successions partielles par une succession totale.
- Les deux composantes demandées, **Centre Ernest-Babelon (CEB)** et **Laboratoire Métallurgies et Cultures (LMC)**, ne sont pas repérées par nom dans le JSON. Proposer **deux SER de composantes**, avec liens temporels à ORG-0393 pour 1999–2021 et à ORG-0299 depuis 2022, **sous réserve de confirmation de leur continuité institutionnelle exacte** et des dates de chaque rattachement. Ne pas attribuer la création du CEB à 2002 : il s'agit de la date de sa contractualisation avec l'université d'Orléans. Le LMC est basé à Sèvenans / site de Belfort et associé à l'UTBM.
- Sources institutionnelles : [présentation IRAMAT UMR 7065](https://iramat.cnrs.fr/presentation-2/) ; [accueil IRAMAT](https://iramat.cnrs.fr/).

### Centre Lenain de Tillemont

- **Non repéré dans le JSON** : candidat **ORG historique**, Paris, FRE 2509, ancien CNRS/Paris-Sorbonne (Paris-IV), inactif.
- **ORG-0391** existe : UMR 8167 *Orient et Méditerranée*, depuis 2006. Source primaire : l'actuelle équipe **Antiquité classique et tardive** a été constituée de l'ancien Centre Lenain de Tillemont. En 2006, Orient et Méditerranée résulte d'un rapprochement de **six équipes**. Qualifier la relation comme **filiation partielle / contribution constitutive**, et non succession totale du Centre par l'intégralité de l'UMR.
- Sources : [Historique du laboratoire](https://www.orient-mediterranee.com/historique-du-laboratoire/) ; [Présentation des équipes](https://www.orient-mediterranee.com/presentation/les-equipes/).

### Variantes : ne pas créer de doublons

- **SER-0188** *Service du patrimoine et des musées de Cavaillon* possède **déjà** l'entrée **HIS-SER-0080** : « Conservation des Musées et du Patrimoine de Cavaillon », variante valide, sans dates. L'autorité est rattachée à **ORG-0708** (Ville de Cavaillon). **Ne rien créer de supplémentaire** pour la demande.
- **ORG-0321** *Association Montagne et Patrimoine* (AMONT) existe. Son site et le CTHS attestent une création en **1981** à **Saint-Martin-Vésubie**. La mairie cite « Association Montagne et Traditions » : proposer l'enregistrement de cette forme comme **variante à sourcer**, ajouter ville et date de création après vérification sur le maître ; actualiser le statut d'activité si la continuité actuelle est établie par les documents de l'association. SIREN `399696905`, à vérifier avec l'identité administrative.
- Sources : [Association AMONT — histoire](https://www.amont-alpesmaritimes.fr/lassociation/objet-et-histoire.html) ; [CTHS](https://cths.fr/an/societe.php?id=3752) ; [mairie de Saint-Martin-Vésubie](https://mairie.saintmartinvesubie.fr/annuaire-categories/associations/).

### Centre européen d'archéométrie : correction d'acronyme

- L'Université de Liège existe déjà comme **ORG-0280**. Le **Centre européen d'archéométrie** est attesté comme centre de l'université créé en **2003** : candidat **SER** relié à ORG-0280.
- **Acronyme officiel : CEA, et non « CAE »**, selon l'Université de Liège. Enregistrer « CAE » seulement si un usage documentaire distinct est attesté ; ne pas fabriquer une variante.
- Sources : [ULiège — CEA](https://www.aap.uliege.be/cms/c_5660663/fr/aap-cea-centre-europeen-d-archeometrie), [ULiège — vingt ans du CEA](https://www.uliege.be/cms/c_18187576/fr/le-centre-europeen-d-archeometrie-de-l-uliege-fete-ses-20-ans).

### ENSG / Géodata Paris

- Non repérée sous ces noms dans le JSON. **École nationale des sciences géographiques (ENSG-Géomatique)** est devenue **Géodata Paris le 1er octobre 2025** : une **seule autorité avec ancienne dénomination**, pas deux établissements successifs.
- Institutionnellement **école de l'IGN** et **école-membre de l'Université Gustave Eiffel** ; le deuxième lien n'est pas une tutelle juridique équivalente au premier. IGN et Université Gustave Eiffel ne sont pas repérés comme autorités dans le JSON, à contrôler dans le maître avant d'ajouter les parents nécessaires.
- Sources : [IGN, 2025](https://www.ign.fr/institut/espace-presse/lensg-geomatique-devient-geodata-paris-lecole-des-ingenieurs-geographes) ; [Université Gustave Eiffel](https://www.univ-gustave-eiffel.fr/luniversite/pages-speciales/vue-detaillee/lensg-geomatique-devient-geodata-paris) ; [décret 2019-1360](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000039508816/).

### CICRP

- Non repéré dans le JSON. **ORG publique autonome de type GIP**, et non SER de la Ville de Marseille ; membres : État (Culture), Ville de Marseille, Région PACA, Département des Bouches-du-Rhône.
- Le site officiel indique une création en **2002**, alors qu'une convention constitutive a été approuvée dès novembre **2001**. **Qualifier le sens de `date_debut`** (constitution juridique / démarrage opérationnel) avant de figer une date.
- Sources : [CICRP](https://cicrp.fr/), [Statuts CICRP](https://cicrp.fr/statuts/), [ministère de la Culture](https://www.culture.gouv.fr/thematiques/sciences-du-patrimoine/partenariats-scientifiques).

## Autres créations candidates (non repérées sous ces appellations)

| Demande du lot | Type proposé | Rattachement connu ou réserve | Source initiale |
|---|---|---|---|
| Institut de préhistoire et d'archéologie Alpes Méditerranée (IPAAM), Nice | ORG, association | Fondation **8 avril 1926 sous un autre nom** ; historique de dénominations à saisir | https://www.ipaam.fr/historiqueasso.htm |
| Société française d'étude de la céramique antique en Gaule (SFECAG) | ORG, association | Autonome, pas un service universitaire | https://sfecag.org/ |
| Tufts University (Medford, Massachusetts, États-Unis) | ORG, université | Contrôle ROR / statut avant saisie | https://www.tufts.edu/ |
| Musée Gassendi, Digne-les-Bains | SER, musée municipal | **Ville de Digne-les-Bains** : ORG parent non repérée, créer si absente du maître ; vérifier la structure du pôle muséal Ambulo | https://www.musee-gassendi.org/ |
| Musée d'Archéologie de Nice / Cimiez | SER, musée municipal | **ORG-0160 Ville de Nice** existe, hors catalogue ; lien `rattachement_service` | https://www.nice.fr/lieux/musee-darcheologie-de-nice-cimiez/ |
| Association Provence Archéologie (APA), Aix-en-Provence | ORG, association | Identité légale et statut à confirmer | Signalement éditorial |
| Céraphin, Arles | ORG, association | Création 2005 proposée, date à vérifier | Signalement éditorial |
| Sapienza Università di Roma | ORG, université | Contrôle d'identifiants institutionnels | https://www.uniroma1.it/ |
| Les Amis de Villeneuve (Alpes-de-Haute-Provence) | ORG, association | Désambiguïser par siège et RNA, homonymies possibles | Signalement éditorial |
| Association archéologique Aristide-Fabre (AAAF), Sainte-Maxime | ORG, association | Identité légale à confirmer | Signalement éditorial |
| Association d'étude et de sauvegarde du patrimoine de l'Embrunais (ASEPE) | ORG, association | Identité légale à confirmer | Signalement éditorial |
| Musée archéologique de Riez | SER, musée municipal | Musée créé en **1929** ; **Ville de Riez** : ORG parent non repérée, créer si absente du maître | https://www.ville-riez.fr/histoire-patrimoine/histoire-village |
| Société d'art et d'histoire du Mentonnais (SAHM) | ORG, association | Création 1975 proposée ; dates à confirmer | https://sahm9.odoo.com/ |
| EURL Archeobat, Mougins | ORG, entreprise | Statut « inactive » à attester par registre ; identifier le SIREN | Signalement éditorial |

**Important :** l'absence dans ce tableau d'un numéro ORG/SER n'est pas un oubli. Les identifiants seront attribués **uniquement après comparaison avec la dernière version du maître**. Le numéro 2026 du catalogue et les nouvelles relations de ce lot restent donc inchangés.

## Étapes de migration des données

1. Récupérer le maître XLSX du 20 novembre ou sa version la plus récente et auditer les identifiants, variantes et références par feuille. Ne pas substituer le JSON public au maître.
2. Traiter d'abord **les deux SER IRAMAT**, **la filiation partielle Lenain de Tillemont**, **les variantes AMONT**, puis **CEA**, **ENSG** et **CICRP** ; les associations et musées suivront après vérification d'identité.
3. Pour les futures relations, distinguer `rattachement_service`, `tutelle`, `filiation_partielle`, `membre` (école-membre), `affiliation_federale` ; vérifier le rendu de chacun avant publication. Ne jamais utiliser le type `tutelle` pour une simple appartenance universitaire sans preuve.
4. Après migration, exporter le JSON et auditer identifiants, relations, total des autorités, présence des images et navigation, notamment vers les parents hors catalogue.

Suivi de lot : [issue #174](https://github.com/nicocoquet/adlfi-referentiels/issues/174).
