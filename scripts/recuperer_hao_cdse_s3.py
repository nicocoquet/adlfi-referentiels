#!/usr/bin/env python3
"""Préparer ou télécharger localement cinq assets de Hao via CDSE S3.

Le mode par défaut est un inventaire hors réseau S3. Le téléchargement nécessite
--download et des clés CDSE exportées dans l'environnement local. Ne jamais
transmettre ces clés à GitHub Actions, à une PR ou au chat.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from inventorier_assets_hao_sentinel2 import ITEM_ID, ITEM_URL, get_json

BANDS=("B02_10m","B03_10m","B04_10m","B08_10m","SCL_20m")
ENDPOINT="https://eodata.dataspace.copernicus.eu"
BUCKET="eodata"
# Ne pas lancer de transfert potentiellement énorme sans plafond explicite.
DEFAULT_MAX_BYTES=1_000_000_000

def validate_asset(asset, name):
    href=asset.get("href")
    if not isinstance(href,str):raise ValueError("URI manquante pour "+name)
    uri=urlparse(href)
    if uri.scheme!="s3" or uri.netloc!=BUCKET or not uri.path.startswith("/Sentinel-2/"):
        raise ValueError("Emplacement CDSE S3 inattendu pour "+name)
    if uri.query or uri.fragment or ".." in Path(uri.path).parts or not uri.path.endswith(".jp2"):
        raise ValueError("Chemin S3 inattendu pour "+name)
    if f"/{ITEM_ID}.SAFE/" not in uri.path and f"/{ITEM_ID}/" not in uri.path:
        # La structure effective du chemin SAFE doit impérativement démontrer
        # l'identité du produit téléchargé, non se fier au seul nom de bande.
        raise ValueError("Chemin S3 non rattaché au produit cible pour "+name)
    return uri.path.lstrip("/")

def plan(item):
    if item.get("id")!=ITEM_ID or item.get("collection")!="sentinel-2-l2a":
        raise ValueError("Produit STAC différent")
    assets=item.get("assets") or {}
    return {name:validate_asset(assets[name],name) for name in BANDS}

def sha256_file(path):
    digest=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            digest.update(chunk)
    return digest.hexdigest()

def boto_client():
    # Paramètres à renseigner uniquement dans le terminal local.
    access=os.environ.get("CDSE_S3_ACCESS_KEY")
    secret=os.environ.get("CDSE_S3_SECRET_KEY")
    if not access or not secret:
        raise RuntimeError("Définir CDSE_S3_ACCESS_KEY et CDSE_S3_SECRET_KEY localement")
    import boto3
    from botocore.config import Config
    return boto3.client(
        "s3",endpoint_url=ENDPOINT,
        aws_access_key_id=access,aws_secret_access_key=secret,
        config=Config(signature_version="s3v4",retries={"max_attempts":3}),
    )

def transfer(client, key, target, max_bytes):
    response=client.head_object(Bucket=BUCKET,Key=key)
    size=int(response["ContentLength"])
    if size<=0 or size>max_bytes:
        raise ValueError("Taille asset hors plafond (octets): "+str(size))
    if target.exists():
        raise FileExistsError("Refus d'écraser "+target.name)
    tmp=target.with_name(target.name+".part")
    if tmp.exists():
        raise FileExistsError("Téléchargement partiel préexistant : "+tmp.name)
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        client.download_file(BUCKET,key,str(tmp))
        if tmp.stat().st_size!=size:
            raise IOError("Taille du fichier local différente de l'asset annoncé")
        os.replace(tmp,target)
    finally:
        if tmp.exists():tmp.unlink()
    return {
        "nom_local":target.name,
        "taille_octets":size,
        "sha256":sha256_file(target),
        "etablissement_source":"CDSE_S3_AUTHENTIFIE",
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--destination",type=Path,required=True)
    p.add_argument("--download",action="store_true",
                   help="Télécharger les 5 JP2, après saisie locale des clés S3 CDSE")
    p.add_argument("--max-bytes-par-fichier",type=int,default=DEFAULT_MAX_BYTES)
    args=p.parse_args()
    if args.max_bytes_par_fichier<=0:raise ValueError("Plafond positif requis")
    destination=args.destination.expanduser().resolve()
    # Garde contre une publication accidentelle dans le dépôt Git.
    if "docs" in destination.parts or any((parent/".git").exists() for parent in (destination,*destination.parents)):
        raise ValueError("Choisir un dossier de données hors du dépôt et hors docs")
    item=get_json(ITEM_URL)
    keys=plan(item)
    if not args.download:
        print(json.dumps({
            "produit":ITEM_ID,"mode":"PREPARATION_SEULEMENT",
            "bandes":list(keys),"fichiers_attendus":[name+".jp2" for name in BANDS],
            "aucun_pixel_telecharge":True,
            "prochaine_etape":"--download avec identifiants locaux CDSE",
        },ensure_ascii=False,sort_keys=True,indent=2))
        return
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError("Répertoire de destination non vide, aucun écrasement")
    client=boto_client()
    reports={}
    for band,key in keys.items():
        reports[band]=transfer(client,key,destination/(band+".jp2"),args.max_bytes_par_fichier)
        print("CDSE_ASSET_ACQUIS",band,reports[band]["taille_octets"],reports[band]["sha256"])
    manifest={
        "schema":"adlfi.lieux.hao.sentinel2.acquisition.locale.v1",
        "produit":ITEM_ID,"item_url":ITEM_URL,
        "mode":"TELECHARGEMENT_S3_AUTHENTIFIE",
        "fichiers":reports,
        "verification_georeferencement":"NON_REALISEE",
        "publication":{"raster":0,"contours":0,"autorites":0,"ark":0},
    }
    (destination/"manifest-local.json").write_text(
        json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":main()
