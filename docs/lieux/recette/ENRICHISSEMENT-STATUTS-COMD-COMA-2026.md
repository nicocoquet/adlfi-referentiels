# Lieux — suivi des sept communes associées/déléguées du lot 001

**État : recette non validante.** Aucun nouvel alignement Pactols–COG et aucune géométrie historique attribuée.

L'audit des **33 états** du graphe des mouvements a daté **26 états `COM`** par leurs couples code–libellé 2026 depuis 1943. Les sept états restants — **six `COMD` et un `COMA`** — ne figurent pas dans la table des couples historiques (`v_commune_depuis_1943.csv`), qui couvre `COM` et `ARM`.

Le script `scripts/auditer_statuts_delegues_associes.py` analyse ces sept états à l'aide de deux fichiers **officiels complémentaires** :

- `v_mvt_commune_2026.csv` : mouvements depuis 1943, dates d'effet, états avant et après ;
- `v_commune_2026.csv` : états présents au 1er janvier 2026, dont `COMD` et `COMA`, avec leur code de commune parente `COMPARENT`.

Sources : https://www.insee.fr/fr/information/8740222

## Méthode

Pour chaque état (`TYPECOM`, `COM`, `LIBELLE`), l'audit recherche **toutes** les lignes de mouvements correspondantes, puis différencie :

1. **Première entrée attestée** : une occurrence du même état dans les colonnes « après » sans apparition du même état dans les colonnes « avant » à cette date ;
2. **Dernière sortie attestée** : apparition dans « avant » sans apparition dans « après » à cette date ;
3. **Transformation interne** : présence du même état dans les deux sens à une date, ce qui n'autorise pas à conclure à son extinction ;
4. **Présence en 2026** : existence exacte de cet état dans `v_commune_2026.csv`, avec `COMPARENT` ;
5. **Absence en 2026** : existence d'un événement de sortie, ou alerte explicite si aucune sortie n'est retrouvée.

La vérification évite de confondre **le code d'une commune déléguée avec le code de sa commune parente** et n'applique pas la période de l'ancienne `COM` à la `COMD` qui lui a succédé.

## Livrables

- `audit-statut-delegue-associe-lot001.json` : sept dossiers détaillés, toutes les lignes de mouvements correspondantes, rattachement `COMPARENT` pour les états encore présents en 2026 ;
- `revue-statut-delegue-associe-lot001.csv` : tableau concis pour la revue ;
- `rapport-statut-delegue-associe-lot001.json` : effectifs et SHA-256 des trois sources.

Les bornes sont toujours qualifiées comme **attestées par les mouvements**, et non comme des périodes administratives intégralement certifiées. Une commune déléguée peut conserver son nom et son code malgré des modifications du statut ou de l'emprise de sa commune parente : on ne pourra valider l'historicité géométrique qu'avec des sources cartographiques de la période étudiée.

## Reproductibilité

```
python3 -m unittest discover -s tests -p 'test_auditer_statuts_delegues_associes.py' -v
```

Le workflow `.github/workflows/audit-periodes-cog-lieux-2026.yml` effectue les téléchargements Insee et dépose les sorties sous forme d'artefact de recette, en conservant les empreintes des sources. Aucune édition des fichiers `docs/data/lieux*`.
