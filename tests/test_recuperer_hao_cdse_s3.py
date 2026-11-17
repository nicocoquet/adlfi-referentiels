"""Garde-fous du téléchargement CDSE de Hao, sans identifiants ni réseau."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from sys import path as syspath
syspath.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from recuperer_hao_cdse_s3 import BUCKET, ITEM_ID, BANDS, plan, validate_asset, transfer,sha256_file

def fake_assets():
    root=f"s3://eodata/Sentinel-2/MSI/L2A/2022/12/26/{ITEM_ID}.SAFE/GRANULE/G/"
    return {b:{"href":root+b+".jp2"} for b in BANDS}

class TestS3Hao(unittest.TestCase):
    def test_plan_produit_exact(self):
        item={"id":ITEM_ID,"collection":"sentinel-2-l2a","assets":fake_assets()}
        d=plan(item)
        self.assertEqual(len(d),5)
        self.assertTrue(all(v.endswith(".jp2") for v in d.values()))
        with self.assertRaises(ValueError):
            plan({"id":"INCORRECT","collection":"sentinel-2-l2a","assets":fake_assets()})

    def test_refus_chemin_externe_ou_produit_different(self):
        for uri in ("https://example.net/B02.jp2",
                    "s3://eodata/other/B02.jp2",
                    "s3://other/Sentinel-2/MSI/B02.jp2",
                    "s3://eodata/Sentinel-2/MSI/L2A/2022/12/26/OTHER.SAFE/GRANULE/G/B02.jp2",
                    f"s3://eodata/Sentinel-2/MSI/L2A/2022/12/26/{ITEM_ID}.SAFE/../B02.jp2"):
            with self.subTest(uri=uri),self.assertRaises(ValueError):
                validate_asset({"href":uri},"B02_10m")

    def test_sha256_et_transfert_synthetique(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"B02_10m.jp2"
            client=Mock()
            client.head_object.return_value={"ContentLength":5}
            client.download_file.side_effect=lambda b,k,p: Path(p).write_bytes(b"hello")
            record=transfer(client,"Sentinel-2/sample",target,100)
            self.assertEqual(record["taille_octets"],5)
            self.assertEqual(len(record["sha256"]),64)
            self.assertEqual(record["sha256"],sha256_file(target))
            self.assertEqual(client.download_file.call_args.args[0],BUCKET)
            with self.assertRaises(FileExistsError):
                transfer(client,"Sentinel-2/sample",target,100)

    def test_plafond_refuse_avant_transfert(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"too_big.jp2"
            client=Mock()
            client.head_object.return_value={"ContentLength":200}
            with self.assertRaises(ValueError):
                transfer(client,"Sentinel-2/sample",target,100)
            client.download_file.assert_not_called()
            self.assertFalse(target.exists())

if __name__=="__main__":
    unittest.main()
