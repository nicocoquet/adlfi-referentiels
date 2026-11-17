"""Tests de non-régression du fond Leaflet sur la branche courante.

Test du comportement en cas de tuiles OSM bloquées sans prétendre que
les tuiles en production sont indisponibles.
"""
from __future__ import annotations
import functools,http.server,threading
from contextlib import contextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"docs"

@contextmanager
def site():
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:"+str(server.server_address[1])
    finally:
        server.shutdown()
        server.server_close()

def main():
    from playwright.sync_api import sync_playwright
    with site() as base,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1200,"height":850})
        # Bloquer uniquement les tuiles, pas Leaflet ni les données locales.
        page.route("https://tile.openstreetmap.org/**",lambda route:route.abort())
        page.goto(base+"/lieux/",wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('18 contours régionaux')",
            timeout=60000)
        page.wait_for_function(
            "() => document.querySelector('#osm-status')?.hidden===false",
            timeout=30000)
        msg=page.locator("#osm-status").text_content()
        assert "fond OpenStreetMap ne se charge pas" in msg,msg
        assert page.locator(".leaflet-tile-pane").count()==1
        assert page.locator(".leaflet-overlay-pane canvas").count()==1
        print("OSM_ERREUR_TUILES_SIGNALEE_SANS_PERTE_DES_CONTOURS — OK")
        browser.close()
if __name__=="__main__":main()
