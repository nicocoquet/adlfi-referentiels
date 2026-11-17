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
        # Navigation clavier native du curseur : plus de boutons annexes.
        page.locator("#year").focus()
        page.locator("#year").press("ArrowLeft")
        page.wait_for_function(
          "() => document.querySelector('#map-status')?.textContent.includes('22 contours régionaux')",
          timeout=30000
        )
        assert page.locator("#year").input_value()=="2015"
        assert page.locator("#year-label").text_content()=="2015"
        inspecter_contours(page,100,"lieux-regions-2015")
        page.locator("#year").press("ArrowRight")
        page.wait_for_function(
          "() => document.querySelector('#map-status')?.textContent.includes('13 contours régionaux')",
          timeout=30000
        )
        assert page.locator("#year-label").text_content()=="2016"
        page.locator("#year").press("ArrowLeft")
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
        page.locator("#year").focus()
        page.locator("#year").press("ArrowRight")
        page.wait_for_function(
          "() => document.querySelector('#year-label')?.textContent === '2016'",
          timeout=30000
        )
        assert page.locator("#detail").get_by_text("Correspondance Pactols",exact=False).count()>=1
        page.locator("#year").press("End")
        page.wait_for_function(
          "() => document.querySelector('#year-label')?.textContent === '2026' && "
          "document.querySelector('#map-status')?.textContent.includes('contours communaux 2026')",
          timeout=60000
        )
        assert page.locator("#year").input_value()=="2026"
        inspecter_contours(page,100,"lieux-communes-2026")
        assert page.locator("#detail").get_by_text("Correspondance Pactols",exact=False).count()>=1

        # Recette nationale COG 2026 : fiches indépendantes de Pactols,
        # aucun contour inventé pour les communes d'outre-mer.
        page.locator("#search").fill("Papeete")
        page.locator("#results button").filter(
            has_text="Commune · COG 2026 · Polynésie française · 98735"
        ).first.click()
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Papeete')",
            timeout=30000)
        assert "Aucune limite de cette commune n’est affichée" in page.locator("#detail").text_content()
        assert page.locator("#level").input_value()=="commune"
        assert "ref_cog=COMER%3ACOM%3A98735" in page.url

        page.locator("#search").fill("Dembeni")
        page.locator("#results button").filter(
            has_text="Commune · COG 2026 · Mayotte · 97607"
        ).first.click()
        assert "26678/crtZcuFSJVYZU" in page.locator("#detail").text_content()
        assert "la correspondance Pactols–COG demeure à valider" in page.locator("#detail").text_content()
        assert page.locator("#detail").get_by_text(
            "Correspondance Pactols validée (2026)", exact=False
        ).count()==0

        page.locator("#search").fill("Acoua")
        page.locator("#results button").filter(
            has_text="Commune · COG 2026 · Mayotte · 97601"
        ).first.click()
        assert "26678/pcrtZfYYjyoUIE" in page.locator("#detail").text_content()
        assert "Correspondance Pactols validée (2026)" in page.locator("#detail").text_content()

        # Mayotte : deux familles documentaires de part et d'autre du 31 mars 2011.
        # Au 1er janvier 2007 : aucune observation dans les deux séries retenues.
        page.goto(base+"/lieux/?ref_cog=DROM%3ACOM%3A97607&annee=2007&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('État COG de Mayotte au 1er janvier 2007')",
            timeout=60000)
        assert "Aucun épisode de Mayotte n’est documenté" in page.locator("#detail").text_content()
        assert "ne prouve pas que les communes n’existaient pas auparavant" in page.locator("#detail").text_content()
        assert "26678/crtZcuFSJVYZU" in page.locator("#detail").text_content()
        assert page.locator("#detail").get_by_text(
            "Correspondance Pactols validée (2026)",exact=False).count()==0

        set_year(2008)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('État COG de Mayotte au 1er janvier 2008')",
            timeout=30000)
        text_ma=page.locator("#detail").text_content()
        assert "COMER · communes des collectivités et territoires d’outre-mer" in text_ma
        assert "2007-02-23 – 2011-03-31" in text_ma
        assert "correspondance Pactols–COG non validée" in text_ma

        page.goto(base+"/lieux/?ref_cog=DROM%3ACOM%3A97601&annee=2011&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('État COG de Mayotte au 1er janvier 2011')",
            timeout=60000)
        text_ma=page.locator("#detail").text_content()
        assert "COMER · communes des collectivités" in text_ma
        assert "avant le changement de statut effectif le 31 mars" in text_ma
        assert "Correspondance Pactols validée (2026)" in text_ma
        assert "26678/pcrtZfYYjyoUIE" in text_ma

        set_year(2012)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('État COG de Mayotte au 1er janvier 2012')",
            timeout=30000)
        text_ma=page.locator("#detail").text_content()
        assert "DROM · communes des départements et régions" in text_ma
        assert "2011-03-31 – en cours dans la source" in text_ma
        assert "976D · Département de Mayotte" in text_ma
        assert "sans contour historique de Mayotte" in text_ma

        set_year(2026)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('État COG de Mayotte au 1er janvier 2026')",
            timeout=30000)
        text_ma=page.locator("#detail").text_content()
        assert "976R · Département-Région de Mayotte" in text_ma
        assert "Correspondance Pactols validée (2026)" in text_ma
        assert "Les 16 correspondances Pactols approuvées pour 2026 ne sont pas rétroactives" in text_ma

        # Saint-Pierre-et-Miquelon : codes communaux 97501/97502 et collectivité
        # 975, sans assimiler l'année de la loi au début d'une commune.
        page.goto(base+"/lieux/?ref_cog=COMER%3ACOM%3A97501&annee=1976&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Saint-Pierre-et-Miquelon au 1er janvier 1976')",
          timeout=60000)
        t=page.locator("#detail").text_content()
        assert "Aucun épisode communal n’est documenté" in t
        assert "non sa date de création" in t
        assert "aucun nouvel alignement Pactols" in t
        assert page.locator("#detail").get_by_text("Correspondance Pactols validée (2026)",exact=False).count()==0

        set_year(1977)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Saint-Pierre-et-Miquelon au 1er janvier 1977')",
          timeout=30000)
        t=page.locator("#detail").text_content()
        assert "97501 · Miquelon-Langlade" in t
        assert "1976-07-21" in t
        assert "Département d’outre-mer (loi du 19 juillet 1976)" in t
        assert "La série COG COMER ne détermine pas le statut juridique historique" in t

        set_year(1985)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Saint-Pierre-et-Miquelon au 1er janvier 1985')",
          timeout=30000)
        assert "Département d’outre-mer" in page.locator("#detail").text_content()
        set_year(1986)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Saint-Pierre-et-Miquelon au 1er janvier 1986')",
          timeout=30000)
        assert "Collectivité territoriale (loi du 11 juin 1985)" in page.locator("#detail").text_content()
        set_year(2003)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Saint-Pierre-et-Miquelon au 1er janvier 2003')",
          timeout=30000)
        assert "Collectivité territoriale (loi du 11 juin 1985)" in page.locator("#detail").text_content()
        set_year(2004)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Saint-Pierre-et-Miquelon au 1er janvier 2004')",
          timeout=30000)
        assert "Collectivité d’outre-mer (article 74" in page.locator("#detail").text_content()

        page.goto(base+"/lieux/?ref_cog=COMER%3ATERRITOIRE%3A975&annee=1985&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Saint-Pierre-et-Miquelon au 1er janvier 1985')",
          timeout=60000)
        assert "Aucun épisode du code territorial 975" in page.locator("#detail").text_content()
        set_year(1986)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Saint-Pierre-et-Miquelon au 1er janvier 1986')",
          timeout=30000)
        t=page.locator("#detail").text_content()
        assert "975 · Saint-Pierre-et-Miquelon" in t
        assert "1985-06-15" in t
        assert "Aucune limite de cette commune n’est affichée" not in t

        page.locator("#search").fill("Kerguelen")
        page.locator("#results button").filter(
            has_text="District · COG 2026"
        ).first.click()
        assert "Archipel des Kerguelen" in page.locator("#detail").text_content()
        assert "n’est pas une commune dans le sélecteur territorial" in page.locator("#detail").text_content()
        assert page.locator("#level").input_value()=="commune"

        page.locator("#search").fill("Île des Faisans")
        page.locator("#results button").filter(
            has_text="Condominium · COG 2026"
        ).first.click()
        assert "COMER:CDM:98101" in page.locator("#detail").text_content()
        assert "Aucun contour de ce zonage" in page.locator("#detail").text_content()

        # Le COG 2026 ne devient pas une géométrie ni un nom historique.
        page.locator("#year").evaluate(
            "(el) => {el.value='2015';el.dispatchEvent(new Event('change',{bubbles:true}));}"
        )
        page.locator("#search").fill("Tahaa")
        page.locator("#results button").filter(has_text="Commune · COG 2026").first.click()
        assert "contour national 2026 présente une anomalie topologique" in page.locator("#detail").text_content()
        assert "Polynésie française · état au 1er janvier 2015" in page.locator("#detail").text_content()
        assert "1972-05-21" in page.locator("#detail").text_content()
        page.goto(base+"/lieux/?ref_cog=COMER%3ACOM%3A98745&annee=2015",
                  wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Tahaa')",
            timeout=60000
        )
        assert "Polynésie française · état au 1er janvier 2015" in page.locator("#detail").text_content()
        assert "1972-05-21" in page.locator("#detail").text_content()
        assert "26678/pcrteZcqWgVUaT" in page.locator("#detail").text_content()
        assert "contour national 2026 présente une anomalie topologique" in page.locator("#detail").text_content()

        # Guyane : états COG documentés indépendants des contours 2026.
        page.goto(base+"/lieux/?ref_cog=DROM%3ACOM%3A97301&annee=1969",
                  wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Approuague-Kaw')",
            timeout=60000)
        assert "Libellé à la date sélectionnée" in page.locator("#detail").text_content()
        assert "correspondances Pactols validées pour 2026 ne sont pas rétroactives" in page.locator("#detail").text_content()
        assert "Aucun contour historique de Guyane n’est affiché" in page.locator("#detail").text_content()
        assert page.locator("#year").input_value()=="1969"
        set_year(1970)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('État COG de Guyane au 1er janvier 1970')",
            timeout=30000)
        assert "Régina" in page.locator("#detail").text_content()

        # Recherche : les quatre autorités anciennes ont leurs propres codes/ARK.
        page.locator("#search").fill("Approuague (chef-lieu Régina)")
        page.locator("#results button").filter(
            has_text="Commune historique · Guyane · 97351"
        ).first.click()
        assert page.locator("#year").input_value()=="1969"
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('26678/pcrtIPUh7AuXTg')",
            timeout=30000)
        assert "Fusion simple (MOD 31)" in page.locator("#detail").text_content()
        assert "97301 · Régina" in page.locator("#detail").text_content()
        assert "lien non encore arbitré" in page.locator("#detail").text_content()
        assert "ref_cog_historique=97351" in page.url

        page.goto(base+"/lieux/?ref_cog_historique=97355&annee=1953",
                  wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Moyenne-Mana')",
            timeout=60000)
        assert "26678/pcrtbvSjznYKWV" in page.locator("#detail").text_content()
        assert "97306 · Mana" in page.locator("#detail").text_content()
        set_year(1970)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Aucun épisode actif')",
            timeout=30000)
        assert "absence historique du lieu" in page.locator("#detail").text_content()

        page.goto(base+"/lieux/?ref_cog=DROM%3ACOM%3A97361&annee=1988",
                  wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Aucun épisode actif')",
            timeout=60000)
        set_year(1989)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Libellé à la date sélectionnée')",
            timeout=30000)
        assert "Awala-Yalimapo" in page.locator("#detail").text_content()
        assert "Correspondance Pactols validée (2026)" in page.locator("#detail").text_content()
        assert "Aucun contour historique de Guyane n’est affiché" in page.locator("#detail").text_content()

        # Martinique : les 34 codes ont un état COG distinct de l'ARK valide pour 2026.
        page.goto(base+"/lieux/?ref_cog=DROM%3ACOM%3A97234&annee=1950&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('État COG de Martinique au 1er janvier 1950')",
            timeout=60000)
        text_m=page.locator("#detail").text_content()
        assert "Aucun épisode actif" in text_m
        assert "Correspondance Pactols validée (2026)" in text_m
        assert "26678/pcrtFk4CSrgt1O" in text_m
        assert "Aucun contour historique de Martinique n’est affiché" in text_m
        set_year(1951)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Libellé à la date sélectionnée')",
            timeout=30000)
        assert "Bellefontaine" in page.locator("#detail").text_content()

        page.goto(base+"/lieux/?ref_cog=DROM%3ACOM%3A97233&annee=1949&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('État COG de Martinique au 1er janvier 1949')",
            timeout=60000)
        assert "Aucun épisode actif" in page.locator("#detail").text_content()
        set_year(1950)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Libellé à la date sélectionnée')",
            timeout=30000)
        assert "Le Morne-Vert" in page.locator("#detail").text_content()
        assert page.locator("#year").input_value()=="1950"

        page.goto(base+"/lieux/?ref_cog=DROM%3ACOM%3A97209&annee=1947",
                  wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Fort-de-France') && document.querySelector('#detail')?.textContent.includes('État COG de Martinique')",
            timeout=60000)
        assert "Aucun contour historique de Martinique n’est affiché" in page.locator("#detail").text_content()

        # Guadeloupe : libellé du même code 97107 avant/après le 4 juin 1976.
        page.goto(base+"/lieux/?ref_cog=DROM%3ACOM%3A97107&annee=1976&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Guadeloupe au 1er janvier 1976')",
          timeout=60000)
        text_g=page.locator("#detail").text_content()
        assert "Capesterre-de-Guadeloupe" in text_g
        assert "Correspondance Pactols validée (2026)" in text_g
        assert "26678/pcrtIusOs61efG" in text_g
        assert "Aucun contour historique de Guadeloupe n’est affiché" in text_g
        set_year(1977)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Guadeloupe au 1er janvier 1977')",
          timeout=30000)
        assert "Capesterre-Belle-Eau" in page.locator("#detail").text_content()
        assert page.locator("#year").input_value()=="1977"

        # Deux anciens codes documentaires, sans ARK ni code de destination COG.
        page.goto(base+"/lieux/?ref_cog_historique_guadeloupe=97123&annee=2007&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Saint-Barthélemy') && document.querySelector('#detail')?.textContent.includes('MOD 30')",
          timeout=60000)
        text_g=page.locator("#detail").text_content()
        assert "Ancien code INSEE" in text_g
        assert "Non renseigné dans le fichier des mouvements COG" in text_g
        assert "Aucune dans l’export RDF Lieux" in text_g
        assert "aucune équivalence automatique" in text_g
        assert "Aucun contour historique de Guadeloupe n’est affiché" in text_g
        assert "97123" in page.url
        set_year(2008)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Aucun épisode actif')",
          timeout=30000)

        page.locator("#search").fill("97127")
        page.locator("#results button").filter(
          has_text="Ancienne commune · Guadeloupe · 97127"
        ).first.click()
        assert page.locator("#year").input_value()=="2007"
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Saint-Martin')",
          timeout=30000)
        assert "ref_cog_historique_guadeloupe=97127" in page.url
        assert "COM_AP" in page.locator("#detail").text_content()

        # Saint-Barthélemy / Saint-Martin : succession expressément prévue par
        # la loi, distincte du mouvement MOD 30 et des codes cinq positions.
        page.goto(base+"/lieux/?ref_cog_historique_guadeloupe=97123&annee=2007&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('transition 2007 · état au 1er janvier 2007')",
          timeout=60000)
        text_2007=page.locator("#detail").text_content()
        assert "Ancienne commune de Guadeloupe" in text_2007
        assert "97123 · Saint-Barthélemy" in text_2007
        assert "977 · Saint-Barthélemy" in text_2007
        assert "97701 · ce n’est pas une nouvelle commune" in text_2007
        assert "MOD 30 · 23 février 2007 ; COM_AP vide" in text_2007
        assert "Loi organique n° 2007-223, article 18-X" in text_2007
        assert "La succession juridique n’est pas une équivalence Pactols" in text_2007
        assert page.locator("#detail").get_by_text(
            "Correspondance Pactols validée (2026)",exact=False).count()==0
        page.locator("#detail").get_by_text(
            "Consulter la collectivité successeure (977)").click()
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Collectivité d’outre-mer') && document.querySelector('#detail')?.textContent.includes('état au 1er janvier 2008')",
          timeout=60000)
        assert "ref_cog=COMER%3ATERRITOIRE%3A977" in page.url
        assert "977 · Saint-Barthélemy" in page.locator("#detail").text_content()
        assert "23 février 2007" in page.locator("#detail").text_content()

        page.goto(base+"/lieux/?ref_cog=COMER%3ACOM%3A97701&annee=2008&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('97701 · Saint-Barthélemy')",
          timeout=60000)
        assert "Code d’application à cinq positions, pas une commune" in page.locator("#detail").text_content()
        assert "pas une nouvelle commune" in page.locator("#detail").text_content()

        page.goto(base+"/lieux/?ref_cog_historique_guadeloupe=97127&annee=2007&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Loi organique n° 2007-223, article 18-XI')",
          timeout=60000)
        text_sm=page.locator("#detail").text_content()
        assert "97127 · Saint-Martin" in text_sm
        assert "978 · Saint-Martin" in text_sm
        assert "97801 · ce n’est pas une nouvelle commune" in text_sm
        assert "COM_AP vide" in text_sm
        set_year(2008)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('transition 2007 · état au 1er janvier 2008')",
          timeout=30000)
        assert "Aucun épisode de ce code (97127) n’est actif" in page.locator("#detail").text_content()
        page.goto(base+"/lieux/?ref_cog=COMER%3ATERRITOIRE%3A978&annee=2007&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('transition 2007 · état au 1er janvier 2007')",
          timeout=60000)
        assert "Aucun épisode de ce code (978) n’est actif" in page.locator("#detail").text_content()
        set_year(2008)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('transition 2007 · état au 1er janvier 2008')",
          timeout=30000)
        assert "978 · Saint-Martin" in page.locator("#detail").text_content()
        assert "Collectivité d’outre-mer" in page.locator("#detail").text_content()

        # Polynésie : 48 communes COG ; année 1972 avant première attestation
        # du 21 mai ; pas de 98 communes associées inventées depuis le COG.
        page.goto(base+"/lieux/?ref_cog=COMER%3ACOM%3A98711&annee=1972&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Polynésie française · état au 1er janvier 1972')",
          timeout=60000)
        pf=page.locator("#detail").text_content()
        assert "Aucun épisode COG pour le code 98711" in pf
        assert "Le curseur représente le 1er janvier 1972" in pf
        assert "98, réparties dans 30 des 48 communes" in pf
        assert "44 communes ajoutées à quatre communes préexistantes" in pf
        assert "Aucune géométrie historique n’est publiée" in pf
        assert "correspondance Pactols–COG communale est validée pour le seul millésime 2026" in pf
        assert "26678/pcrtwSlYRcWVFw" in pf
        set_year(1973)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Polynésie française · état au 1er janvier 1973')",
          timeout=30000)
        pf=page.locator("#detail").text_content()
        assert "98711 · Anaa" in pf
        assert "Correspondance Pactols validée (2026)" in pf
        assert "1972-05-21" in pf
        assert "Commune de Polynésie française" in pf

        page.goto(base+"/lieux/?ref_cog=COMER%3ATERRITOIRE%3A987&annee=2007&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Polynésie française · état au 1er janvier 2007')",
          timeout=60000)
        pf=page.locator("#detail").text_content()
        assert "987 · Polynésie française" in pf
        assert "98799 Clipperton" in pf
        assert "Correspondance Pactols validée (2026)" not in pf
        assert "Il n’est pas une des 48 communes actuelles" in pf
        set_year(2008)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Polynésie française · état au 1er janvier 2008')",
          timeout=30000)
        assert "Code historique distinct à cette date" not in page.locator("#detail").text_content()
        page.goto(base+"/lieux/?ref_cog=COMER%3ACOM%3A98735&annee=2026&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('98735 · Papeete')",
          timeout=60000)
        pf=page.locator("#detail").text_content()
        assert "Commune de Polynésie française" in pf
        assert "26678/pcrtr90gKcAXiG" in pf
        assert "Correspondance Pactols validée (2026)" in pf
        assert "ISPF" in pf
        assert "n’est pas la date de création de toutes les communes" in pf

        # Wallis-et-Futuna : trois CIR non communales, loi 1961 ≠ COG 1985.
        page.goto(base+"/lieux/?ref_cog=COMER%3ATERRITOIRE%3A986&annee=1962&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Wallis-et-Futuna au 1er janvier 1962')",
          timeout=60000)
        wf=page.locator("#detail").text_content()
        assert "Aucun épisode du code 986 n’est documenté" in wf
        assert "98609 · Wallis-et-Futuna" in wf
        assert "Trois circonscriptions territoriales prévues par la loi" in wf
        assert "Aucune commune à Wallis-et-Futuna" in wf
        assert "98607 du COG historique porte le libellé « Nouvelle-Calédonie »" in wf
        assert "aucun alignement Pactols" in wf
        page.locator("#search").fill("98609")
        page.wait_for_function(
          "() => [...document.querySelectorAll('#results button')].some(x => x.textContent.includes('Wallis-et-Futuna'))",
          timeout=30000)
        page.locator("#results button").filter(has_text="Wallis-et-Futuna").first.click()
        assert "ref_cog=COMER%3ATERRITOIRE%3A986" in page.url
        set_year(1985)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Wallis-et-Futuna au 1er janvier 1985')",
          timeout=30000)
        wf=page.locator("#detail").text_content()
        assert "986 · Wallis-et-Futuna" in wf
        assert "1985-01-01" in wf
        assert "Alo (98611), Sigave (98612), Uvea (98613)" in wf

        page.goto(base+"/lieux/?ref_cog=COMER%3ACIR%3A98611&annee=1984&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Wallis-et-Futuna au 1er janvier 1984')",
          timeout=60000)
        wf=page.locator("#detail").text_content()
        assert "Aucun épisode du code 98611 n’est documenté" in wf
        assert "Leur codification COG propre ne débute qu’en 1985" in wf
        set_year(1985)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de Wallis-et-Futuna au 1er janvier 1985')",
          timeout=30000)
        wf=page.locator("#detail").text_content()
        assert "98611 · Alo" in wf
        assert "Circonscription territoriale (non commune)" in wf
        assert "1985-01-01" in wf
        assert "Aucune commune à Wallis-et-Futuna" in wf
        assert "aucune assimilation des circonscriptions à des communes" in wf

        page.goto(base+"/lieux/?ref_cog=COMER%3ACIR%3A98613&annee=2026&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('98613 · Uvea')",
          timeout=60000)
        assert "Circonscription territoriale (non commune)" in page.locator("#detail").text_content()

        # La Réunion : même code Saint-Louis avant/après la division du 5 février 1965.
        page.goto(base+"/lieux/?ref_cog=DROM%3ACOM%3A97414&annee=1965&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de La Réunion au 1er janvier 1965')",
          timeout=60000)
        text_r=page.locator("#detail").text_content()
        assert "Saint-Louis" in text_r and "97414" in text_r
        assert "Avant la division du 5 février 1965" in text_r
        assert "Cilaos (97424, nouveau code)" in text_r
        assert "Aucun contour historique de La Réunion n’est affiché" in text_r
        assert "Correspondance Pactols validée (2026)" in text_r
        assert "26678/pcrtBwoUOdthOV" in text_r
        set_year(1966)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de La Réunion au 1er janvier 1966')",
          timeout=30000)
        assert "Après la division du 5 février 1965" in page.locator("#detail").text_content()
        assert "Période code–libellé COG" in page.locator("#detail").text_content()

        # Cilaos ne possède pas d'état au 1er janvier 1965, contrairement à 1966.
        page.goto(base+"/lieux/?ref_cog=DROM%3ACOM%3A97424&annee=1965&niveau=commune",
                  wait_until="domcontentloaded")
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('État COG de La Réunion au 1er janvier 1965')",
          timeout=60000)
        text_r=page.locator("#detail").text_content()
        assert "Aucun épisode actif" in text_r
        assert "Cilaos n’apparaît dans les états au 1er janvier qu’en 1966" in text_r
        assert "Correspondance Pactols validée (2026)" in text_r
        set_year(1966)
        page.wait_for_function(
          "() => document.querySelector('#detail')?.textContent.includes('Libellé COG à la date sélectionnée')",
          timeout=30000)
        text_r=page.locator("#detail").text_content()
        assert "Cilaos" in text_r and "1965-02-05" in text_r
        assert "Aucun contour historique de La Réunion n’est affiché" in text_r

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
