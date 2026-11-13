# Référentiel Lieux — préparation nationale Pactols / COG historique / géométries

**État :** recette technique, **non publiée** dans `docs/data` ni intégrée à la carte du module Lieux. 

## Périmètre et résultats sur l'extraction XML du 13 novembre 2026

La table d'observations provient de `extraire_lieux_xml_adlfi.py` (branche
`feat/lieux-extraction-xml-adlfi-20261113`, PR n°22). Le périmètre porte sur
les **fichiers XML sélectionnés par les règles d'inventaire de ce script**, et
non sur une affirmation d'exhaustivité de toutes les archives AdlFI.

- **9 928 ARK Pactols terminaux** attestés, sans seuil minimal de notices.
- **103 alignements Pactols–COG 2026 validés dans le pilote PACA**, conservés en l'état.
- **9 088** ARK directement placés sous un département dans au moins une chaîne Pactols : candidats prioritaires à la qualification communale, **pas** une preuve d'identité administrative.
- **595** ARK situés sous une autre entité d'une chaîne départementale, incluant notamment d'anciennes communes, sections et sites : maintenir leur identité Pactols.
- **176** autres lieux géographiques français ; **25** hydrographiques ; **14** de géographie physique ; **30** relevant d'autres ensembles.
- **2 018** ARK ont plusieurs chemins de *codes* Pactols attestés. Si l'on distingue également les différentes versions textuelles des mêmes chaînes, **2 034** ARK ont plusieurs représentations.
- À ce stade, **aucune nouvelle correspondance COG historique n'a été validée**. Le COG historique n'a pas encore été chargé dans cette recette.

Le comptage des notices n'est pas un critère d'inclusion. En revanche les traces
`notice_id`, chemin du fichier XML et années d'opération sont conservées pour
l'audit et la provenance. Une année d'opération n'est jamais utilisée comme date
administrative de validité du toponyme ou de sa géométrie.

## Entrées

- `autorites_lieux.csv` : une ligne par ARK terminal ;
- `occurrences_lieux.csv` : chaînes hiérarchiques Pactols, formes et témoin documentaire ;
- `alignements_lieux.csv` : validations PACA héritées de l'extracteur national ;
- **optionnel pour la première exécution, indispensable pour l'étape historique :**
  `v_commune_depuis_1943.csv` du **COG 2026 de l'Insee**.

Téléchargement officiel de l'historique des communes depuis 1943 :

https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_depuis_1943.csv

Documentation de la source : https://www.insee.fr/fr/information/8740222

Le fichier Insee décrit les **couples code–libellé** depuis 1943, avec
`TYPECOM`, `COM`, `LIBELLE`, `DATE_DEBUT`, `DATE_FIN`.
Cette table **n'est pas un référentiel des contours historiques**. Les
mouvements de communes `v_mvt_commune_2026.csv` fournissent les événements de
fusion, changement, création, disparition et succession : ils constituent une
**source supplémentaire à exploiter lors de l'instruction des propositions**.

## Première exécution sur Mac (sans COG historique)

Depuis la racine de `adlfi-referentiels`, en ayant extrait le jeu d'audit v2
sur le Bureau dans `AdlFI-audit-lieux-v2` :

```bash
python3 scripts/construire_referentiel_lieux_national.py \
  --autorites "$HOME/Desktop/AdlFI-audit-lieux-v2/autorites_lieux.csv" \
  --occurrences "$HOME/Desktop/AdlFI-audit-lieux-v2/occurrences_lieux.csv" \
  --alignements "$HOME/Desktop/AdlFI-audit-lieux-v2/alignements_lieux.csv" \
  --sortie "$HOME/Desktop/AdlFI-lieux-national-recette"
```

Ces CSV sont ceux de l'extraction AdlFI déjà faite ; il n'y a pas à retraiter
les fichiers XML à ce stade.

## Exécution avec le COG historique

