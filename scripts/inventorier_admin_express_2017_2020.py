#!/usr/bin/env python3
"""Inventaire vérifiable des éditions SIG IGN pour les millésimes manquants.

N'effectue AUCUNE interpolation géométrique et n'écrit rien dans docs/.
Repère les ressources vectorielles historiques (SHP/7z) séparément des
services WMS/WMTS (rendus, pas sources polygonales brutes).
Source officielle de découverte :
https://data.geopf.fr/telechargement/resource/{product}
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

YEARS = (2017, 2020)
PRODUCTS = ("ADMIN-EXPRESS-COG", "ADMIN-EXPRESS-COG-CARTO", "ADMIN-EXPRESS")
ROOT = "https://data.geopf.fr/telechargement/resource/"
MAX_PAGES = 8
LIMIT = 50


def page(url: str, tries: int = 4) -> bytes:
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "AdlFI-Lieux-Referentiels/1.0 (edition historique et provenance)",
                "Accept": "application/atom+xml,application/xml,text/xml,*/*",
            })
            with urllib.request.urlopen(req, timeout=35) as r:
                data = r.read(8_000_000 + 1)
                if len(data) > 8_000_000:
                    raise ValueError("Atom XML inattendu (>8 Mio) : " + url)
                return data
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))
    raise RuntimeError("Échec inexpliqué : " + url)


def parse_entries(raw: bytes) -> dict:
    """Parser Atom avec espaces de noms libres, sans présupposer le vocabulaire."""
    root = ET.fromstring(raw)
    def local(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]
    entries = []
    for elem in root.iter():
        if local(elem.tag) != "entry":
            continue
        row = {"title": "", "id": "", "updated": "", "links": []}
        for child in elem:
            tag = local(child.tag)
            if tag in ("title", "id", "updated", "summary") and child.text:
                row[tag] = child.text.strip()
            if tag == "link" and child.attrib.get("href"):
                row["links"].append({"href": child.attrib["href"],
                                     "type": child.attrib.get("type", ""),
                                     "rel": child.attrib.get("rel", "")})
        entries.append(row)
    totals = []
    for elem in root.iter():
        if local(elem.tag).lower() in ("totalentries", "totalresults"):
            try:
                totals.append(int((elem.text or "0").strip()))
            except ValueError:
                pass
    return {"entries": entries, "total": max(totals) if totals else None,
            "root": local(root.tag), "bytes": len(raw)}


def inventorier() -> dict:
    report = {"schema": "adlfi.lieux.admin-express.inventaire.v1",
              "date_cog_au_premier_janvier": True,
              "projection_geometrique_retroactive": False,
              "producteur": "IGN",
              "url_api": ROOT,
              "annees": {},
              "erreurs": []}
    for year in YEARS:
        report["annees"][str(year)] = {}
        for product in PRODUCTS:
            annual = []
            all_count = None
            retrieved = []
            for n in range(1, MAX_PAGES + 1):
                query = urllib.parse.urlencode({
                    "editionDateFrom": f"{year}-01-01",
                    "editionDateTo": f"{year}-12-31",
                    "page": n, "limit": LIMIT,
                })
                url = ROOT + product + "?" + query
                try:
                    answer = parse_entries(page(url))
                    all_count = answer["total"]
                    retrieved.append({"page": n, "count": len(answer["entries"]),
                                      "root": answer["root"], "bytes": answer["bytes"]})
                    annual.extend(answer["entries"])
                    if not answer["entries"] or len(answer["entries"]) < LIMIT:
                        break
                    if all_count is not None and len(annual) >= all_count:
                        break
                except Exception as exc:
                    report["erreurs"].append({
                        "annee": year, "produit": product, "page": n,
                        "erreur": type(exc).__name__ + ": " + str(exc),
                    })
                    break
            unique = {}
            for entry in annual:
                key = entry["id"] or entry["title"] or json.dumps(entry, sort_keys=True)
                unique[key] = entry
            rows = list(unique.values())
            candidats = [r for r in rows if re.search(rf"(^|[^0-9]){year}([^0-9]|$)",
                r["title"] + " " + r["id"] + " " +
                " ".join(l["href"] for l in r["links"]))]
            subresources = []
            # Les dossiers Atom ne sont pas eux-mêmes les archives téléchargeables.
            # Lire l'étage inférieur pour vérifier les .7z, tailles et liens.
            for e in candidats[:5]:
                url = next((l["href"] for l in e["links"]
                            if l.get("type") == "application/atom+xml"), e["id"])
                if not url.startswith(ROOT):
                    raise ValueError("Lien d'archive hors du service IGN officiel")
                try:
                    sub = parse_entries(page(url + "?page=1&limit=50"))
                    subresources.append({"dossier":e["title"],"url":url,
                                         "entries":sub["entries"],"nombre":len(sub["entries"]),
                                         "total":sub["total"]})
                except Exception as exc:
                    report["erreurs"].append({"annee":year,"produit":product,
                                               "sous_dossier":e["title"],
                                               "erreur":type(exc).__name__+": "+str(exc)})
            report["annees"][str(year)][product] = {
                "url": ROOT + product,
                "total_annonce": all_count, "pages": retrieved,
                "entrees": rows[:160],
                "candidats_annee": candidats[:100],
                "fichiers_dossiers": subresources,
            }
            print(f"{year} {product}: {len(rows)} entries, {len(candidats)} candidat(s), total={all_count}",
                  flush=True)
            for e in candidats[:7]:
                print(" ", e["title"][:180], e["id"][:200], flush=True)
            for sub in subresources:
                for file in sub["entries"][:9]:
                    print("  FICHIER:",file["title"][:150],file["id"][:250],flush=True)
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sortie", type=Path, required=True)
    args = p.parse_args()
    if "docs" in args.sortie.resolve().parts or args.sortie.exists():
        raise ValueError("Sortie documentaire de recette existante ou située dans docs/")
    result = inventorier()
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+"\n",
                           encoding="utf-8")
    print("Erreur(s) accès IGN:",len(result["erreurs"]))
