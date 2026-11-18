# Pays de la Loire — les 60 codes 2026 à ARK multiples

Recette **non validante**. Le script `scripts/auditer_pdl_ark_multiples_2026.py` reprend le RDF Pactols et le COG 2026 épinglés de l'audit régional, puis croise les 60 codes avec les événements déjà enregistrés dans `cog-pdl.json`.

La priorité « COMMUNE_NOUVELLE » est exclusivement une **priorité documentaire** fondée sur un événement COG MOD32 de création de commune nouvelle. Elle ne tranche pas entre les ARK. Les événements, leurs dates et les concepts RDF restent distincts.

Le rapport JSON de CI conserve les assertions `exactMatch`, les ARK concurrents, les libellés et statuts Pactols, ainsi que les mouvements COG. Aucun ARK n'est sélectionné. Aucun lien, géométrie ou épisode historique n'est publié dans `docs`.

**Contrôles :** exactement 60 codes, unicité des codes, deux exécutions bit à bit identiques, absence de décisions éditoriales et de publication. Après exécution, instruire les communes nouvelles par petits lots en confrontant chaque ARK à sa définition, aux variantes et aux périodes COG. Les autres cas seront traités séparément.

Situation de départ : **1 143 / 1 228** correspondances publiées, **85 exceptions** ouvertes (60 + 24 + Rives-du-Fougerais). Suivi : #130.
