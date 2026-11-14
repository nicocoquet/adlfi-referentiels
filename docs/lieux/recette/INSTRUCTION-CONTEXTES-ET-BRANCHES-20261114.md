# Référentiel Lieux — instruction documentaire complémentaire (lot 001)

**État : recette non validante ; aucun alignement Pactols–COG nouveau, aucune géométrie ajoutée.**

## Méthode et niveau de preuve

Les constats documentaires ci-dessous sont tirés de l'extraction XML AdlFI v2
(`notices.csv` et `occurrences_lieux.csv`, avec leur identifiant
`fichier.xml::notice-XXXXXX`). Les intitulés de notices, les ARK
terminaux et les chaînes hiérarchiques ont été vérifiés dans ces fichiers.

**Limite :** pour Bethon et Usson, nous ne disposons pas dans cette
recette du texte intégral du paragraphe TEI où l'index intervient.
Les sources administratives et archéologiques externes apportent un
faisceau d'indices, mais ne prouvent pas encore l'erreur de saisie.

Les données structurées à intégrer à la revue sont dans
`dossiers-contextes-001-20261114.json`.

## A. Bethon (Marne) / Béthon (Sarthe) : confusion d'autorité très probable

- Index actuel : **Bethon**, ARK `26678/pcrt5YI2zQtodM`, commune
  COG candidate `51056` (Marne).
- Attestation unique : `AdlFI_Pays-de-la-Loire/AdlFI_PdL_1996/XML/AdlFI_PdL_1996.xml::notice-000047`,
  notice **Autoroute A28** (1996), index `zone_tei=p`.
- **15 lieux terminaux** dans cette notice : **14** rattachés à la
  Sarthe, et seul **Bethon** à la Marne. Les autres mentions comprennent
  notamment **Champfleur, Vivoin, Yvré-l'Évêque, Écommoy, La Bazoge,
  Brette-les-Pins**.
- La commune **Béthon** (accent aigu), COG **`72036`**, se situe
  en **Sarthe**. L'Insee la distingue de **Bethon `51056`**
  en Marne. Le rapport de l'enquête publique préfectorale de Sarthe
  précise que **Béthon est traversée par l'A28 depuis 2001** et
  partage son contexte local avec Champfleur.

**Avis de préinstruction : `suspicion_forte_erreur_indexation`.**
Il ne s'agit pas d'une correction du concept Pactols « Bethon » :
il faut vérifier dans le XML d'origine si l'index d'**Autoroute A28**
devrait porter sur l'autorité distincte **Béthon (Sarthe)**, puis
corriger à la source s'il y a lieu. **Ne pas publier** cet
alignement Pactols `pcrt5YI2zQtodM` → COG `51056`
sur la seule base de cette notice.

Sources :
- https://www.insee.fr/fr/metadonnees/geographie/commune/51056-bethon
- https://www.insee.fr/fr/metadonnees/geographie/commune/72036-bethon
- https://www.sarthe.gouv.fr/contenu/telechargement/15618/99564/file/rapport_commissaire_enqueteur_partie_1.pdf
  (partie « Situation géographique du projet »).

## B. Usson (Puy-de-Dôme) / Usson-en-Forez (Loire) : ambiguïté à instruire

- Index actuel : **Usson**, ARK `26678/pcrtavZRJRD9Uf`,
  candidat COG **`63439`** (Puy-de-Dôme).
- Attestation unique : `AdlFI_Auvergne_Rhone-Alpes/AdlFI_Rhone_Alpes/AdlFI_Rhone_Alpes_2015/XML/AdlFI_Rhone_Alpes_2015.xml::notice-000184`
  ; titre **Habitats agglomérés en pays ségusiave : les formes du fait
  urbain dans la cité ségusiave du Ier au IIIe s. apr. J.-C.**
- Cinq index terminaux : **La Pacaudière, Roanne, Feurs, Moingt,
  Usson** ; les quatre premiers se situent dans la Loire.
- **Usson-en-Forez**, COG **`42318`**, est dans la Loire.
  La littérature archéologique mentionne le PCR consacré aux
  habitats agglomérés en pays ségusiave et des recherches à
  Usson-en-Forez, mais les limites antiques ségusiaves/vellaves
  étaient discutées : **ne pas inférer une appartenance antique
  à partir du seul département actuel**.

