#!/usr/bin/env python3
"""Inspecter sans publication une archive GEOFLA Guyane 2015 issue d'un miroir tiers.

L'analyse inventorie les objets, identifiants et géométries, puis confronte
les contours à une couche nationale 2026 de référence. Aucune forme GEOFLA,
différence de polygones ou frontière reconstituée n'est exportée.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import re
from pathlib import Path

SCHEMA="adlfi.lieux.guyane.geofla2015.audit-source.v1"
ARCHIVE_NAME="GEOFLA_2-1_COMMUNE_SHP_UTM22RGFG95_D973_2015-12-01.rar"
SOURCE_TIERS_SHA="3aac9e8b979118b25df48e9ef21fc1029d735cc3c99a025cd1f5688560f41298"
SHA_NATIONAL="4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"


def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconnaitre_code(attributes:dict)->tuple[str|None,str|None]:
    """Ne jamais déduire un code depuis un nom ou une position géométrique."""
    possibilities=[]
    normalized={str(k).upper():str(v).strip() for k,v in attributes.items()}
    for field in ("CODE_INSEE","INSEE_COM","INSEE","INSEE_COM1","CODE_COM",
                  "INSEE_COMM","CODEINSEE","COD_INSEE","INSEE_C"):
        val=normalized.get(field)
        if val and re.fullmatch(r"973\d\d",val):
            possibilities.append((field,val))
    codes={code for _,code in possibilities}
    if len(codes)==1:
        return possibilities[0][1],possibilities[0][0]
    return None,None


def lire_geojson(path:Path,codes:set[str])->dict:
    from shapely.geometry import shape
    from shapely.ops import transform
    from pyproj import Transformer
    opener=gzip.open if path.suffix==".gz" else open
    with opener(path,"rt",encoding="utf-8") as fh:
        doc=json.load(fh)
    if doc.get("type")!="FeatureCollection":
        raise ValueError("Source nationale non GeoJSON FeatureCollection")
    proj=Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True)
    bycode=collections.defaultdict(list)
    for f in doc.get("features",[]):
        code=str(f.get("properties",{}).get("code",""))
        if code in codes:
            g=shape(f.get("geometry"))
            bycode[code].append(transform(proj.transform,g))
    return bycode


def comparer_geometries(a,b)->dict:
    """Mesures sur copies dans la projection équivalente EPSG:6933."""
    if a.is_empty or b.is_empty or not a.is_valid or not b.is_valid:
        raise ValueError("Géométrie non valide pour une comparaison fiable")
    intersection=a.intersection(b).area
    union=a.union(b).area
    source_area=a.area
    reference_area=b.area
    return {
        "source2015_km2":round(source_area/1e6,6),
        "national2026_km2":round(reference_area/1e6,6),
        "difference_symetrique_km2":round(a.symmetric_difference(b).area/1e6,6),
        "source2015_hors_2026_km2":round(a.difference(b).area/1e6,6),
        "national2026_hors_2015_km2":round(b.difference(a).area/1e6,6),
        "jaccard_pct":round(intersection/union*100,6) if union else None,
    }



def decomposer_ecarts_cartographiques(source:dict, reference:dict,
                                       focus:tuple[str,...]=("97301","97312","97303"))->dict:
    """Décomposer des différences *de dessin*, pas des mutations juridiques.

    2015 et 2026 sont des partitions surfaciques potentiellement généralisées.
    Dans leur emprise commune : A_i ∩ B_j, i != j, est une différence de
    classement cartographique (ce n'est PAS un transfert administratif).
    Aux marges : A \ B et B \ A sont des différences de contour extérieur.
    """
    from shapely.ops import unary_union

    if set(source)!=set(reference) or len(source)!=22:
        raise ValueError("Partitions comparées incomplètes ou hétérogènes")
    if not set(focus).issubset(source):
        raise ValueError("Commune prioritaire absente des géométries")

    for obj in [*source.values(),*reference.values()]:
        if obj.is_empty or not obj.is_valid or obj.area<=0:
            raise ValueError("Géométrie non valide pour une partition")
    ua=unary_union(list(source.values()))
    ub=unary_union(list(reference.values()))
    if not ua.is_valid or not ub.is_valid:
        raise ValueError("Union de communes invalide")

    # Vérifier qu'une commune ne recouvre pas une autre du même millésime.
    for year,features,union in (("2015",source,ua),("2026",reference,ub)):
        duplicate_area=sum(x.area for x in features.values())-union.area
        if abs(duplicate_area)>100:  # m² sur 22 géométries très généralisées
            raise ValueError("Recouvrement/géométrie incohérent pour "+year)

    km=lambda a:round(a/1e6,6)
    rows=[]
    for code in sorted(source):
        a,b=source[code],reference[code]
        marge_2015=a.difference(ub).area
        marge_2026=b.difference(ua).area
        sortant=a.intersection(ub).difference(b).area
        entrant=b.intersection(ua).difference(a).area
        total=a.symmetric_difference(b).area
        somme=marge_2015+marge_2026+sortant+entrant
        if abs(total-somme)>100:  # m²
            raise ValueError("Non fermeture du bilan géométrique : "+code)
        rows.append({
            "code":code,
            "difference_symetrique_totale_km2":km(total),
            "hors_emprise_2026_depuis_carte_2015_km2":km(marge_2015),
            "hors_emprise_2015_depuis_carte_2026_km2":km(marge_2026),
            "ecart_interne_sortant_2015_vers_autre_code_2026_km2":km(sortant),
            "ecart_interne_entrant_autre_code_2015_vers_2026_km2":km(entrant),
            "ecart_externe_total_km2":km(marge_2015+marge_2026),
            "ecart_interne_double_km2":km(sortant+entrant),
            "part_externe_pct":round((marge_2015+marge_2026)/total*100,3)
                if total else 0,
        })

    # Calculer les échanges cartographiques seulement pour les 3 cas prioritaires.
    prioritaires={}
    for code in focus:
        outgoing=[]
        incoming=[]
        for neighbor in sorted(source):
            if code==neighbor:
                continue
            a=source[code].intersection(reference[neighbor]).area
            b=source[neighbor].intersection(reference[code]).area
            if a>100:
                outgoing.append({"code_2026":neighbor,"intersection_km2":km(a)})
            if b>100:
                incoming.append({"code_2015":neighbor,"intersection_km2":km(b)})
        prioritaires[code]={
            "ecarts_de_codes_cartographiques_2015_vers_2026":
                sorted(outgoing,key=lambda x:(-x["intersection_km2"],x["code_2026"])),
            "ecarts_de_codes_cartographiques_2026_depuis_2015":
                sorted(incoming,key=lambda x:(-x["intersection_km2"],x["code_2015"])),
        }

    source_externe=sum(source[code].difference(ub).area for code in source)
    ref_externe=sum(reference[code].difference(ua).area for code in source)
    total=sum(source[code].symmetric_difference(reference[code]).area
              for code in source)
    total_internes=sum(
        source[code].intersection(ub).difference(reference[code]).area
        for code in source)
    total_entrants=sum(
        reference[code].intersection(ua).difference(source[code]).area
        for code in source)
    emprise_externe=ua.symmetric_difference(ub).area
    if (abs(total_internes-total_entrants)>100
        or abs((source_externe+ref_externe)-emprise_externe)>100
        or abs(total-(emprise_externe+total_internes+total_entrants))>100):
        raise ValueError("Non fermeture comptable des partitions spatiales")
    return {
        "statut":"DIFFERENCES_DE_CARTES_NON_JURIDIQUES",
        "decomposition_global_km2":{
            "ecart_externe_total_km2":km(emprise_externe),
            "ecart_externe_2015_hors_2026_km2":km(source_externe),
            "ecart_externe_2026_hors_2015_km2":km(ref_externe),
            "ecart_interne_unique_km2":km(total_internes),
            "ecart_interne_compte_deux_fois_km2":km(total_internes+total_entrants),
            "somme_ecarts_communaux_km2":km(total),
            "equation":"sommes communales = écart externe + 2 × écart interne, pour des partitions sans recouvrement",
        },
        "par_commune":sorted(rows,key=lambda x:(-x["difference_symetrique_totale_km2"],x["code"])),
        "priorites":prioritaires,
        "incertitudes":[
            "Une intersection de deux codes différents entre éditions n'établit aucune décision administrative.",
            "La différence d'emprise peut relever du trait de côte, de frontières externes, de précision ou de méthode.",
            "Les métriques ne contiennent aucune géométrie historique ou actuelle publiable.",
        ],
    }

def inspecter(dossier:Path,rar:Path,national:Path,sortie:Path)->dict:
    import shapefile
    from shapely.geometry import shape
    from shapely.ops import transform, unary_union
    from pyproj import CRS,Transformer,Geod
    if rar.name!=ARCHIVE_NAME:
        raise ValueError("Nom d'archive non conforme au produit attendu")
    if sha256(rar)!=SOURCE_TIERS_SHA:
        raise ValueError("La copie GEOFLA tierce ne correspond plus à l'empreinte de recette")
    if sha256(national)!=SHA_NATIONAL:
        raise ValueError("Le millésime national 2026 n'est pas celui de la recette")
    if "docs" in sortie.resolve().parts or sortie.resolve().is_relative_to(dossier.resolve()):
        raise ValueError("Rapport de recette interdit dans les sources ou le site")
    shapefiles=sorted(p for p in dossier.rglob("*") if p.is_file()
                      and p.suffix.lower()==".shp")
    communes=[p for p in shapefiles if p.stem.upper()=="COMMUNE"]
    limites=[p for p in shapefiles if p.stem.upper()=="LIMITE_COMMUNE"]
    if len(communes)!=1 or len(limites)!=1 or len(shapefiles)!=2:
        raise ValueError("Couches GEOFLA COMMUNE et LIMITE_COMMUNE non reconnues : "+
                         ", ".join(str(p.relative_to(dossier)) for p in shapefiles))
    shp=communes[0]
    prj=shp.with_suffix(".prj")
    if not prj.exists():
        raise ValueError("Projection source absente : pas de géocodage par hypothèse")
    src_crs=CRS.from_wkt(prj.read_text(encoding="utf-8",errors="replace"))
    if not src_crs.is_projected:
        raise ValueError("Source GEOFLA sans système projeté vérifiable")
    to6933=Transformer.from_crs(src_crs,"EPSG:6933",always_xy=True)
    to_geo=Transformer.from_crs(src_crs,"EPSG:4326",always_xy=True)
    ref_crs=CRS.from_epsg(2972)
    crs_equiv_2972=src_crs.equals(ref_crs,ignore_axis_order=True)
    to_geo_officiel=Transformer.from_crs(ref_crs,"EPSG:4326",always_xy=True)
    geod=Geod(ellps="WGS84")
    offsets_crs_m=[]
    source=collections.defaultdict(list)
    code_fields=collections.Counter()
    centres_wgs84=[]
    records=[]
    with shapefile.Reader(str(shp),encoding="latin-1") as shpfile:
        fields=[x[0] for x in shpfile.fields[1:]]
        for sr in shpfile.iterShapeRecords():
            attr=dict(zip(fields,list(sr.record)))
            code,field=reconnaitre_code(attr)
            if field:code_fields[field]+=1
            if code:
                original=shape(sr.shape.__geo_interface__)
                centre=original.representative_point()
                lon,lat=to_geo.transform(centre.x,centre.y)
                if not (-60<lon<-48 and 0<lat<7):
                    raise ValueError("Coordonnées projetées hors Guyane : "+code)
                centres_wgs84.append((lon,lat))
                lon_ref,lat_ref=to_geo_officiel.transform(centre.x,centre.y)
                distance=geod.inv(lon,lat,lon_ref,lat_ref)[2]
                offsets_crs_m.append(distance)
                source[code].append(transform(to6933.transform,original))
            records.append({"code_identifie":code,"champs":sorted(attr.keys())})
    cogs={code for code in source if code.startswith("973")}
    if any(code not in cogs for code in source):raise ValueError("Commune non guyanaise dans la couche")
    comparison=[]
    target=lire_geojson(national,cogs)
    for code,gs in sorted(source.items()):
        refs=target.get(code,[])
        if len(gs)!=1 or len(refs)!=1:
            comparison.append({"code":code,"statut":"AMBIGU_OU_ABSENT",
                 "nb_source":len(gs),"nb_reference":len(refs)})
            continue
        a,b=gs[0],refs[0]
        row={"code":code,"statut":"COMPARAISON_NON_VALIDANTE",
             "source_valide":a.is_valid,"reference_valide":b.is_valid,
             "mesures":None}
        if a.is_valid and b.is_valid and not a.is_empty and not b.is_empty:
            row["mesures"]=comparer_geometries(a,b)
        comparison.append(row)
    # La comparaison de l'emprise totale distingue un désaccord sur le
    # contour externe de désaccords au sein du maillage de communes.
    # Ce n'est PAS une preuve de mutation administrative : généralisation
    # et changements de sources sont des causes concurrentes.
    communs=sorted(code for code in source if len(source[code])==1
                   and len(target.get(code,[]))==1)
    source_union=unary_union([source[c][0] for c in communs])
    target_union=unary_union([target[c][0] for c in communs])
    if not (source_union.is_valid and target_union.is_valid
            and not source_union.is_empty and not target_union.is_empty):
        raise ValueError("Union des contours communaux non exploitable")
    area= lambda geom:round(geom.area/1e6,6)
    sommes_source=sum(source[c][0].area for c in communs)
    sommes_cible=sum(target[c][0].area for c in communs)
    emprise_comparaison={
        "communes_comparees":len(communs),
        "source2015_union_km2":area(source_union),
        "national2026_union_km2":area(target_union),
        "ecart_externe_symetrique_km2":area(source_union.symmetric_difference(target_union)),
        "source2015_hors_2026_union_km2":area(source_union.difference(target_union)),
        "national2026_hors_2015_union_km2":area(target_union.difference(source_union)),
        "surcomptage_surface_source2015_km2":round((sommes_source-source_union.area)/1e6,6),
        "surcomptage_surface_national2026_km2":round((sommes_cible-target_union.area)/1e6,6),
        "interpretation":"Mesures de différences de dessins/cartes, non de changements administratifs.",
    }
    for source_key in ("surcomptage_surface_source2015_km2",
                       "surcomptage_surface_national2026_km2"):
        if emprise_comparaison[source_key] < -0.000001:
            raise ValueError("Union incohérente : "+source_key)
    stats={
        "fichiers_2015":len(records),
        "codes_reconnus":len(cogs),
        "codes_cog_2026_couverts":sum(bool(target.get(code)) for code in cogs),
        "codes_avec_comparaison_valide":sum(x.get("mesures") is not None for x in comparison),
        "geometries_2015_valides":sum(g.is_valid for shapes in source.values() for g in shapes),
        "codes_2015_non_uniques":sorted(c for c,gs in source.items() if len(gs)!=1),
        "codes_2015_absents_par_rapport_2026":sorted(set(target)-set(source)),
        "emprise_collective_comparaison":emprise_comparaison,
        "ecart_cumule_des_comparaisons_par_code_km2":round(
            sum(x["mesures"]["difference_symetrique_km2"]
                for x in comparison if x.get("mesures") is not None),6),
        "geometries_source_2015_dans_le_domaine_guyane":len(centres_wgs84),
        "principaux_ecarts_km2":sorted(
            [{"code":x["code"],"ecart_km2":x["mesures"]["difference_symetrique_km2"],
              "jaccard_pct":x["mesures"]["jaccard_pct"]}
              for x in comparison if x.get("mesures") is not None],
            key=lambda x:(-x["ecart_km2"],x["code"]))[:8],
    }
    decomposition=decomposer_ecarts_cartographiques(
        {c:gs[0] for c,gs in source.items() if len(gs)==1},
        {c:target[c][0] for c in source if len(target.get(c,[]))==1}
    )
    report={
        "schema":SCHEMA,"statut":"AUDIT_SOURCE_TIERCE_NON_AUTHENTIFIEE",
        "source2015":{
            "fichier":rar.name,"source_externe":"miroir GitHub non officiel",
            "sha256":sha256(rar),
            "format":"shapefile archivé au format RAR",
            "shapefile_dans_archive":str(shp.relative_to(dossier)),
            "shapefiles_inventory": [str(p.relative_to(dossier)) for p in shapefiles],
            "couche_limite_commune_presente":True,
            "champs_attributaires":fields,
            "champ_code_detecte":dict(code_fields),
            "crs_wkt_sha256":hashlib.sha256(prj.read_bytes()).hexdigest(),
            "epsg_resolu":src_crs.to_epsg(),
            "crs_equivalent_epsg2972":crs_equiv_2972,
            "epsg2972_attendu_selon_ign":2972,
            "datum_wkt":src_crs.datum.name if src_crs.datum else None,
            "ellipsoide_wkt":src_crs.ellipsoid.name if src_crs.ellipsoid else None,
            "projection_wkt":src_crs.coordinate_operation.method_name if src_crs.coordinate_operation else None,
            "parametres_projection_wkt":[{
                "nom":p.name,"valeur":p.value,"unite":p.unit_name}
                for p in src_crs.coordinate_operation.params] if src_crs.coordinate_operation else [],
            "controle_operationnel_epsg2972":{
                "nombre_points":len(offsets_crs_m),
                "ecart_maximum_wgs84_m":round(max(offsets_crs_m),6),
                "ecart_moyen_wgs84_m":round(sum(offsets_crs_m)/len(offsets_crs_m),6),
                "interpretation":"Distance de position calculée en coordonnées WGS84, sans authentifier le CRS source.",
            },
            "centres_wgs84_plage_lons":[round(min(x for x,y in centres_wgs84),6),
                                       round(max(x for x,y in centres_wgs84),6)],
            "centres_wgs84_plage_lats":[round(min(y for x,y in centres_wgs84),6),
                                       round(max(y for x,y in centres_wgs84),6)],
            "identite_source_IGN_confirmee":False,
            "date_fichier_nom":"2015-12-01",
            "date_limites_administratives_attestee":None,
        },
        "source2026":{"sha256":sha256(national),
            "edition":"2026-05-04",
            "nature":"contours nationaux généralisés, distincts de GEOFLA"},
        "statistiques":stats,"comparaisons_par_code":comparison,
        "decomposition_ecarts_cartographiques":decomposition,
        "contours_historiques_adoptes":0,
        "geometries_publiees":0,
        "publication_possible":False,
        "avertissement":[
            "Une archive publiée par un tiers n'établit pas son identité ou intégrité vis-à-vis d'un paquet officiel IGN.",
            "La validité topologique d'un shapefile ne suffit pas à en garantir la validité juridique.",
            "Les différences de généralisation de GEOFLA et du fichier national 100 m rendent impossible la lecture des écarts comme seuls changements administratifs.",
            "La date d'édition du paquet 2015 ne prouve pas les limites en 1993 ou 1969.",
            "Aucune différence de polygones ni géométrie historique ne sont exportées.",
        ],
    }
    sortie.parent.mkdir(parents=True,exist_ok=True)
    sortie.write_text(json.dumps(report,ensure_ascii=False,
                      sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dossier",type=Path,required=True)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--national",type=Path,required=True)
    p.add_argument("--sortie",type=Path,required=True)
    a=p.parse_args()
    result=inspecter(a.dossier,a.archive,a.national,a.sortie)
    print(json.dumps({"source2015":result["source2015"],
          "statistiques":result["statistiques"],
          "publication_possible":False},ensure_ascii=False,indent=2))
