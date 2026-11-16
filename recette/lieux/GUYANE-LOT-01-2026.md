# Lieux — Guyane, lot 01 : identités COG, histoire, Pactols, géométries

**16 novembre 2026 · Recette uniquement. Aucun nouvel alignement ni contour publié.**

## Périmètre

- **22 communes COG 2026**, département 973, région COG 03 : noms et codes déjà présents dans l'index public du module Lieux.
- **Historique depuis 1943** : observations datées code–libellé, distinctes des événements communaux et des éventuelles relations de succession.
- **Pactols Lieux (SKOS)** : distinguer une **URI INSEE citée explicitement dans un concept** d'une **simple concordance de libellé**. Aucune des deux ne constitue, seule, une décision éditoriale AdlFI.
- **Contours 2026** : validité topologique, présence et surface indicative, sans réparation automatique ni géométrie publiée.

**Précaution institutionnelle** : la Guyane est une collectivité territoriale unique succédant aux institutions régionale et départementale et exerçant leurs compétences depuis décembre 2015. Les codes COG de région 03 et de département 973 demeurent nécessaires à la navigation géographique, sans créer deux autorités institutionnelles contemporaines indépendantes. Le sélecteur du site reste **Région / Département / Commune**.

### Sources

- [Insee, département de Guyane (22 communes COG 2026)](https://www.insee.fr/fr/metadonnees/geographie/departement/973-guyane)
- [Insee, historique des communes de Guyane](https://www.insee.fr/fr/metadonnees/historique-commune?debut=0&departement=973&taille=100)
- [Insee, fichiers COG](https://www.insee.fr/fr/information/8740222)
- [Légifrance, loi n° 2011-884 du 27 juillet 2011](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000024403725/)
- [Légifrance, CGCT — Collectivité territoriale de Guyane](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070633/LEGISCTA000024405343/2026-07-30)
- [Pactols, dépôt Frantiq (export épinglé du 22 juillet 2026)](https://github.com/frantiq/PACTOLS/tree/69bf9697e24cefd645a69465bbd271702786285a)

## Priorités d'instruction historique

| Groupe | Événements à instruire | Risques de confusion |
| --- | --- | --- |
| Réorganisation de 1969 | Régina et Approuague-Kaw, Saint-Georges et Oyapoc, Remire-Montjoly, Saül, Mana, Roura, Montsinéry-Tonnegrande | Fusion, changement de nom et périmètre territorial ne sont pas équivalents |
| Maroni 1976 | Apatou (97360) et Grand-Santi (97357) | Distinction entre date de décision, date d'effet et rétablissement d'une commune |
| Ouest guyanais 1988–1989 | Awala-Yalimapo (97361) et Mana (97306) | Le portail affiche 31 décembre 1988, tandis que la création est documentée au 1er janvier 1989 |
| Maroni 1992–1993 | Papaichton (97362) et Grand-Santi (97357) | Dissocier les événements au 31 décembre 1992 et la situation au 1er janvier 1993 |
| Codes et territoires anciens | Maripasoula, Saül, Saint-Élie, Ouanary ; anciens codes 97351, 97354, 97355, 97359, etc. | Ne pas attribuer un contour 2026 à une unité administrative disparue |

Le portail historique INSEE affiche **56 résultats** pour le département. Ce nombre n'est **pas** imposé comme cardinalité des mouvements COG : une même modification peut concerner plusieurs communes ou un rattachement à un arrondissement. La recette distinguera les différentes unités de comptage.

## Production contrôlée

- Script d'audit : scripts/auditer_guyane_2026.py
- Tests : tests/test_auditer_guyane_2026.py
- CI : .github/workflows/lieux-guyane-audit-2026.yml

Entrées sous empreintes SHA-256 : COG 2026 (communes, historique et mouvements), géométries nationales à 100 m datées du 4 mai 2026, index public AdlFI, Pactols Lieux RDF de juillet 2026. L'absence d'un concept dans l'export daté **ne prouve pas son absence du référentiel vivant**.

La CI produit deux fois des sorties octet à octet identiques dans des répertoires temporaires ; elle conserve un artefact de recette comprenant :

1. **guyane-22-communes-audit.json** : une fiche par commune actuelle, ses épisodes, événements, indices Pactols et diagnostic de géométrie ;
2. **guyane-historique-mouvements.json** : épisodes historiques et lignes de mouvements distincts, y compris les codes disparus ;
3. **guyane-revue-22-communes.csv** : tableau de validation éditoriale à 22 lignes ;
4. **manifest-guyane.json** : sources et sorties SHA-256, compteurs et garanties.

Le fichier RDF est l'export Git LFS du 22 juillet 2026, commit épinglé. Les citations de codes INSEE ou concordances lexicales sont **des candidats**, jamais un alignement automatiquement approuvé.

**Aucune modification de données publiques sous docs, aucune frontière publiée, aucune validation Pactols créée.** Pour les géométries anciennes, il faudra identifier une source datée ou une reconstruction spatialement et historiquement justifiée.

Après validation de cette méthode sur la Guyane, le protocole sera étendu à la Martinique puis à la Guadeloupe.
