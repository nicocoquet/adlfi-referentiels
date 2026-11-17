"""Chromium : les 129 communes des DROM disposent de contours datés 2026."""
from __future__ import annotations
from test_lieux_corse_pactols_navigateur import serveur

def main():
    from playwright.sync_api import sync_playwright
    cases=[
        ("97101","DROM:COM:97101","antilles"),
        ("97209","DROM:COM:97209","antilles"),
        ("97302","DROM:COM:97302","antilles"),
        ("97411","DROM:COM:97411","indien"),
        ("97611","DROM:COM:97611","indien"),
    ]
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1360,"height":900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        for code,ref,zoom in cases:
            page.goto(url+"/lieux/?zoom="+zoom+"&ref_cog="+ref+"&annee=2026&niveau=commune",
                      wait_until="domcontentloaded",timeout=45000)
            page.wait_for_function("() => document.querySelector('#map-status')?.textContent.includes('129 communes des cinq DROM')",
                timeout=60000)
            page.wait_for_function("(code) => document.querySelector('#detail')?.textContent.includes(code)",
                arg=code,timeout=30000)
            detail=page.locator("#detail").text_content()
            assert "Contour communal de référence 2026 affiché" in detail,detail
            assert "Pactols validée (2026)" in detail,detail
            assert page.locator(".leaflet-overlay-pane canvas").count()==1
            page.locator("#year").evaluate(
                "(el) => { el.value='1975'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
            page.locator("#year").dispatch_event("change")
            page.wait_for_function("() => document.querySelector('#year-label')?.textContent.includes('1975')")
            page.wait_for_function("() => document.querySelector('#detail')?.textContent.includes('ne restitue pas les limites de 1975')")
            assert "Contour communal de référence 2026 affiché" not in page.locator("#detail").text_content()
        assert not errors,errors
        print("DROM_129_NAVIGATEUR_OK — cinq DROM, fiches 2026 et frise 1975 sans rétroprojection")
        browser.close()

if __name__=="__main__": main()