```bash
mkdir -p "$HOME/Desktop/AdlFI-sources-COG-2026"
curl -fL --retry 3 \
  'https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_depuis_1943.csv' \
  -o "$HOME/Desktop/AdlFI-sources-COG-2026/v_commune_depuis_1943.csv"

python3 scripts/construire_referentiel_lieux_national.py \
  --autorites "$HOME/Desktop/AdlFI-audit-lieux-v2/autorites_lieux.csv" \
  --occurrences "$HOME/Desktop/AdlFI-audit-lieux-v2/occurrences_lieux.csv" \
  --alignements "$HOME/Desktop/AdlFI-audit-lieux-v2/alignements_lieux.csv" \
  --cog-historique "$HOME/Desktop/AdlFI-sources-COG-2026/v_commune_depuis_1943.csv" \
  --sortie "$HOME/Desktop/AdlFI-lieux-national-recette"
```

Le script produit dans le dossier de sortie :

1. `autorites_nationales.json` : 9 928 concepts, formes et hiérarchies
   attestées, témoin documentaire, état du rapprochement, validation PACA
   existante et pointeur de géométrie *contemporaine* lorsqu'elle est validée.
2. `candidatures_cog_historiques.csv` : correspondances lexicales candidates,
   **une ligne par code / forme / période** ; **aucune équivalence validée**.
3. `rapport_preparation.json` : statistiques, anomalies et SHA-256 des sources.

La correspondance nominative ne vaut ni `skos:exactMatch`, ni succession
historique, ni coïncidence géométrique.

## Règles de décision pour les lots à instruire

1. **Autorité Pactols** : son ARK est la clé primaire. Plusieurs noms ou chemins
   Pactols peuvent correspondre à ce même concept ; ils ne sont pas fusionnés.
2. **Identité COG historique** : les dates du couple code–libellé servent à
   qualifier des *états de nom*, pas à dater à elles seules une identité
   communale ni ses modifications territoriales. Analyser les **mouvements
   officiels** avant d'établir une succession ou une équivalence.
3. **Homonymies** : deux codes correspondant au même libellé restent des
   candidats distincts ; le département Pactols et les événements historiques
   servent au contrôle, mais ne suffisent pas toujours à prouver l'alignement.
4. **Anciennes communes** : ne pas faire pointer leur ARK directement sur la
   géométrie 2026 du successeur. Conserver la nature de la relation
   (`ancienne_commune`, `fusion`, `rattachement`, etc.) et son intervalle.
5. **Géométrie** : lier uniquement un code COG au contour du millésime
   effectivement disponible et documenté ; la géométrie 2026 de data.gouv.fr
   n'est pas rétroprojetée à l'année d'opération. Les géométries 100 m/1000 m
   et les limites communales existantes du module Lieux devront être comparées
   par code et par provenance, avec le contrôle développé pour Marseille.
6. **Hors COG communal** : les cours d'eau, reliefs, sites archéologiques,
   secteurs et pays étrangers ne sont pas des échecs d'alignement COG : ils
   nécessitent d'autres autorités et/ou d'autres types de géométrie.
7. **Publication** : seules les correspondances éditoriales validées entrent
   dans le JSON et la carte publics. La table de candidatures et les
   rapprochements incertains demeurent en recette.

## Test

```bash
python3 -m unittest discover -s tests -p 'test_referentiel_lieux_national.py' -v
```

Le script n'a pas besoin de dépendance Python externe. Il lit ses sources sans
les modifier et interdit qu'un fichier de sortie écrase un fichier source.

## État et limites

**Fait** : reprise des 9 928 ARK, conservation des chemins, 103 validations
PACA, classification provisoire, reproductibilité, génération d'une table de
candidatures sur le schéma historique Insee (cas synthétiques testés).

**Non fait** : exécution sur le CSV Insee réel ; exploitation des mouvements de
communes ; résolution des homonymies ; comparaison systématique des géométries
historisées ; publication d'un index complet dans le navigateur. Aucune
candidature lexicale ne doit être présentée comme un alignement vérifié.