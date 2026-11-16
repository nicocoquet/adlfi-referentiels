#!/usr/bin/env python3
"""Assembler la carte BFC autonome pour revue locale, sans publication Pages."""
import argparse
import hashlib
import json
from pathlib import Path

def assembler(modele:Path, dossier:Path, sortie:Path):
    a=json.loads((dossier/"regions-2015-bfc.geojson").read_text(encoding="utf8"))
    b=json.loads((dossier/"regions-2016-bfc.geojson").read_text(encoding="utf8"))
    rapport=json.loads((dossier/"rapport-geometries-bfc.json").read_text(encoding="utf8"))
    if (len(a["features"]),len(b["features"]))!=(2,1):
        raise ValueError("Le pilote doit avoir deux régions en 2015 et une en 2016")
    if {f["properties"]["code_region"] for f in a["features"]}!={"26","43"}:
        raise ValueError("Les régions anciennes sont erronées")
    if {f["properties"]["code_region"] for f in b["features"]}!={"27"}:
        raise ValueError("Le successeur régional est erroné")
    if any(f["properties"]["millesime_geometrie"]!=int(y) for y,geo in (("2015",a),("2016",b)) for f in geo["features"]):
        raise ValueError("Géométries de millésime incorrect")
    if rapport["nombre_geometries_historiques_inferrees"]!=0 or rapport["nombre_nouveaux_alignements_pactols"]!=0:
        raise ValueError("Veto : inférence géométrique ou alignement non validé")
    template=Path(modele).read_text(encoding="utf8")
    if template.count("__BFC_INLINE_DATA__")!=1:
        raise ValueError("Point d'injection unique requis")
    data=json.dumps({"2015":a,"2016":b},ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
    html=template.replace("__BFC_INLINE_DATA__",data)
    if "https://tile.openstreetmap.org/" in html:
        raise ValueError("Ce pilote doit fonctionner en HTML autonome")
    sortie=Path(sortie)
    if "docs" in sortie.resolve().parts:raise ValueError("Refus de publication dans Pages")
    sortie.parent.mkdir(parents=True,exist_ok=True)
    sortie.write_text(html,encoding="utf8")
    return {"chemin":str(sortie),"octets":sortie.stat().st_size,
            "sha256":hashlib.sha256(sortie.read_bytes()).hexdigest(),"contours":3}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("modele","dossier","sortie"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(assembler(**vars(a)),ensure_ascii=False,indent=2))
