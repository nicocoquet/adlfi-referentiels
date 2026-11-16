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



def inspecter_contours(page, attendu, capture):
    details=page.evaluate("""() => {
      const map=document.getElementById('map');
      const canvases=[...document.querySelectorAll('.leaflet-overlay-pane canvas')];
      return {
        map_status:document.getElementById('map-status').textContent,
        map_rect:map.getBoundingClientRect().toJSON(),
        canvas_count:canvases.length,
        canvases:canvases.map(c=>{
          const ctx=c.getContext('2d');
          const d=ctx.getImageData(0,0,c.width,c.height).data;
          let pixels=0;
          for(let i=3;i<d.length;i+=4){if(d[i]>0)pixels++;}
          return {width:c.width,height:c.height,drawn_pixels:pixels,css:c.getAttribute('style')};
        })
      };
    }""")
    print('COUCHES TEST',capture,details,flush=True)
    page.screenshot(path='/tmp/'+capture+'.png',full_page=True)
    assert any(c['drawn_pixels']>attendu for c in details['canvases']),details
    assert details['canvas_count']==1, 'Accumulation de canevas Leaflet : '+str(details)

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
          "() => document.querySelector('#map-status')?.textContent.includes('18 contours régionaux')",
          timeout=60000
        )
        assert page.locator("#year").input_value()=="2026"
        assert page.locator("#year").get_attribute("type")=="range"
        assert page.locator("#year-label").text_content()=="2026"
        assert page.locator("#level").input_value()=="region"
        assert page.evaluate("typeof L")=="object"
        assert page.locator(".leaflet-tile-pane").count()==1
        assert "Repère cartographique" not in page.locator("#map-status").text_content()
        inspecter_contours(page,100,"lieux-regions-2026")
        page.locator("#reference").uncheck()
        inspecter_contours(page,100,"lieux-regions-2026-sans-repere")
        page.locator("#reference").check()

        # DROM géographiquement visibles : cadrage sans changement d'année ou d'échelon.
        page.locator("#zoom").select_option("indien")
        assert page.locator("#year").input_value()=="2026"
        assert page.locator("#level").input_value()=="region"
        inspecter_contours(page,100,"lieux-region-mayotte-reunion-2026")
        page.locator("#search").fill("Mayotte")
        page.locator("#results button").filter(has_text="Région · COG 2026 · 06").first.click()
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('4 mai 2026')",
          timeout=30000
        )
        assert "06" in page.locator("#detail").text_content()
        assert "976R" in page.locator("#detail").text_content()
        page.locator("#level").select_option("departement")
        page.wait_for_function(
          "() => document.querySelector('#map-status')?.textContent.includes('101 contours départementaux')",
          timeout=30000
        )
        inspecter_contours(page,100,"lieux-departements-drom-2026")
        page.locator("#zoom").select_option("metropole")
        inspecter_contours(page,100,"lieux-departements-2026")

        page.locator("#level").select_option("region")
        page.locator("#year").evaluate("(el) => {el.value='2016';el.dispatchEvent(new Event('change',{bubbles:true}));}")
        page.wait_for_function(
          "() => document.querySelector('#map-status')?.textContent.includes('13 contours régionaux')",
          timeout=30000
        )
        inspecter_contours(page,100,"lieux-regions-2016")

        # Couches réellement millésimées ; ne jamais confondre un repère et
        # la géométrie géographique de la situation COG.
        def set_year(new_year):
            page.locator("#year").evaluate(
                "(el, y) => {el.value=String(y);el.dispatchEvent(new Event('change',{bubbles:true}));}",
                new_year)
        set_year(2019)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('COG au 1er janvier 2019')",
            timeout=30000)
        inspecter_contours(page,100,"lieux-regions-2019")
        page.locator("#search").fill("Bretagne")
        page.locator("#results button").filter(has_text="Région · COG 2019 · 53").click()
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Millésime 2019')",
            timeout=30000)
        assert "Repère cartographique" not in page.locator("#map-status").text_content()

        # En 2020, les limites proviennent de l'IGN ADMIN EXPRESS COG
        # du 20 novembre 2020, croisées avec le COG au 1er janvier.
        set_year(2020)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('IGN ADMIN EXPRESS COG, édition 2020-11-20')",
            timeout=30000)
        inspecter_contours(page,100,"lieux-regions-2020")
        assert "Repère cartographique" not in page.locator("#map-status").text_content()
        page.locator("#search").fill("Bretagne")
        page.locator("#results button").filter(has_text="Région · COG 2020 · 53").first.click()
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('2020-11-20')",
            timeout=30000)
        set_year(2025)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('COG au 1er janvier 2025')",
            timeout=30000)
        inspecter_contours(page,100,"lieux-regions-2025")
        page.locator("#level").select_option("departement")
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('101 contours départementaux')",
            timeout=30000)
        inspecter_contours(page,100,"lieux-departements-2025")
        set_year(2019)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('COG au 1er janvier 2019')",
            timeout=30000)
        inspecter_contours(page,100,"lieux-departements-2019")
        set_year(2017)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('IGN ADMIN EXPRESS COG, édition 2017-06-19')",
            timeout=30000)
        inspecter_contours(page,100,"lieux-departements-2017")
        assert "Repère cartographique" not in page.locator("#map-status").text_content()
        page.locator("#search").fill("Côtes-d'Armor")
        page.locator("#results button").filter(has_text="Département · COG 2017 · 22").first.click()
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('2017-06-19')",
            timeout=30000)
        page.locator("#level").select_option("region")
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('18 contours régionaux')",
            timeout=30000)
        inspecter_contours(page,100,"lieux-regions-2017")
        page.locator("#level").select_option("region")
        set_year(2016)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('13 contours régionaux')",
            timeout=30000)
        inspecter_contours(page,100,"lieux-regions-2016-reprise")

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
        inspecter_contours(page,100,"lieux-regions-2015")
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

        inspecter_contours(page,100,"lieux-departements-2015")

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
        inspecter_contours(page,100,"lieux-communes-2026")
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
        page.wait_for_function(
          "() => document.querySelector('#map-status')?.textContent.includes('contours communaux 2026 (et NON 2015)')",
          timeout=60000
        )
        inspecter_contours(page,100,"lieux-communes-repere-2015")
        assert not failures,failures
        page.screenshot(path=os.environ.get("ADLFI_CAPTURE","/tmp/lieux-publication.png"),full_page=True)
        print("PUBLICATION LIEUX : navigateur Leaflet, 13/22/96 états, Pactols et redirection OK")
        browser.close()


if __name__=="__main__":
    main()
