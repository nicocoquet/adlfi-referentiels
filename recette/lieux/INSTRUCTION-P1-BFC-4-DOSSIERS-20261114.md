# Lieux AdlFI — instruction des quatre dossiers P1 (Bourgogne-Franche-Comté)

**14 novembre 2026 — recette non validante — PR n°24 en brouillon.**

## Portée

Les quatre candidatures P1 du lot de 29 représentent **deux créations de communes nouvelles**, datées du 1er janvier 2019 et du 1er janvier 2025. Les chiffres correspondent à **quatre relations documentaires sources**, et non à quatre événements administratifs indépendants.

Les fichiers `dossiers-p1-bfc-4.csv`, `evenements-administratifs-p1-bfc-2.csv`, `transitions-cog-p1-bfc-6.csv` et `concepts-pactols-p1-bfc-4.csv` conservent leurs preuves. Le rapport JSON indique les empreintes des quatre sources de calcul ; le RDF intégral Pactols du 22 juillet 2026 a pour SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7` et a été vérifié dans la CI de la PR n°24.

## Dossier A — Saint-Hymetière-sur-Valouse, Jura (`39137`)

**Fait administratif établi.** Par arrêté préfectoral du **11 décembre 2018** (publié au Journal officiel du **7 mars 2019**), la commune nouvelle **Saint-Hymetière-sur-Valouse** est créée **à compter du 1er janvier 2019** en lieu et place de **Cézia (`39089`), Chemilla (`39137`), Lavans-sur-Valouse (`39287`) et Saint-Hymetière (`39483`)**. Les quatre lignes correspondantes de `v_mvt_commune_2026.csv` présentent `MOD=32`, `TYPECOM_AV=COM`, `TYPECOM_AP=COM` et la même cible `39137`. Le fichier COG 2026 contient une entrée `COM 39137 Saint-Hymetière-sur-Valouse`.

**Source juridique :** https://www.legifrance.gouv.fr/eli/arrete/2018/12/11/TERB1904807A/jo/texte

**Source administrative :** https://www.insee.fr/fr/metadonnees/geographie/commune/39137-saint-hymetiere-sur-valouse

**Situation Pactols vérifiée au 22 juillet 2026 :**

- `26678/pcrt2v0xk9OjyW`, **Chemilla** : `skos:exactMatch` vers `http://id.insee.fr/geo/commune/39137` ; concept historique distinct.
- `26678/pcrt80xbz0p4vht8kdd4mtdx`, **Saint-Hymetière-sur-Valouse** : libellé préféré concordant ; **aucun** `exactMatch` Insee numérique dans le RDF, mais un lien vers Wikidata.
- Les trois anciennes communes **Cézia**, **Lavans-sur-Valouse** et **Saint-Hymetière** disposent chacune de leur propre ARK (voir le CSV P1).

**Vérification supplémentaire dans Pactols vivant, 14 novembre 2026 :** l'API de recherche `th17` renvoie les deux ARK ; le concept Saint-Hymetière-sur-Valouse déclare une équivalence vers Wikidata, **toujours pas** vers l'Insee ; Chemilla conserve l'équivalence Insee `39137`. Le rapport JSON original des réponses HTTP 200 figure dans `sources/live/controle-pactols-vivant-p1.json`.

**Qualification proposée, non validée :** modéliser **un seul événement** de création de commune nouvelle avec **quatre communes participantes** et une cible administrative `COM 39137` au millésime 2019. Les relations des trois dossiers P1 pourraient être représentées par « participe à la création de » ou « commune antérieure intégrée à », datées du 1er janvier 2019. **Ce ne sont pas des `skos:exactMatch` entre les ARK.**

**Point éditorial unique à soumettre à Frantiq :** décider du traitement de l'URI Insee commune/39137, actuellement associé à Chemilla, alors que le code a été réutilisé par la commune nouvelle dont un concept Pactols existe déjà. Ne **pas** déplacer, supprimer ou dupliquer un `skos:exactMatch` sans arbitrage sur sa portée temporelle ; ne jamais fusionner Chemilla et Saint-Hymetière-sur-Valouse. Le RDF SKOS ne fournit pas, à lui seul, de période de validité à `skos:exactMatch`.

## Dossier B — Verdun-Ciel, Saône-et-Loire (`71566`)

**Fait administratif établi.** L'arrêté du **27 septembre 2024** (publié au Journal officiel du **1er janvier 2025**) crée **Verdun-Ciel** à compter du **1er janvier 2025**, en lieu et place de **Ciel (`71131`)** et **Verdun-sur-le-Doubs (`71566`)**. Les deux lignes COG `MOD=32` montrent que la commune nouvelle **réutilise** le code de Verdun-sur-le-Doubs.

**Source juridique :** https://www.legifrance.gouv.fr/eli/arrete/2024/9/27/ATDB2434662A/jo/texte

**Source administrative :** https://www.insee.fr/fr/metadonnees/geographie/commune/71566-verdun-ciel

**Situation Pactols :**

- Ciel : `26678/pcrtfuk9c6Th7Q`, concept d'ancienne commune, code `71131`.
- Verdun-sur-le-Doubs : `26678/pcrtoFlfDwt01N`, concept historique dont l'`exactMatch` pointe vers le code `71566`.
- Verdun-Ciel : **aucun concept sous ce libellé identifié** parmi les 50 691 concepts du snapshot du 22 juillet 2026, ni dans les recherches publiques par nom du 14 novembre 2026. Les recherches publiques négatives ne prouvent toutefois pas l'absence absolue de toute autorité dans le thésaurus vivant.

**Qualification proposée, non validée :** conserver **deux communes participantes** et une entité administrative nouvelle distincte `COM 71566` à compter de 2025. Ne pas attribuer à cette dernière l'ARK historique de Verdun-sur-le-Doubs, même si le code est réutilisé.

**Point éditorial à soumettre à Frantiq :** demander la vérification d'un concept Verdun-Ciel dans la base complète en ligne ; si son absence est confirmée, proposer **la création d'une autorité distincte** avec la forme préférée « Verdun-Ciel », l'année 2025 et le rattachement géographique Saône-et-Loire, en préservant les deux concepts anciens. Aucun nouvel ARK n'a été créé par AdlFI.

## Considérations SKOS

Selon la norme W3C SKOS, `skos:exactMatch` exprime une correspondance conceptuelle forte et est **transitif**. La réutilisation d'un identifiant administratif Insee entre deux périodes et deux territoires de référence ne justifie donc pas l'attribution automatique d'un `exactMatch` identique aux deux concepts. L'alignement temporel devra être traité dans le modèle d'événements AdlFI et, si nécessaire, dans les règles éditoriales de Pactols.

**Source normative :** https://www.w3.org/TR/skos-reference/

## Décisions réservées à la validation éditoriale

1. **P1-A :** valider ou ajuster le type de relation `participation_a_creation_commune_nouvelle` entre les quatre prédécesseurs et la commune nouvelle, datée du 1er janvier 2019. Instruire avec Frantiq l'assertion Insee `39137` sur les deux concepts Pactols distincts.
2. **P1-B :** valider ou ajuster le type de relation administrative vers Verdun-Ciel au 1er janvier 2025 ; solliciter Frantiq pour une vérification de l'existence ou une éventuelle création du concept nouveau.

Les champs `validation_editoriale`, `justification_validation`, `verificateur` et `date_validation` restent **vides** dans les CSV. **Aucune relation publiée, aucune géométrie historique générée.**