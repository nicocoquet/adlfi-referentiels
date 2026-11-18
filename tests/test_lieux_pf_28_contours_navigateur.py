"""Chromium : géométrie polynésienne présélectionnée, fiche, chronologie et exclusions."""
from __future__ import annotations
from test_lieux_corse_pactols_navigateur import serveur

def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(url+'/lieux/?zoom=pacifique&ref_cog=COMER:COM:98735&annee=2026&niveau=commune',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('28 communes de Polynésie')",
            timeout=60000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Papeete')",
            timeout=30000)
        detail=page.locator('#detail').text_content()
        assert 'Contour communal de référence cartographique Etalab 2026 affiché' in detail,detail
        assert 'fonds territoriaux diffusés en 2022' in detail,detail
        assert 'ni restitution historique' in detail.lower(),detail
        assert page.locator('.leaflet-overlay-pane canvas').count()==1
        page.locator('#search').fill('Papeete')
        page.wait_for_function("() => !document.querySelector('#results')?.hidden",timeout=10000)
        assert '98735' in page.locator('#results').text_content()
        page.locator('#year').evaluate(
            "(el) => { el.value='1975'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
        page.locator('#year').dispatch_event('change')
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('ne restitue pas les limites de 1975')",
            timeout=30000)
        for code,needle in [
            ('98745','anomalie topologique'),
            ('98726','pas encore été qualifiée')
        ]:
            page.goto(url+'/lieux/?zoom=pacifique&ref_cog=COMER:COM:'+code+
                      '&annee=2026&niveau=commune',wait_until='domcontentloaded',timeout=45000)
            page.wait_for_function(
                "() => document.querySelector('#map-status')?.textContent.includes('28 communes de Polynésie')",
                timeout=60000)
            page.wait_for_function(
                "(text) => document.querySelector('#detail')?.textContent.includes(text)",
                arg=needle,timeout=30000)
            assert 'Contour communal de référence cartographique Etalab 2026 affiché' not in page.locator('#detail').text_content()
        assert not errors,errors
        print('PF_28_NAVIGATEUR_OK — Papeete 2026, frise 1975, Tahaa et Makemo exclus')
        browser.close()

if __name__=='__main__':
    main()
