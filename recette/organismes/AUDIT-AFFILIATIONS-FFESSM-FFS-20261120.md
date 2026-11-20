# Audit AdlFI — FFESSM / FFS et reclassification ORG–SER

**Date :** 20 novembre 2026  
**Statut :** instruction sourcée ; **aucune modification du XLSX maître, des identifiants ni du JSON public**.  
**Source de comparaison :** `docs/data/organismes.json`, version 0.3.0, export du 20 novembre 2026 à 16 h UTC depuis `AdlFI_referentiel_1-49_enrichi_relations_586_20261120.xlsx`, SHA-256 source `2fcec08dccecc1532cbd25b590514118156e0161292de4b368d665ca992768f4`. Base : 920 autorités (725 ORG, 195 SER), 586 relations.

## Constats reproductibles dans le JSON public

- Dans les **195 SER**, **un seul** porte la catégorie BSR `ASS` et le type `groupe_associatif` : **SER-0063**, Groupe de recherche archéologique sous-marine (GRASM, Marseille).
- Son unique lien institutionnel publié vers la FFESSM est **RSE-0083** : `SER-0063 → ORG-0120`, `rattachement_service`, validé. **Ce lien qualifie incorrectement une affiliation associative comme un lien administratif.**
- **ORG-0422**, Comité départemental de spéléologie et de canyon des Alpes-Maritimes (CDS 06), est déjà ORG/ASS, mais sa date d'activité est indéterminée et **aucune relation avec ORG-0701 (FFS) n'est publiée**.
- **ORG-0120** (FFESSM) n'a, dans le réseau des 586 relations du JSON, que le lien RSE-0083 ; **ORG-0701** (FFS) n'en a aucun. Les compteurs `usage.affiliations_*` du JSON sont des alignements de **sources éditoriales**, **pas** des affiliations fédérales : ne pas les confondre.
- Un balayage lexical des noms et acronymes identifie **25 ORG/ASS** à explorer (spéléologie, plongée, subaquatique, etc.), mais **ce n'est pas une preuve d'affiliation** ; l'audit ne prétend pas identifier exhaustivement les clubs.

## Classements et liens documentés

