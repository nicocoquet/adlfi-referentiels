# Préflight du reclassement GRASM (SER-0063 → ORG à attribuer)

**Objet.** Contrôle de sécurité préalable à la migration du GRASM, association autonome actuellement publiée comme service `SER-0063` du référentiel AdlFI. Le rattachement `RSE-0083` vers `ORG-0120` (FFESSM), typé `rattachement_service`, doit être remplacé par une affiliation fédérale documentée.

**État :** outil d'inventaire **lecture seule**, pas de migration automatique, pas de nouvel identifiant généré.

## Commande sur l'ordinateur disposant du XLSX maître courant

```bash
python3 scripts/auditer_reclassement_grasm.py \
  '/chemin/vers/AdlFI_referentiel_1-49_enrichi_relations_586_20261120.xlsx' \
  --rapport '/tmp/adlfi-preflight-grasm.json'
```

L'outil n'utilise que la bibliothèque standard de Python. Il parcourt **toutes les feuilles physiques du XLSX**, y compris celles hors des dix feuilles exportées dans le JSON public. Il détecte les cellules qui contiennent `SER-0063`, avec feuille, numéro de ligne, colonne, en-tête et extrait, et présente les lignes `Relations_services` pertinentes. Il vérifie l'unicité du SER et signale une ORG déjà nommée GRASM pour empêcher un doublon. Le rapport inclut l'empreinte SHA-256 du fichier utilisé.

Le rapport est **privé** : les extraits de cellules du maître ne doivent pas être déposés tels quels dans le dépôt public. L'outil n'écrit aucun contenu dans le XLSX. Il renvoie 0 lorsque les hypothèses préliminaires sont satisfaites, 2 si une incohérence est détectée.

## Invariants et suites

1. Vérifier les références dans `Correspondances_affiliations` et les autres feuilles avant de modifier l'identifiant. Le compte `usage.affiliations_linked=3` du JSON ne garantit pas, à lui seul, un décompte identique des lignes du classeur : faire le rapprochement réel.
2. Réserver un identifiant `ORG-XXXX` **non utilisé** dans le maître à jour. Ne pas conserver `SER-0063` comme autorité fictive « inactive » et ne pas établir une relation de succession fictive.
3. Définir l'alias technique `SER-0063 → ORG-XXXX` pour les URL historiques, imports, recherches et backlinks.
4. Migrer toutes les correspondances référentielles ; corriger `RSE-0083` en `affiliation_federale` du nouvel ORG vers `ORG-0120`. Conserver la preuve et ses éventuelles bornes chronologiques.
5. Reprendre l'identité visuelle `SER-0063.jpg` en `ORG-XXXX.jpg`, et contrôler l'intégrité des références de l'ancien identifiant.
6. Exporter les données par `scripts/export_organismes.py`, contrôler les effectifs attendus (migration 1 SER → 1 ORG : **ORG +1, SER −1, total inchangé** à l'exclusion d'autres créations simultanées) et exécuter tous les tests, y compris Chromium, puis recette sur le site.

**Important :** le test d'égalité `relation RSE-0083` du préflight s'applique **à l'état préalable** à la migration. Après migration, son échec est normal : ne pas l'utiliser comme contrôle de validité du classeur déjà migré.

Dossier de suivi : [issue #174](https://github.com/nicocoquet/adlfi-referentiels/issues/174).
