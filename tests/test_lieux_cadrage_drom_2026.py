"""Les cadrages de la carte incluent tous les polygones DROM publiés."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "docs/assets/lieux-multiechelon.js"
GEOM = ROOT / "docs/data/lieux-outremer/contours-communes-drom-2026.geojson"


def fenetre(zone, code):
    exp = re.search(r"\b"+re.escape(zone)+r":\[\[([-\d.]+),([-\d.]+)\],\[([-\d.]+),([-\d.]+)\]\]", code)
    if exp is None:
        raise ValueError("Cadrage absent : "+zone)
    return tuple(map(float, exp.groups()))


def sommets(coords):
    if not coords:
        return
    if isinstance(coords[0], (int, float)):
        yield coords[:2]
    else:
        for v in coords:
            yield from sommets(v)


class TestCadrageOutremer(unittest.TestCase):
    def test_cadrages_contiennent_les_cinq_drom(self):
        code = UI.read_text(encoding="utf-8")
        fc = json.loads(GEOM.read_text(encoding="utf-8"))
        self.assertEqual(len(fc["features"]),129)
        antilles=fenetre("antilles",code)
        indien=fenetre("indien",code)
        checked={}
        for f in fc["features"]:
            c=f["properties"]["code"]
            pre=c[:3]
            west = pre in ("971","972","973")
            bounds=antilles if west else indien
            minlat,minlon,maxlat,maxlon=bounds
            self.assertLess(minlat,maxlat)
            self.assertLess(minlon,maxlon)
            n=0
            for lon,lat in sommets(f["geometry"]["coordinates"]):
                self.assertGreaterEqual(lon,minlon,c)
                self.assertLessEqual(lon,maxlon,c)
                self.assertGreaterEqual(lat,minlat,c)
                self.assertLessEqual(lat,maxlat,c)
                n+=1
            self.assertGreater(n,0,c)
            checked[pre]=checked.get(pre,0)+1
        self.assertEqual(checked,{"971":32,"972":34,"973":22,"974":24,"976":17})
        # Zone des îles du Nord — borne cartographique utile au zoom Antilles,
        # sans leur inventer ici un contour communal.
        self.assertGreaterEqual(antilles[2],18.3)

if __name__=="__main__":
    unittest.main()