| Autorité AdlFI | Cible | Décision / qualification | Sources |
|---|---|---|---|
| **SER-0063 GRASM** | ORG-0120 FFESSM | **Reclasser en ORG/ASS** (association autonome) ; **retirer/remplacer RSE-0083** par une affiliation fédérale ; conserver le renvoi de l'ancien ID | [GRASM](https://www.grasm-plongee.com/) (site du club, affiliation déclarée) ; [Office de tourisme de Marseille](https://www.marseille-tourisme.com/offres/g-r-a-s-m-et-ecole-europeenne-de-plongees-aux-melanges-marseille-7eme-fr-3753842/) ; RNA **W133005037**, SIREN **391556040** (registre secondaire [Assoce](https://assoce.fr/waldec/W133005037/GROUPE-DE-RECHERCHE-ARCHEOLOGIQUE-SOUS-MARINE-GRASM-)) |
| **ORG-0069 CASAVO** | ORG-0120 FFESSM | **Affiliation fédérale explicite** ; ne pas créer de SER | [Présentation officielle CASAVO](https://casavo.fr/the/) (se déclare affilié) |
| **ORG-0419 IERO** | ORG-0120 FFESSM | **Affiliation attestée historiquement** ; qualifier la date/validité à partir des saisons fédérales ; pas de nouveau SER | [Article FFESSM](https://subaqua.ffessm.fr/article/feminisation-de-la-plongee-le-iero-prend-une-longueur-davance) ; [liste FFESSM](https://ffessm.fr/uploads/media/docs/0001/12/d9bf52a41c5041bbe443e29f605cad6fac6cb80d.pdf) |
| **ORG-0521 Royan Océan Club Plongée** | ORG-0120 FFESSM | **Affiliation documentée pour 2022–2023**, à ne pas supposer éternelle | [Annuaire FFESSM hockey subaquatique 2022–2023](https://hockeysub.ffessm.fr/uploads/media/docs/0001/10/9a458d31c19a64c2fff8d6735eeaa529ce5de92c.pdf) |
| **ORG-0422 CDS 06** | ORG-0701 FFS | **Affiliation/comité déconcentré établie** ; statut `actif` réexaminable à la date de l'annuaire ; ville d'origine actuelle `Mandelieu-la-Napoule` à comparer à l'adresse postale fédérale `Villeneuve-Loubet` sans réécrire une localisation historique | [Annuaire officiel FFS](https://ffspeleo.fr/comite-departement-region.html) ; [convention département 06, mars 2025](https://www.departement06.fr/sites/default/files/media/downloads/cp16_14-03-25.pdf) |

### Le cas décisif ARESMAR / Les Aresmarins / section plongée

Les sources primaires conduisent à **distinguer trois réalités**, qui ne doivent pas être fusionnées automatiquement :

1. **ORG-0132 ARESMAR**, association de recherche archéologique (Perpignan) déjà présente dans AdlFI.
2. **Les Aresmarins**, **association autonome déclarée le 12 novembre 2002 à Narbonne**, agissant comme club affilié à la FFESSM, **absente du JSON actuel** : **candidate à une nouvelle ORG**, pas une simple variante d'ORG-0132. Le rapport d'AG ARESMAR du 6 décembre 2014 la présente sans ambiguïté comme une association avec sa propre AG, intervenant pour que les membres ARESMAR puissent se licencier et pour transmettre les financements fédéraux. Code de club cité : `08110389`. **Ne pas inférer sa dissolution ou une succession institutionnelle sans document**. [Rapport ARESMAR 2014, p. 13–14](https://s8ef27ab2e0882a74.jimcontent.com/download/version/1710778697/module/12337179332/name/AG%20du%206%20d%C3%A9cembre%202014.pdf).
3. **Section plongée FFESSM de l'ARESMAR**, subdivision interne **sans comptabilité ni patrimoine propres**, documentée dans le règlement disponible sur le site de l'association ; son affiliation à la FFESSM est explicite. **Ne pas la confondre avec Les Aresmarins**. Une SER de section n'est utile que si elle apparaît comme signataire/auteur institutionnel distinct dans les documents AdlFI ; sinon qualifier l'affiliation de l'ARESMAR comme « via sa section plongée ». [Statuts et règlement intérieur de la section](https://www.aresmar.fr/vie-associative/les-statuts/).

**Chronologie à consolider :** le [compte rendu du bureau du 26 septembre 2020](https://s8ef27ab2e0882a74.jimcontent.com/download/version/1685172115/module/14387892132/name/R%C3%A9union%20du%20bureau-26-09-20.pdf) décrit **la proposition de création** d'une section interne pour remplacer l'intermédiation financière des Aresmarins. Le règlement publié sur le site indique une approbation par une AG du « 17 janvier 2020 », antérieure à la proposition de septembre : **discordance chronologique non élucidée**. Ne pas fixer artificiellement une date de début à partir de ces deux mentions contradictoires.

## Affiliation vraisemblable, mais non validée à ce stade

- **ORG-0355** (EESV) : [référencée par le CDS du Rhône](https://www.csr-rhonealpes.fr/cds69/les-clubs/), ce qui présume son insertion dans le réseau de la FFS ; **établir l'affiliation fédérale précise et sa période**.
- **ORG-0418** (Clan spéléo pontoisien) : documentée dans les [publications FFS](https://spelunca-memoires.ffspeleo.fr/200509_Spelunca_memoires_28.pdf) et les [activités fédérales historiques](https://www.cosif.fr/wp-content/uploads/2012/01/CR-Premi%C3%A8re-rencontre-des-cadres-dIdF-le-17-mai-2014.pdf) ; **ne pas conclure automatiquement à une affiliation en 2026**.
- **ORG-0531** (Société spéléo-archéologique de Caussade) : travaux relayés par la FFS, mais activité actuellement enregistrée **inactive** ; éventuellement affiliation **historique** à dater, pas de réactivation.
- **ORG-0318** (2ASM, Arles) : proximité et collaborations avec la FFESSM attestées, **mais partenariat ≠ affiliation** ; recherche complémentaire nécessaire.
- **ORG-0171** (GRAS, Brunoy), **ORG-0131** (Ampevas), **ORG-0175** (SRASSMF), **ORG-0709** (GREC Luberon) : candidats à recherche de preuves, pas de relation validée par leur seul nom.
- **ORG-0342** (fédération monégasque) et **ORG-0693** (groupe de Bergame) : pas d'affiliation automatique aux fédérations françaises.

## Règle ORG / SER et type de relation

1. **ORG** pour toute association/club/comité détenteur de sa propre personnalité morale, même adhérent d'une fédération.
2. **SER** uniquement pour une commission/section interne sans personnalité morale, et seulement si sa présence comme unité documentaire le justifie. Les structures déconcentrées FFESSM peuvent avoir ou non leur personnalité morale : vérifier **au cas par cas**, conformément aux [statuts FFESSM](https://ffessm.fr/documents-statutaires/statuts-reglements).
3. Relation nouvelle proposée : `affiliation_federale`, source = membre (ORG, éventuellement SER interne qualifié), cible = fédération ORG ; jamais `rattachement_service` pour un club autonome.
4. Pour les comités territoriaux, une relation plus spécifique `organisation_deconcentree_federale` peut être envisagée si nécessaire ; ne pas multiplier les types avant d'avoir défini le rendu public.
5. **Dates** : indiquer la période documentée (une saison donnée ne prouve pas la permanence) ; sans date historique sourcée, ne pas inventer `date_debut` ou `date_fin`.
6. **Preuve** : URL officielle/registre, qualification de la relation, période, statut de validation. Le JSON actuel n'exporte pas de champ `source_documentaire` pour ses relations : **conserver la preuve dans le maître ou un registre de provenance dédié**, sans l'inventer dans les sorties.

## Dépendances de migration et publication

- **SER-0063 → nouvel identifiant ORG** : attribution après dédoublonnage dans la dernière version privée du maître ; **table de correspondance pérenne** `SER-0063 -> ORG-XXXX` ; migration de `RSE-0083` et de toutes les AFF, références éditoriales, logos (actuellement `SER-0063.jpg`), recherches et liens directs. Le statut du SER initial n'est **pas** une succession historique réelle : **ne pas créer une pseudo-autorité inactive**.
- **Code du site** : `docs/assets/organismes.js` ne reconnaît actuellement dans `RATTACHEMENT_TYPES` que `rattachement_administratif`, `rattachement_service`, `rattachement_institutionnel`, `rattachement` et `tutelle`. Un `affiliation_federale` ajouté au JSON serait **invisible** : prévoir une section d'affiliations fédérales avec libellé propre, navigation vers/depuis la fédération et distinction explicite des tutelles et rattachements.
- **Garde-fous** : exporter depuis le XLSX maître actualisé seulement après rapprochement ; contrôler continuité des 920 anciennes autorités via IDs ou alias de migration, absence de références orphelines, conservation des 586 liens précédents hors **correction justifiée** de `RSE-0083`, tests schéma/export et recette visuelle.
- **Aucun changement de données publiques dans cette PR d'instruction**.

Dossier général de suivi : [issue #174](https://github.com/nicocoquet/adlfi-referentiels/issues/174).
