#!/usr/bin/env python3
"""Audit historique COG des 103 validations PACA et 7 candidatures.

La portée de validation des 103 correspondances est le millésime COG 2026.
Aucun état COG antérieur, aucun mouvement MOD et aucune géométrie actuelle
n'est élevé par ce script en identité historique Pactols–COG validée.

Sorties hors docs/ : préinstruction seulement, décisions historiques vides.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

try:
    from preparer_index_cog_national_temporel import SOURCES as COG_SHA
except ImportError:
    from scripts.preparer_index_cog_national_temporel import SOURCES as COG_SHA

REGION="93"
DEPARTEMENTS={"04","05","06","13","83","84"}
HISTORIC_SOURCE_COMMIT="bc0455c7d1dbf65f579e9b25a01eb7928a8054d5"
HISTORIC_SOURCE_BLOB="8d039fe574413df89524b39540ba962ce89ca0a0"
MOD_FIELDS=("MOD","DATE_EFF","TYPECOM_AV","COM_AV","TNCC_AV","NCC_AV",
            "NCCENR_AV","LIBELLE_AV","TYPECOM_AP","COM_AP","TNCC_AP",
            "NCC_AP","NCCENR_AP","LIBELLE_AP")
CANDIDATE_HEADER=("ark_pactols","libelle_pactols","code_cog_propose",
                  "libelle_cog_propose","statut_source","origine_github_commit",
                  "etat_decision_parite","decision_editoriale","justification",
                  "verificateur","date_validation")

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_csv(path, names, sep=","):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f,delimiter=sep)
        if not set(names).issubset(rd.fieldnames or ()):
            raise ValueError("Colonnes absentes : "+str(path))
        return list(rd)

def ecrire_csv(path, rows, header):
    with Path(path).open("w",encoding="utf-8-sig",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=header,delimiter=";",lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)

def charger_valides(pilote):
    data=json.loads(Path(pilote).read_text(encoding="utf-8"))
    if (data.get("schema_version")!="0.1.0" or data.get("perimetre")!="PACA"
            or data.get("totaux",{}).get("autorites_pactols")!=103):
        raise ValueError("Pilote de publication PACA inattendu")
    if data.get("provenance",{}).get("autorites",{}).get("git_blob_sha")!=HISTORIC_SOURCE_BLOB:
        raise ValueError("Provenance de la table éditoriale PACA modifiée")
    out=[]
    for a in data["autorites"]:
        links=a.get("correspondances",[])
        if len(links)!=1:raise ValueError("Correspondance PACA non unique")
        link=links[0]
        if (link.get("validation",{}).get("statut")!="VALIDE_EDITEUR_2026_10_18"
            or link.get("validation",{}).get("date")!="2026-10-18"
            or link.get("millesime_cog")!=2026
            or link.get("relation_editoriale")!="correspondance_communale_validee"):
            raise ValueError("Validation PACA 2026 de provenance ambiguë")
        out.append({
            "ark_pactols":a["ark_pactols"],
            "libelle_pactols":a["libelle_pactols"],
            "code_cog_propose":link["code_insee"],
            "libelle_cog_propose":link["libelle_cog"],
            "statut_initial":"valide_editeur_2026-10-18",
            "validation_millesime_2026":"valide_et_conservee",
            "source_documentaire":link["validation"]["source"],
        })
    if len(out)!=103 or len({r["ark_pactols"] for r in out})!=103:
        raise ValueError("103 ARK validés attendus")
    if len({r["code_cog_propose"] for r in out})!=103:
        raise ValueError("Collisions inattendues entre 103 codes publiés")
    return out

def charger_candidats(path):
    rows=read_csv(path,CANDIDATE_HEADER,sep=";")
    if len(rows)!=7:raise ValueError("Sept dossiers PACA non validés attendus")
    out=[]
    for row in rows:
        if (row["origine_github_commit"]!=HISTORIC_SOURCE_COMMIT
            or row["statut_source"]!="REVU_EDITEUR_A_DOCUMENTER"
            or row["etat_decision_parite"]!="candidat_non_valide"
            or any(row[k] for k in ("decision_editoriale","justification",
                                    "verificateur","date_validation"))):
            raise ValueError("Candidate déjà décidée, invalide ou provenance absente")
        out.append({
            "ark_pactols":row["ark_pactols"],"libelle_pactols":row["libelle_pactols"],
            "code_cog_propose":row["code_cog_propose"],
            "libelle_cog_propose":row["libelle_cog_propose"],
            "statut_initial":"revu_editeur_a_documenter",
            "validation_millesime_2026":"non_valide",
            "source_documentaire":"atlas-documentaire@"+HISTORIC_SOURCE_COMMIT+
                                   ": experimentation/donnees/autorite_pactols_insee.csv",
        })
    if {r["code_cog_propose"] for r in out}!={"13028","83069","06159","13056","06029","06088","13055"}:
        raise ValueError("Codes des sept candidats modifiés")
    return out

def mouvement_id(r):
    raw=json.dumps({key:r[key] for key in MOD_FIELDS},
                   ensure_ascii=False,sort_keys=True,separators=(",",":"))
    return "mvt:"+hashlib.sha256((raw+"\n").encode()).hexdigest()[:24]

def regroupement_evenement(mouvement):
    """Un groupe de lignes COG, pas nécessairement un acte juridique unique.

    Pour une création d'arrondissements municipaux (MOD20), grouper les
    lignes de Marseille sous la commune d'origine, sans créer seize
    changements successifs d'identité communale.
    """
    m=mouvement
    if m["MOD"]=="20" and m["typecom_avant"]=="COM" and m["typecom_apres"]=="ARM":
        porteur=m["code_avant"]
        type_pivot="commune_source_arrondissements"
    else:
        porteur=m["code_apres"] or m["code_avant"]
        type_pivot="code_receveur"
    if not porteur:
        raise ValueError("Mouvement sans commune de référence")
    return (f"PACA-COG-{m['date_effet']}-{m['MOD']}-{porteur}",
            porteur,type_pivot)


def construire(pilote,candidats,courant,historique,mouvements,sortie,
               controle_sources=True):
    paths={"courant":Path(courant),"historique":Path(historique),
           "mouvements":Path(mouvements)}
    if controle_sources:
        for role,path in paths.items():
            if sha256(path)!=COG_SHA[role]:
                raise ValueError("Empreinte COG 2026 incorrecte : "+role)
    records=charger_valides(pilote)+charger_candidats(candidats)
    if len(records)!=110 or len({r["ark_pactols"] for r in records})!=110:
        raise ValueError("110 autorités PACA distinctes attendues")
    codes={r["code_cog_propose"] for r in records}
    if len(codes)!=110:
        raise ValueError("Un code COG proposé plusieurs fois : arbitrage nécessaire")
    current={r["COM"]:r for r in read_csv(courant,("TYPECOM","COM","REG","DEP","LIBELLE"))
             if r["COM"] in codes and r["TYPECOM"]=="COM"}
    if len(current)!=110 or any(r["REG"]!=REGION or r["DEP"] not in DEPARTEMENTS
                                for r in current.values()):
        raise ValueError("Code communal du lot hors région PACA ou absent du COG2026")
    per=collections.defaultdict(list)
    for r in read_csv(historique,("TYPECOM","COM","LIBELLE","DATE_DEBUT","DATE_FIN")):
        if r["TYPECOM"]=="COM" and r["COM"] in codes:
            per[r["COM"]].append(r)
    mouv=collections.defaultdict(list)
    unique={}
    for r in read_csv(mouvements,MOD_FIELDS):
        affected={r["COM_AV"],r["COM_AP"]}&codes
        if not affected:continue
        mid=mouvement_id(r)
        event={"id":mid,"date_effet":r["DATE_EFF"],"MOD":r["MOD"],
               "typecom_avant":r["TYPECOM_AV"],"code_avant":r["COM_AV"],
               "libelle_avant":r["LIBELLE_AV"],"typecom_apres":r["TYPECOM_AP"],
               "code_apres":r["COM_AP"],"libelle_apres":r["LIBELLE_AP"],
               "source":"Insee COG 2026 v_mvt_commune_2026.csv"}
        if mid in unique and unique[mid]!=event:
            raise ValueError("Identifiant de mouvement contradictoire")
        unique[mid]=event
        for c in affected:
            mouv[c].append(mid)
    groupes=collections.defaultdict(list)
    groupe_info={}
    groupes_par_code=collections.defaultdict(set)
    for event in unique.values():
        eid,pivot,typ=regroupement_evenement(event)
        groupes[eid].append(event["id"])
        if eid in groupe_info and groupe_info[eid]!=(event["date_effet"],event["MOD"],pivot,typ):
            raise ValueError("Groupe COG administratif incohérent")
        groupe_info[eid]=(event["date_effet"],event["MOD"],pivot,typ)
    for code,ids in mouv.items():
        groupes_par_code[code]={regroupement_evenement(unique[mid])[0] for mid in ids}
    out=[]
    for r in records:
        code=r["code_cog_propose"]
        states=sorted(per[code],key=lambda x:(x["DATE_DEBUT"],x["DATE_FIN"],x["LIBELLE"]))
        if not states:raise ValueError("Code sans période COM : "+code)
        opened=[x for x in states if not x["DATE_FIN"]]
        if len(opened)!=1 or opened[0]["LIBELLE"]!=current[code]["LIBELLE"]:
            raise ValueError("État COG courant non cohérent avec série historique : "+code)
        for before,after in zip(states,states[1:]):
            if before["DATE_FIN"] and before["DATE_FIN"]>after["DATE_DEBUT"]:
                raise ValueError("Périodes COM chevauchantes : "+code)
        mod=sorted({unique[mid]["MOD"] for mid in mouv[code]})
        labels=sorted({p["LIBELLE"] for p in states})
        row={**r,
             "code_insee":code,
             "libelle_cog_2026":current[code]["LIBELLE"],
             "departement_cog_2026":current[code]["DEP"],
             "typecom_cog_2026":"COM",
             "nombre_periodes_com":len(states),
             "formes_com_historiques":" | ".join(labels),
             "nombre_mouvements_lies":len(set(mouv[code])),
             "nombre_groupes_evenements_lies":len(groupes_par_code[code]),
             "ids_groupes_evenements":" | ".join(sorted(groupes_par_code[code])),
             "modalites_cog":" | ".join(mod),
             "presence_changement_nom_ou_identite": "oui" if len(labels)>1 else "non",
             "presence_mouvement_fusion":"oui" if set(mod)&{"31","32","33","34","35"} else "non",
             "preuve_annee_mouvement":" | ".join(sorted(
                  {unique[mid]["date_effet"] for mid in mouv[code]})),
             "portee_alignement":"millesime_2026_uniquement",
             "etat_audit_historique":"preuves_COG_rassemblees_relation_non_revalidee",
             "decision_historique":"","justification_decision":"",
             "verificateur":"","date_validation":"",
             "geometrie_historique_attribuee":"non"}
        out.append(row)
    out.sort(key=lambda r:(r["validation_millesime_2026"]!="non_valide",
                           -r["nombre_mouvements_lies"],
                           r["libelle_pactols"].casefold(),r["ark_pactols"]))
    summary={
      "schema":"adlfi.lieux.paca.historique.recette.v1",
      "statut":"recette_non_publiable",
      "paca_autorites_du_pilote_2026":110,
      "alignements_2026_deja_valides_conserves":103,
      "candidatures_2026_non_validees":7,
      "autres_lignes_de_la_source_editoriale_initiale":108,
      "codes_communes_actuelles_concernes":len(codes),
      "periodes_COM_liees":sum(len(per[code]) for code in codes),
      "mouvements_COG_uniques_lies":len(unique),
      "groupes_evenements_COG_uniques_lies":len(groupes),
      "autorites_avec_plusieurs_formes_COM":sum(r["presence_changement_nom_ou_identite"]=="oui" for r in out),
      "autorites_avec_mouvement_fusion":sum(r["presence_mouvement_fusion"]=="oui" for r in out),
      "candidatures_avec_mouvements":sum(r["validation_millesime_2026"]=="non_valide" and r["nombre_mouvements_lies"]>0 for r in out),
      "statut_audit":"préinstruction, non validation historique de l'ARK",
      "nouvelles_validations":0,
      "geometries_historiques":0,
      "completude_regionale":"non_etablie_liste_originale_nationale_non_exhaustive",
      "provenance":{
         "pilote_publie":"docs/data/lieux.json",
         "source_editoriale_originale":"atlas-documentaire:"+HISTORIC_SOURCE_COMMIT,
         "source_editoriale_blob_git":HISTORIC_SOURCE_BLOB,
         "source_sept_candidatures":str(candidats),
         "cog_2026_SHA256":{key:sha256(path) for key,path in paths.items()}
      }
    }
    target=Path(sortie)
    target.mkdir(parents=True,exist_ok=True)
    headers=list(out[0])
    ecrire_csv(target/"PACA-110-REVUE-HISTORIQUE.csv",out,headers)
    movements_out=sorted(unique.values(),key=lambda r:(r["date_effet"],r["id"]))
    ecrire_csv(target/"PACA-MOUVEMENTS-COG.csv",movements_out,list(movements_out[0]) if movements_out else ["id"])
    grouped=[]
    for ident,ids in sorted(groupes.items()):
        d,mod,pivot,pivot_type=groupe_info[ident]
        grouped.append({"id_evenement":ident,"date_effet":d,"MOD":mod,
                        "code_regroupement":pivot,"mode_regroupement":pivot_type,
                        "nombre_lignes_COG":len(ids),
                        "ids_mouvements":" | ".join(sorted(ids)),
                        "statut":"observation_COG_non_validation_Pactols"})
    grouped.sort(key=lambda x:(x["date_effet"],x["MOD"],x["code_regroupement"]))
    ecrire_csv(target/"PACA-EVENEMENTS-COG.csv",grouped,list(grouped[0]))
    (target/"PACA-RAPPORT-AUDIT.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return summary

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ("pilote","candidats","courant","historique","mouvements","sortie"):
        parser.add_argument("--"+arg,type=Path,required=True)
    opts=parser.parse_args()
    print(json.dumps(construire(**vars(opts)),ensure_ascii=False,indent=2))
