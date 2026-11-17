#!/usr/bin/env python3
"""Confronter les 179 unités GEO PF/ISPF par clés de géographie, jamais par nom.

Le nombre identique d'objets entre sources ne démontre PAS une indépendance
cartographique : ces fichiers peuvent dériver d'une base institutionnelle commune.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile
from inspecter_nomenclature_geographique_ispf import read_xlsx
from qualifier_communes_associees_ispf import SHA as XLSX_SHA, rows, normaliser
from inventorier_geopf_polynesie import audit as audit_geopf

GEO_PF_SHA = "29230c18487385f84ca480e9b2c921ea389f848663a4a9574e77b9cbbf40db7b"
CHAMPS = {
    "IDGeo": "code_geogr",
    "IDIle": "id_ile",
    "IDComas": "code_com_1",
    "IDCom": "code_commu",
    "IDSub": "code_subdi",
}
NOMS = {"Geo": "nom_geogra", "Ile": "nom", "Comas": "nom_commun"}
# La correspondance des champs lexicaux est exploratoire et peut différer
# selon la signification des colonnes : elle ne valide aucun identifiant.

def code(value, width=None):
    if value is None or isinstance(value, bool):
        raise ValueError("Code manquant")
    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError("Code fractionnaire")
        value=int(value)
    s=str(value).strip()
    if not s.isascii() or not s.isdecimal():
        raise ValueError("Code non numérique : "+s)
    return s.zfill(width) if width else str(int(s))

def lire_geopf(archive: Path):
    import shapefile
    with ZipFile(archive) as z:
        names = z.namelist()
        candidates = [name for name in names if name.lower().endswith(".shp")]
        if len(candidates) != 1:
            raise ValueError("Attendu : un shapefile GEO PF")
        shp = candidates[0]
        stem = shp[:-4]
        def lire(ext):
            matches=[name for name in names if name.casefold()==(stem+ext).casefold()]
            if len(matches)!=1:
                raise ValueError("Composant shapefile manquant : "+ext)
            return io.BytesIO(z.read(matches[0]))
        with shapefile.Reader(shp=lire(".shp"),shx=lire(".shx"),dbf=lire(".dbf"),
                              encoding="utf-8",encodingErrors="replace") as shpfile:
            return [sr.record.as_dict() for sr in shpfile.iterShapeRecords()]

def qualifier(xlsx: Path, archive: Path):
    if hashlib.sha256(xlsx.read_bytes()).hexdigest()!=XLSX_SHA:
        raise ValueError("SHA du classeur ISPF non conforme")
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=GEO_PF_SHA:
        raise ValueError("SHA de l'archive GEO PF non conforme")
    sheets={s["feuille"]:s for s in read_xlsx(xlsx)}
    if "Geo" not in sheets: raise ValueError("Feuille Geo ISPF absente")
    expected=rows(sheets["Geo"])
    observed=lire_geopf(archive)
    if len(expected)!=179 or len(observed)!=179:
        raise ValueError("Cardinalité de géographie altérée")

    def indexer(items, field, width):
        by_id={};duplicates=[]
        for row in items:
            raw=row.get(field)
            try: k=code(raw,width)
            except ValueError as err:
                duplicates.append({"raw":str(raw),"motif":str(err)})
                continue
            if k in by_id: duplicates.append({"code":k,"motif":"doublon"})
            else: by_id[k]=row
        return by_id,duplicates

    xls,dx=indexer(expected,"IDGeo",5)
    shp,ds=indexer(observed,"code_geogr",5)
    missing=sorted(set(xls)-set(shp))
    extra=sorted(set(shp)-set(xls))
    mismatches=[];lexical=[]
    for ident in sorted(set(xls)&set(shp)):
        x= xls[ident]; y=shp[ident]
        for field in ("IDIle","IDComas","IDCom","IDSub"):
            name=CHAMPS[field]
            width=3 if field=="IDComas" else 2 if field=="IDCom" else None
            try:
                left=code(x[field],width);right=code(y.get(name),width)
                if left!=right:
                    mismatches.append({"IDGeo":ident,"champ":field,
                                       "ispf":left,"geopf":right})
            except ValueError as err:
                mismatches.append({"IDGeo":ident,"champ":field,"erreur":str(err)})
        for col,other in NOMS.items():
            # Les colonnes de dénomination peuvent désigner des niveaux
            # différents ; ces écarts sont seulement des alertes lexicales.
            if x.get(col) and y.get(other) and normaliser(str(x[col]))!=normaliser(str(y[other])):
                lexical.append({"IDGeo":ident,"champ":col,
                                "ispf":x[col],"geopf":str(y[other])})
    return {
        "schema":"adlfi.lieux.polynesie.geopf.ispf.jointures.geo.audit.v1",
        "statut":"RECETTE_NON_VALIDANTE",
        "source_xlsx_sha256":XLSX_SHA,
        "source_geopf_sha256":GEO_PF_SHA,
        "nombre_xlsx":len(expected),"nombre_geopf":len(observed),
        "codes_IDGeo_communs":len(set(xls)&set(shp)),
        "codes_absents_geopf":missing,"codes_supplementaires_geopf":extra,
        "doublons_ou_codes_invalides_xlsx":dx,
        "doublons_ou_codes_invalides_geopf":ds,
        "divergences_identifiants_hierarchiques":mismatches,
        "variantes_lexicales_exploratoires":lexical,
        "independance_des_geometries":"NON_ETABLIE",
        "comparaison_de_polygones":"NON_REALISEE",
        "publication":{"contours":0,"ark":0,"autorites":0},
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xlsx",type=Path,required=True)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--sortie",type=Path,required=True)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Recette hors docs, sans écrasement")
    report=qualifier(a.xlsx,a.archive)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(report,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GEO_PF_ISPF_CLES",json.dumps({
        "communs":report["codes_IDGeo_communs"],
        "absents":report["codes_absents_geopf"],
        "extras":report["codes_supplementaires_geopf"],
        "doublons_geopf":report["doublons_ou_codes_invalides_geopf"],
        "divergences_hierarchiques":report["divergences_identifiants_hierarchiques"][:30],
        "nombre_divergences_hierarchiques":len(report["divergences_identifiants_hierarchiques"]),
        "nombre_variantes_lexicales":len(report["variantes_lexicales_exploratoires"])
    },sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
