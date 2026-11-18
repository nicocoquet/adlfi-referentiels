"""Chromium : contour néo-calédonien 2026, fiche, recherche, frise, Dumbéa exclue."""
from __future__ import annotations
from test_lieux_corse_pactols_navigateur import serveur

def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        code='98827'  # Poya, commune sur deux provinces ; son contour ne fixe aucune province.
        page.goto(url+'/lieux/?ref_cog=COMER:COM:'+code+
                  '&annee=2026&niveau=commune',wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('32 communes de Nouvelle-Calédonie')",
            timeout=60000)
        page.wait_for_function(
            "(code) => document.querySelector('#detail')?.textContent.includes(code)",
            arg=code,timeout=30000)
        detail=page.locator('#detail').text_content()
        assert 'Poya' in detail and 'Contour communal de référence 2026 affiché' in detail,detail
        assert 'non homologué comme limite juridique' in detail,detail
        assert page.locator('.leaflet-overlay-pane canvas').count()==1
        page.locator('#search').fill('Poya')
        page.wait_for_function("() => !document.querySelector('#results')?.hidden")
        assert '98827' in page.locator('#results').text_content()
        page.locator('#year').evaluate(
            "(el) => { el.value='1975'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
        page.locator('#year').dispatch_event('change')
        page.wait_for_function("() => document.querySelector('#year-label')?.textContent.includes('1975')")
        page.wait_for_function("() => document.querySelector('#detail')?.textContent.includes('ne restitue pas les limites de 1975')")
        page.goto(url+'/lieux/?ref_cog=COMER:COM:98805&annee=2026&niveau=commune',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('32 communes de Nouvelle-Calédonie')",
            timeout=60000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('anomalie topologique')",
            timeout=30000)
        assert 'Contour communal de référence 2026 affiché' not in page.locator('#detail').text_content()
        assert not errors,errors
        print('NC_32_NAVIGATEUR_OK — Poya, frise 1975, Dumbéa sans contour')
        browser.close()

if __name__=='__main__':
    main()
