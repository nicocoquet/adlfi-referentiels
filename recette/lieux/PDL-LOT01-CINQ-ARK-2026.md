# Pays de la Loire — lot 01 : cinq collisions ARK / communes nouvelles

**Proposition de qualification uniquement, sans publication (18 novembre 2026).**

Cinq codes COG 2026 possèdent deux ARK Pactols pointant par skos:exactMatch sur le même code INSEE. Un seul concept porte le libellé actuel ; le second correspond à une ancienne commune. Le COG documente dans chaque cas un mouvement MOD32 au 1er janvier 2016, avec COM vers COM pour la commune nouvelle et COM vers COMD pour l'ancienne commune dont le code est réemployé.

| Code | Commune actuelle, ARK candidat | Ancienne commune, ARK concurrent |
|---|---|---|
| 44005 | Chaumes-en-Retz, 26678/pcrtN3127ZAunw | Arthon-en-Retz, 26678/pcrtju3LL59HiZ |
| 44021 | Villeneuve-en-Retz, 26678/pcrt5umeCC5nWQ | Bourgneuf-en-Retz, 26678/pcrt7IaoJP82qR |
| 44029 | Divatte-sur-Loire, 26678/pcrtir0x0oi7Z7 | La Chapelle-Basse-Mer, 26678/pcrt5I1iVlmViA |
| 44087 | Machecoul-Saint-Même, 26678/pcrt9dHhZhLkZ1 | Machecoul, 26678/pcrtRIS4y4XXSl |
| 44163 | Vair-sur-Loire, 26678/pcrthouCaXtWcI | Saint-Herblon, 26678/pcrtl9Hc5lXKyi |

Sources : Pactols-Lieux th17 du 22 juillet 2026 (commit 69bf9697e24cefd645a69465bbd271702786285a, SHA-256 3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7) et COG Insee 2026 (SHA-256 7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3). Rapports reproductibles de la PR 135, workflow 44322479886.

**Principe :** le code COG conservé ne rend pas équivalents l'ARK de la commune nouvelle et celui de l'ancienne commune. Les anciennes autorités restent distinctes, potentiellement liées à des épisodes historiques COM / COMD documentés ; aucun lien ARK-ARK n'est inféré.

Le CSV associé conserve le statut PROPOSITION_A_CONTROLER. Aucune correspondance, géométrie ou relation historique n'est ajoutée à la publication GitHub Pages.
