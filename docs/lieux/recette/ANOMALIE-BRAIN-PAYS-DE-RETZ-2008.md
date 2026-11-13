# Lot 001 — Anomalie probable d'indexation géographique : Brain / Brains

**Statut : signalement argumenté, correction non appliquée.**

## Source documentaire

Extraction nationale v2, notice :
`AdlFI_Pays-de-la-Loire/AdlFI_PdL_2008/XML/AdlFI_PdL_2008.xml::notice-000030`.

- Titre : **Pays de Retz**.
- Sous-titre : **Prospection inventaire (2008)**.
- Nombre d'occurrences Pactols terminales : **36**.
- Parmi elles, **35** sont hiérarchisées sous le département de la
  **Loire-Atlantique**, au sein de la région Pays de la Loire.
- Une seule occurrence, numéro **4**, est indexée
  **Brain** (`26678/pcrtXSoREPOwqU`) dans la chaîne :
  Europe → France → France métropolitaine →
  Bourgogne-Franche-Comté → département de la Côte-d'Or → Brain.
- Le parseur TEI signale `zone_tei=p`, une extraction structurellement
  réussie (`qualite=ok`) et l'année d'opération **2008**.

## Vérification administrative

Le COG 2026 distingue deux communes réelles :

- **Brain**, Côte-d'Or, code INSEE **21100** :
  https://www.insee.fr/fr/statistiques/2011101?geo=COM-21100
- **Brains**, Loire-Atlantique, code INSEE **44024** :
  https://www.insee.fr/fr/metadonnees/geographie/commune/44024-brains

La différence est une lettre finale, **s**. Le contexte documentaire
collectif (35 autres lieux indexés sous Loire-Atlantique) rend plausible
une erreur de saisie ou de choix d'autorité **Brain** à la place de
**Brains**. **Cela ne prouve pas que Brains était le lieu voulu** :
la notice complète pourrait contenir une référence réellement pertinente
à Brain (Côte-d'Or).

Dans les **9 928 ARK terminaux attestés** par notre extraction nationale v2,
aucun libellé terminal exactement égal à « Brains » n'a été observé.
Cela ne démontre pas l'absence d'une autorité Brains dans Pactols lui-même.

## Décision de recette

- **Ne pas valider** l'alignement de l'ARK Brain vers COG 21100
  au motif de cette seule attestation.
- **Ne pas substituer automatiquement** le code 44024 à un ARK dont
  la hiérarchie désigne réellement Brain (Côte-d'Or).
- Vérifier la notice TEI d'origine, en particulier le passage auquel
  se rapporte la 4e occurrence indexée dans le paragraphe.
- Rechercher si une autorité Pactols distincte « Brains (Loire-Atlantique) »
  existe ; en cas d'erreur avérée, corriger l'indexation documentaire
  à la source, conserver la trace de correction, puis régénérer l'export.
- Ne pas supprimer l'autorité Brain dans l'absolu : seule **son
  attestation dans cette notice** est suspecte.

Ce dossier constitue un cas d'école pour un contrôle de cohérence fondé
sur **l'ensemble des localisations d'une notice**, plutôt que sur
le seul couple nom/département de chaque concept pris isolément.
