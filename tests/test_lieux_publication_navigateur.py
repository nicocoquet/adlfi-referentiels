#!/usr/bin/env python3
"""Parcours de non-régression du Lieux AdlFI publié avec Playwright/Chromium."""
import contextlib
import functools
import http.server
import os
import re
import shutil
import socketserver
import threading
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None  # Tests navigateur exécutés dans un environnement dédié

ROOT=Path(__file__).resolve().parents[1] / "docs"


@contextlib.contextmanager
def site_local():
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address=True
    with Server(("127.0.0.1",0),handler) as server:
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:yield "http://127.0.0.1:"+str(server.server_address[1])
        finally:
            server.shutdown()
            thread.join(timeout=5)


def main():
    if sync_playwright is None:
        raise RuntimeError('Exécuter la recette navigateur après installation de Playwright')
    binary=next((shutil.which(s) for s in ("google-chrome","chromium","chromium-browser") if shutil.which(s)),None)
    with site_local() as base, sync_playwright() as playwright:
        kw={"headless":True,"args":["--no-sandbox"]}
        if binary:kw["executable_path"]=binary
        browser=playwright.chromium.launch(**kw)
        page=browser.new_page(viewport={"width":1400,"height":900})
        failures=[]
        page.on("pageerror",lambda error:failures.append(str(error)))
        page.goto(base+"/lieux/",wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function(
          "() => document.querySelector('#map-status')?.textContent.includes('13 contours régionaux')",
          timeout=60000
        )
        assert page.locator("#year").input_value()=="2016"
        assert page.locator("#year").get_attribute("type")=="range"
        assert page.locator("#year-label").text_content()=="2016"
        assert page.locator("#level").input_value()=="region"
        assert page.evaluate("typeof L")=="object"
        assert page.locator(".leaflet-tile-pane").count()==1

        page.locator("#zoom").select_option("bfc")
        assert page.locator("#year").input_value()=="2016"
        assert page.locator("#level").input_value()=="region"
        page.locator("#year-prev").click()
        page.wait_for_function(
          "() => document.querySelector('#map-status')?.textContent.includes('22 contours régionaux')",
          timeout=30000
        )
        assert page.locator("#year").input_value()=="2015"
        assert page.locator("#year-label").text_content()=="2015"
        page.locator("#year-next").click()
        page.wait_for_function(
          "() => document.querySelector('#map-status')?.textContent.includes('13 contours régionaux')",
          timeout=30000
        )
        assert page.locator("#year-label").text_content()=="2016"
        page.locator("#year-prev").click()
        page.wait_for_function(
          "() => document.querySelector('#map-status')?.textContent.includes('22 contours régionaux')",
          timeout=30000
        )
        page.locator("#level").select_option("departement")
        page.wait_for_function(
          "() => document.querySelector('#map-status')?.textContent.includes('96 contours départementaux')",
          timeout=30000
        )

        page.locator("#search").fill("Bourgogne")
        page.locator("#results button").first.wait_for(timeout=15000)
        page.locator("#results button").first.click()
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Édition IGN')",
          timeout=30000
        )

        page.locator("#search").fill("26678/pcrt3pvNQUYc80")
        page.locator("#results button").first.wait_for(timeout=15000)
        page.locator("#results button").first.click()
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Correspondance Pactols')",
          timeout=30000
        )
        assert page.locator("#level").input_value()=="commune"
        assert page.locator("#detail").get_by_text("2026 seulement",exact=False).count()>=1

        # La frise doit conserver la commune sélectionnée quand la date change.
        page.locator("#year-next").click()
        page.wait_for_function(
          "() => document.querySelector('#year-label')?.textContent === '2016'",
          timeout=30000
        )
        assert page.locator("#detail").get_by_text("Correspondance Pactols",exact=False).count()>=1
        page.locator("#year-now").click()
        page.wait_for_function(
          "() => document.querySelector('#year-label')?.textContent === '2026' && "
          "document.querySelector('#map-status')?.textContent.includes('contours communaux 2026')",
          timeout=60000
        )
        assert page.locator("#year-now").is_disabled()
        assert page.locator("#detail").get_by_text("Correspondance Pactols",exact=False).count()>=1

        page.goto(base+"/lieux/chronologie/?region=bfc&annee=2015&code=25368",wait_until="domcontentloaded")
        page.wait_for_url(re.compile(r"/lieux/\?"),timeout=30000)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('25368')",
          timeout=60000
        )
        assert page.locator("#zoom").input_value()=="bfc"
        assert page.locator("#year").input_value()=="2015"
        assert page.locator("#year-label").text_content()=="2015"
        assert page.locator("#level").input_value()=="commune"
        assert not failures,failures
        page.screenshot(path=os.environ.get("ADLFI_CAPTURE","/tmp/lieux-publication.png"),full_page=True)
        print("PUBLICATION LIEUX : navigateur Leaflet, 13/22/96 états, Pactols et redirection OK")
        browser.close()


if __name__=="__main__":
    main()
