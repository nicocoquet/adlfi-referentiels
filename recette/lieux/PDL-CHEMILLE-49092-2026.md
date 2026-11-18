# Pays de la Loire — Chemillé-en-Anjou (49092), trois identités sous un même code

**Instruction éditoriale pour le millésime COG 2026 — 18 novembre 2026.**

Les données COG enregistrées dans `docs/data/lieux-chronologie/cog-pdl.json` et les fiches officielles de l'Insee documentent trois situations successives :

| Intervalle COM (code 49092) | Concept Pactols | Rôle dans la publication |
|---|---|---|
| 1943–2013, Chemillé | `26678/pcrtL5GRFXn3Zs` | Concept historique à conserver, non promu en 2026 |
| 2013–15 décembre 2015, Chemillé-Melay | `26678/pcrtWU8rdgPSSH` | Concept de l'ancienne commune nouvelle, non promu en 2026 |
| Depuis le 15 décembre 2015, Chemillé-en-Anjou | `26678/pcrtzDf0WnnRyr` | Concept proposé pour l'alignement COG 2026 |

Les trois ARK possèdent un `skos:exactMatch` vers l'URI de code INSEE `http://id.insee.fr/geo/commune/49092`, mais le concept Chemillé-en-Anjou est le seul dont le `skos:prefLabel` désigne exactement la commune **créée en 2015**, toujours en vigueur au 1er janvier 2026. Le générateur exige l'absence de dépréciation et de remplacement et vérifie les autres URI INSEE pour chacun des trois ARK.

La transition est **COM Chemillé → COM Chemillé-Melay** le 1er janvier 2013 (MOD32), puis **COM Chemillé-Melay → COM Chemillé-en-Anjou** le 15 décembre 2015 (MOD32), en conservant le code. Cette succession n'autorise ni `owl:sameAs` entre les concepts, ni rétroprojection de l'ARK actuel sur les états 2013 ou antérieurs.

**Sources faisant autorité :**
- [Fiche communale Insee 2026 — Chemillé-en-Anjou, 49092](https://www.insee.fr/fr/metadonnees/geographie/commune/49092-chemille-en-anjou).
- [Insee, dossier complet 2026](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49092), rubrique changements de contour, qui documente les créations de 2013 et de 2015.
- RDF Pactols-Lieux th17 du 22 juillet 2026, commit Frantiq `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- `recette/lieux/PDL-QUATRE-CREATIONS-SUCCESSIVES-2026.md`, qualification dans la PR 137.

**Décision 2026 proposée :** valider uniquement `26678/pcrtzDf0WnnRyr` pour la commune 49092 ; conserver les deux autres ARK comme concepts distincts, sans créer de relation historique entre eux.

**Effet recherché après succès CI :** un nouveau lien, de 1 148 à **1 149 / 1 228**, 79 exceptions. Aucune géométrie nouvelle, aucun ancien ARK promu, aucun épisode historique inféré.
