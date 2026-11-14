# Lieux AdlFI — préinstruction des 20 dossiers P3 (Bourgogne-Franche-Comté)

**14 novembre 2026 — PR n°24, recette non validante.**

## Résultats et provenance

Le lot de 20 candidatures est une extraction sans modification du lot éditorial BFC de 29 dossiers. Les décisions, justifications, vérificateurs et dates de validation demeurent vides.

Le script **scripts/instruire_p3_bfc_cog.py** rapproche ces 20 dossiers avec les fichiers officiels du **COG 2026** (communes, mouvements et historiques depuis 1943), exige leurs trois empreintes SHA-256 et contrôle les transitions avant/après.

Sources : https://www.insee.fr/fr/information/8740222 et nomenclature : https://www.insee.fr/fr/information/8740218.

| Unité | Résultat |
| --- | ---: |
| Candidatures documentaires P3 | **20** |
| Fusions simples (MOD 31) | 4 |
| Créations/extensions de communes nouvelles (MOD 32) | 15 |
| Fusion-association (MOD 33) | 1 |
| Événements administratifs initiaux distincts | **16** |
| Événements initiaux déjà présents en P2 | **2** |
| Événements administratifs ultérieurs | **6** |
| Total d'événements distincts dans cette recette | **22** |
| Lignes de mouvements des événements initiaux | 51 |
| Lignes de mouvements des événements ultérieurs | 14 |
| **Lignes COG préservées** | **65** |
| Périodes code–libellé documentées | 49 |

**Les 20 relations documentaires, les 22 événements administratifs et les 65 lignes du COG sont trois unités de comptage différentes.** Les lignes de mouvement n'équivalent pas à autant d'actes juridiques indépendants.

## Seize événements initiaux

| Date | MOD | Commune réceptrice au moment de l'événement | Candidatures P3 |
| --- | --- | --- | --- |
| 1972-12-31 | 33 | Saulnot (70477) | Gonvillars |
| 1973-01-01 | 31 | Baume-les-Dames (25047) | Champvans-les-Baume |
| 1973-01-01 | 31 | Belleherbe (25051) | Droitfontaine |
| 1973-01-01 | 31 | Orgelet (39397) | Sézéria |
| 1974-04-01 | 31 | Vaire-Arcier (25575) | Arcier |
| 2016-01-01 | 32 | Sancey (25529) | Sancey-le-Long ; **même événement que P2** |
| 2016-01-01 | 32 | La Chailleuse (39021) | Essia, Saint-Laurent-la-Roche, Varessia |
| 2017-01-01 | 32 | Chemaudin et Vaux (25147) | Vaux-les-Prés |
| 2017-01-01 | 32 | Valzin en Petite Montagne (39290) | Chatonnay, Fétigny, Savigna |
| 2017-01-01 | 32 | Val Suran (39485) | Villechantria |
| 2017-01-01 | 32 | Thoirette-Coisia (39530) | Coisia |
| 2018-01-01 | 32 | Bouclans (25078) | Vauchamps |
| 2018-01-01 | 32 | Marchaux-Chaudefontaine (25368) | Chaudefontaine ; **même événement que P2** |
| 2018-01-01 | 32 | Arinthod (39016) | Chisséria |
| 2019-01-01 | 32 | Fontain (25245) | Arguel (Doubs) |
| 2022-01-01 | 32 | Cussey-sur-Lison (25185) | Châtillon-sur-Lison |

Les identifiants des opérations **Sancey 2016** et **Marchaux 2018** sont strictement réutilisés depuis P2, ce qui évite de doubler les événements dans le futur graphe.

## Six événements ultérieurs

| Date | MOD | Destination et codes | Conséquence administrative |
| --- | --- | --- | --- |
| 1997-05-01 | 34 | Saulnot (70477) | Gonvillars : transformation de fusion-association en fusion simple |
| 2016-06-01 | 32 | Vaire (25575) | Vaire-Arcier et Vaire-le-Petit participent à une commune nouvelle |
| 2020-01-01 | 35 | Thoirette-Coisia (39530) | Suppression des statuts délégués de Coisia et de Thoirette |
| 2020-03-15 | 35 | La Chailleuse (39021) | Suppression des statuts délégués d'Essia, Saint-Laurent-la-Roche et Varessia |
| 2020-03-15 | 35 | Val Suran (39485) | Suppression des statuts délégués de Bourcia, Louvenne, Saint-Julien et Villechantria |
| 2021-03-15 | 35 | Bouclans (25078) | Suppression du statut délégué de Vauchamps |

Huit dossiers sources P3 sont affectés par une étape ultérieure : six par suppression du statut de commune déléguée, un par transformation de fusion-association, un parce que la commune réceptrice a participé à une autre création de commune nouvelle.

### Points de vigilance

**Arcier → Vaire-Arcier → Vaire :** la fusion simple du 1er avril 1974 donne Vaire-Arcier (code 25575). La nouvelle opération du 1er juin 2016 aboutit à Vaire, qui conserve ce code. Le libellé Vaire-Arcier attesté en 1974 ne doit pas être remplacé rétrospectivement par Vaire.

**Gonvillars :** le mouvement du 31 décembre 1972 crée une situation de fusion-association avec Saulnot, transformée en fusion simple le 1er mai 1997. Le statut COMA intermédiaire doit être documenté.

**Noms et codes inchangés :** sept dossiers ont une réceptrice dont le nom et le code sont inchangés dans la ligne principale du mouvement (dont Fontain, Bouclans, Arinthod et Cussey-sur-Lison). Ce fait ne signifie pas un périmètre territorial inchangé.

**MOD 35 :** la suppression d'une commune déléguée supprime un statut administratif, pas le toponyme, l'ARK ou le lieu de la notice.

## Modélisation et sorties

Conserver distincts :
1. **Concept Pactols** : ARK documentaire, sans fusion sur code INSEE partagé ;
2. **Événement administratif** : date, MOD, tous les états COG avant/après et provenance ;
3. **Participation d'une ancienne commune**, ou rattachement historique, distinct d'une équivalence SKOS ;
4. **Évolution de statut COMD/COMA**, sans assimiler la suppression du statut à une seconde fusion ;
5. **Géométries historiques**, qui nécessiteront des données datées indépendantes.

Les 49 périodes historiques portent sur les couples code–libellé, **pas sur des contours**.

**Livrables du workflow de recette :**
- preinstruction-p3-20.csv : vingt candidatures avec événements et alertes temporelles ;
- evenements-p3-22.csv : seize événements initiaux et six ultérieurs ;
- preuves-mouvements-p3-65.csv : toutes les lignes avant/après retenues ;
- periodes-noms-p3.csv : périodes de libellés ;
- rapport-p3.json : contrôles, empreintes et limites.

Toutes les sorties ont été générées deux fois et comparées octet par octet dans GitHub Actions. **Aucune nouvelle relation éditoriale n'a été validée et aucune géométrie historique n'a été attribuée.** PR n°24 maintenue en brouillon.
