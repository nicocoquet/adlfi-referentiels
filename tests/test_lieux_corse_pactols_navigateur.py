"""Recette du module Lieux corse dans Chromium : recherche, fiche, chronologie."""
from __future__ import annotations
import functools,http.server,threading
from contextlib import contextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"docs"

@contextmanager
def serveur():
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
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1280,"height":900})
        page.goto(url+"/lieux/?region=corse&code=2A001&annee=2026&niveau=commune",
                  wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('contours communaux 2026')",
            timeout=60000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('26678/pcrtgs2LLPYow2')",
            timeout=30000)
        fich=page.locator("#detail").text_content()
        assert "Afa" in fich and "Correspondance Pactols–COG" in fich
        assert "2026 seulement" in fich
        assert page.locator('#detail a[href="https://ark.frantiq.fr/ark:/26678/pcrtgs2LLPYow2"]').count()==1
        assert page.locator(".leaflet-overlay-pane canvas").count()==1

        page.locator('#search-tool').evaluate("(el) => { el.open = true; }")
        page.locator('#search').fill("26678/pcrtgs2LLPYow2")
        page.wait_for_function("() => !document.querySelector('#results')?.hidden")
        hits=page.locator("#results").text_content()
        assert "Afa" in hits and "Pactols validé en 2026" in hits,hits
        page.locator("#year").evaluate("(el) => { el.value='1975'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
        page.locator("#year").dispatch_event("change")
        page.wait_for_function("() => document.querySelector('#year-label')?.textContent.includes('1975')")
        assert "2026 seulement" in page.locator("#detail").text_content()
        assert "Aucun état COM attesté" in page.locator("#detail").text_content()
        assert page.locator(".leaflet-overlay-pane canvas").count()==1
        print("CORSE_360_NAVIGATEUR_OK — ARK affiché et recherché, sans attribution rétroactive")
        browser.close()
if __name__=="__main__":main()
