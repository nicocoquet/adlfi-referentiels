# Normandie — préflight Pactols–COG 2026 et occurrences AdlFI

**19 novembre 2026 — première tranche non publiante.** Suivi : [#152](https://github.com/nicocoquet/adlfi-referentiels/issues/152).

## 1. Périmètre documentaire validé (exports AdlFI)

Les deux fichiers CSV transmis à l'équipe pour le présent audit ne sont **pas déposés dans le dépôt public**. Leur contenu a été vérifié en lecture seule, avec séparateur `;`, et les comptages des autorités concordent avec leurs occurrences.

- `autorites_lieux.csv` : **9 928** autorités, SHA-256 `878aa70f32d43313ea5bd36bbb30bbd6b57b4872ba2f68a5117ac6c35b6380b6`.
- `occurrences_lieux.csv` : **30 772** occurrences, SHA-256 `b2e7332515c051e0c63e1fb29c840fa338aa85040fb2358a7df64d735b2942cd`.
- Pour **Normandie**, après `France métropolitaine` dans `chaine_libelles_fr` : **1 220 autorités terminales distinctes**, **3 656 occurrences**, **2 470 notices distinctes** et cinq départements.
- Profondeur du terminal *après l'étiquette régionale* (autorités distinctes) : profondeur 0 = **1** (région), profondeur 1 = **5** (départements), profondeur 2 = **1 038**, profondeur 3 = **175**, profondeur 4 = **1**. La profondeur 3 présente notamment d'anciens noms de communes dans les hiérarchies de communes nouvelles ; **la profondeur ne constitue pas une preuve de statut juridique**.
- Occurrences rattachées à ces profondeurs : 0 = **4**, 1 = **37**, 2 = **3 254**, 3 = **360**, 4 = **1**.

Le rattachement à la Normandie est une **assertion documentaire de hiérarchie Pactols**, non une validation COG 2026. Les identifiants de notices, chemins de fichiers et ARK individuels ne sont pas reproduits ici.

## 2. Audit officiel reproductible à exécuter

Le script `scripts/auditer_pactols_cog_region_metropolitaine_2026.py` réutilise le parseur RDF et la règle de préflight déjà validés dans les audits régionaux. Ses deux sources externes sont épinglées :

- COG Insee **2026**, `v_commune_2026.csv` SHA-256 `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3` ;
- RDF Pactols **22 juillet 2026**, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.

Filtre COG : `TYPECOM=COM` et `REG=28`, exclusivement. Aucune commune déléguée (`COMD`), associée (`COMA`) ou arrondissement (`ARM`) n'est promu en commune autonome.

Le rapport qualifie chaque code en : `ELIGIBLE_SELON_REGLE`, `A_INSTRUIRE_PLUSIEURS_ARK`, `A_INSTRUIRE_LIBELLE_STATUT_OU_URI` ou `SANS_EXACTMATCH`. Ce sont des **statuts de préflight**, **pas des validations éditoriales**. Aucune correspondance ni géométrie nouvelle n'est publiée.

Exécution reproductible (sources préalablement téléchargées et contrôlées) :

```bash
python3 scripts/auditer_pactols_cog_region_metropolitaine_2026.py \
  --region 28 --rdf /chemin/source/Pactols_Lieux_th17_20260722.rdf \
  --cog /chemin/source/v_commune_2026.csv \
  --sortie /tmp/audit-normandie-2026.json
```

Le workflow de recette télécharge les sources publiques vérifiées, exécute le même audit **deux fois**, compare les fichiers octet à octet et conserve les preuves dans un artefact GitHub Actions à durée limitée. Les premiers **effectifs COG et RDF doivent être lus dans le résultat réellement exécuté**, sans chiffre supposé.

## 3. Croisement facultatif avec les deux fichiers AdlFI locaux

L'option `--autorites ... --occurrences ... --sortie-corpus ...` calcule uniquement des **agrégats** des ARK terminaux normands, par statut du lien Pactols–COG 2026 : univoque éligible, lien explicite à instruire, ou pas de lien direct à une **commune actuelle de la région** dans le RDF épinglé.

Ce dernier statut **ne signifie pas** que l'ARK serait absent de Pactols ou erroné : une autorité peut correspondre à une ancienne commune, une subdivision ou une autre catégorie géographique.

Les fichiers AdlFI demeurent hors du dépôt, hors de l'exécution CI et hors des sorties de synthèse publiques. Aucune identité ancienne, relation de succession ni géométrie historique n'est inférée.

## 4. Étapes après le préflight

1. Examiner et chiffrer les exceptions du RDF Normandie.
2. Croiser les ARK terminaux des notices avec les codes COG normands et hiérarchiser les exceptions **selon leur fréquence documentaire**.
3. Mettre en place le chargeur de géométries progressif décrit dans #152, avec tests de rendu Chromium.
4. Publier les correspondances 2026 admissibles et les contours contemporains dans des PR distinctes, sans confondre identité et emprise administrative.
