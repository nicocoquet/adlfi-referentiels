# Pays de la Loire — préqualification du lot 02 : 54 collisions Pactols–COG encore ouvertes

**Recette non validante, 18 novembre 2026**. État de départ : **1 149 / 1 228** correspondances publiées ; **79 exceptions**, dont 54 codes associés à plusieurs ARK Pactols.

Le script `scripts/prequalifier_pdl_lot02_2026.py` repart des sources Pactols RDF th17 épinglées et COG INSEE 2026, puis soustrait **les six codes déjà publiés** (lot 01 de cinq communes nouvelles et Chemillé-en-Anjou).

Sur les 54 cas résiduels, la classification préalable distingue :
- **49** collisions avec un seul libellé courant compatible (ne constituent pas des validations) ;
- **3** créations administratives successives : Baugé-en-Anjou, Ingrandes-le-Fresne-sur-Loire, Montsûrs ;
- **2** cas avec intitulé explicitement historique : Le Lion-d'Angers et Le Lude.

Pour attribuer le statut `CANDIDAT_LOT02_A_VERIFIER`, on exige simultanément : exactement deux ARK concurrents ; un seul ARK de libellé principal courant strict ; un seul ARK au libellé de l'ancienne commune ; `exactMatch` vers le code INSEE actuel et aucune autre URI INSEE pour **les deux concepts** ; absence de dépréciation/remplacement ; un seul événement de création MOD32 ; un mouvement COG de l'ancienne commune **COM vers COMD** conservant le même code ; et une période COM actuelle dont le début coïncide avec l'événement.

Tous les autres cas sont placés en `INSTRUCTION_COMPLEMENTAIRE`, avec la liste motivée des vérifications bloquantes. Les critères stricts peuvent produire des faux négatifs : ce triage cherche surtout à **éviter les faux positifs**. Même les candidats sans anomalie doivent être validés éditorialement avant toute nouvelle publication.

**Aucun lien, aucune géométrie, aucune relation historique inférée** par cette recette. Rapports JSON reproductibles dans les artefacts GitHub Actions. La prochaine PR de publication, si le rapport est favorable, pourra porter sur un lot homogène sans refaire l'instruction des trois créations successives ni des deux cas à statuts historiques ambigus.

La refonte de l'interface graphique du référentiel Lieux est prévue **après la consolidation Pays de la Loire**, sur la base des idées qui seront transmises par l'éditeur ; aucun arbitrage d'interface n'est effectué ici.
