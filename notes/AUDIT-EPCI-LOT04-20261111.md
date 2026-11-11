# Lot 04 — Audit des cinq dossiers EPCI et syndicats réservés

**11 novembre 2026.** Base privée : maître 1.43 `AdlFI_referentiel_1-43_20261111_historique_EPCI_lot03.xlsx`. **Ce dossier est une proposition non appliquée** : la PR n° 14 reste en brouillon, le JSON 1.43 prépublié n'est pas changé.

## Dossiers et résultats

| ID | Élément documentaire contrôlé | Proposition | Réserve |
|---|---|---|---|
| `ORG-0162` SAN Ouest Provence | SCA créé le **18 décembre 1972** puis devenu SAN par arrêté de juillet 1984 ; SAN SIREN **241300177** (immatriculé postérieurement) | Documenter l’antécédent SCA sans antidater immédiatement la personne morale de l’ORG | Le mot « transformation » dans le rapport CRC ne démontre pas seul une personnalité juridique inchangée. Effet juridique de l'arrêté du 12 juillet 1984 à contrôler. |
| `ORG-0659` Clos du Cotentin | SIREN **200060762** ; forme **syndicat mixte fermé** ; la DGCL confirme que le SMF n'est pas un EPCI | Ajouter la forme historique `syndicat_mixte_ferme`, 2016–2018 ; retirer ou expliciter le niveau `intercommunal` | Source d’immatriculation secondaire, arrêté/statuts signés à rechercher ; ne pas modifier le type `syndicat_mixte`. |
| `ORG-0213` Nord du Bassin de Thau | SIREN **243400751** attesté dans des actes préfectoraux ; arrêté n° **2000-1-4255** du 21 décembre 2000 | `date_debut=2000` (année) ; `communaute_communes` jusqu'au 2016-12-31 | Date de signature de l'acte ≠ nécessairement date d'effet. |
| `ORG-0403` Cap Calaisis | Ancien SIREN **246201149** confirmé par l'Insee ; distinct de `ORG-0636` **200090751** | `date_debut=2001` (année) ; `communaute_agglomeration` jusqu'au 2019-11-30 | Vérifier le jour d'effet de l'arrêté de décembre 2000. |
| `ORG-0214` Sète agglopôle | Prédécesseurs : ancienne CA du Bassin de Thau **243400827** (2002–2016) et CCNBT **243400751** ; nouvelle CA **200066355** depuis le 2017-01-01 | `date_debut=2017-01-01`, `actif=oui` ; proposer `ORG-0676` ancienne CA du Bassin de Thau et `REL-0306` succession vers ORG-0214 | **Création d’autorité à arbitrer** : aucune affiliation XML du maître ne lui correspond directement ; le nom « CA du Bassin de Thau » est aussi employé par la nouvelle CA en 2017. |

## Sources primaires et institutionnelles

- CRC PACA, rapport d’observations SANOP, p. 9 : https://www.ccomptes.fr/sites/default/files/EzPublish/JF00123164.pdf
- Loi n° 83-636 sur les agglomérations nouvelles : https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000692492/1988-12-28
- DGCL, syndicats mixtes (les SMF ne sont pas des EPCI) : https://www.collectivites-locales.gouv.fr/connaitre-les-acteurs-et-les-institutions/structures-territoriales/les-intercommunalites-et-groupements-de-collectivites/les-groupements-intercommunaux
- SIREN SMF Clos du Cotentin (annuaire secondaire) : https://www.eterritoire.fr/territoires/normandie/manche/valognes/50615/19307?annuaire=administrations
- CC Nord du Bassin de Thau, SIREN 243400751, recueil préfectoral de mars 2016 : https://www.herault.gouv.fr/content/download/18178/138346/file/Recueil%20%20du%2025%20mars%202016.pdf
- Jurisprudence citant son arrêté de création : https://www.legifrance.gouv.fr/ceta/id/CETATEXT000020219972
- CA Calaisis, SIREN 246201149, Insee : https://www.insee.fr/fr/statistiques/4986976
- Ancienne CA du Bassin de Thau, SIREN 243400827, Insee : https://www.insee.fr/fr/statistiques/2020952?geo=EPCI-243400827
- Ancienne CA du Bassin de Thau : arrêté préfectoral portant création au 31 décembre 2002 : https://www.herault.gouv.fr/contenu/telechargement/2091/11338/file/Special_2002_T.pdf
- Fusion de Thau au 1er janvier 2017, Insee : https://www.insee.fr/fr/statistiques/3287786

## Arbitrages de schéma et de publication

1. Proposer un **`identifiant_siren` facultatif dans `Organismes`** : il aide à distinguer les personnes morales françaises mais ne doit pas effacer l'historicité d'identification ni être exigé des autorités étrangères.
2. Les syndicats mixtes restent `type_organisme=syndicat_mixte` ; leur **forme** est distincte de l'**échelon institutionnel**. Ne pas déduire `intercommunal` du seul périmètre des membres.
3. Une même dénomination peut correspondre à deux personnes morales distinctes à des dates différentes. `HIS-0016` concerne le **nouvel** EPCI de Thau en 2017, distinct du prédécesseur homonyme constitué en 2002.
4. Avant création éventuelle de `ORG-0676` et `REL-0306`, revérifier les identifiants libres au dernier maître. N'affecter aucune affiliation aux nouvelles autorités sans source.
5. **Aucune modification du XLSX privé, du JSON ni de la facette ne résulte du présent audit.** La PR n° 14 reste non fusionnée pour recette visuelle.

Le dossier complet éditorial (XLSX à six feuilles, note et empreintes) est remis séparément à l'éditeur, sans être déposé sur GitHub.