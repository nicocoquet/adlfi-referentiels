#!/usr/bin/env python3
"""Nouvelle-Calédonie : 33 communes COG ≠ 3 provinces statutaires.

Vérifie les épisodes COG originaux (6 CSV Insee SHA-256), distingue
le décret de création juridique de Kouaoua 25 avril 1995 d'une date
de première attestation du couple code-libellé COG ; inventorie les
relatons 2026 des 3 provinces et la bipartition de Poya (98827).
L'inventaire ne produit NI contour, NI ARK, NI effet rétroactif.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path
from auditer_cog_polynesie_2026 import SHAS,read,sha,episode

PROVINCES={
 "NORD":{
  "libelle":"Province Nord",
  "communes_entieres":["98801","98804","98807","98808","98810","98811",
       "98812","98819","98822","98823","98824","98825","98826","98830",
       "98831","98833"],
  "communes_partielles":["98827"]},
 "SUD":{
  "libelle":"Province Sud",
  "communes_entieres":["98802","98803","98805","98806","98809","98813",
       "98816","98817","98818","98821","98828","98829","98832"],
  "communes_partielles":["98827"]},
 "ILES-LOYAUTE":{
  "libelle":"Province des îles Loyauté",
  "communes_entieres":["98814","98815","98820"],
  "communes_partielles":[]}
}
LEGAL={
 "source_provinces":"https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000020960246",
 "source_codification":"https://www.insee.fr/fr/information/7929495",
 "source_kouaoua":"https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000000534060",
 "date_decret_kouaoua":"1995-04-25",
 "code_commune_origine":"98804",
 "code_commune_creee":"98833",
 "source_provinces_1988":"Loi n° 88-1028 du 9 novembre 1988",
 "creation_provinces_1989_documentaire":True,
 "limites_provinciales_spatiales_verifiees":False
}

def liste_publique(index:Path)->tuple[dict[str,str],dict]:
 d=json.loads(index.read_text(encoding="utf-8"))
 if (d.get("schema")!="adlfi.lieux.recherche.outremer.public.v1" or
     len(d.get("pactols_valides",{}))!=176 or
     len(d.get("pactols_collectivites_valides",{}))!=4 or
     d.get("contours_invalides")!=["98745","98805"] or
     len(d.get("autres",[]))!=21):
  raise ValueError("Socle éditorial ultramarin incompatible")
 pairs=[row.split("|",1) for row in d["communes"]["988"].splitlines()]
 if (len(pairs)!=33 or any(len(p)!=2 for p in pairs) or
     len(set(p[0] for p in pairs))!=33):
  raise ValueError("33 codes communaux COG 988 attendus")
 actual=dict(pairs)
 if set(actual)!={f"988{x:02d}" for x in range(1,34)}:
  raise ValueError("Codes 98801–98833 incomplets")
 if "988" in d["pactols_collectivites_valides"] or any(
     x.startswith("988") for x in d["pactols_valides"]):
  raise ValueError("Les ARK 988 doivent être instruits séparément")
 return actual,d

def verifier_provinces(communes:dict[str,str])->tuple[list[dict],list[dict]]:
 if len(PROVINCES)!=3:raise ValueError("Trois provinces attendues")
 rel=[]
 for key,p in PROVINCES.items():
  for code in p["communes_entieres"]:
   rel.append({"province_id":"NC:PROVINCE:"+key,
    "province_libelle":p["libelle"],"commune_code_COG":code,
    "commune_libelle_COG":communes[code],
    "type_rattachement":"COMMUNE_ENTIERE"})
  for code in p["communes_partielles"]:
   rel.append({"province_id":"NC:PROVINCE:"+key,
    "province_libelle":p["libelle"],"commune_code_COG":code,
    "commune_libelle_COG":communes[code],
    "type_rattachement":"PARTIE_DE_COMMUNE",
    "partie_de_commune":"nord" if key=="NORD" else "sud"})
 allcodes=collections.Counter(r["commune_code_COG"] for r in rel)
 if (len(rel)!=34 or set(allcodes)!=set(communes) or
     {c:n for c,n in allcodes.items() if n>1}!={"98827":2} or
     sorted([r["province_id"] for r in rel if r["commune_code_COG"]=="98827"])!=
      ["NC:PROVINCE:NORD","NC:PROVINCE:SUD"] or
     len([r for r in rel if r["type_rattachement"]=="PARTIE_DE_COMMUNE"])!=2):
  raise ValueError("Poya appartient à deux provinces : 34 liens obligatoires")
 if (sorted(len(p["communes_entieres"]) for p in PROVINCES.values())!=[3,13,16]
     or len(PROVINCES["NORD"]["communes_partielles"])!=1
     or len(PROVINCES["SUD"]["communes_partielles"])!=1):
  raise ValueError("Répartition 16 Nord + 13 Sud + 3 Îles, et Poya nord/sud")
 return sorted(rel,key=lambda x:(x["commune_code_COG"],x["province_id"])),[
  {"id":"NC:PROVINCE:"+code,"libelle":p["libelle"],
   "communes_entieres":len(p["communes_entieres"]),
   "parties_de_communes":len(p["communes_partielles"])}
  for code,p in PROVINCES.items()]

def analyser(folder:Path,index:Path)->dict:
 for name,digest in SHAS.items():
  if sha(folder/name)!=digest:
   raise ValueError("Source COG originale différente SHA256 : "+name)
 raw={name:read(folder/name) for name in SHAS}
 communes,d=liste_publique(index)
 rows=[r for r in raw["v_commune_comer_2026.csv"] if r["COMER"]=="988"]
 current={r["COM_COMER"]:r["LIBELLE"] for r in rows if r["NATURE_ZONAGE"]=="COM"}
 if (current!=communes or len(rows)!=33 or
     any(r["NATURE_ZONAGE"]!="COM" for r in rows)):
  raise ValueError("33 communes COG 988 différentes du référentiel public")
 territories=[r for r in raw["v_comer_2026.csv"] if r["COMER"]=="988"]
 if len(territories)!=1 or territories[0]["LIBELLE"]!="Nouvelle-Calédonie":
  raise ValueError("Statut territorial COG 988 différent")
 if any(r["COM"].startswith("988") for r in raw["v_commune_2026.csv"]
        ) or any(r["COM"].startswith("988") for r in raw["v_commune_depuis_1943.csv"]):
  raise ValueError("Commune COG 988 anormalement répertoriée comme DROM")
 hist=[episode(r,"COM_COMER","COMMUNE_HISTORIQUE_COMER")
  for r in raw["v_commune_outremer_depuis_1943.csv"]
  if r["COM_COMER"] in communes]
 extras=[episode(r,"COM_COMER","AUTRE_ZONAGE_988_A_QUALIFIER")
  for r in raw["v_commune_outremer_depuis_1943.csv"]
  if r["COM_COMER"].startswith("988") and r["COM_COMER"] not in communes]
 terrhist=[episode(r,"COMER","TERRITOIRE_COG")
  for r in raw["v_tom_depuis_1943.csv"] if r["COMER"]=="988"]
 if {r["code"] for r in hist}!=set(communes) or not terrhist:
  raise ValueError("Épisodes COG historiques 988 manquants")
 if any(r["nature_zonage_COG"]!="COM" for r in hist):
  raise ValueError("Un zonage historique 988 n'est pas une commune COM")
 # Les dates historiques ne sont pas devinées ici. Inspection du rapport
 # avant toute publication des périodes sur le site.
 rel,provinces=verifier_provinces(communes)
 dates=collections.Counter(x["debut_inclus"] for x in hist)
 episodes_par_code=collections.Counter(x["code"] for x in hist)
 return {
  "schema":"adlfi.lieux.nouvelle-caledonie.audit.cog-provinces2026.v1",
  "statut":"PREINSTRUCTION_HISTORIQUE_NON_VALIDANTE",
  "source_COG":{"url":"https://www.insee.fr/fr/information/8740222",
        "sha256":SHAS,"edition":"2026-01-01"},
  "sources_juridiques":LEGAL,
  "territoire_2026":{"code":"988","libelle":"Nouvelle-Calédonie",
    "statut":"COLLECTIVITE_A_STATUT_PARTICULIER_NON_COM_ART74"},
  "communes_actuelles":[{"code":code,"libelle":nom,
     "nature_zonage_COG":"COM"} for code,nom in sorted(communes.items())],
  "episodes_communes_COG":sorted(hist,
    key=lambda x:(x["code"],x["debut_inclus"])),
  "episodes_territoire_COG":sorted(terrhist,
    key=lambda x:(x["code"],x["debut_inclus"])),
  "autres_codes_historiques_988_a_instruire":sorted(extras,
    key=lambda x:(x["code"],x["debut_inclus"])),
  "provinces_2026":provinces,
  "relations_commune_province_2026":rel,
  "dates_debut_episodes_COG":dict(sorted(dates.items())),
  "episodes_par_commune":dict(sorted(episodes_par_code.items())),
  "controle":{
    "communes_COG_2026":33,"provinces":3,
    "communes_entieres_Nord":16,"communes_entieres_Sud":13,
    "communes_entieres_Iles_Loyaute":3,
    "communes_a_deux_provinces":["98827"],
    "nombre_relations_province_commune":34,
    "nombre_episodes_communes_COG":len(hist),
    "nombre_episodes_territoire_COG":len(terrhist),
    "codes_historiques_non_courants":len(extras),
    "Poya_parts_geom_non_homologuees":2,
    "contour_Dumbea_98805_invalide_non_homologue":True,
    "alignements_Pactols_communes_conserves":176,
    "alignements_Pactols_collectivites_conserves":4,
    "nouveaux_ARK":0,"nouvelles_geometries":0,
    "dates_creation_juridique_issues_seulement_COG":0,
    "identites_historiques_inferrees":0,
    "publication_docs":False
  }
 }
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ("sources","index-public","sortie"):
  p.add_argument("--"+key,type=Path,required=True)
 a=p.parse_args()
 if "docs" in a.sortie.resolve().parts or a.sortie.exists():
  raise ValueError("Sortie d'audit sous docs/ ou existante interdite")
 d=analyser(a.sources,getattr(a,"index_public"))
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
  encoding="utf-8")
 print("CALEDONIE_2026_BILAN",
       json.dumps(d["controle"],ensure_ascii=False,sort_keys=True))
 print("CALEDONIE_2026_DATES_COG",
       json.dumps(d["dates_debut_episodes_COG"],ensure_ascii=False,sort_keys=True))
 print("CALEDONIE_2026_KOUAOUA",json.dumps([
  x for x in d["episodes_communes_COG"] if x["code"]=="98833"],
  ensure_ascii=False))
 print("CALEDONIE_2026_CANALA",json.dumps([
  x for x in d["episodes_communes_COG"] if x["code"]=="98804"],
  ensure_ascii=False))
 print("CALEDONIE_2026_TERRITOIRE",
       json.dumps(d["episodes_territoire_COG"],ensure_ascii=False))
 print("CALEDONIE_2026_AUTRES_HISTORIQUES",
       json.dumps(d["autres_codes_historiques_988_a_instruire"],ensure_ascii=False))
if __name__=="__main__":main()