**Avis : `suspicion_a_instruire`.** Le code
`63439` reste une candidature correspondant bien au concept
Pactols *Usson*, mais le contexte de la notice peut renvoyer à
`42318` (*Usson-en-Forez*). La lecture du texte intégral et, si
nécessaire, du rapport original du PCR est indispensable avant
toute correction d'indexation.

Sources :
- https://www.insee.fr/fr/statistiques/1405599?geo=COM-63439
- https://www.insee.fr/fr/statistiques/1405599?geo=COM-42318
- https://www.arar.mom.fr/presentation/annuaire-du-personnel/le-nezet-celestin-monique
- https://www.culture.gouv.fr/content/download/153311/file/bilan-scientifique-archeologique-rhone-alpes-2006-2.pdf

## C. Marsangy (Yonne) : contexte confirmé, pas une anomalie

- ARK `26678/pcrttMIHapwXmV`, candidat COG `89245` (Yonne).
- Notice `AdlFI_Ile-de-France/AdlFI_Ile-de-France_1996/XML/AdlFI_Ile-de-France_1996_Interdep-PCR.xml::notice-000005`,
  **Habitats et peuplements du Tardiglaciaire dans le Bassin parisien**
  ; six index terminaux sur plusieurs départements.
- Le texte publié de la **même notice** cite explicitement le
  gisement de **Marsangy** parmi ceux du centre du Bassin parisien,
  et de nouveau en contexte magdalénien avec Cepoy.
- La bibliographie scientifique atteste le site magdalénien de
  Marsangy dans l'Yonne.

**Avis : `coherence_documentaire_corroboree`.** Retirer cette
notice de la file des **anomalies potentielles d'indexation**.
La mise en cohérence documentaire ne vaut pas encore validation
formelle du lien de l'ARK Pactols au COG `89245`.

Sources :
- https://journals.openedition.org/adlfi/216489
- https://www.insee.fr/fr/metadonnees/geographie/commune/89245-marsangy
- https://www.persee.fr/doc/bspf_0249-7638_1993_num_90_5_10456

## D. Deux changements de branche Pactols : interprétation typologique

### Lac d'Annecy — `26678/pcrtTJFe71EA69`

**12 occurrences, deux chaînes** :
- 11 occurrences sous `Europe hydrographie → Annecy L` ;
- 1 occurrence sous `_espaces géographiques aquatiques →
  Europe hydrographique → lac d'Annecy` (2022).

Il s'agit d'**un même ARK hydrographique**, hiérarchisé
différemment dans les XML. Conserver les deux chaînes pour la
provenance et conserver le concept dans un référentiel de lieux
hydrographiques, **hors du COG communal**. La géométrie d'un lac
éventuellement fournie par une base hydrographique ne doit pas être
substituée par la géométrie de la commune d'Annecy.

### Poitou-Charentes — `26678/pcrtvyPdfBr78V`

**Deux attestations sous deux branches** :
- notice bretonne de **1998** : `Europe → France → France
  métropolitaine → Poitou-Charentes` ;
- notice de Nouvelle-Aquitaine de **2021** :
  `entités du passé → entités du passé récent → Poitou-Charentes`.

Cette variation est compatible avec la réforme régionale du
**1er janvier 2016** (intégration de Poitou-Charentes dans la
Nouvelle-Aquitaine). Conserver **un seul ARK** et les deux
attestations temporellement contextualisées. Pour une autorité
administrative régionale historique, recourir aux codes régionaux
et aux événements administratifs pertinents, **pas au COG
communal**.

Source officielle :
https://www.nouvelle-aquitaine.gouv.fr/prefecture-de-region

## E. Évolution souhaitable du contrôle automatique

Le signal `notice_transdepartementale` est utile pour rechercher
des discordances, mais il ne suffit pas à qualifier une anomalie.
Deux situations doivent être distinguées :

1. **une seule indexation décalée**, accompagnée de nombreux lieux
   concordants et d'un quasi-homonyme dans le département
   majoritaire : profil Bethon, et hypothèse Usson ;
2. **une synthèse réellement multirégionale**, dans laquelle
   le lieu est explicitement mentionné dans le texte :
   profil Marsangy, Angers ou Paris.

Développer un futur indicateur d'**exception contextuelle** fondé
sur le département majoritaire, le nombre de mentions et
la proximité des libellés des communes candidates.
Il doit classer la **priorité de revue**, jamais effectuer une
substitution automatique d'ARK ou de code INSEE.

**Aucun des cinq cas n'a changé de statut de validation Pactols–COG.
Aucune géométrie 2026 ou historique n'a été ajoutée.**
