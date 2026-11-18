#!/usr/bin/env python3
"""Correspondance éditoriale indirecte Abriès-Ristolas au COG 2026.

Pactols exactMatch -> Wikidata Q57664391 (P374=05001, P571=2019), vérifié
séparément par le COG/Insee. Ne crée PAS d'exactMatch Pactols->Insee absent.
L'ancienne commune Abriès et Ristolas conservent leurs ARK respectifs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from auditer_paca_abries_ristolas_2026 import (
    SCHEMA as AUDIT_SCHEMA, NEW, OLD, NEW_LABEL, OLD_LABEL, COG, audit_cog,
    RDF_SHA,
)

SCHEMA="adlfi.lieux.pactols.paca.abries_ristolas.editorial.2026.public.v1"
WIKIDATA="https://www.wikidata.org/wiki/Q57664391"
WIKIDATA_REVISION="https://www.wikidata.org/w/index.php?title=Q57664391&oldid=2563106214"
INSEE_CURRENT="https://www.insee.fr/fr/metadonnees/geographie/commune/05001-abries-ristolas"
INSEE_DELEGATED="https://www.insee.fr/fr/metadonnees/geographie/commune-deleguee/05001-abries"
ARRETE="https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000038316958"
PARENT="https://ark.frantiq.fr/ark:/26678/pcrthvHLIWAcHD"
RISTOLAS_ARK="26678/pcrt2YWpB2NDPZ"
RISTOLAS_WIKIDATA="https://www.wikidata.org/wiki/Q624317"
ABRIES_WIKIDATA="https://www.wikidata.org/wiki/Q331508"

def construire(audit:dict,pilote:dict,complement:dict,renommages:dict,nouvelles:dict,cog:dict)->dict:
    if (audit.get("schema")!=AUDIT_SCHEMA or audit.get("statut")!="RECETTE_NON_VALIDANTE"
        or audit.get("sources",{}).get("pactols_RDF",{}).get("sha256")!=RDF_SHA
        or audit.get("bilan",{}).get("concepts_RDF_examines")!=50556
        or audit.get("bilan",{}).get("prefLabel_actuel_unique") is not True
        or audit.get("bilan",{}).get("exactMatch_INSEE_nouveau")!=0
        or audit.get("bilan",{}).get("nouveaux_ARK_valides")!=0
        or audit.get("bilan",{}).get("communes_PACA_alignees_avant")!=945):
        raise ValueError("Audit du concept actuel absent ou altéré")
    admin=audit["administratif"]
    expected=audit_cog(cog,nouvelles)
    if admin!=expected or admin["sources_officielles"]!={ 
        "insee_2026":INSEE_CURRENT,
        "insee_commune_deleguee":INSEE_DELEGATED,
        "arrete_creation_2018":ARRETE}:
        raise ValueError("Preuve COG officielle de 2019 altérée")
    rdf=audit["rdf"]
    newer=rdf["concept_actuel"]
    older=rdf["concept_ancienne_commune"]
    other=next((x for x in rdf["autres_concepts_lexicaux"] if
                x["ark_pactols"]==RISTOLAS_ARK),None)
    if not other or len(rdf["autres_concepts_lexicaux"])!=1:
        raise ValueError("Identification de Ristolas non univoque")
    def french(obj,field="prefLabel"):
        return [x["value"] for x in obj["skos_literals"][field] if x["lang"]=="fr"]
    if (newer["ark_pactols"]!=NEW or newer["rdf_type"]!=[
            "http://www.w3.org/2004/02/skos/core#Concept"]
        or french(newer)!=[NEW_LABEL] or newer["exactMatch_INSEE"] or
        newer["skos_relations"]["exactMatch"]!=[WIKIDATA] or
        newer["deprecated"] or newer["dct_relations"]["isReplacedBy"] or
        newer["owl_sameAs"] or
        newer["skos_relations"]["broader"]!=[PARENT] or
        older["ark_pactols"]!=OLD or french(older)!=[OLD_LABEL] or
        older["exactMatch_INSEE"]!=["http://id.insee.fr/geo/commune/05001"] or
        ABRIES_WIKIDATA not in older["skos_relations"]["exactMatch"] or
        other["skos_relations"]["broader"]!=[PARENT] or
        RISTOLAS_WIKIDATA not in other["skos_relations"]["exactMatch"] or
        other["exactMatch_INSEE"]!=["http://id.insee.fr/geo/commune/05120"]):
        raise ValueError("Contradiction dans les trois concepts Pactols")
    definitions=french(newer,"definition")
    if (len(definitions)!=1 or not all(
        part in definitions[0] for part in
        ("Abriès-Ristolas","commune nouvelle","1er janvier 2019","Abriès","Ristolas","Hautes-Alpes"))):
        raise ValueError("La définition Pactols ne décrit plus la fusion de 2019")
    if (nouvelles.get("schema")!="adlfi.lieux.pactols.paca.sept_communes_nouvelles.2026.public.v1" or
        nouvelles.get("alignements_total_PACA_2026")!=945 or
        nouvelles.get("exceptions_restantes")!=["05001"] or
        len(nouvelles["alignements_Pactols_COG_valides_2026"])!=7 or
        renommages.get("schema")!="adlfi.lieux.pactols.paca.renommages.2026.public.v2" or
        len(renommages["alignements_Pactols_COG_valides_2026"])!=3 or
        complement.get("schema")!="adlfi.lieux.pactols.paca.complement.2026.public.v1" or
        len(complement["alignements_Pactols_COG_valides_2026"])!=832 or
        len(pilote.get("autorites",[]))!=103):
        raise ValueError("945 correspondances PACA préexistantes modifiées")
    keys=set()
    arks=set()
    for item in pilote["autorites"]:
        code=item["correspondances"][0]["code_insee"]
        ark=item["ark_pactols"]
        if code in keys or ark in arks:
            raise ValueError("Pilote PACA non unique")
        keys.add(code);arks.add(ark)
    for source in (complement,renommages,nouvelles):
        for item in source["alignements_Pactols_COG_valides_2026"]:
            code=item["code_insee"]
            ark=item["ark_pactols"]
            if code in keys or ark in arks:
                raise ValueError("Doublon des alignements PACA antérieurs")
            keys.add(code);arks.add(ark)
    if len(keys)!=945 or len(arks)!=945 or COG in keys or NEW in arks or OLD in arks:
        raise ValueError("La dernière exception PACA n'est plus Abriès-Ristolas")
    if (nouvelles["ARK_anciens_concepts_non_promus"].count(OLD)!=1 or
        RISTOLAS_ARK in arks):
        raise ValueError("Identités historiques altérées")
    return {
      "schema":SCHEMA,
      "region":"paca","millesime_cog":"2026-01-01",
      "preuve":"CONVERGENCE_EDITORIALE_PACTOLS_WIKIDATA_INSEE_COG",
      "predicat_Pactols":"skos:exactMatch",
      "cible_Pactols_Wikidata":WIKIDATA,
      "Wikidata_revision_verifiee":WIKIDATA_REVISION,
      "propriete_Wikidata_code_INSEE":"P374",
      "valeur_Wikidata_P374":"05001",
      "propriete_Wikidata_creation":"P571",
      "valeur_Wikidata_P571":"2019-01-01",
      "information_Wikidata_non_autorite_INSEE":True,
      "source_INSEE_courante":INSEE_CURRENT,
      "source_INSEE_commune_deleguee":INSEE_DELEGATED,
      "source_arrete_creation":ARRETE,
      "source_audit_RDF":"recette/lieux/PACA-ABRIES-RISTOLAS-AUDIT-2026.json",
      "source_RDF_sha256":RDF_SHA,
      "alignements_pilote_conserves":103,
      "alignements_exactMatch_direct_conserves":832,
      "renommages_conserves":3,
      "communes_nouvelles_explicites_conservees":7,
      "nouvelles_validations_editoriales":1,
      "total_PACA_alignements_2026":946,
      "communes_PACA_COG_2026":946,
      "exceptions_restantes":[],
      "geometries_ajoutees":0,
      "relations_historiques_inferrees":0,
      "alignements_Pactols_COG_valides_2026":[{
        "code_insee":COG,
        "libelle_COG_2026":NEW_LABEL,
        "ark_pactols":NEW,
        "libelle_pactols":NEW_LABEL,
        "date_creation_commune_nouvelle":"2019-01-01",
        "ancienne_commune_code_conserve":OLD_LABEL,
        "ark_ancienne_commune_distinct":OLD,
        "ark_ancienne_Ristolas_distinct":RISTOLAS_ARK,
        "uri_cog_insee":"http://id.insee.fr/geo/commune/05001",
        "uri_insee_exactMatch_direct_pactols":None,
        "uri_exactMatch_pactols_wikidata":WIKIDATA,
        "code_insee_wikidata":"05001",
        "source_INSEE":INSEE_CURRENT,
        "source_fusion_COG":ARRETE,
        "source_audit_RDF":"recette/lieux/PACA-ABRIES-RISTOLAS-AUDIT-2026.json",
        "source_RDF_sha256":RDF_SHA,
        "millesime_validation":2026,
        "date_validation":"2026-11-18",
        "statut":"correspondance_editoriale_indirecte_validee_PACA_2026",
        "type_validation":"Pactols_exactMatch_Wikidata_INSEE_COG_et_fusion_2019",
        "portee_chronologique":"2026_SEULEMENT",
      }]
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("audit","pilote","complement","renommages","nouvelles","cog","sortie"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie neuve en recette seulement")
    load=lambda p:json.loads(p.read_text(encoding="utf-8"))
    d=construire(load(a.audit),load(a.pilote),load(a.complement),load(a.renommages),
                load(a.nouvelles),load(a.cog))
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(d,ensure_ascii=False,separators=(",",":"),sort_keys=True)+"\n",
                        encoding="utf-8")
    print("PACA_ABRIES_RISTOLAS_EDITORIAL_VALIDATION",json.dumps({
        "ajouts":1,"PACA_total":946,"exceptions":0,"source_indirecte":"Wikidata P374 corroborée INSEE",
        "geometries":0
    },ensure_ascii=False))
if __name__=="__main__":main()
